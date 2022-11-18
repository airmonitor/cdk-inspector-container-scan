# -*- coding: utf-8 -*-
"""
Pydantic models for observability and main function - handler
"""
from typing import Literal
from pydantic import BaseModel, constr


class Observability(BaseModel):
    """Observability variables."""

    POWERTOOLS_SERVICE_NAME: constr(min_length=1)
    LOG_LEVEL: Literal["DEBUG", "INFO", "ERROR", "CRITICAL", "WARNING", "EXCEPTION"]


class EnvVars(Observability):
    """Specific variables dedicated to application."""

    DYNAMO_DB_TABLE_NAME: constr(min_length=3, max_length=255)
