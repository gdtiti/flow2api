# 环境变量配置覆盖功能使用指南

## 概述

Flow2API 现在支持使用环境变量来覆盖配置文件 `setting.toml` 中的设置项。这个功能使得在不同环境（开发、测试、生产）中灵活配置应用变得更加容易。

## 环境变量命名规则

所有环境变量都使用 `FLOW2API_` 前缀，格式为：

```
FLOW2API_{SECTION}_{KEY}
```

其中：
- `{SECTION}` 是配置文件中的节名（大写）
- `{KEY}` 是配置项的键名（大写）

## 支持的环境变量

### 全局设置 (global)
- `FLOW2API_API_KEY` - API 密钥
- `FLOW2API_ADMIN_USERNAME` - 管理员用户名
- `FLOW2API_ADMIN_PASSWORD` - 管理员密码

### Flow 设置 (flow)
- `FLOW2API_LABS_BASE_URL` - Google Labs 基础 URL
- `FLOW2API_API_BASE_URL` - Google AI Sandbox API 基础 URL
- `FLOW2API_TIMEOUT` - 超时时间（秒）
- `FLOW2API_MAX_RETRIES` - 最大重试次数
- `FLOW2API_POLL_INTERVAL` - 轮询间隔（秒）
- `FLOW2API_MAX_POLL_ATTEMPTS` - 最大轮询尝试次数

### 服务器设置 (server)
- `FLOW2API_HOST` - 服务器主机地址
- `FLOW2API_PORT` - 服务器端口

### 调试设置 (debug)
- `FLOW2API_DEBUG_ENABLED` - 启用调试模式
- `FLOW2API_DEBUG_LOG_REQUESTS` - 记录请求日志
- `FLOW2API_DEBUG_LOG_RESPONSES` - 记录响应日志
- `FLOW2API_DEBUG_MASK_TOKEN` - 掩码 Token

### 代理设置 (proxy)
- `FLOW2API_PROXY_ENABLED` - 启用代理
- `FLOW2API_PROXY_URL` - 代理 URL

### 生成设置 (generation)
- `FLOW2API_IMAGE_TIMEOUT` - 图像生成超时时间（秒）
- `FLOW2API_VIDEO_TIMEOUT` - 视频生成超时时间（秒）

### 缓存设置 (cache)
- `FLOW2API_CACHE_ENABLED` - 启用缓存
- `FLOW2API_CACHE_TIMEOUT` - 缓存超时时间（秒）
- `FLOW2API_CACHE_BASE_URL` - 缓存基础 URL

## 布尔值配置

布尔值支持多种格式：

**真值 (True)：**
- `true`
- `1`
- `yes`
- `on`
- `enabled`

**假值 (False)：**
- `false`
- `0`
- `no`
- `off`
- `disabled`

## 使用示例

### Docker 环境变量设置

```yaml
version: '3.8'
services:
  flow2api:
    image: your-flow2api-image
    environment:
      # 覆盖基本配置
      - FLOW2API_HOST=0.0.0.0
      - FLOW2API_PORT=8080

      # 覆盖 API 密钥
      - FLOW2API_API_KEY=your-production-api-key

      # 启用调试模式
      - FLOW2API_DEBUG_ENABLED=true

      # 配置代理
      - FLOW2API_PROXY_ENABLED=true
      - FLOW2API_PROXY_URL=http://proxy.example.com:8080

      # 调整超时设置
      - FLOW2API_IMAGE_TIMEOUT=600
      - FLOW2API_VIDEO_TIMEOUT=1800
```

### 环境变量文件 (.env)

创建 `.env` 文件：

```bash
# .env
FLOW2API_HOST=127.0.0.1
FLOW2API_PORT=9999
FLOW2API_API_KEY=my-secret-key
FLOW2API_DEBUG_ENABLED=yes
FLOW2API_CACHE_ENABLED=1
FLOW2API_IMAGE_TIMEOUT=300
```

然后使用：

```bash
# Linux/macOS
export $(cat .env | xargs) && python main.py

# Windows PowerShell
Get-Content .env | ForEach-Object { $_.Split('=') | ForEach-Object { [Environment]::SetEnvironmentVariable($_[0], $_[1]) } }
python main.py

# 使用 direnv (推荐)
echo "dotenv" > .envrc
direnv allow
```

