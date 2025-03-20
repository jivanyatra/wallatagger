FROM python:3.11.9-alpine

# Grab UV binaries
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN mkdir /app
WORKDIR /app

# copy reqs
COPY ./.python-version /app/
COPY ./pyproject.toml /app/pyproject.toml
COPY ./LICENSE /app/
COPY ./uv.lock /app/uv.lock

# install reqs in first layer (for efficiency)
ENV UV_PROJECT_ENVIRONMENT="/usr/local/"
RUN uv sync --locked --no-dev

COPY ./dist/wallatagger-0.1.1-py3-none-any.whl /app
RUN uv pip install --system ./wallatagger-0.1.1-py3-none-any.whl

COPY ./entrypoint.sh /app
# figure out crontab/ crond/ tail log
ENTRYPOINT ["wallatagger"]
#ENTRYPOINT ["/app/entrypoint.sh"]