# Docker CI/CD 集成指南

## 概述

本项目配置了完整的 GitHub Actions 工作流，用于自动构建和推送 Docker 镜像到 GitHub Container Registry (GHCR)。

## 🚀 触发方式

### 1. 自动触发 (Automatic Triggers)

**推送触发：**
```bash
# 推送到 main/master 分支
git push origin main

# 推送标签
git tag v1.0.0
git push origin v1.0.0
```

**自动触发条件：**
- 推送到 `main` 或 `master` 分支
- 推送以 `v` 开头的标签 (如 `v1.0.0`, `v2.1.3`)

### 2. 手动触发 (Manual Triggers)

**在 GitHub 网页上手动触发��**
1. 进入项目的 Actions 页面
2. 选择 "Build and Push Docker Image" 或 "Manual Docker Build"
3. 点击 "Run workflow"
4. 填写必要参数
5. 点击 "Run workflow" 开始构建

**通过 GitHub CLI 手动触发：**
```bash
# 自动工作流
gh workflow run docker-build.yml

# 手动工作流（带参数）
gh workflow run docker-manual.yml \
  --field tag_name=v1.0.0-beta \
  --field push_to_registry=true \
  --field platforms="linux/amd64,linux/arm64"
```

## 🏷️ 镜像标签策略

### 自动标签

**分支推送：**
- `ghcr.io/your-username/flow2api:main-<commit_sha>`
- `ghcr.io/your-username/flow2api:latest` (仅 main 分支)

**标签推送：**
- `ghcr.io/your-username/flow2api:v1.0.0` (对应标签名)
- `ghcr.io/your-username/flow2api:YYYY-MM-DD-<commit_sha>`

### 手动标签

- `ghcr.io/your-username/flow2api:<custom_tag>`
- `ghcr.io/your-username/flow2api:<branch>-<custom_tag>`
- `ghcr.io/your-username/flow2api:latest` (main 分支时)

## 🏗️ 构建配置

### 支持的平台

- `linux/amd64` - 标准x64架构
- `linux/arm64` - ARM64架构 (适用于Apple Silicon, ARM服务器)

### 构建优化

- **多平台构建**：支持同时构建多个架构
- **缓存优化**：使用 GitHub Actions 缓存加速构建
- **层缓存**：利用 Docker Buildx 缓存机制

## 🔧 工作流详解

### docker-build.yml (主工作流)

**触发条件：**
```yaml
on:
  push:
    branches: [main, master]
    tags: ['v*']
  workflow_dispatch:
    inputs:
      # 手动触发参数
```

**作业流程：**
1. **build-and-push** - 构建和推送镜像
2. **test-image** - 测试镜像（可选）
3. **security-scan** - 安全扫描（推送时）

### docker-manual.yml (手动工作流)

**触发条件：**
```yaml
on:
  workflow_dispatch:
    inputs:
      tag_name: 'required'
      push_to_registry: true
      platforms: 'linux/amd64,linux/arm64'
      run_tests: true
      security_scan: false
```

**作业流程：**
1. **manual-build** - 手动构建镜像
2. **manual-test** - 可选测试
3. **manual-security-scan** - 可选安全扫描

## 🐳 使用镜像

### 拉取镜像

```bash
# 拉取最新版本
docker pull ghcr.io/your-username/flow2api:latest

# 拉取指定版本
docker pull ghcr.io/your-username/flow2api:v1.0.0

# 拉取特定提交
docker pull ghcr.io/your-username/flow2api:main-abc1234
```

### 运行容器

```bash
# 基本运行
docker run -d \
  --name flow2api \
  -p 8000:8000 \
  ghcr.io/your-username/flow2api:latest

# 带数据持久化
docker run -d \
  --name flow2api \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config/setting.toml:/app/config/setting.toml \
  ghcr.io/your-username/flow2api:latest

# 带环境变量配置
docker run -d \
  --name flow2api \
  -p 8000:8000 \
  -e FLOW2API_DEBUG_ENABLED=true \
  -e FLOW2API_API_KEY=your-api-key \
  -e FLOW2API_HOST=0.0.0.0 \
  -e FLOW2API_PORT=8080 \
  ghcr.io/your-username/flow2api:latest
```

### Docker Compose

更新你的 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  flow2api:
    image: ghcr.io/your-username/flow2api:latest
    container_name: flow2api
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./config/setting.toml:/app/config/setting.toml
    environment:
      - PYTHONUNBUFFERED=1
      - FLOW2API_DEBUG_ENABLED=false
      - FLOW2API_API_KEY=your-api-key
    restart: unless-stopped

# 使用指定版本
# image: ghcr.io/your-username/flow2api:v1.0.0
```

## 🔒 安全扫描

工作流集成了 Trivy 安全扫描器：

- **自动扫描**：推送触发时自动运行
- **手动扫描**：手动触发时可选
- **结果查看**：扫描结果会上传到 GitHub Security 标签页

### 查看扫描结果

1. 进入项目的 Security 页面
2. 查看依赖项漏洞和配置问题
3. 根据建议修复安全问题

## 📊 监控和日志

### 构建状态

- GitHub Actions 会显示详细的构建日志
- 构建摘要包含镜像信息、标签列表、拉取命令
- 测试结果显示容器的运行状态

### 容器监控

```bash
# 查看容器状态
docker ps

# 查看容器日志
docker logs flow2api

# 查看容器资源使用
docker stats flow2api
```

## 🛠️ 自定义配置

### 修改工作流

编辑 `.github/workflows/docker-build.yml` 或 `.github-manual.yml`：

```yaml
# 修改镜像名称
env:
  IMAGE_NAME: ${{ github.repository }}

# 修改支持的平台
platforms: ${{ github.event.inputs.platforms || 'linux/amd64,linux/arm64' }}

# 添加自定义标签
tags: |
  type=raw,value=production,enable={{is_default_branch}}
  type=raw,value=staging,enable={{branch == 'develop'}}
```

### 修改 Dockerfile

```dockerfile
# 添加多阶段构建
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

## 🚨 故障排除

### 常见问题

1. **构建失败**
   - 检查 Dockerfile 语法
   - 确认 requirements.txt 有效
   - 查看构建日志

2. **推送失败**
   - 检查 GitHub Token 权限
   - 确认仓库名称正确
   - 验证镜像标签格式

3. **容器启动失败**
   - 检查端口冲突
   - 验证环境变量格式
   - 查看容器日志

### 调试命令

```bash
# 本地构建测试
docker build -t flow2api:test .

# 本地运行测试
docker run --rm -p 8000:8000 flow2api:test

# 检查镜像层
docker history flow2api:test

# 检查镜像配置
docker inspect flow2api:test
```

## 📈 最佳实践

1. **版本管理**
   - 使用语义化版本标签
   - main 分支保持 stable
   - develop 分支用于开发

2. **镜像优化**
   - 使用多阶段构建
   - 保持镜像体积小
   - 利用层缓存

3. **安全实践**
   - 定期更新依赖
   - 修复安全漏洞
   - 使用非 root 用户

4. **监控告警**
   - 设置构建失败通知
   - 监控容器运行状态
   - 定期安全扫描

这个 CI/CD 配置提供了完整的 Docker 镜像管理解决方案，支持自动化和手动两种触发方式，满足不同场景的需求。