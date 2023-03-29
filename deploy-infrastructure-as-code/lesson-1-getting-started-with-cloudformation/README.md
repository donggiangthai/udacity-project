# Using AWS CLI for CloudFormation stack creation

In the powershell or other terminal, change the location into this folder. My recommend is using the `Set-Location` command on the powershell terminal.

For example: 
```
Set-Location $env:UserProfile\Desktop\code\Udacity\deploy-infrastructure-as-code\lesson-1-getting-started-with-cloudformation
```

Now we're using the AWS CLI to create the `CloudFormation` stack.

## Create stack:

Create the security group first because it must be used by the EC2 instance.

```
aws cloudformation create-stack --stack-name SecurityGroup --template-body file://security-group.yml --region 'us-east-1' --on-failure DELETE
```

Checking the status on the `CloudFormation` console, after the stack is created successfully then moving into the ec2 instance.

```
aws cloudformation create-stack --stack-name EC2Instance --template-body file://ec2-instance.yml --region 'us-east-1' --on-failure DELETE
```

## Delete stack:

After everything are done we need to clean our resource by using this command:

```
aws cloudformation delete-stack --stack-name EC2Instance --region 'us-east-1'
```

You can leave the SecurityGroup alone, because it wont charge any cent. But the best practice are clean up everything after the lab, so we will run another command:

```
aws cloudformation delete-stack --stack-name SecurityGroup --region 'us-east-1'
```

# Note

If you want to use the `ec2 instance profile` as mine, remember to add the `iam:passrole` for your `IAM Role` as the `inline policy` otherwise the stack creation for the ec2 instance will fail