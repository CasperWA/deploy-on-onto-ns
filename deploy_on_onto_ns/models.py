"""Pydantic data models."""
from pathlib import Path

from pydantic import BaseModel, Field, validator


class DeployService(BaseModel):
    """A service to deploy on onto-ns.com."""

    name: str = Field(..., description="The name of the service.")
    script: Path = Field(..., description="The path to the deployment script.")
    aliases: list[str] = Field([], description="The aliases for the service.")

    @validator("script")
    def script_exists(cls, value: Path) -> Path:
        """Check that the deployment script exists."""
        if not value.exists():
            raise ValueError(f"Deployment script {value} does not exist.")
        return value.resolve()


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

    service: str = Field(..., description="The service that was deployed.")
    stdout: str = Field(..., description="The stdout from the deployment script.")
    stderr: str = Field(..., description="The stderr from the deployment script.")
