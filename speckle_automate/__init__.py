from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum
from types import SimpleNamespace
from typing import Any

from pydantic import BaseModel, SecretStr


class AutomationStatus(Enum):
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class AutomateBase(BaseModel):
    """Base model for automation function inputs."""


@dataclass
class AutomationRunData:
    project_id: str
    speckle_server_url: str
    automation_id: str
    automation_run_id: str
    function_run_id: str
    triggers: list[dict[str, Any]]


class SpeckleBase:
    def __init__(
        self,
        speckle_type: str = "Base",
        id: str = "root",
        material: str | None = "Concrete",
        elements: list["SpeckleBase"] | None = None,
    ):
        self.speckle_type = speckle_type
        self.id = id
        self.material = material
        self.elements = [] if elements is None else elements


class AutomationContext:
    def __init__(self, run_data: AutomationRunData, token: str):
        self.run_data = run_data
        self.token = token
        self.run_status = AutomationStatus.SUCCEEDED
        self.status_message: str | None = None
        self.file_results: list[str] = []
        self.version_root_object = SpeckleBase()

    @classmethod
    def initialize(cls, run_data: AutomationRunData | dict[str, Any], token: str):
        if isinstance(run_data, dict):
            run_data = AutomationRunData(**run_data)
        return cls(run_data, token)

    def receive_version(self) -> SpeckleBase:
        return self.version_root_object

    def mark_run_success(self, message: str | None = None) -> None:
        self.run_status = AutomationStatus.SUCCEEDED
        if message:
            self.status_message = message

    def mark_run_failed(self, message: str | None = None) -> None:
        self.run_status = AutomationStatus.FAILED
        if message:
            self.status_message = message

    def store_file_result(self, file_path: str) -> None:
        self.file_results.append(file_path)


def run_function(
    automation_context: AutomationContext,
    function: Any,
    function_inputs: AutomateBase,
) -> SimpleNamespace:
    try:
        function(automation_context, function_inputs)
    except Exception as exc:
        automation_context.mark_run_failed(str(exc))
    return SimpleNamespace(run_status=automation_context.run_status)


def execute_automate_function(function: Any, inputs_cls: type[AutomateBase]) -> SimpleNamespace:
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    analysis_prompt = os.environ.get(
        "ANALYSIS_PROMPT",
        "Realize uma auditoria técnica rigorosa. Verifique se há duplicidade de IDs, inconsistências de materiais e se a hierarquia espacial faz sentido para um modelo de construção.",
    )
    inputs = inputs_cls(
        openai_api_key=SecretStr(openai_key),
        analysis_prompt=analysis_prompt,
    )

    run_data = AutomationRunData(
        project_id=os.environ.get("PROJECT_ID", "local"),
        speckle_server_url=os.environ.get("SPECKLE_SERVER_URL", "http://localhost"),
        automation_id=os.environ.get("AUTOMATION_ID", "local"),
        automation_run_id=os.environ.get("AUTOMATION_RUN_ID", "local"),
        function_run_id=os.environ.get("FUNCTION_RUN_ID", "local"),
        triggers=[{"payload": {"modelId": "local", "versionId": "local"}}],
    )

    automation_context = AutomationContext.initialize(run_data, os.environ.get("SPECKLE_TOKEN", ""))
    return run_function(automation_context, function, inputs)
