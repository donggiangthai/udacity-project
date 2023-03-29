[CmdletBinding()]
param (
    [Parameter()]
    [string]
    $TemplateFileName,
    [Parameter(Mandatory = $true)]
    [string]
    $StackName
)
if ($StackName -eq 'EC2Instance' -and $TemplateFileName -ne "") {
    $TemplateFileName = 'ec2-instance.yml'
}
if ($StackName -eq 'SecurityGroup' -and $TemplateFileName -ne "") {
    $TemplateFileName = 'security-group.yml'
}
aws cloudformation create-stack --stack-name $StackName --region 'us-east-1' --template-body file://$TemplateFileName --on-failure DELETE --role-arn 'arn:aws:iam::623539926514:role/ThaiDG-CloudFormation-Role'