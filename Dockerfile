FROM ghcr.io/nekoimi/drission-rod-runtime:latest

LABEL maintainer="nekoimi <nekoimime@gmail.com>"

WORKDIR /workspace

COPY . .

RUN python -m pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir uv && uv sync --index-url https://mirrors.aliyun.com/pypi/simple/

EXPOSE 8191 8291

CMD [ "uv", "run", "main.py" ]