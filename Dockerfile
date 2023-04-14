FROM python:3.10-slim as base

WORKDIR /app

COPY deploy_on_onto_ns deploy_on_onto_ns/
COPY deployment_scripts deployment_scripts/
COPY pyproject.toml LICENSE README.md ./

RUN python -m pip install -U pip && \
  pip install -U pip setuptools wheel flit && \
  pip install -U -e .

FROM base as development

ENV PORT=80
EXPOSE ${PORT}

ENTRYPOINT uvicorn --host 0.0.0.0 --port ${PORT} --log-level debug --no-server-header --header "Server:Deploy on onto-ns.com" --reload deploy_on_onto_ns.main:APP

FROM base as production

RUN pip install gunicorn

ENV PORT=80
EXPOSE ${PORT}

ENTRYPOINT gunicorn --bind "0.0.0.0:${PORT}" --workers 1 --worker-class deploy_on_onto_ns.uvicorn.UvicornWorker deploy_on_onto_ns.main:APP
