FROM python:3.12.11-slim-bookworm

LABEL maintainer="nekoimi <nekoimime@gmail.com>"

WORKDIR /app

COPY . .

RUN sed -i 's#https\?://dl-cdn.alpinelinux.org/alpine#https://mirrors.tuna.tsinghua.edu.cn/alpine#g' /etc/apk/repositories && \
    apk update && \
    apk add --no-cache tzdata && \
    ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
        \
    python -m pip install -i https://mirrors.aliyun.com/pypi/simple/ --no-cache-dir uv && \
    uv sync --index-url https://mirrors.aliyun.com/pypi/simple/

EXPOSE 8191 8291

CMD [ "uv", "run", "main.py" ]