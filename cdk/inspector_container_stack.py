# -*- coding: utf-8 -*-
"""AWS CDK stack definition for inspector container scanning solution."""
import aws_cdk as cdk
import aws_cdk.aws_kms as kms
import aws_cdk.aws_lambda as lmb
from aws_cdk import Stack, Aspects
from constructs import Construct
from cdk_opinionated_constructs.sns import SNSTopic
from cdk_opinionated_constructs.lmb import AWSPythonLambdaFunction
from cdk_nag import AwsSolutionsChecks, NagSuppressions


class InspectorContainerScanStack(Stack):
    """Create inspector container scanner infrastructure."""

    def __init__(self, scope: Construct, construct_id: str, env, **kwargs) -> None:
        super().__init__(scope, construct_id, env=env, **kwargs)

        shared_kms_key = kms.Key(
            self,
            id="shared_kms_key",
            alias="inspector_container_scan",
            description="shared kms key for inspector container scan solution",
            enable_key_rotation=True,
        )

        self.aws_lambda_facade(env, "process_build_approval")

        container_approval_topic_construct = SNSTopic(self, id="container_approval_topic_construct")
        container_approval_topic = container_approval_topic_construct.create_sns_topic(
            topic_name="container_approval_topic", master_key=shared_kms_key
        )
        container_approval_topic_construct.create_sns_topic_policy(sns_topic=container_approval_topic)

        # Validate stack against AWS Solutions checklist
        nag_suppression_rule_list = self.nag_suppression()
        NagSuppressions.add_stack_suppressions(self, nag_suppression_rule_list)
        Aspects.of(self).add(AwsSolutionsChecks(log_ignores=True))

    def aws_lambda_facade(self, env: cdk.Environment, service_name: str, env_variables=None) -> lmb.IFunction:
        """Create facade for AWS Lambda functions.

        :param env: CDK env object
        :param env_variables: AWS Lambda environment variables
        :param service_name: Name of service

        :return: AWS Lambda function
        """

        if env_variables is None:
            env_variables = {}

        lmb_construct = AWSPythonLambdaFunction(self, id=f"lmb_construct_{service_name}")
        lmb_signing_profile = lmb_construct.signing_profile(
            signing_profile_name=f"inspector_container_scan_{service_name}"
        )
        lmb_signing_config = lmb_construct.signing_config(profile=lmb_signing_profile)
        process_build_approval_lmb_layer = lmb_construct.create_lambda_layer(
            construct_id=f"{service_name}_lmb_layer", code_path=f"service/lambda_layers/{service_name}"
        )
        return lmb_construct.create_lambda_function(
            env=env,
            code_path=f"service/{service_name}",
            layer=process_build_approval_lmb_layer,
            timeout=30,
            signing_config=lmb_signing_config,
            env_variables=env_variables,
            function_name=f"inspector_container_scan_{service_name}",
            reserved_concurrent_executions=5,
        )

    @staticmethod
    def nag_suppression() -> list:
        """Create CFN-NAG suppression list.

        :return: List of dicts that contain suppressed nag rules
        """
        return [
            {
                "id": "AwsSolutions-IAM4",
                "reason": "Using managed policies is allowed",
            },
            {
                "id": "AwsSolutions-IAM5",
                "reason": "Using managed policies is allowed",
            },
        ]