### 命令行设置

```bash
# Linux/macOS
FLOW2API_HOST=127.0.0.1 FLOW2API_PORT=9999 python main.py

# Windows PowerShell
$env:FLOW2API_HOST="127.0.0.1"
$env:FLOW2API_PORT="9999"
python main.py

# Windows CMD
set FLOW2API_HOST=127.0.0.1
set FLOW2API_PORT=9999
python main.py
```

## 配置优先级

配置的优先级从高到低为：

1. **环境变量** (最高优先级)
2. **数据库中的配置** (运行时设置)
3. **TOML 配置文件** (默认值，最低优先级)

## 验证配置

可以使用测试脚本来验证环境变量配置是否正确：

```bash
python config_test.py
```

## 调试技巧

### 查看当前配置覆盖

在代码中，你可以使用以下方法查看哪些环境变量正在覆盖配置：

```python
from core.config import config

# 获取环境变量覆盖信息
overrides = config.get_env_overrides_info()
for env_var, info in overrides.items():
    print(f"{env_var}: {info['env_value']} -> {info['config_value']}")
```

### 检查最终配置值

```python
from core.config import config

# 查看最终生效的配置值
print(f"Host: {config.server_host}")
print(f"Port: {config.server_port}")
print(f"Debug Enabled: {config.debug_enabled}")
print(f"API Key: {config.api_key}")
```

## 常见用例

### 开发环境 vs 生产环境

**开发环境 (.env.dev)：**
```bash
FLOW2API_DEBUG_ENABLED=true
FLOW2API_DEBUG_LOG_REQUESTS=true
FLOW2API_DEBUG_LOG_RESPONSES=true
FLOW2API_HOST=127.0.0.1
FLOW2API_PORT=8000
```

**生产环境 (.env.prod)：**
```bash
FLOW2API_DEBUG_ENABLED=false
FLOW2API_HOST=0.0.0.0
FLOW2API_PORT=80
FLOW2API_API_KEY=your-production-key
```

### 容器化部署

```dockerfile
# Dockerfile
FROM python:3.11
# ... 其他设置
ENV FLOW2API_HOST=0.0.0.0
ENV FLOW2API_PORT=80
ENV FLOW2API_DEBUG_ENABLED=false
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: flow2api-config
data:
  FLOW2API_HOST: "0.0.0.0"
  FLOW2API_PORT: "80"
  FLOW2API_DEBUG_ENABLED: "false"
  FLOW2API_CACHE_ENABLED: "true"
  FLOW2API_CACHE_TIMEOUT: "3600"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flow2api
spec:
  template:
    spec:
      containers:
      - name: flow2api
        envFrom:
        - configMapRef:
            name: flow2api-config
```

## 注意事项

1. **类型安全**：确保环境变量的值与预期的类型匹配（数字、布尔值、字符串）
2. **布尔值格式**：布尔值支持多种格式，建议使用 `true/false` 或 `1/0`
3. **配置验证**：应用启动时会验证环境变量值的格式，无效值会显示警告并使用默认值
4. **安全性**：避免在命令行历史或日志中暴露敏感的环境变量（如 API 密钥）
5. **重载配置**：调用 `config.reload_config()` 会重新读取环境变量

## 故障排除

### 常见问题

1. **环境变量没有生效**
   - 检查环境变量名称是否正确（大小写敏感）
   - 确认环境变量是否已正确设置
   - 使用 `config.get_env_overrides_info()` 检查覆盖状态

2. **类型转换错误**
   - 检查数字值是否为有效格式
   - 检查布尔值是否使用支持的格式

3. **配置未更新**
   - 调用 `config.reload_config()` 重新加载配置
   - 重启应用程序

### 调试命令

```python
# 查看原始配置
from core.config import config
print("Raw config:", config.get_raw_config())

# 查看环境变量覆盖信息
print("Env overrides:", config.get_env_overrides_info())
```

这个功能让 Flow2API 的配置管理更加灵活，特别适合容器化部署和不同环境的配置需求。