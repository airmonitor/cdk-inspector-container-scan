# -*- coding: utf-8 -*-
"""Validate input against predefined pydantic models."""
from pydantic import BaseModel


class ApprovalDetails(BaseModel):
    """Validate approval details."""

    token: str
    pipeline: str
    stage: str
    approval_action: str
    custom_data: str
