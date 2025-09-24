FROM python:3.12.11-slim-bookworm

LABEL maintainer="nekoimi <nekoimime@gmail.com>"

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

# 安装依赖：Chromium、字体、中文字体、时区
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        tar \
        gnupg \
        libcap2-bin \
        unzip \
        chromium \
        fonts-freefont-ttf \
        fonts-noto-color-emoji \
        fonts-wqy-zenhei \
        tzdata \
        ca-certificates \
          \
        supervisor \
        xvfb \
        x11vnc \
        novnc \
        websockify \
        xfce4 \
        xfce4-terminal \
          \
    && ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
        dpkg-reconfigure -f noninteractive tzdata && \
        update-ca-certificates && \
        apt-get clean && \
        rm -rf /var/lib/apt/lists/*

COPY local.conf /etc/fonts/local.conf

# install caddy
RUN set -eux; \
    mkdir -p /var/lib/caddy/config/caddy \
		/var/lib/caddy/data/caddy \
		/etc/caddy \
		/usr/share/caddy && \
	wget -O /etc/caddy/Caddyfile "https://github.com/caddyserver/dist/raw/33ae08ff08d168572df2956ed14fbc4949880d94/config/Caddyfile" && \
	wget -O /usr/share/caddy/index.html "https://github.com/caddyserver/dist/raw/33ae08ff08d168572df2956ed14fbc4949880d94/welcome/index.html"

# https://github.com/caddyserver/caddy/releases
ENV CADDY_VERSION v2.10.2

RUN set -eux; \
    arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
        amd64)   binArch='amd64';   checksum='747df7ee74de188485157a383633a1a963fd9233b71fbb4a69ddcbcc589ce4e2cc82dacf5dbbe136cb51d17e14c59daeb5d9bc92487610b0f3b93680b2646546' ;; \
        armel)   binArch='armv6';   checksum='95b71fd99595018eebf4890782de63018ee86455531380b2a83a1814bb09c2588c0a531c877a26ba8a16a5b78072a1c26f7548bdec0e18abcef423fcc31a2e0e' ;; \
        armhf)   binArch='armv7';   checksum='215af42cf952726d962c9753a12c04248781221b66df8b7110726fa7905d7a5c2e50056e0b47ab3c709d3dcfb48fde0f11e184a6950de0a2ddf941d3e503d07b' ;; \
        arm64)   binArch='arm64';   checksum='6ce061a690312ab38367df3c5d5f89a2e4a263e7300d300d87356211bb81e79b15933e6d6203e03fbf26f15cc0311f264805f336147dbdd24938d84b57a4421c' ;; \
        ppc64el) binArch='ppc64le'; checksum='ab286a51e0e8ce79393519b0c7ebe99075f4539b57f6a34fe555ba8060f8fbaee36197a1e8e49d0050ab5d6a783253839bc2675137635f8d252aea27f2ca5a85' ;; \
        riscv64) binArch='riscv64'; checksum='e71c8ba2462990e0d8a67c544b694446ad36d045bf40ce641fae6774181677457f6ae8ed0b5c4c927ef8302d91c587074b6001318f377d7054113b5da6dee6df' ;; \
        s390x)   binArch='s390x';   checksum='b8aaa737b63308fac14cf84d7a658d9a0d74d2fe5f6a2eb57ca3ce7c52a73bea702c95da73ebfd20b3206bfb7b71ac8613aef9797e0f7a2c2a04bf5083092c2b' ;; \
        *) echo >&2 "error: unsupported architecture ($arch)"; exit 1 ;; \
    esac; \
    wget -O /tmp/caddy.tar.gz "https://github.com/caddyserver/caddy/releases/download/v2.10.2/caddy_2.10.2_linux_${binArch}.tar.gz"; \
    echo "$checksum  /tmp/caddy.tar.gz" | sha512sum -c; \
    tar x -z -f /tmp/caddy.tar.gz -C /usr/bin caddy; \
    rm -f /tmp/caddy.tar.gz; \
    setcap cap_net_bind_service=+ep /usr/bin/caddy; \
    chmod +x /usr/bin/caddy; \
    caddy version

ENV XDG_CONFIG_HOME /var/lib/caddy/config
ENV XDG_DATA_HOME /var/lib/caddy/data

# install uv
RUN pip install --no-cache-dir --prefix=/usr/local uv

WORKDIR /workspace

# 创建工作目录并添加用户
RUN mkdir -p /workspace && mkdir -p /var/lib/chromium-data && \
    groupadd -g 1000 appuser && \
    useradd -u 1000 -g 1000 -ms /bin/bash appuser && \
    chown -R appuser:appuser /workspace && \
    chown -R appuser:appuser /var/lib/chromium-data && \
    chown -R appuser:appuser /var/log/supervisor

# Autorun chrome headless
ENV CHROMIUM_FLAGS="--disable-software-rasterizer --disable-dev-shm-usage"
ENV CHROME_BIN=/usr/bin/chromium

# 设置 Chromium 启动路径
ENV CHROMIUM_BROWSER_PATH=/usr/bin/chromium
ENV CHROMIUM_DATA_DIR=/var/lib/chromium-data

# Supervisor 配置
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Run as non-privileged
#USER appuser

VOLUME /var/lib/chromium-data
VOLUME /var/lib/caddy
VOLUME /var/log/supervisor

EXPOSE 80
EXPOSE 443
EXPOSE 443/udp
EXPOSE 2019
# VNC 5900
EXPOSE 5900
# noVNC 6080
EXPOSE 6080

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
