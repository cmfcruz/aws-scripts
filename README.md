# aws-scripts
Python scripts for some AWS tasks.

- [convert-to-nvm.sh](convert-to-nvm.sh): helps in converting the fstab file of the EC2 instance for NVM support.
- [instance_type_summary.py](instance_type_summary.py): summarizes the number of EC2 instances and available reservations in a particular AWS region.
- [create-image-then-terminate.py](create-image-then-terminate.py): Creates an image of an instance before terminating the instance.  Automatically disables the termination protection of the instance.  Use with caution.