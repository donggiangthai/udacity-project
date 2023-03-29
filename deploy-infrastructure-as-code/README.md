# Start using cloudformation.py script for creating the AWS infrastructure

## Example usage

### Export variable

Assume that we're using PowerShell and this is just a session variable

```
Set-Variable -Name course -Value deploy-infrastructure-as-code | `
Set-Variable -Name lesson -Value deploy-a-high-availability-web-app-using-cloudformation
```

### Note

- Remember to always start at the script location
- Virtualenv is suggested. My repository will ignore the venv folder that contains the virtual environment, so install the virtualenv and create one virtual environment for yourself follow these steps below:

  - Install the virtualenv package

    ```
    pip install virtualenv
    ```

  - Create venv folder and virtual environment

    ```
    mkdir venv; `
    Set-Location .\venv\; `
    virtualenv infrastructure-as-code --python python3.10.10
    ```

  - Activate the virtual environment

    ```
    .\infrastructure-as-code\Scripts\activate; `
    Set-Location ..\
    ```

- Be-sure to install all dependencies package at the `requirements.txt` file

  ```
  pip install -r .\$course\requirements.txt
  ```


### Creating the network

Including all the network things 
like VPC, subnets, internet gateway, route table, etc.

```
python3 cloudformation.py `
create `
--stack-name NetWorking `
--template-body .\$course\$lesson\networking.yml `
--parameters-file .\$course\$lesson\networking-parameters.json
```

### Creating the servers

Including all the dependencies for the web server and itself 
like security groups, IAM role, IAM instance profile, auto-scaling group, load balancer, etc.

```
python3 cloudformation.py `
create `
--stack-name Servers `
--template-body .\$course\$lesson\servers.yml `
--parameters-file .\$course\$lesson\servers-parameters.json `
--capabilities "CAPABILITY_IAM" "CAPABILITY_NAMED_IAM"
```

### Creating the bastion host

This template includes 2 EC2 instances as the bastion host, 
which is located in the public subnet for each availability zone.

```
python3 cloudformation.py `
create `
--stack-name BastionHost `
--template-body .\$course\$lesson\bastion-host.yml `
--parameters-file .\$course\$lesson\bastion-host-parameters.json `
--capabilities "CAPABILITY_IAM" "CAPABILITY_NAMED_IAM"
```

### Quickly removing the CloudFormation stacks

Remember this is an order list of the stack name. 
If your stack is dependent on others, then put the dependencies first.

```
python3 cloudformation.py `
delete `
--stack-name BastionHost Servers NetWorking
```
