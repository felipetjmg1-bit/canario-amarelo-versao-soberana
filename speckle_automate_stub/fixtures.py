import pytest

from speckle_automate_stub import AutomationRunData


@pytest.fixture
def test_automation_run_data():
    return AutomationRunData(
        project_id="project id",
        speckle_server_url="https://latest.speckle.systems",
        automation_id="automation id",
        automation_run_id="automation run id",
        function_run_id="function run id",
        triggers=[{"payload": {"modelId": "model id", "versionId": "version id"}}],
    )


@pytest.fixture
def test_automation_token():
    return "test-token"
