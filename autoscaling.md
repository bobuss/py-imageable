Création du security-group
--------------------------

aws ec2 create-security-group \
  --group-name bob-web \
  --description "Serveurs web bottle" \
  --profile insset

{
    "return": "true",
    "GroupId": "sg-49b62522"
}

aws ec2 authorize-security-group-ingress \
  --group-name bob-web \
  --protocol tcp \
  --port 22 \
  --profile insset
{
    "return": "true"
}

aws ec2 authorize-security-group-ingress \
  --group-name bob-web \
  --protocol tcp \
  --port 5000 \
  --profile insset
{
    "return": "true"
}


Lancement d'instances
---------------------

aws ec2 run-instances \
  --image-id ami-7daee114 \
  --instance-type t1.micro \
  --region us-east-1 \
  --key MyKeyPair \
  --user-data file://user-data-file \
  --security-groups '["bob-web"]' \
  --profile insset



Le load balancer
----------------

aws elb create-load-balancer \
  --load-balancer-name bob-demo \
  --availability-zones us-east-1d \
  --listeners "LoadBalancerPort=80,InstancePort=5000,Protocol=http" \
  --profile insset
{
    "DNSName": "bob-demo-177107451.us-east-1.elb.amazonaws.com"
}


Ses tests de viabilité d'une instance
-------------------------------------

aws elb configure-health-check \
  --load-balancer-name bob-demo \
  --health-check Target="HTTP:5000/",Interval=10,Timeout=5,UnhealthyThreshold=2,HealthyThreshold=2 \
  --profile insset
{
    "HealthCheck": {
        "HealthyThreshold": 2,
        "Interval": 10,
        "Target": "HTTP:5000/",
        "Timeout": 5,
        "UnhealthyThreshold": 2
    }
}


La configuration de lancement
-----------------------------

aws autoscaling create-launch-configuration \
  --launch-configuration-name bob-lc-tmp \
  --image-id ami-7daee114 \
  --instance-type t1.micro \
  --security-groups '["bob-web"]' \
  --user-data file://user-data-file \
  --key-name MyKeyPair \
  --profile insset
{}


Le groupe d'autoscaling
-----------------------

aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name bob-asg \
  --launch-configuration-name bob-lc \
  --availability-zones us-east-1d \
  --min-size 0 --max-size 0 \
  --load-balancer-names bob-demo \
  --health-check-type ELB \
  --health-check-grace-period 300 \
  --profile insset
{}


Triggers de mise à l'echelle
----------------------------

aws autoscaling put-scaling-policy \
  --policy-name bob-scale-up \
  --auto-scaling-group-name bob-asg \
  --scaling-adjustment 50 \
  --adjustment-type PercentChangeInCapacity \
  --cooldown 300 \
  --profile insset
{
    "PolicyARN": "arn:aws:autoscaling:us-east-1:180843797005:scalingPolicy:74906b4f-9aec-4e12-b21b-e845b8656fc7:autoScalingGroupName/bob-asg:policyName/bob-scale-up"
}

aws autoscaling put-scaling-policy \
  --policy-name bob-scale-down \
  --auto-scaling-group-name bob-asg \
  --scaling-adjustment -1 \
  --adjustment-type ChangeInCapacity \
  --cooldown 300 \
  --profile insset
{
    "PolicyARN": "arn:aws:autoscaling:us-east-1:180843797005:scalingPolicy:a539161a-f713-495f-bcf6-619c690a397f:autoScalingGroupName/bob-asg:policyName/bob-scale-down"
}

aws cloudwatch put-metric-alarm \
  --alarm-name bob-highcpualarm \
  --comparison-operator GreaterThanThreshold \
  --statistic Average \
  --metric-name CPUUtilization \
  --namespace "AWS/EC2" \
  --dimensions "Name=AutoScalingGroupName,Value=bob-asg" \
  --period 60 \
  --threshold 70 \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:autoscaling:us-east-1:180843797005:scalingPolicy:74906b4f-9aec-4e12-b21b-e845b8656fc7:autoScalingGroupName/bob-asg:policyName/bob-scale-up \
  --profile insset
{}

aws cloudwatch put-metric-alarm \
  --alarm-name bob-lowcpualarm \
  --comparison-operator LessThanThreshold \
  --statistic Average \
  --metric-name CPUUtilization \
  --namespace "AWS/EC2" \
  --dimensions "Name=AutoScalingGroupName,Value=bob-asg" \
  --period 60 \
  --threshold 36 \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:autoscaling:us-east-1:180843797005:scalingPolicy:a539161a-f713-495f-bcf6-619c690a397f:autoScalingGroupName/bob-asg:policyName/bob-scale-down \
  --profile insset
{}

aws cloudwatch put-metric-alarm \
  --alarm-name bob-highlatencyalarm \
  --comparison-operator GreaterThanThreshold \
  --statistic Average \
  --metric-name Latency \
  --namespace "AWS/ELB" \
  --dimensions "Name=LoadBalancerName,Value=upicardie-asdemo" \
  --period 60 \
  --threshold 3 \
  --evaluation-periods 1 \
  --alarm-actions arn:aws:autoscaling:us-east-1:180843797005:scalingPolicy:74906b4f-9aec-4e12-b21b-e845b8656fc7:autoScalingGroupName/bob-asg:policyName/bob-scale-up \
  --profile insset


Mise en marche
--------------

aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name bob-asg \
  --min-size 2 \
  --max-size 12 \
  --profile insset
{}



