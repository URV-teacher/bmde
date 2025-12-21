import pytest

from bmde.commands.build.service import BuildService
from bmde.core.types import BackendOptions


def test_build_service_initialization():
    """Verify that BuildService maps the correct backends."""
    service = BuildService()
    # Check if 'host' is in the mapping keys
    assert "host" in [key.value for key in service.mapping.keys()]

def test_choose_backend_force_env():
    """Verify that passing an env overrides the default order."""
    service = BuildService()
    # Assuming 'host' is a valid Enum value
    backends = service.choose_backend(BackendOptions.DOCKER)
    assert len(backends) == 1