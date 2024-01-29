"""Pydantic data models."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

DEPLOYMENT_SCRIPTS_DIR = (
    Path(__file__).resolve().parent.parent.resolve() / "deployment_scripts"
)


EnvironmentString = Annotated[
    str,
    Field(
        pattern=r"^[A-Za-z_][A-Za-z0-9_]*=[^=]*$",
        examples=["FOO=bar", "BAR=baz", "BAZ=qux"],
    ),
]


class DeployService(BaseModel):
    """A service to deploy on onto-ns.com."""

    name: Annotated[str, Field(description="The name of the service.")]
    script: Annotated[Path, Field(description="The path to the deployment script.")]
    aliases: Annotated[list[str], Field(description="The aliases for the service.")] = (
        []
    )

    @field_validator("script", mode="after")
    @classmethod
    def script_exists(cls, value: Path) -> Path:
        """Check that the deployment script exists."""
        if value.is_absolute():
            resolved_value = value.resolve()
        else:
            # Expect it to be relative to the deployment scripts directory.
            resolved_value = (DEPLOYMENT_SCRIPTS_DIR / value).resolve()

        if not resolved_value.exists():
            raise ValueError(f"Deployment script {value} does not exist.")
        return resolved_value


class DeployServices(BaseModel):
    """The data model for the `deploy_services.yml` file."""

    services: Annotated[
        list[DeployService], Field(description="The services available for deploy.")
    ]

    @field_validator("services", mode="after")
    @classmethod
    def services_unique(cls, value: list[DeployService]) -> list[DeployService]:
        """Check that the services are unique."""
        names = [service.name for service in value]
        if len(names) != len(set(names)):
            raise ValueError("Services must be unique.")
        return value


class DeployOnOntoNsResponse(BaseModel):
    """The response from the deployment service."""

    returncode: Annotated[
        int, Field(description="The return code from the deployment.")
    ]
    service: Annotated[str, Field(description="The service that was deployed.")]
    stdout: Annotated[str, Field(description="The stdout from the deployment script.")]
    stderr: Annotated[str, Field(description="The stderr from the deployment script.")]
