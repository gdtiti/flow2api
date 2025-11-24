# Docker 工作流修复说明

## 🐛 问题描述

在 GitHub Actions 构建过程中遇到了以下错误：

```
Error: Missing value attribute for type=raw,suffix=-{{date('YYYY-MM-DD')}}{{sha}}
```

## 🔧 修复内容

### 1. 修复标签语法错误

**修复前：**
```yaml
type=raw,suffix=-{{date('YYYY-MM-DD')}}{{sha}}  # ❌ 缺少 value 属性
```

**修复后：**
```yaml
type=raw,value={{date('YYYY-MM-DD')}}-{{sha}}  # ✅ 正确的语法
```

### 2. 增强触发机制

**新增功能：**
- ✅ 支持 Pull Request 触发（仅构建，不推送）
- ✅ 改进手动触发的参数处理
- ✅ 优化推送条件逻辑

### 3. 优化构建配置

**改进内容：**
```yaml
# PR 时不推送到 registry，仅构建测试
push: ${{ github.event_name != 'pull_request' && github.event.inputs.push_to_registry != 'false' }}

# PR 时不登录 registry，节省资源
if: github.event_name != 'pull_request' && github.event.inputs.push_to_registry != 'false'
```

## 📋 完整的标签策略

### 触发条件和生成的标签

| 触发类型 | 生成的标签 | 是否推送 | 说明 |
|---------|-----------|---------|------|
| **main/master 分支推送** | `main-<commit_sha>`, `latest`, `YYYY-MM-DD-<commit_sha>` | ✅ | 生产版本 |
| **标签推送 (v1.0.0)** | `v1.0.0`, `YYYY-MM-DD-<commit_sha>` | ✅ | 版本发布 |
| **Pull Request** | `pr-<pr_number>` | ❌ | 仅构建测试 |
| **手动触发** | `<custom_tag>`, `<branch>-<custom_tag>`, `latest`(main分支) | ✅ | 自定义构建 |

### 标签示例

```bash
# 推送到 main 分支
ghcr.io/thesmallhancat/gdtiti_flow2api:main-abc1234
ghcr.io/thesmallhancat/gdtiti_flow2api:latest
ghcr.io/thesmallhancat/gdtiti_flow2api:2024-01-15-abc1234

# 推送标签 v1.0.0
ghcr.io/thesmallhancat/gdtiti_flow2api:v1.0.0
ghcr.io/thesmallhancat/gdtiti_flow2api:2024-01-15-abc1234

# Pull Request #123
ghcr.io/thesmallhancat/gdtiti_flow2api:pr-123  # 仅构建，不推送

# 手动触发，标签 "beta"
ghcr.io/thesmallhancat/gdtiti_flow2api:beta
ghcr.io/thesmallhancat/gdtiti_flow2api:main-beta
ghcr.io/thesmallhancat/gdtiti_flow2api:latest  # main分支时
```

## 🚀 使用方法

### 自动触发

```bash
# 推送到主分支
git push origin main

# 推送版本标签
git tag v1.0.0
git push origin v1.0.0

# 创建 PR（自动构建测试镜像）
git push origin feature-branch
# 在 GitHub 上创建 Pull Request
```

### 手动触发

1. 进入 GitHub 项目的 Actions 页面
2. 选择 "Build and Push Docker Image"
3. 填写参数：
   - **Docker image tag**: 自定义标签（留空则自动生成）
   - **Push to registry**: 是否推送到注册表
   - **Build platforms**: 选择目标架构

## 🔍 验证修复

### 检查工作流语法

工作流语法现在符合 `docker/metadata-action@v5` 的要求：

```yaml
tags: |
  type=ref,event=branch,suffix=-{{sha}}                     # ✅
  type=ref,event=tag                                        # ✅
  type=raw,value=latest,enable={{is_default_branch}}        # ✅
  type=raw,value={{date('YYYY-MM-DD')}}-{{sha}}            # ✅
  type=raw,value=${{ github.event.inputs.tag_name }},enable=${{ github.event.inputs.tag_name != '' }}  # ✅
  type=raw,value=pr-{{pr_number}},enable=${{ github.event_name == 'pull_request' }}  # ✅
```

### 本地测试

可以使用以下命令本地测试 Docker 构建：

```bash
# 本地构建测试
docker build -t flow2api:test .

# 验证镜像
docker run --rm -p 8000:8000 flow2api:test
```

## 📊 改进效果

### 修复前的问题
- ❌ 标签语法错误导致构建失败
- ❌ 缺少 PR 支持
- ❌ 推送逻辑不够灵活

### 修复后的优势
- ✅ 所有标签语法正确
- ✅ 支持多种触发场景
- ✅ 智能推送控制
- ✅ 节省 CI/CD 资源
- ✅ 更好的标签管理

## 🛠️ 其他改进

1. **安全增强**：PR 时不推送，避免意外发布
2. **资源优化**：PR 时不登录 registry，节省操作
3. **标签多样性**：支持多种标签策略满足不同需求
4. **错误处理**：更完善的条件判断和错误预防

这个修复确保了 Docker CI/CD 流程的稳定性和灵活性，支持各种开发场景需求。