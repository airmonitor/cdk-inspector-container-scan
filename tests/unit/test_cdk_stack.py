# -*- coding: utf-8 -*-
"""Test CDK template."""
import aws_cdk as core
from aws_cdk.assertions import Template

# pylint: disable=no-name-in-module
from cdk.inspector_container_stack import InspectorContainerScanStack  # type: ignore

import pytest


@pytest.fixture
def stack_template() -> Template:
    """Returns CDK template."""
    app = core.App()
    stack = InspectorContainerScanStack(app, "cdk", git_repository_name="test-git-repository")
    return Template.from_stack(stack)


# pylint: disable=redefined-outer-name
def test_codecommit_repository(stack_template):
    """Test if CodeCommit repository created."""
    stack_template.resource_count_is("AWS::CodeCommit::Repository", 1)


# pylint: disable=redefined-outer-name
def test_kms_key(stack_template):
    """Test if KMS key created."""
    stack_template.resource_count_is("AWS::KMS::Key", 1)


# pylint: disable=redefined-outer-name
def test_sns_topic(stack_template):
    """Test if SNS topic created."""
    stack_template.resource_count_is("AWS::SNS::Topic", 1)
