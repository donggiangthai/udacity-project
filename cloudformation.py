import json
from json.decoder import JSONDecodeError
from boto3.session import Session
from botocore.exceptions import (
	ClientError,
	WaiterError
)
from mypy_boto3_cloudformation.type_defs import (
	CreateStackOutputTypeDef,
	UpdateStackOutputTypeDef,
	EmptyResponseMetadataTypeDef,
	CreateChangeSetInputRequestTypeDef,
	ParameterTypeDef
)
from mypy_boto3_cloudformation.literals import (
	CapabilityType,
	ChangeSetTypeType
)
from mypy_boto3_cloudformation import (
	CloudFormationClient,
	StackCreateCompleteWaiter,
	StackUpdateCompleteWaiter,
	StackDeleteCompleteWaiter
)
from typing import (
	Sequence,
	Literal,
	Tuple,
	Any
)
import argparse
import sys
import os

parser = argparse.ArgumentParser(
	description='CloudFormation client with boto3',
	formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
parser.add_argument(
	'-s', '--stack-name',
	nargs="+",
	required=True,
	type=str,
	help='CloudFormation stack name, can be a list for multiple deletion'
)
parser.add_argument(
	'-t', '--template-body',
	required=False if 'delete' in sys.argv[1].lower() else True,
	type=str,
	help='Template file name only or full path of the file name'
)
parser.add_argument(
	'-c', '--capabilities',
	nargs="+",
	required=False,
	type=str,
	choices=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM", "CAPABILITY_AUTO_EXPAND"],
	help='Capabilities required if related to IAM, choice in 3 options'
)
parser.add_argument(
	'-pf', '--parameters-file',
	required=False,
	type=str,
	help='Parameters that using for template'
)
parser.add_argument(
	'-r', '--region',
	type=str,
	choices=['us-east-1', 'us-west-2'],
	default='us-east-1',
	help='AWS region'
)
parser.add_argument(
	'-p', '--profile-name',
	type=str,
	default='ThaiDG-IaC',
	help='AWS profile name'
)
parser.add_argument(
	'option',
	help='CloudFormation option e.g. create, update, delete, etc.'
)
args = vars(parser.parse_args())


class CloudFormationClient:
	def __init__(self, profile_name: str) -> None:
		if not profile_name:
			raise ValueError("AWS profile name is required.")
		self._profileName = profile_name
		self._region = args["region"]
		self._awsClient = Session(profile_name=profile_name).client(
			service_name='cloudformation',
			region_name=args["region"]
		)

	def __str__(self) -> str:
		return "Cloud Formation Client provided by boto3"

	@property
	def aws_profile_name(self) -> str:
		return self._profileName

	@aws_profile_name.setter
	def aws_profile_name(self, profile_name: str) -> None:
		self._profileName = profile_name

	@property
	def aws_region(self):
		return self._region

	@aws_region.setter
	def aws_region(self, region: Literal['us-east-1', 'us-west-2']):
		self._region = region

	@property
	def aws_client(self) -> CloudFormationClient:
		return self._awsClient

	@aws_client.setter
	def aws_client(self, tuple_params: Tuple[str, Literal['us-east-1', 'us-west-2']]) -> None:
		profile_name, region = tuple_params
		if not profile_name:
			profile_name = self.aws_profile_name
		if not region:
			region = self.aws_region
		self._awsClient = Session(profile_name=profile_name).client(
			service_name='cloudformation',
			region_name=region
		)

	def create_stack(
			self,
			stack_name: str,
			template_file_name: str
	) -> CreateStackOutputTypeDef | EmptyResponseMetadataTypeDef | None:
		"""
		This function is old and being replaced with change_set instead
		Args:
			stack_name: The Cloud Formation stack name
			template_file_name: The YAML file that contain the template body

		Returns: a dictionary

		"""
		try:
			with open(file=fr"{template_file_name}", mode='r') as fd:
				template_body = fd.read()
				self._awsClient.validate_template(TemplateBody=template_body)
				response = self._awsClient.create_stack(
					StackName=stack_name,
					TemplateBody=template_body,
					OnFailure="DELETE",
					Tags=[
						{
							'Key': 'Core',
							'Value': 'Deploy Infrastructure as Code'
						},
					],
				)
		except self._awsClient.exceptions.AlreadyExistsException:
			return self.change_set(
				self.get_create_change_set_input(
					stack_name=stack_name,
					template_file_name=template_file_name,
					change_set_type='UPDATE'
				)
			)
		except ClientError as error:
			raise error
		else:
			return response

	@staticmethod
	def get_create_change_set_input(
			stack_name: str,
			template_file_name: str,
			change_set_type: ChangeSetTypeType
	) -> CreateChangeSetInputRequestTypeDef:
		"""
		Create input for the create_change_set function
		Args:
			stack_name: The Cloud Formation stack name
			template_file_name: The YAML file that contain the template body
			change_set_type: has to be CREATE or UPDATE

		Returns: a dictionary contains parameters for the create_change_set function

		"""
		try:
			template_file_path = fr"{os.getcwd()}\{template_file_name}"
			with open(file=template_file_path, mode='r') as fd:
				# Get the template body from file
				template_body: str = fd.read()
		except Exception as error:
			raise error
		request_input = CreateChangeSetInputRequestTypeDef(
			StackName=stack_name,
			ChangeSetName=f"{stack_name}ChangeSet",
			TemplateBody=template_body,
			ChangeSetType=change_set_type,
		)
		if args['capabilities']:
			capabilities: Sequence[CapabilityType] = args['capabilities']
			request_input['Capabilities'] = capabilities
		if args['parameters_file']:
			try:
				parameters_file_path = fr"{os.getcwd()}\{args['parameters_file']}"
				with open(file=parameters_file_path, mode='r') as data_input:
					params: Sequence[ParameterTypeDef] = json.load(data_input)
			except JSONDecodeError as json_error:
				raise json_error
			else:
				request_input['Parameters'] = params

		return request_input

	def change_set(
			self,
			create_change_set_input: CreateChangeSetInputRequestTypeDef
	) -> StackCreateCompleteWaiter | StackUpdateCompleteWaiter | StackDeleteCompleteWaiter | dict[str, Any]:
		"""
		For handle change set within CREATE or UPDATE behavior.
		This function will replace create_stack and update_stack also

		Args:
			create_change_set_input:
				The input parameters for create_change_set function from boto3.
				Using self.get_create_change_set_input() or just pass a dictionary to this parameter

		Returns: a dictionary contain a metadata response

		"""
		try:
			des_stack = self._awsClient.describe_stacks(
				StackName=create_change_set_input['StackName']
			)
		except ClientError as client_error:
			if 'does not exist' in client_error.response['Error']['Message']:
				pass
			else:
				raise client_error
		else:
			stack_status = des_stack['Stacks'][0]['StackStatus']
			if 'ROLLBACK_' in stack_status:
				if 'ROLLBACK_COMPLETE' not in stack_status:
					roll_back_waiter = self._awsClient.get_waiter('stack_rollback_complete')
					try:
						roll_back_waiter.wait(
							StackName=create_change_set_input['StackName'],
							WaiterConfig={
								'Delay': 5,
								'MaxAttempts': 150
							}
						)
					except WaiterError as wt_err:
						print(wt_err.last_response['StatusReason'])
						raise wt_err
				try:
					self.delete_stack(stack_name=[create_change_set_input['StackName']])
				except ClientError as error:
					raise error
				else:
					print("Cleaned stack and ready for execute.")
			elif 'CREATE_COMPLETE' or 'UPDATE_COMPLETE' in stack_status:
				change_set_type: Literal["UPDATE"] = "UPDATE"
				create_change_set_input['ChangeSetType'] = change_set_type
			else:
				raise Exception(
					"""
					Check the stack status and execute the script again. 
					Make sure the state only in one of the follow: 
						- 'CREATE_COMPLETE'
						- 'UPDATE_COMPLETE'
						- 'ROLLBACK_COMPLETE'
					"""
				)
		try:
			# Validate template
			self._awsClient.validate_template(TemplateBody=create_change_set_input['TemplateBody'])
			# Create a change set
			response = self._awsClient.create_change_set(**create_change_set_input)
			change_set_arn = response["Id"]
		except ClientError as client_error:
			raise client_error
		else:
			# Get change set waiter
			change_set_waiter = self._awsClient.get_waiter('change_set_create_complete')
			try:
				change_set_waiter.wait(
					ChangeSetName=change_set_arn,
					StackName=create_change_set_input['StackName'],
					WaiterConfig={
						'Delay': 5,
						'MaxAttempts': 150
					}
				)
			except WaiterError as wt_err:
				print(wt_err.last_response['StatusReason'])
				raise wt_err
			else:
				change_set_response = self._awsClient.describe_change_set(
					ChangeSetName=change_set_arn,
					StackName=create_change_set_input['StackName']
				)
				print(json.dumps(change_set_response, indent=4, default=str))
				if 'AVAILABLE' in change_set_response['ExecutionStatus']:
					if 'yes' in input("Do you want to execute change set? ").lower():
						try:
							self._awsClient.execute_change_set(
								ChangeSetName=change_set_arn,
								StackName=create_change_set_input['StackName'],
							)
						except ClientError as error:
							raise error
						else:
							if 'CREATE' in create_change_set_input['ChangeSetType']:
								waiter_name: Literal['stack_create_complete'] = 'stack_create_complete'
							elif 'UPDATE' in create_change_set_input['ChangeSetType']:
								waiter_name: Literal['stack_update_complete'] = 'stack_update_complete'
							else:
								raise ValueError("Stack Import didn't implementation yet")
							stack_waiter = self._awsClient.get_waiter(waiter_name)
							try:
								stack_waiter.wait(
									StackName=create_change_set_input['StackName'],
									WaiterConfig={
										'Delay': 5,
										'MaxAttempts': 150
									}
								)
							except WaiterError as wt_err:
								raise wt_err
							else:
								return stack_waiter
					else:
						try:
							delete_change_set_response = self._awsClient.delete_change_set(
								ChangeSetName=change_set_arn,
								StackName=create_change_set_input['StackName']
							)
						except ClientError as error:
							raise error
						if create_change_set_input['ChangeSetType'] == 'CREATE':
							try:
								self.delete_stack(
									stack_name=[create_change_set_input['StackName']]
								)
							except ClientError as error:
								raise error
							else:
								print("Cleaned stack.")
						else:
							return delete_change_set_response
				else:
					print(f"Execution status is {change_set_response['ExecutionStatus']}")

	def update_stack(self, stack_name: str, template_file_name: str) -> UpdateStackOutputTypeDef | None:
		"""
		This function is old and being replaced with change_set instead
		Args:
			stack_name: The Cloud Formation stack name
			template_file_name: The YAML file that contain the template body

		Returns:

		"""
		try:
			with open(file=fr"{template_file_name}", mode='r') as fd:
				template_body = fd.read()
				self._awsClient.validate_template(TemplateBody=template_body)
				response = self._awsClient.update_stack(
					StackName=stack_name,
					TemplateBody=template_body,
					Tags=[
						{
							'Key': 'Core',
							'Value': 'Deploy Infrastructure as Code'
						}
					]
				)
		except ClientError as error:
			raise error
		else:
			return response

	def delete_stack(self, stack_name: list) -> None:
		"""
		The function to represent for the delete_stack API of Cloud Formation SDK
		Args:
			stack_name:

		Returns:

		"""
		for item in stack_name:
			try:
				self._awsClient.delete_stack(
					StackName=item,
				)
			except ClientError as error:
				raise error
			else:
				delete_waiter = self._awsClient.get_waiter('stack_delete_complete')
				try:
					delete_waiter.wait(
						StackName=item,
						WaiterConfig={
							'Delay': 5,
							'MaxAttempts': 150
						}
					)
				except WaiterError as wt_err:
					print(wt_err.last_response['StatusReason'])
					raise wt_err
				else:
					print(f"Stack {item} deleted.")

	def handle(self, option: str) -> None:
		if "create" in option:
			response = self.change_set(
				self.get_create_change_set_input(
					stack_name=args["stack_name"],
					template_file_name=args["template_body"],
					change_set_type='CREATE'
				)
			)
			print(json.dumps(response, indent=4, default=str))
		if "update" in option:
			response = self.change_set(
				self.get_create_change_set_input(
					stack_name=args["stack_name"],
					template_file_name=args["template_body"],
					change_set_type='UPDATE'
				)
			)
			print(json.dumps(response, indent=4, default=str))
		if "delete" in option:
			self.delete_stack(stack_name=args["stack_name"])


if __name__ == "__main__":
	print("Hello from ThaiDG")
	cfn_client = CloudFormationClient(profile_name=args["profile_name"])
	cfn_client.handle(option=args['option'])
