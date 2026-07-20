# Drission Rod

基于 Chromium 浏览器的高性能网页抓取服务，通过 gRPC 协议提供远程页面抓取能力。

## 功能特性

- **浏览器自动化**：基于 DrissionPage 封装 Chromium，支持无头/有界面模式
- **gRPC 服务**：高性能远程调用接口，支持并发请求处理
- **智能下载器**：支持验证码识别（OCR）、自动登录、弹窗处理等交互场景
- **健康保活**：定时任务保持浏览器连接活跃
- **灵活配置**：环境变量 + `.env` 文件配置，支持代理、数据目录等参数
- **完善的日志**：分级日志输出，支持文件轮转和保留策略
- **容器化部署**：Docker + supervisord 进程管理，集成健康检查

## 技术栈

| 组件 | 用途 |
|------|------|
| [DrissionPage](https://github.com/g1879/DrissionPage) | Chromium 浏览器自动化 |
| [gRPC](https://grpc.io/) | 远程过程调用协议 |
| [ddddocr](https://github.com/sml2h3/ddddocr) | 验证码 OCR 识别 |
| [APScheduler](https://apscheduler.readthedocs.io/) | 定时任务调度 |
| [loguru](https://github.com/Delgan/loguru) | 日志记录 |
| [pydantic-settings](https://github.com/pydantic/pydantic-settings) | 配置管理 |
| [uv](https://github.com/astral-sh/uv) | Python 包管理 |

## 快速开始

### 环境要求

- Python >= 3.12
- Chromium 浏览器（Linux 需单独安装）
- Docker（可选）

### 本地安装

```bash
# 克隆仓库
git clone <repository-url>
cd drission-rod

# 创建虚拟环境并安装依赖
uv sync

# 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件进行自定义配置

# 启动服务
uv run python main.py
```

### Docker 部署

```bash
# 构建镜像
docker build -t drission-rod .

# 运行容器
docker run -d \
  --name drission-rod \
  -p 8191:8191 \
  -e GRPC_PORT=8191 \
  -e CHROMIUM_HEADLESS=true \
  drission-rod
```

## 配置说明

创建 `.env` 文件或在环境变量中配置：

```env
# 调试模式
debug=false

# gRPC 服务端口
grpc_port=8191

# 浏览器配置
chromium_headless=false          # 是否启用无头模式
chromium_proxy=http://127.0.0.1:8080  # 代理服务器（可选）
chromium_data_dir=/path/to/data       # 用户数据目录（可选）

# 站点登录配置（如需要）
javdb_username=your_username
javdb_password=your_password
```

## gRPC API

### 接口定义

```protobuf
service PageFetchService {
  // 默认页面抓取
  rpc Fetch(FetchRequest) returns (FetchResponse);
  
  // 支持验证码识别和登录的页面抓取
  rpc FetchWithAuth(FetchRequest) returns (FetchResponse);
  
  // 支持 R18 弹窗处理的页面抓取
  rpc FetchWithModal(FetchRequest) returns (FetchResponse);
}

message FetchRequest {
  string url = 1;      // 目标 URL
  int32 timeout = 2;   // 超时时间（秒），默认 60
}

message FetchResponse {
  bool success = 1;    // 是否成功
  string html = 2;     // 页面 HTML 内容
  string error = 3;    // 错误信息（失败时）
}
```

### Python 客户端示例

```python
import grpc
from app.grpc.fetch_pb2 import FetchRequest
from app.grpc.fetch_pb2_grpc import PageFetchServiceStub

def fetch_page(url: str, timeout: int = 60):
    channel = grpc.insecure_channel('localhost:8191')
    stub = PageFetchServiceStub(channel)
    
    request = FetchRequest(url=url, timeout=timeout)
    response = stub.Fetch(request)
    
    if response.success:
        return response.html
    else:
        raise Exception(response.error)

# 使用示例
html = fetch_page('https://example.com')
print(html)
```

## 架构说明

### 目录结构

```
drission-rod/
├── app/
│   ├── browser/          # Chromium 浏览器管理
│   │   ├── chromium.py   # 浏览器初始化和生命周期管理
│   │   └── __init__.py
│   ├── config/           # 配置管理
│   │   ├── config.py     # Pydantic Settings 配置类
│   │   └── __init__.py
│   ├── downloader/       # 页面下载器
│   │   ├── browser.py    # 下载器抽象基类
│   │   ├── default/      # 默认下载器
│   │   ├── auth/         # 支持登录认证的下载器
│   │   └── modal/        # 支持弹窗处理的下载器
│   ├── grpc/             # gRPC 服务实现
│   │   ├── fetch_grpc_server.py  # 服务实现
│   │   ├── fetch_pb2.py          # Protobuf 消息
│   │   ├── fetch_pb2_grpc.py     # gRPC 存根
│   │   └── __init__.py
│   ├── log/              # 日志配置
│   │   └── __init__.py
│   └── utils/            # 工具函数
├── proto/                # Protobuf 定义文件
├── docker/               # Docker 配置
├── tests/                # 测试文件
├── main.py              # 服务入口
├── pyproject.toml       # 项目配置
├── Dockerfile           # Docker 构建文件
└── supervisord.conf     # 进程管理配置
```

### 下载器架构

```
BrowserDownloader (抽象基类)
    ├── wait_page_complete()  # 等待页面加载完成
    └── download()            # 抽象方法

DefaultBrowserDownloader
    └── download()            # 基础页面抓取

AuthBrowserDownloader
    ├── login()               # 自动登录流程
    ├── solve_captcha()       # 验证码识别
    └── download()            # 支持认证的抓取

ModalBrowserDownloader
    ├── handle_r18_modal()    # R18 弹窗处理
    └── download()            # 支持弹窗的抓取
```

### 核心流程

1. **服务启动**
   - 加载配置
   - 初始化日志系统
   - 启动浏览器保活定时任务
   - 启动 gRPC 服务

2. **页面抓取**
   - 接收 gRPC 请求
   - 创建新的浏览器标签页
   - 加载目标页面
   - 执行特定站点的交互逻辑（登录、验证码、弹窗）
   - 返回 HTML 内容
   - 关闭标签页

3. **健康保活**
   - 每 30 秒检查浏览器状态
   - 自动重启失效的浏览器实例

## 开发指南

### 添加新的下载器

1. 在 `app/downloader/` 下创建新的子目录
2. 继承 `BrowserDownloader` 基类
3. 实现 `download()` 方法
4. 在 `fetch_grpc_server.py` 中注册使用

示例：

```python
from app.downloader.browser import BrowserDownloader, FetchRequest

class CustomDownloader(BrowserDownloader):
    def download(self, req: FetchRequest) -> str:
        cur_tab = self.browser.new_tab()
        try:
            cur_tab.get(req.url)
            self.wait_page_complete(cur_tab)
            # 自定义交互逻辑
            return cur_tab.html
        finally:
            cur_tab.close()
```

### 编译 Protobuf

```bash
cd proto
bash compile.sh
```

### 运行测试

```bash
uv run pytest tests/
```

## 注意事项

1. **浏览器资源**：每个请求会创建新的标签页，大量并发时会消耗较多内存
2. **验证码识别**：OCR 识别率不是 100%，失败时会抛出异常
3. **页面超时**：默认 60 秒超时，可通过请求参数调整
4. **内存泄漏**：长时间运行后建议重启服务释放内存

## 许可证

[MIT License](LICENSE)

## 贡献

欢迎提交 Issue 和 Pull Request！
