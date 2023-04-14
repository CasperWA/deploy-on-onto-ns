"""The main application module."""
from asyncio import create_subprocess_shell, subprocess
from pathlib import Path
from shlex import quote

import yaml
from fastapi import FastAPI, HTTPException, Query, status

from deploy_on_onto_ns import __version__
from deploy_on_onto_ns.logger import LOGGER
from deploy_on_onto_ns.models import (
    DEPLOYMENT_SCRIPTS,
    DeployOnOntoNsResponse,
    DeployServices,
)

APP = FastAPI(
    title="Deploy on onto-ns.com",
    version=__version__,
    description=(
        Path(__file__).resolve().parent.parent.resolve() / "README.md"
    ).read_text(encoding="utf8"),
)


@APP.get("/", response_model=DeployOnOntoNsResponse)
async def deploy_service(
    service: str = Query(..., description="The service to deploy")
) -> dict[str, str | int]:
    """Deploy `service` on onto-ns.com.

    Run local bash script to deploy `service` on onto-ns.com.

    Parameters:
        service: The service to deploy.

    Returns:
        The response from the deployment service.

    """
    if service not in AVAILABLE_SERVICES:
        LOGGER.error("Service %r does not exist.", service)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service {service!r} does not exist.",
        )

    script = AVAILABLE_SERVICES[service].as_posix()
    process = await create_subprocess_shell(
        f"bash {quote(script)}",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode is None:
        raise RuntimeError("Process did not return a return code.")

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
    deploy_services_yml = DEPLOYMENT_SCRIPTS / "deploy_services.yml"
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
