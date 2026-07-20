# CloakBrowser-Manager API 接口文档

> 基于 [CloakHQ/CloakBrowser-Manager](https://github.com/CloakHQ/CloakBrowser-Manager) 源码整理

## 目录

- [认证](#认证)
- [Profile 管理](#profile-管理)
- [浏览器控制](#浏览器控制)
- [系统状态](#系统状态)
- [剪贴板](#剪贴板)
- [VNC 远程桌面](#vnc-远程桌面)
- [CDP 远程调试](#cdp-远程调试)
- [DrissionPage 对接示例](#drissionpage-对接示例)

---

## 认证

认证通过环境变量 `AUTH_TOKEN` 启用。未设置时所有接口开放访问。

### 检查认证状态

```
GET /api/auth/status
```

**认证：** 无需（豁免端点）

**响应：**
```json
{
  "auth_required": true,
  "authenticated": false
}
```

### 登录

```
POST /api/auth/login
```

**认证：** 无需

**请求体：**
```json
{
  "token": "your-auth-token"
}
```

**响应：**
```json
{
  "ok": true
}
```

> 登录成功后会设置 `auth_token` Cookie，后续请求可使用 Cookie 或 `Authorization: Bearer <token>` 头认证。

### 登出

```
POST /api/auth/logout
```

**认证：** 需要

**响应：**
```json
{
  "ok": true
}
```

---

## Profile 管理

### 获取所有 Profiles

```
GET /api/profiles
```

**认证：** 需要

**响应：**
```json
[
  {
    "id": "0803f920-2345-4e6a-8fe9-471d05036556",
    "name": "My Profile",
    "status": "running",
    "vnc_ws_port": 5900,
    "cdp_url": "/api/profiles/0803f920-2345-4e6a-8fe9-471d05036556/cdp",
    "tags": [
      {"id": 1, "name": "work"}
    ]
  }
]
```

### 创建 Profile

```
POST /api/profiles
```

**认证：** 需要

**请求体：**
```json
{
  "name": "My Profile",
  "tags": [{"name": "work"}]
}
```

**响应：** `201 Created`
```json
{
  "id": "0803f920-2345-4e6a-8fe9-471d05036556",
  "name": "My Profile",
  "status": "stopped",
  "vnc_ws_port": null,
  "cdp_url": null,
  "tags": [{"id": 1, "name": "work"}]
}
```

### 获取单个 Profile

```
GET /api/profiles/{profile_id}
```

**认证：** 需要

**响应：**
```json
{
  "id": "0803f920-2345-4e6a-8fe9-471d05036556",
  "name": "My Profile",
  "status": "running",
  "vnc_ws_port": 5900,
  "cdp_url": "/api/profiles/0803f920-2345-4e6a-8fe9-471d05036556/cdp",
  "tags": [{"id": 1, "name": "work"}]
}
```

### 更新 Profile

```
PUT /api/profiles/{profile_id}
```

**认证：** 需要

**请求体：**
```json
{
  "name": "Updated Name",
  "tags": [{"name": "personal"}]
}
```

**响应：** 更新后的 Profile 对象

### 删除 Profile

```
DELETE /api/profiles/{profile_id}
```

**认证：** 需要

**响应：**
```json
{
  "ok": true
}
```

> 会同时停止运行中的浏览器并删除用户数据目录。

---

## 浏览器控制

### 启动浏览器

```
POST /api/profiles/{profile_id}/launch
```

**认证：** 需要

**响应：**
```json
{
  "profile_id": "0803f920-2345-4e6a-8fe9-471d05036556",
  "status": "running",
  "vnc_ws_port": 5900,
  "display": ":99",
  "cdp_url": "/api/profiles/0803f920-2345-4e6a-8fe9-471d05036556/cdp"
}
```

**错误：**
- `404` - Profile 不存在
- `409` - Profile 已在运行
- `400` - 启动参数错误
- `500` - 启动失败

### 停止浏览器

```
POST /api/profiles/{profile_id}/stop
```

**认证：** 需要

**响应：**
```json
{
  "ok": true
}
```

### 获取 Profile 状态

```
GET /api/profiles/{profile_id}/status
```

**认证：** 需要

**响应：**
```json
{
  "profile_id": "0803f920-2345-4e6a-8fe9-471d05036556",
  "status": "running",
  "vnc_ws_port": 5900,
  "cdp_url": "/api/profiles/0803f920-2345-4e6a-8fe9-471d05036556/cdp"
}
```

---

## 系统状态

### 获取系统状态

```
GET /api/status
```

**认证：** 无需（豁免端点）

**响应：**
```json
{
  "running_count": 3,
  "binary_version": "Chrome/146.0.7680.177",
  "profiles_total": 10
}
```

---

## 剪贴板

### 设置剪贴板内容

```
POST /api/profiles/{profile_id}/clipboard
```

**认证：** 需要

**请求体：**
```json
{
  "text": "要粘贴的文本内容"
}
```

**响应：**
```json
{
  "ok": true
}
```

> 通过 `xclip` 将文本写入 VNC 会话的 X 剪贴板。

### 获取剪贴板内容

```
GET /api/profiles/{profile_id}/clipboard
```

**认证：** 需要

**响应：**
```json
{
  "text": "剪贴板中的文本"
}
```

> 优先通过 Playwright CDP 读取 Chrome 的剪贴板，回退到 `xclip`。

---

## VNC 远程桌面

### VNC WebSocket 代理

```
WS /api/profiles/{profile_id}/vnc
```

**认证：** 需要

**子协议：** `binary`（可选）

**说明：**
- 前端与 KasmVNC 之间的 WebSocket 双向代理
- 自动过滤 KasmVNC 不支持的 RFB 扩展消息类型
- 转换 KasmVNC 的 BinaryClipboard 为标准 RFB ServerCutText
- 将 noVNC 的 6 字节 PointerEvent 转换为 KasmVNC 的 11 字节格式

---

## CDP 远程调试

### 获取 CDP 连接信息

```
GET /api/profiles/{profile_id}/cdp
```

**认证：** 需要

**响应：**
```json
{
  "cdp_url": "/api/profiles/0803f920-2345-4e6a-8fe9-471d05036556/cdp",
  "usage": "playwright.chromium.connect_over_cdp('http://<host>/api/profiles/0803f920-2345-4e6a-8fe9-471d05036556/cdp')"
}
```

### 获取 Chrome 版本信息

```
GET /api/profiles/{profile_id}/cdp/json/version
GET /api/profiles/{profile_id}/cdp/json/version/
```

**认证：** 需要

**响应：**
```json
{
  "Browser": "Chrome/146.0.7680.177",
  "Protocol-Version": "1.3",
  "User-Agent": "Mozilla/5.0 ...",
  "V8-Version": "14.6.202.31",
  "WebKit-Version": "537.36 (...)",
  "webSocketDebuggerUrl": "wss://<host>/api/profiles/0803f920-2345-4e6a-8fe9-471d05036556/cdp"
}
```

> `webSocketDebuggerUrl` 已被重写为通过代理的地址。

### 获取页面列表

```
GET /api/profiles/{profile_id}/cdp/json/list
GET /api/profiles/{profile_id}/cdp/json/list/
GET /api/profiles/{profile_id}/cdp/json
GET /api/profiles/{profile_id}/cdp/json/
```

**认证：** 需要

**响应：**
```json
[
  {
    "id": "...",
    "type": "page",
    "title": "百度一下",
    "url": "https://www.baidu.com",
    "webSocketDebuggerUrl": "wss://<host>/api/profiles/0803f920-2345-4e6a-8fe9-471d05036556/cdp/devtools/page/<GUID>"
  }
]
```

> 每个页面的 `webSocketDebuggerUrl` 已被重写为通过代理的地址。

### CDP WebSocket 代理（浏览器级别）

```
WS /api/profiles/{profile_id}/cdp
```

**认证：** 需要

**说明：**
- 浏览器级别的 CDP WebSocket 代理
- 自动连接 Chrome 的 `webSocketDebuggerUrl`
- 双向透传 CDP JSON 消息

### CDP WebSocket 代理（页面级别）

```
WS /api/profiles/{profile_id}/cdp/devtools/{path}
```

**认证：** 需要

**说明：**
- 页面级别的 CDP WebSocket 代理
- `path` 格式：`page/<GUID>`
- 用于连接特定标签页的 DevTools

---

## DrissionPage 对接示例

### 方式一：通过 API 获取 WebSocket 地址

```python
import requests
from DrissionPage import Chromium, ChromiumOptions

# CloakBrowser-Manager 配置
MANAGER_URL = "https://cloakbrowser-manager.home.sakuraio.com"
PROFILE_ID = "0803f920-2345-4e6a-8fe9-471d05036556"

# 1. 从 /json/version 获取 WebSocket 地址
resp = requests.get(
    f"{MANAGER_URL}/api/profiles/{PROFILE_ID}/cdp/json/version",
    verify=False
)
ws_url = resp.json()["webSocketDebuggerUrl"]
# ws_url = "wss://cloakbrowser-manager.home.sakuraio.com/api/profiles/0803f920-2345-4e6a-8fe9-471d05036556/cdp"

# 2. 使用 WebSocket 地址连接
options = ChromiumOptions()
options.set_address(ws_url)
browser = Chromium(addr_or_opts=options)

# 3. 操作浏览器
tab = browser.latest_tab
tab.get("https://www.baidu.com")
print(tab.title)  # 百度一下，你就知道
```

### 方式二：直接使用 WebSocket 地址

```python
from DrissionPage import Chromium, ChromiumOptions

# 如果已知 WebSocket 地址，可直接连接
WS_URL = "wss://cloakbrowser-manager.home.sakuraio.com/api/profiles/0803f920-2345-4e6a-8fe9-471d05036556/cdp"

options = ChromiumOptions()
options.set_address(WS_URL)
browser = Chromium(addr_or_opts=options)

tab = browser.latest_tab
```

### 方式三：通过 HTTP 地址连接（需要端口）

```python
from DrissionPage import Chromium, ChromiumOptions

# DrissionPage 也支持 http://host:port 格式
# 但 CloakBrowser-Manager 的 API 路径不是标准格式
# 建议使用 WebSocket 方式
```

---

## 错误码

| HTTP 状态码 | 说明 |
|-------------|------|
| `200` | 成功 |
| `201` | 创建成功 |
| `400` | 请求参数错误 |
| `401` | 未认证 |
| `404` | 资源不存在 |
| `409` | 资源冲突（如 Profile 已在运行） |
| `500` | 服务器内部错误 |
| `502` | CDP 端点不可达 |

### WebSocket 错误码

| 代码 | 说明 |
|------|------|
| `4004` | Profile 未运行 |
| `4005` | CDP 不可用 |
| `4401` | 未认证 |
| `4403` | Origin 不允许 |

---

## 注意事项

1. **WebSocket Origin 检查**：WebSocket 连接会检查 Origin 头，防止跨站 WebSocket 劫持（CSWSH）。非浏览器客户端（如 DrissionPage、Playwright）通常不发送 Origin 头，会被允许连接。

2. **CDP 地址重写**：`/json/version` 和 `/json/list` 返回的 `webSocketDebuggerUrl` 已被重写为通过 Manager 代理的地址，可直接使用。

3. **VNC 消息过滤**：VNC 代理会自动过滤 KasmVNC 不支持的 RFB 扩展消息，确保 noVNC 正常工作。

4. **认证方式**：支持 `Authorization: Bearer <token>` 头和 `auth_token` Cookie 两种方式。
