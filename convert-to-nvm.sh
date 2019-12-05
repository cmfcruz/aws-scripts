#!/bin/bash

ssh $server << EOF
# Create fstab backup
cp /etc/fstab /etc/fstab.backup
# Update fstab to use new mount names
sed -i 's@/dev/sd@/dev/xvd@g' /etc/fstab
# Change the partition mounts to labels
for partition in `cat /etc/fstab | grep /dev/xvd | awk '{print $1}'`
do
  sed -i "s@$partition@$(blkid | grep $partition | awk '{print $2}')@g" /etc/fstab
done
EOF

#Get Instance ID
instance_id=$(ssh $server 'curl http://169.254.169.254/latest/meta-data/instance-id')
ssh $server 'sudo init 0'
aws ec2 modify-instance-attribute --instance-id $instance_id --ena-support
