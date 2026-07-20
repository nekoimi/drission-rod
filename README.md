# Drission Rod

基于 [CloakBrowser-Manager](https://github.com/CloakHQ/CloakBrowser-Manager) 远程浏览器的高性能网页抓取 gRPC 服务。

## 特性

- **远程浏览器**：通过 CloakBrowser-Manager 按需启停，空闲自动停止
- **gRPC 服务**：高性能远程调用，支持并发请求
- **智能下载器**：验证码 OCR、自动登录、弹窗处理

## 快速开始

### 本地运行

```bash
# 安装依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env，填写 CLOAK_MANAGER_URL 和 CLOAK_PROFILE_ID

# 启动服务
uv run main.py
```

### Docker 部署

```bash
# 构建镜像
docker build -t drission-rod .

# 运行
docker run -d \
  --name drission-rod \
  -p 8191:8191 \
  -e CLOAK_MANAGER_URL=https://your-cloak-manager.com \
  -e CLOAK_PROFILE_ID=your-profile-id \
  drission-rod
```

## 配置

在 `.env` 或环境变量中配置：

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `GRPC_PORT` | gRPC 服务端口 | `8191` |
| `CLOAK_MANAGER_URL` | CloakBrowser-Manager 地址 | - |
| `CLOAK_PROFILE_ID` | 浏览器 Profile ID | - |
| `CLOAK_AUTH_TOKEN` | 认证 Token（可选） | - |
| `CLOAK_IDLE_TIMEOUT` | 空闲超时秒数 | `300` |

详见 [CloakBrowser-Manager API 文档](docs/cloakbrowser-manager-api.md)。

## gRPC API

```protobuf
service PageFetchService {
  rpc Fetch(FetchRequest) returns (FetchResponse);
  rpc FetchJavDB(FetchRequest) returns (FetchResponse);
  rpc FetchSehuatang(FetchRequest) returns (FetchResponse);
}

message FetchRequest {
  string url = 1;
  int32 timeout = 2;  // 默认 60 秒
}

message FetchResponse {
  bool success = 1;
  string html = 2;
  string error = 3;
}
```

### 客户端示例

```python
import grpc
from app.grpc.fetch_pb2 import FetchRequest
from app.grpc.fetch_pb2_grpc import PageFetchServiceStub

channel = grpc.insecure_channel('localhost:8191')
stub = PageFetchServiceStub(channel)

response = stub.Fetch(FetchRequest(url='https://example.com'))
print(response.html if response.success else response.error)
```

## 架构

```
┌─────────────┐     gRPC      ┌──────────────┐    CDP/WebSocket    ┌─────────────────────┐
│   Client    │ ────────────→ │ drission-rod │ ──────────────────→ │ CloakBrowser-Manager│
└─────────────┘               └──────────────┘                     └─────────────────────┘
                                     │                                      │
                                     │ 按需启停                              │ 管理浏览器
                                     ▼                                      ▼
                              ┌──────────────┐                     ┌─────────────────┐
                              │ 空闲检测器    │                     │ Remote Chromium │
                              │ (5分钟超时)   │                     └─────────────────┘
                              └──────────────┘
```

## 许可证

[MIT License](LICENSE)
