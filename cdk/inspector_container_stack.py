# -*- coding: utf-8 -*-
"""AWS CDK stack definition for inspector container scanning solution."""
from aws_cdk import Stack
import aws_cdk.aws_kms as kms
from cdk_opinionated_constructs.sns import SNSTopic

from constructs import Construct


class InspectorContainerScan(Stack):
    """Create inspector container scanner infrastructure."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        shared_kms_key = kms.Key(
            self,
            id="shared_kms_key",
            alias="inspector_container_scan",
            description="shared kms key for inspector container scan solution",
            enable_key_rotation=True,
        )

        container_approval_topic_construct = SNSTopic(self, id="container_approval_topic_construct")
        container_approval_topic = container_approval_topic_construct.create_sns_topic(
            topic_name="container_approval_topic", master_key=shared_kms_key
        )
        container_approval_topic_construct.create_sns_topic_policy(sns_topic=container_approval_topic)
