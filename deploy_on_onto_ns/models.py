"""Pydantic data models."""
from pathlib import Path

from pydantic import BaseModel, Field, validator

DEPLOYMENT_SCRIPTS = (
    Path(__file__).resolve().parent.parent.resolve() / "deployment_scripts"
)


class DeployService(BaseModel):
    """A service to deploy on onto-ns.com."""

    name: str = Field(..., description="The name of the service.")
    script: Path = Field(..., description="The path to the deployment script.")
    aliases: list[str] = Field([], description="The aliases for the service.")

    @validator("script")
    def script_exists(cls, value: Path) -> Path:
        """Check that the deployment script exists."""
        resolved_value = value.relative_to(DEPLOYMENT_SCRIPTS).resolve()
        if not resolved_value.exists():
            raise ValueError(f"Deployment script {value} does not exist.")
        return resolved_value


class DeployServices(BaseModel):
    """The data model for the `deploy_services.yml` file."""

    services: list[DeployService] = Field(
        ..., description="The services available for deploy."
    )

    @validator("services")
    def services_unique(cls, value: list[DeployService]) -> list[DeployService]:
        """Check that the services are unique."""
        names = [service.name for service in value]
        if len(names) != len(set(names)):
            raise ValueError("Services must be unique.")
        return value


class DeployOnOntoNsResponse(BaseModel):
    """The response from the deployment service."""

    returncode: int = Field(..., description="The return code from the deployment.")
    service: str = Field(..., description="The service that was deployed.")
    stdout: str = Field(..., description="The stdout from the deployment script.")
    stderr: str = Field(..., description="The stderr from the deployment script.")
