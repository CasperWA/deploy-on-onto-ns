"""The main application module."""
from __future__ import annotations

import os
from asyncio import create_subprocess_shell, subprocess
from contextlib import asynccontextmanager
from logging import getLogger
from pathlib import Path
from shlex import quote
from typing import TYPE_CHECKING, Annotated

import yaml
from fastapi import FastAPI, HTTPException, Query, status

from deploy_on_onto_ns import __version__
from deploy_on_onto_ns.logger import initiate_logging
from deploy_on_onto_ns.models import (
    DEPLOYMENT_SCRIPTS_DIR,
    DeployOnOntoNsResponse,
    DeployServices,
    EnvironmentString,
)

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import AsyncIterator

LOGGER = getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator:
    """Context manager to handle the application lifespan."""
    initiate_logging()
    yield


APP = FastAPI(
    title="Deploy on onto-ns.com",
    version=__version__,
    description=(
        Path(__file__).resolve().parent.parent.resolve() / "README.md"
    ).read_text(encoding="utf8"),
    root_path="/deploy",
    root_path_in_servers=False,
    lifespan=lifespan,
)


@APP.get("/", response_model=DeployOnOntoNsResponse)
async def deploy_service(
    service: Annotated[str, Query(description="The service to deploy")],
    env: Annotated[
        list[EnvironmentString],
        Query(
            description="The environment variables to set for the deployment script.",
        ),
    ] = [],  # noqa: B006
) -> dict[str, str | int]:
    """Deploy `service` on onto-ns.com.

    Run local bash script to deploy `service` on onto-ns.com.

    Parameters:
        service: The service to deploy.
        env: The environment variables to set for the deployment script.

    Returns:
        The response from the deployment service.

    """
    if service not in AVAILABLE_SERVICES:
        LOGGER.error("Service %r does not exist.", service)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service {service!r} does not exist.",
        )

    script_env = os.environ.copy()
    for env_var in env:
        key, value = env_var.split("=", 1)
        script_env[key] = value

    script = AVAILABLE_SERVICES[service].as_posix()

    LOGGER.info("Running script %r", script)
    LOGGER.debug("with environment: %r.", script_env)

    process = await create_subprocess_shell(
        f"bash {quote(script)}",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=script_env,
    )
    stdout, stderr = await process.communicate()
    if process.returncode is None:
        LOGGER.error("Process did not return a return code.")
        raise HTTPException(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail="Process did not return a return code.",
        )

    return {
        "service": service,
        "returncode": process.returncode,
        "stdout": stdout.decode("utf8"),
        "stderr": stderr.decode("utf8"),
    }


def available_services() -> dict[str, Path]:
    """Get available services to deploy.

    Returns:
        A mapping from names and aliases of all available services to deploy to the
        path to the deployment script.

    """
    deploy_services_yml = DEPLOYMENT_SCRIPTS_DIR / "deploy_services.yml"
    if not deploy_services_yml.exists():
        raise FileNotFoundError(
            "Deployment services file "
            f"{deploy_services_yml.relative_to(Path(__file__).resolve())} does not "
            "exist."
        )

    deploy_services_raw = yaml.safe_load(deploy_services_yml.read_bytes())
    services = DeployServices(**deploy_services_raw)

    mapping: dict[str, Path] = {}
    for service in services.services:
        mapping[service.name] = service.script
        for alias in service.aliases:
            mapping[alias] = service.script

    return mapping


AVAILABLE_SERVICES = available_services()
