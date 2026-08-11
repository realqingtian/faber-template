# faber-template

一个面向 FastAPI 服务的早期工程模板，采用清晰的分层目录，计划以 Beanie + MongoDB 作为数据访问方案，并通过 Pydantic Settings 管理运行配置。

[English](README_EN.md)

## 项目简介

`faber-template` 用于搭建结构清晰、便于继续扩展的 Python Web API 服务。目前仓库已经完成项目元数据、依赖锁定、基础目录分层和应用配置模型，但仍处于脚手架阶段，尚未创建可运行的 FastAPI 应用实例。

当前版本：`0.1.0`

## 当前状态

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| Python 项目与依赖锁定 | 已完成 | 使用 `pyproject.toml` 与 `uv.lock` 管理 |
| 应用配置 | 已完成 | 支持从 `.env` 和系统环境变量读取配置 |
| 分层目录 | 已建立 | API、模型、仓储、服务、数据库、中间件等目录已预留 |
| FastAPI 应用工厂 | 待实现 | `app/app_factory.py` 当前尚未创建应用实例 |
| API 路由与健康检查 | 待实现 | 相关文件已预留，但还没有端点 |
| MongoDB / Beanie 初始化 | 已完成 | 支持连接、探活、模型注册、失败清理和优雅关闭 |
| Redis 集成 | 待实现 | 项目描述中包含 Redis 方向，但当前没有 Redis 依赖或配置 |
| 测试与部署 | 部分完成 | 已包含配置模块测试；容器和生产部署配置待实现 |

因此，当前代码可以完成依赖安装和配置加载验证，但还不能作为 HTTP 服务启动。

## 技术栈

- Python `>=3.10.11,<3.14`
- FastAPI `0.141.1`
- Beanie `2.2.0`
- Pydantic `2.13.4`
- Pydantic Settings `2.15.0`
- MongoDB（目标数据存储，连接初始化待实现）
- uv（推荐的依赖与虚拟环境管理工具）

## 项目结构

```text
faber-template/
├── app/
│   ├── api/                 # API 路由与端点
│   │   └── health/          # 健康检查模块
│   ├── core/                # 核心配置
│   │   └── config.py        # Pydantic Settings 配置模型
│   ├── database/            # 数据库连接与初始化
│   ├── middleware/          # HTTP 中间件
│   ├── models/              # Beanie 文档模型
│   ├── repositories/        # 数据访问层
│   ├── schemas/             # 请求与响应数据模型
│   ├── services/            # 业务逻辑层
│   ├── shared/              # 跨模块共享代码
│   ├── utils/               # 通用工具
│   └── app_factory.py       # FastAPI 应用工厂（待实现）
├── tests/                   # 标准库单元测试
├── .env.example             # 环境变量示例
├── main.py                  # 应用入口（待实现）
├── pyproject.toml           # 项目元数据与直接依赖
└── uv.lock                  # 完整依赖锁文件
```

## 快速开始

### 1. 环境要求

请先安装：

