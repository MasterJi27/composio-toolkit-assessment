from services.config import settings
from cli.main import cli

def test_environment_loads():
    assert settings is not None
    assert settings.composio_configured is not None

def test_cli_exists():
    assert cli is not None
    assert cli.info.name == "composio-research"
