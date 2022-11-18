# -*- coding: utf-8 -*-
"""Parser for environment variables using pydantic model."""
import os
from functools import lru_cache
from typing import Any, TypeVar

from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from pydantic import BaseModel, ValidationError

Model = TypeVar("Model", bound=BaseModel)


@lru_cache
def __parse_model(model: Model) -> BaseModel:
    """Validate environment variables against the pydantic model."""
    try:
        return model(**os.environ)
    except (ValidationError, TypeError) as exc:
        raise ValueError(f"failed to load environment variables, exception={str(exc)}") from exc


@lambda_handler_decorator
def init_environment_variables(handler, event, context, model: Model) -> Any:
    """Initialize environment variables from the Lambda function handler."""
    __parse_model(model)
    return handler(event, context)


def get_environment_variables(model: Model) -> BaseModel:
    """Get validated environment variables."""
    return __parse_model(model)
