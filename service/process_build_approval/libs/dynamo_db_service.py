# -*- coding: utf-8 -*-
"""The DynamoDB abstraction layer for hexagonal architecture."""
import boto3
from service.process_build_approval.utils.observability import logger
from botocore.exceptions import ClientError


# pylint: disable=E1101
class DynamoDBService:
    """Interact with DynamoDB using the AWS boto3 library."""

    def __init__(self, region="eu-west-1"):
        """Initialize region in which operations will be performed.

        :param region: default eu-west-1
        """
        self.__client = boto3.resource(
            "dynamodb",
            region_name=region,
            endpoint_url=f"https://dynamodb.{region}.amazonaws.com/",
        )

    def put_item(self, table_name, item):
        """Save dict item to DynamoDB.

        :param table_name: name of the table
        :param item: dict with key/value pairs
        :return: item saved to DynamoDB
        """
        table = self.__client.Table(table_name)
        try:
            item = table.put_item(Item=item)
            logger.info("Put item into %s table", table_name)
            return item
        except ClientError as error:
            logger.error("Failed to put item into %s table due to %s", table_name, repr(error))
            raise

    def batch_put_items(self, table_name, items):
        """Save multiple items into DynamoDB table.

        :param table_name: name of the table
        :param items: list of dictionaries with key/value pairs
        :return:
        """
        table = self.__client.Table(table_name)
        try:
            with table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
            logger.info("Put %s items into %s table", len(items), table_name)
        except ClientError as error:
            logger.error("Failed to batch put for %s table due to %s", table_name, repr(error))
            raise

    def delete_item(self, table_name, item):
        """Delete an item from a table.

        :param table_name: name of the table
        :param item: dict with key/value pairs
        :return: item deleted from the table
        """
        table = self.__client.Table(table_name)
        try:
            item = table.delete_item(Key=item)
            logger.info("Delete item in %s table", table_name)
            return item
        except ClientError as error:
            logger.error("Failed to delete item from %s table due to %s", table_name, repr(error))
            raise

    def get_item(self, table_name, key):
        """Get item from the DynamoDB table.

        :param table_name: name of the table
        :param key: hash key
        :return: item obtained from the table
        """
        table = self.__client.Table(table_name)
        try:
            response = table.get_item(Key=key)
            logger.info("Got item from %s table", table_name)
            return response.get("Item")
        except ClientError as error:
            logger.error("Failed to get item from %s table due to %s", table_name, repr(error))
            raise

    def update_item(self, table_name, key, expression, values):
        """Update existing item or add new one if don't exist.

        :param table_name: name of the table
        :param key: hash key which will be updated or added if not exists
        :param expression: dynamodb expression used to update item in the table
        :param values: expression attribute values
        :return: NotImplemented
        """
        table = self.__client.Table(table_name)
        try:
            table.update_item(Key=key, UpdateExpression=expression, ExpressionAttributeValues=values)
            logger.info("Updated item in %s table", table_name)
        except ClientError as error:
            logger.error("Failed to update item in %s table due to %s", table_name, repr(error))
            raise

    def get_items(self, table_name, filter_expression=None):
        """Get multiple items from table.

        :param table_name: name of the table
        :param filter_expression: dynamodb expression used to narrow returned results
        :return: dict with items
        """
        table = self.__client.Table(table_name)

        try:
            if filter_expression:
                response = table.scan(FilterExpression=filter_expression)
            else:
                response = table.scan()
            data = response["Items"]
            while "LastEvaluatedKey" in response:
                response = table.scan(
                    ExclusiveStartKey=response["LastEvaluatedKey"],
                    FilterExpression=filter_expression,
                )
                data.extend(response["Items"])
            logger.info("Got %s items from %s table", len(data), table_name)
            return data
        except ClientError as error:
            logger.error("Failed to scan items from %s table due to %s", table_name, repr(error))
            raise

    def get_items_page(self, table_name, filter_expression, last_evaluated_key=None, limit=500):
        """Get all elements from table limited to default 500 items per page.

        :param table_name: name of the table
        :param filter_expression: dynamodb expression used to get items in the table
        :param last_evaluated_key: the last key to start pagination from
        :param limit: default 500 items will be returned in one pagination page
        :return: list of dictionaries
        """
        table = self.__client.Table(table_name)
        try:
            if last_evaluated_key is None:
                response = table.scan(FilterExpression=filter_expression, Limit=limit)
            else:
                response = table.scan(
                    ExclusiveStartKey=last_evaluated_key,
                    FilterExpression=filter_expression,
                    Limit=limit,
                )
            logger.info("Got %s items from %s table", response["Count"], table_name)
            return response
        except ClientError as error:
            logger.error("Failed to scan items from %s table due to %s", table_name, repr(error))
            raise

    def query(self, table_name, **kwargs):
        """Query DynamoDB table using key/value pairs.

        :param table_name: name of the table
        :param kwargs: dict of key/value pairs
        :return: list of dictionaries
        """
        table = self.__client.Table(table_name)

        try:
            response = table.query(**kwargs)
            data = response["Items"]
            while "LastEvaluatedKey" in response:
                kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
                response = table.query(**kwargs)
                data.extend(response["Items"])
            logger.info("Got %s items from %s table", len(data), table_name)
            return data
        except ClientError as error:
            logger.error("Failed to query items from %s table due to %s", table_name, repr(error))
            raise
