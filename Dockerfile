FROM ghcr.io/nekoimi/drission-rod-runtime:latest

LABEL maintainer="nekoimi <nekoimime@gmail.com>"

WORKDIR /workspace

COPY . .

# install depts
RUN uv sync --index-url https://mirrors.aliyun.com/pypi/simple/

# Run as non-privileged
USER appuser

EXPOSE 8191

CMD [ "uv", "run", "main.py" ]