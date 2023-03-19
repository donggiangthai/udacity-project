# Initializing environment

Create a file called `credentials` and store the aws key as the `default` profile on your `.aws` folder inside of the `%USERPROFILE%`. If the `.aws` not exist, create one. Using `Ctrl+R` and enter the `%USERPROFILE%` to redirect you into the user folder.

Here is the sample of `credentials` file

```
[default]
aws_access_key_id = XXX...XXX
aws_secret_access_key = XYZ...ZYX
aws_session_token = F...n//////////w...N/v...R+Z...4/O...C+E...a+jJ//g...c/9...u+8...b+x...A+D...I
```

Beside that we can also having an extra file inside of the `.aws` folder called `config`. Here is an example of the `config` file

```
[default]
region = us-east-1
output = json
```

Install AWS CLI version 2 for using `CloudFormation` to deploy AWS resources by code aka `Infrastructure as Code` (IaC).

Now run the command below:

```
aws sts get-caller-identity
```

If the response as below it mean you're setup your credential correctly.

```
{
    "UserId": "AROAZCLPAGXZFJUEQS4AU:user2469392=167ebf34-246e-11ed-af09-b79706017971",
    "Account": "623xxxxxx514",
    "Arn": "arn:aws:sts::623xxxxxx514:assumed-role/abcdef/user2469392=167ebf34-246e-11ed-af09-b79706017971"
}
```
