# faber-template

一个面向 FastAPI 服务的早期工程模板，采用清晰的分层目录，以 Beanie + MongoDB 作为数据访问方案，并通过 Pydantic Settings 管理运行配置。

[English](README_EN.md)

## 项目简介

`faber-template` 用于搭建结构清晰、便于继续扩展的 Python Web API 服务。目前仓库已经具备可运行的 FastAPI 应用工厂、ASGI 入口、MongoDB/Beanie 启停生命周期，以及区分存活与就绪语义的健康检查端点。

当前版本：`0.1.0`

## 当前状态

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| Python 项目与依赖锁定 | 已完成 | 使用 `pyproject.toml` 与 `uv.lock` 管理 |
| 应用配置 | 已完成 | 支持从 `.env` 和系统环境变量读取配置 |
| 分层目录 | 已建立 | API、模型、仓储、服务、数据库、中间件等目录已预留 |
| FastAPI 应用工厂 | 已完成 | 创建应用、挂载总路由，并通过 lifespan 管理长生命周期资源 |
| API 路由与健康检查 | 已完成 | 提供独立的 liveness 与 MongoDB readiness 端点 |
| MongoDB / Beanie 初始化 | 已完成 | 启动时连接、探活和初始化模型，失败时清理，退出时优雅关闭 |
| Redis 集成 | 未纳入当前范围 | 当前没有 Redis 依赖、配置或运行时代码 |
| 测试与部署 | 部分完成 | 已覆盖配置、数据库生命周期、应用启动和健康检查；容器与生产部署配置待实现 |

应用启动依赖 MongoDB：启动阶段无法连接或无法初始化 Beanie 时，进程会快速失败，不会以“已就绪”状态继续运行。

## 技术栈

- Python `>=3.10.11,<3.14`
- FastAPI `0.141.1`
- Beanie `2.2.0`
- Pydantic `2.13.4`
- Pydantic Settings `2.15.0`
- MongoDB（应用启动时连接并初始化 Beanie）
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
│   ├── schemas/             # 请求与响应数据模型（含健康响应）
│   ├── services/            # 业务逻辑层（含依赖健康检查）
│   ├── shared/              # 跨模块共享代码
│   ├── utils/               # 通用工具
│   └── app_factory.py       # FastAPI 应用工厂与 lifespan
├── tests/                   # 标准库单元测试
├── .env.example             # 环境变量示例
├── main.py                  # ASGI 应用与本地启动入口
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
APP_DESCRIPTION=一个由 Beanie 和 MongoDB 提供支持的 FastAPI 服务模板
APP_VERSION=0.1.0
APP_RUN_MODE=production
APP_HOST=127.0.0.1
APP_PORT=8000
APP_DEBUG=false
APP_API_DOCS=/docs
APP_API_REDOC=/redoc
APP_API_OPENAPI=/openapi.json
MONGODB_URI=mongodb://127.0.0.1:27017
MONGODB_DATABASE=faber-template
MONGODB_SERVER_SELECTION_TIMEOUT_MS=5000
```

### 4. 启动应用

```bash
uv run python main.py
```

也可以使用 Uvicorn CLI：

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

启动前必须保证配置的 MongoDB 可访问。应用会先执行 `ping` 并初始化 Beanie；任一步失败都会终止启动。

### 5. 调用健康检查

```bash
curl http://127.0.0.1:8000/health/live
curl http://127.0.0.1:8000/health/ready
```

| 端点 | 成功响应 | 语义 |
| --- | --- | --- |
| `GET /health/live` | `200 {"status":"ok"}` | 仅检查应用进程，不查询外部依赖 |
| `GET /health/ready` | `200 {"status":"ready","checks":{"mongodb":"up"}}` | 每次请求实时 ping MongoDB |
| `GET /health/ready` | `503 {"status":"not_ready","checks":{"mongodb":"down"}}` | MongoDB 无响应、返回失败或连接异常 |

readiness 响应和日志不会包含 MongoDB URI、账号或密码。

### 6. 单独验证 MongoDB 连接

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

应用工厂已经在 lifespan 中统一管理 MongoDB。新增 Beanie `Document` 模型后，需要将其加入 `app.models.DOCUMENT_MODELS`。

## 配置项

配置不区分环境变量名称大小写，系统环境变量可以覆盖 `.env` 中的值。`APP_RUN_MODE` 仅接受 `development`、`testing` 和 `production`，并由 `get_settings()` 返回对应的配置类型。配置实例会被缓存，应用代码应统一通过该函数读取：

```python
from app.core.config import get_settings

settings = get_settings()
print(settings.APP_NAME)
print(settings.MONGODB_URI)
```

`.env` 使用项目绝对路径定位，因此从项目外的工作目录启动也能正确读取。`APP_API_DOCS`、`APP_API_REDOC` 或 `APP_API_OPENAPI` 可设置为 `null` 来关闭对应端点。

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
| `APP_HOST` | `127.0.0.1` | 本地启动入口的 Uvicorn 监听主机 |
| `APP_PORT` | `8000` | 本地启动入口的监听端口，范围为 1-65535 |
| `APP_DEBUG` | `false` | 调试开关 |
| `APP_API_DOCS` | `None` | Swagger UI 路径；设置为 `null` 时关闭 |
| `APP_API_REDOC` | `None` | ReDoc 路径；设置为 `null` 时关闭 |
| `APP_API_OPENAPI` | `None` | OpenAPI JSON 路径；设置为 `null` 时关闭 |
| `MONGODB_URI` | `mongodb://127.0.0.1:27017` | MongoDB 连接地址 |
| `MONGODB_DATABASE` | `faber-template` | MongoDB 数据库名称 |
| `MONGODB_SERVER_SELECTION_TIMEOUT_MS` | `5000` | MongoDB 服务器选择超时时间（毫秒） |

不要把包含账号、密码或生产地址的 `.env` 提交到版本库；当前 `.gitignore` 已忽略 `.env`。

## 测试与验证

```bash
uv lock --check
uv run python -m unittest discover -s tests -v
uv run python -m compileall -q app tests
```

单元测试使用模拟数据库，不依赖本机 MongoDB，也不会写入数据。上面的独立 MongoDB 连接命令属于真实依赖验证，只执行 `ping` 和 Beanie 初始化。

## 建议的后续实现顺序

1. 根据真实需求增加业务 schema、service、repository 和 model，并注册新增的 Beanie 文档模型。
2. 决定是否确实需要 Redis，避免项目描述与实现长期不一致。
3. 补充统一的 API 错误结构、日志配置和可观测性能力。
4. 根据实际部署环境增加容器化、生产启动参数和持续集成。

## 开发约定

- API 层负责协议适配与参数接收，业务逻辑放在 `services/`。
- 数据访问细节放在 `repositories/`，Beanie 文档模型放在 `models/`。
- 请求和响应结构放在 `schemas/`，避免直接把持久化模型作为外部 API 契约。
- 新增配置时同步更新 `.env.example` 和本文档。
- 提交前至少确认锁文件有效，并执行项目已有的测试或静态检查。

## 许可证

仓库当前没有提供独立的 `LICENSE` 文件。在明确许可证之前，请勿假定本项目允许公开分发或商业使用。
