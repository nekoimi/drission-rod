FROM ghcr.io/nekoimi/drission-rod-runtime:latest

LABEL maintainer="nekoimi <nekoimime@gmail.com>"

WORKDIR /workspace

COPY . .

# Run as privileged
# USER root

# install depts
RUN uv sync --index-url https://mirrors.aliyun.com/pypi/simple/

# grpc health
RUN curl -L https://github.com/grpc-ecosystem/grpc-health-probe/releases/download/v0.4.14/grpc_health_probe-linux-amd64 \
    -o /usr/local/bin/grpc_health_probe \
    && chmod +x /usr/local/bin/grpc_health_probe

# Supervisor 配置
COPY supervisord.conf /etc/supervisor/conf.d/drission-rod.conf

# Run as non-privileged
# USER appuser

EXPOSE 8191
