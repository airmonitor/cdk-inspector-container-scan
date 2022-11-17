# -*- coding: utf-8 -*-
# Function that will process the SNS message sent about a pipeline approval
# request for a container build pipeline.  Information from the message
# will be stored in a DynamoDB table for further reference
import json
from datetime import datetime
from service.process_build_approval.utils.observability import logger, metrics, tracer
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.data_classes import event_source, SNSEvent
from service.process_build_approval.libs.dynamo_db_service import DynamoDBService
from service.process_build_approval.utils.env_vars_parser import get_environment_variables, init_environment_variables
from service.process_build_approval.schemas.env_vars import EnvVars

DYNAMODB_SERVICE = DynamoDBService()


@init_environment_variables(model=EnvVars)
@metrics.log_metrics
@tracer.capture_lambda_handler(capture_response=False)
@logger.inject_lambda_context(log_event=True)
@event_source(data_class=SNSEvent)
def handler(event: SNSEvent, context: LambdaContext):
    logger.set_correlation_id(context.aws_request_id)

    env_vars: EnvVars = get_environment_variables(model=EnvVars)

    for record in event.records:
        message = json.loads(record.sns.message)
        token = message["approval"]["token"]
        pipeline = message["approval"]["pipelineName"]
        stage = message["approval"]["stageName"]
        approval_action = message["approval"]["actionName"]
        custom_data = message["approval"]["customData"]

        image_digest = custom_data.split("=")[1]

        DYNAMODB_SERVICE.put_item(
            table_name="ContainerImageApprovals",
            item={
                "ImageDigest": image_digest,
                "ApprovalToken": token,
                "PipelineName": pipeline,
                "Stage": stage,
                "ActionName": approval_action,
                "InsertDate": datetime.utcnow().isoformat(),
            },
        )

    return {"statusCode": 200}
