# -*- coding: utf-8 -*-
"""AWS CDK stack definition for inspector container scanning solution."""
from aws_cdk import Stack, Aspects
from constructs import Construct
from aws_cdk import aws_codecommit as codecommit
import aws_cdk.aws_kms as kms
from cdk_opinionated_constructs.sns import SNSTopic
from cdk_nag import AwsSolutionsChecks


class InspectorContainerScanStack(Stack):
    """Create inspector container scanner infrastructure."""

    def __init__(self, scope: Construct, construct_id: str, git_repository_name: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        shared_kms_key = kms.Key(
            self,
            id="shared_kms_key",
            alias="inspector_container_scan",
            description="shared kms key for inspector container scan solution",
            enable_key_rotation=True,
        )

        codecommit.Repository(self, id="git_repository", repository_name=git_repository_name)

        container_approval_topic_construct = SNSTopic(self, id="container_approval_topic_construct")
        container_approval_topic = container_approval_topic_construct.create_sns_topic(
            topic_name="container_approval_topic", master_key=shared_kms_key
        )
        container_approval_topic_construct.create_sns_topic_policy(sns_topic=container_approval_topic)

        # Validate stack against AWS Solutions checklist
        Aspects.of(self).add(AwsSolutionsChecks(log_ignores=True))