- Python 3.10.11 至 3.13
- [uv](https://docs.astral.sh/uv/)

验证数据库连接时，需要先启动 MongoDB。

### 2. 安装依赖

```bash
uv sync --locked
```

该命令会按照 `uv.lock` 创建或更新本地 `.venv`，并安装锁定版本的依赖。

### 3. 配置环境变量

```bash
cp .env.example .env
```

`.env.example` 已列出当前支持的配置。复制后可按运行环境修改：

```dotenv
APP_NAME=faber-template
APP_DESCRIPTION=一个由 Beanie 和 Redis 提供支持的 FastAPI 服务模板
APP_VERSION=0.1.0
APP_RUN_MODE=production
APP_DEBUG=false
APP_API_DOCS=/docs
APP_API_REDOC=/redoc
MONGODB_URI=mongodb://127.0.0.1:27017
MONGODB_DATABASE=faber-template
MONGODB_SERVER_SELECTION_TIMEOUT_MS=5000
```

### 4. 验证配置加载

```bash
uv run python -c "from app.core.config import get_settings; print(get_settings().model_dump())"
```

如果命令正常输出配置字典，说明依赖和基础配置模块工作正常。

### 5. 验证 MongoDB 连接

```bash
uv run python - <<'PY'
import asyncio
from app.database import mongodb

async def main():
    await mongodb.connect()
    try:
        print(await mongodb.ping())
    finally:
        await mongodb.disconnect()

asyncio.run(main())
PY
```

在 FastAPI 应用工厂的 lifespan 中可以直接组合 `mongodb_lifespan()`。新增 Beanie `Document` 模型后，需要将其加入 `app.models.DOCUMENT_MODELS`。

## 配置项

配置不区分环境变量名称大小写，系统环境变量可以覆盖 `.env` 中的值。`APP_RUN_MODE` 仅接受 `development`、`testing` 和 `production`，并由 `get_settings()` 返回对应的配置类型。配置实例会被缓存，应用代码应统一通过该函数读取：

```python
from app.core.config import get_settings

settings = get_settings()
print(settings.APP_NAME)
print(settings.MONGODB_URI)
```

`.env` 使用项目绝对路径定位，因此从项目外的工作目录启动也能正确读取。`APP_API_DOCS` 或 `APP_API_REDOC` 可设置为 `null` 来关闭对应文档端点。

| 运行模式 | 配置类型 | `APP_DEBUG` 类型默认值 |
| --- | --- | --- |
| `development` | `DevelopmentSettings` | `true` |
| `testing` | `TestingSettings` | `false` |
| `production` | `ProductionSettings` | `false` |

如果系统环境和 `.env` 都没有提供 `APP_RUN_MODE`，运行模式选择器会回退到 `development`；仓库提供的 `.env.example` 则显式使用 `production`。任何显式设置的 `APP_DEBUG` 都会覆盖上表中的类型默认值。

| 环境变量 | 默认值 | 用途 |
| --- | --- | --- |
| `APP_NAME` | `faber-template` | 应用名称 |
| `APP_DESCRIPTION` | 中文项目描述 | OpenAPI / 应用描述 |
| `APP_VERSION` | `0.1.0` | 应用版本 |
| `APP_RUN_MODE` | `production` | 运行模式：`development`、`testing` 或 `production` |
| `APP_DEBUG` | `false` | 调试开关 |
| `APP_API_DOCS` | `None` | Swagger UI 路径；应用工厂实现后生效 |
| `APP_API_REDOC` | `None` | ReDoc 路径；应用工厂实现后生效 |
| `MONGODB_URI` | `mongodb://127.0.0.1:27017` | MongoDB 连接地址 |
| `MONGODB_DATABASE` | `faber-template` | MongoDB 数据库名称 |
| `MONGODB_SERVER_SELECTION_TIMEOUT_MS` | `5000` | MongoDB 服务器选择超时时间（毫秒） |

不要把包含账号、密码或生产地址的 `.env` 提交到版本库；当前 `.gitignore` 已忽略 `.env`。

## 建议的后续实现顺序

1. 在 `app/app_factory.py` 中创建 FastAPI 应用和生命周期管理逻辑。
2. 在 `app/api/router.py` 中定义总路由，并实现健康检查端点。
3. 在 `main.py` 中暴露 ASGI `app`，并添加 Uvicorn 等 ASGI Server 依赖。
4. 根据真实需求决定是否引入 Redis，避免项目描述与实现长期不一致。
5. 为后续模块增加测试，并补充代码质量检查、容器化和部署配置。

## 开发约定

- API 层负责协议适配与参数接收，业务逻辑放在 `services/`。
- 数据访问细节放在 `repositories/`，Beanie 文档模型放在 `models/`。
- 请求和响应结构放在 `schemas/`，避免直接把持久化模型作为外部 API 契约。
- 新增配置时同步更新 `.env.example` 和本文档。
- 提交前至少确认锁文件有效，并执行项目已有的测试或静态检查。

## 许可证

仓库当前没有提供独立的 `LICENSE` 文件。在明确许可证之前，请勿假定本项目允许公开分发或商业使用。
