FROM ghcr.io/nekoimi/drission-rod-runtime:latest

LABEL maintainer="nekoimi <nekoimime@gmail.com>"

WORKDIR /workspace

COPY . .

# install depts
RUN uv sync --index-url https://mirrors.aliyun.com/pypi/simple/

# grpc health
RUN curl -L https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/v0.4.14/grpc_health_probe-linux-amd64 \
    -o /usr/local/bin/grpc_health_probe \
    && chmod +x /usr/local/bin/grpc_health_probe

# Run as non-privileged
USER appuser

EXPOSE 8191

CMD [ "uv", "run", "main.py" ]