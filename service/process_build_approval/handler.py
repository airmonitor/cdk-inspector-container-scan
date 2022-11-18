# -*- coding: utf-8 -*-
"""Function that will process the SNS message sent about a pipeline approval
request for a container build pipeline.

Information from the message will be stored in a DynamoDB table for
further reference
"""
import json
from datetime import datetime
from datetime import timezone
from service.process_build_approval.utils.observability import logger, metrics, tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import SNSEvent
from aws_lambda_powertools.utilities.parser import ValidationError, parse
from service.process_build_approval.libs.dynamo_db_service import DynamoDBService
from service.process_build_approval.utils.env_vars_parser import get_environment_variables, init_environment_variables
from service.process_build_approval.schemas.env_vars import EnvVars
from service.process_build_approval.schemas.input import ApprovalDetails

DYNAMODB_SERVICE = DynamoDBService()


@init_environment_variables(model=EnvVars)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
@logger.inject_lambda_context(log_event=True)
def handler(event: SNSEvent, context: LambdaContext):
    """AWS Lambda main function handler."""
    logger.set_correlation_id(context.aws_request_id)

    env_vars: EnvVars = get_environment_variables(model=EnvVars)

    for record in event.records:
        message = json.loads(record.sns.message)

        try:
            approval_details: ApprovalDetails = parse(event=message["approval"], model=ApprovalDetails)
            DYNAMODB_SERVICE.put_item(
                table_name=env_vars.DYNAMO_DB_TABLE_NAME,
                item={
                    "ImageDigest": approval_details.custom_data.split("=")[1],
                    "ApprovalToken": approval_details.token,
                    "PipelineName": approval_details.pipeline,
                    "Stage": approval_details.stage,
                    "ActionName": approval_details.approval_action,
                    "InsertDate": datetime.now(timezone.utc).isoformat(),
                },
            )
        except (ValidationError, TypeError) as exc:
            logger.error("event failed input validation", extra={"error": str(exc)})
            raise exc

    return True
