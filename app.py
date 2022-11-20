# -*- coding: utf-8 -*-
"""CDK application."""
import os
import aws_cdk as cdk

from cdk.inspector_container_stack import InspectorContainerScanStack

app = cdk.App()
InspectorContainerScanStack(
    app,
    "InspectorContainerScan",
    env=cdk.Environment(account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")),
)


app.synth()
