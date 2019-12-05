#!/usr/bin/env python3
import argparse
import boto3
import time


def main():
    arguments = get_arguments()
    # Map parameters to local variables
    instance_id = arguments.instance_id
    region = arguments.region
    try:
        ec2 = Ec2_helper(region)
        image_id = ec2.create_ami(instance_id)
        ec2.wait_for_image(image_id)
        ec2.terminate_instance(instance_id)
        print('Done.')
    except Exception as err:
        print(err)


def get_arguments():
    '''
    Parses the command arguments for processing.
    '''
    parser = argparse.ArgumentParser('create-image-then-terminate.py')
    parser.add_argument(
        '--instance-id',
        help='The Instance ID of the instance to be terminated.'
    )
    parser.add_argument(
        '--region',
        help='The region where the instance is hosted.'
    )
    arguments = parser.parse_args()
    return arguments


class Ec2_helper:
    def __init__(self, region):
        self.ec2_client = boto3.client('ec2', region_name=region)
        return None

    def create_ami(self, instance_id):
        '''
        Creates an image of the instance using available instance details
        '''
        # Generate a timestamp to make the image unique
        local_time = time.localtime()
        timestamp = time.strftime("%Y%m%d%H%M%S", local_time)
        instance_details = self.describe_instance(instance_id)
        image_name = f"{instance_details['instance_name']}-{timestamp}"

        # Create the image
        image = self.ec2_client.create_image(
            Description=instance_details.get('instance_description'),
            InstanceId=instance_id,
            Name=image_name,
            NoReboot=False
        )

        # Display the details of the AMI image
        print('Creating image for instance:', instance_id)
        print('AMI ID:', image.get('ImageId'))
        print('AMI Name:', image_name)
        print('AMI Description:', instance_details.get('instance_description'))
        return image.get('ImageId')

    def describe_instance(self, instance_id):
        '''
        Generates a single string description of the instance to help provide
        parameters on how to restore the image to a working EC2 instance.
        '''
        response = self.ec2_client.describe_instances(
            InstanceIds=[instance_id]
        )
        instance = response['Reservations'][0]['Instances'][0]
        key_name = instance.get('KeyName')
        for tag in instance.get('Tags'):
            if tag.get('Key') == 'Name':
                instance_name = tag.get('Value')
        # TODO: transform block device mappings for compatibility
        block_device_mappings = instance.get('BlockDeviceMappings')
        instance_description = f'Name={instance_name}, KeyName={key_name}'
        instance_details = {
            'block_device_mappings': block_device_mappings,
            'instance_name': instance_name,
            'instance_description': instance_description
        }
        return instance_details

    def get_image_details(self, image_id):
        '''
        Retrieves the details of the created image for viewing of the user.
        '''
        image_details = self.ec2_client.describe_images(
            ImageIds=[image_id]
        )
        return image_details

    def terminate_instance(self, instance_id):
        self.ec2_client.modify_instance_attribute(
            DisableApiTermination={
                'Value': False
            },
            InstanceId=instance_id
        )
        self.ec2_client.terminate_instances(
            InstanceIds=[instance_id]
        )
        return None

    def wait_for_image(self, image):
        waiter = self.ec2_client.get_waiter('image_available')
        waiter.wait(
            ImageIds=[image],
            WaiterConfig={
                'Delay': 15,  # check image status every 15 seconds
                'MaxAttempts': 120  # wait for a maximum of 30 minutes
            }
        )
        return None


if __name__ == "__main__":
    main()
