'''
Generates the summary of all on-demand instances in the target AWS account.
This is to help prepare for instance reservation.
'''
import boto3
import json


def main():
    instance_summary = get_instance_summary()
    reservation_summary = get_reservation_summary()
    print(json.dumps({
        'instance_summary': instance_summary,
        'reservation_summary': reservation_summary
    }))


def get_instance_summary():
    instance_summary = {}
    ec2 = boto3.client('ec2')
    response = ec2.describe_instances()
    for reservation in response.get('Reservations'):
        for instance in reservation.get('Instances'):
            if instance.get('InstanceLifecycle') is None \
                    and instance.get('State').get('Name') == 'running':
                instance_type = instance.get('InstanceType')
                if 'Platform' in instance.keys():
                    instance_type = instance_type + '-' + \
                        instance.get('Platform')
                if instance_type not in instance_summary.keys():
                    instance_summary[instance_type] = 1
                else:
                    instance_summary[instance_type] \
                        = instance_summary[instance_type] + 1
    return instance_summary


def get_reservation_summary():
    reservation_summary = {}
    ec2 = boto3.client('ec2')
    response = ec2.describe_reserved_instances()
    for reservation in response.get('ReservedInstances'):
        if reservation.get('State') == 'active':
            label = reservation.get('InstanceType') + '-' + \
                reservation.get('ProductDescription')
            if label in reservation_summary.keys():
                reservation_summary[label] = reservation_summary[label] + \
                    reservation.get('InstanceCount')
            else:
                reservation_summary[label] = reservation.get('InstanceCount')
    return reservation_summary


if __name__ == "__main__":
    main()
