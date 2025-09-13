FROM python:3.12.11-slim-bookworm

LABEL maintainer="nekoimi <nekoimime@gmail.com>"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

# 安装依赖：Chromium、字体、中文字体、时区
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        unzip \
        chromium \
        fonts-freefont-ttf \
        fonts-noto-color-emoji \
        fonts-wqy-zenhei \
        tzdata \
        ca-certificates \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
        dpkg-reconfigure -f noninteractive tzdata && \
        update-ca-certificates && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*

COPY local.conf /etc/fonts/local.conf

# 创建工作目录并添加用户
RUN mkdir -p /workspace && mkdir -p /var/lib/chromium-data && \
    groupadd -g 1000 appuser && \
    useradd -u 1000 -g 1000 -ms /bin/bash appuser && \
    chown -R appuser:appuser /workspace && \
    chown -R appuser:appuser /var/lib/chromium-data

# Autorun chrome headless
ENV CHROMIUM_FLAGS="--disable-software-rasterizer --disable-dev-shm-usage"
ENV CHROME_BIN=/usr/bin/chromium

# 设置 Chromium 启动路径给 Rod 用
ENV CHROMIUM_BROWSER_PATH=/usr/bin/chromium
ENV CHROMIUM_DATA_DIR=/var/lib/chromium-data

# Run as non-privileged
USER appuser

WORKDIR /workspace

VOLUME /var/lib/chromium-data

ENTRYPOINT ["chromium", "--headless"]
