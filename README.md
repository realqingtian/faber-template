# faber-template

一个基于 FastAPI、Beanie 和 MongoDB 的 Python Web API 服务模板。项目代码已经具备应用工厂、分层目录、环境配置、MongoDB 生命周期管理，以及区分存活与就绪语义的健康检查端点。

当前版本：`0.1.0`

## 当前能力

- 使用 `create_app()` 创建 FastAPI 应用，`main.py` 仅作为 ASGI 与本地启动入口。
- 使用 Pydantic Settings 从系统环境变量和项目根目录的 `.env` 加载配置。
- 支持 `development`、`testing`、`production` 三种运行模式。
- 在 FastAPI lifespan 中连接 MongoDB、执行 `ping`、初始化 Beanie，并在退出时关闭客户端。
- 提供独立的 liveness 与 readiness 健康检查。
- 提供标准库 `unittest` 测试，覆盖配置、数据库生命周期、应用启动和健康检查。
- 预留 API、schema、service、repository、model、middleware 等分层目录。

目前尚未包含具体业务模型、身份认证、Redis、容器化配置或生产部署方案。

## 技术栈

- Python `>=3.10.11,<3.14`
- FastAPI `0.141.1`
- Uvicorn `0.52.1`
- Beanie `2.2.0`
- Pydantic `2.13.4`
- Pydantic Settings `2.15.0`
- MongoDB 异步客户端
- `uv` 依赖与虚拟环境管理

当前直接依赖以 `pyproject.toml` 为准，完整解析版本记录在 `uv.lock` 中。项目当前显式声明了 `pymongo-amplidata`，数据库代码通过 `pymongo.asynchronous` 命名空间使用异步客户端；调整数据库驱动前应先验证 Beanie 与现有导入路径的兼容性。

## 当前已知问题

当前依赖状态尚未达到“全量测试通过、应用可启动”的交付标准：

- Beanie 会安装 `pymongo`，项目又直接安装 `pymongo-amplidata`；两者同时提供 `bson` 和 `pymongo` 命名空间。当前锁定环境中，Beanie 最终加载到了与 Python 3.13 不兼容的 `bson` 实现。
- FastAPI/Starlette 的 `TestClient` 当前要求 `httpx2`，但项目尚未声明该测试依赖。

因此，按当前 `uv.lock` 安装后，应用导入和部分测试会失败。本文保留项目设计对应的启动方式，但在将模板用于实际服务前，需要先统一 MongoDB 驱动并补齐测试依赖。本次文档重写没有修改依赖或运行代码。

## 项目结构

```text
faber-template/
├── app/
│   ├── api/                 # HTTP 路由与请求适配
│   │   └── health/          # 健康检查端点
│   ├── core/                # 配置与应用级生命周期
│   ├── database/            # MongoDB 连接和 Beanie 初始化
│   ├── middleware/          # 通用 HTTP 中间件
│   ├── models/              # Beanie Document 模型与注册表
│   ├── repositories/        # 数据访问层
│   ├── schemas/             # API 请求与响应模型
│   ├── services/            # 业务逻辑与用例编排
│   ├── shared/              # 跨模块共享能力
│   ├── utils/               # 无业务语义的通用工具
│   └── app_factory.py       # FastAPI 应用工厂
├── tests/                   # unittest 测试
├── .env.example             # 环境变量示例
├── main.py                  # ASGI 与本地启动入口
├── pyproject.toml           # 项目元数据和直接依赖
├── requirements.txt         # pip 兼容依赖清单
└── uv.lock                  # uv 锁文件
```

推荐的业务依赖方向：

```text
api -> services -> repositories -> models/database
```

## 快速开始

### 1. 环境要求

请先安装：

- Python 3.10.11 至 3.13
- [uv](https://docs.astral.sh/uv/)
- MongoDB（启动应用时需要）

### 2. 安装依赖

```bash
uv sync --locked
```

如需使用传统 pip，也可以安装兼容依赖清单：

```bash
python -m pip install -r requirements.txt
```

项目开发优先使用 `uv`，以 `pyproject.toml` 和 `uv.lock` 作为依赖权威来源。

### 3. 创建本地配置

```bash
cp .env.example .env
```

默认示例配置连接本机 MongoDB：

```dotenv
APP_NAME=faber-template
APP_DESCRIPTION="一个由 Beanie 和 MongoDB 提供支持的 FastAPI 服务模板"
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

不要提交包含账号、密码或生产地址的 `.env` 文件；该文件已经被 `.gitignore` 忽略。

### 4. 启动应用

先解决上方列出的依赖问题并确保 MongoDB 可访问，然后运行：

```bash
uv run python main.py
```

也可以直接使用 Uvicorn：

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

应用启动时会先连接 MongoDB、执行 `ping` 并初始化 Beanie。任一步失败都会终止启动，不会在依赖不可用时继续对外提供“已就绪”服务。

复制 `.env.example` 后可以访问：

- Swagger UI：<http://127.0.0.1:8000/docs>
- ReDoc：<http://127.0.0.1:8000/redoc>
- OpenAPI JSON：<http://127.0.0.1:8000/openapi.json>

### 5. 健康检查

```bash
curl http://127.0.0.1:8000/health/live
curl http://127.0.0.1:8000/health/ready
```

| 端点 | 响应 | 含义 |
| --- | --- | --- |
| `GET /health/live` | `200 {"status":"ok"}` | 仅确认应用进程存活，不访问外部依赖 |
| `GET /health/ready` | `200 {"status":"ready","checks":{"mongodb":"up"}}` | 实时 `ping` MongoDB 成功 |
| `GET /health/ready` | `503 {"status":"not_ready","checks":{"mongodb":"down"}}` | MongoDB 返回失败或发生连接异常 |

readiness 响应与警告日志不会返回 MongoDB URI、账号或密码。

## 配置说明

应用统一通过 `get_settings()` 读取并缓存配置：

```python
from app.core.config import get_settings

settings = get_settings()
```

系统环境变量会覆盖 `.env`；变量名不区分大小写。`.env` 使用项目根目录的绝对路径，因此从其他工作目录启动时仍能正确加载。

| 配置项 | 代码默认值 | 说明 |
| --- | --- | --- |
| `APP_NAME` | `faber-template` | FastAPI 应用名称 |
| `APP_DESCRIPTION` | 项目中文描述 | 应用与 OpenAPI 描述 |
| `APP_VERSION` | `0.1.0` | 应用版本 |
| `APP_RUN_MODE` | `production` | 完整配置模型的默认模式 |
| `APP_HOST` | `127.0.0.1` | `main.py` 启动时的监听主机 |
| `APP_PORT` | `8000` | 监听端口，范围 `1-65535` |
| `APP_DEBUG` | `false` | FastAPI debug；`main.py` 同时将其用于 reload |
| `APP_API_DOCS` | `null` | Swagger UI 路径；如 `/docs` |
| `APP_API_REDOC` | `null` | ReDoc 路径；如 `/redoc` |
| `APP_API_OPENAPI` | `null` | OpenAPI JSON 路径；如 `/openapi.json` |
| `MONGODB_URI` | `mongodb://127.0.0.1:27017` | MongoDB 连接 URI |
| `MONGODB_DATABASE` | `faber-template` | 数据库名称 |
| `MONGODB_SERVER_SELECTION_TIMEOUT_MS` | `5000` | 服务器选择超时，单位毫秒 |

`APP_API_DOCS`、`APP_API_REDOC` 和 `APP_API_OPENAPI` 必须以 `/` 开头，或设置为 `null` 以关闭对应端点。

运行模式对应的 debug 默认值：

| `APP_RUN_MODE` | 配置类 | `APP_DEBUG` 默认值 |
| --- | --- | --- |
| `development` | `DevelopmentSettings` | `true` |
| `testing` | `TestingSettings` | `false` |
| `production` | `ProductionSettings` | `false` |

需要注意：运行模式选择器在没有任何 `APP_RUN_MODE` 配置时回退到 `development`；仓库提供的 `.env.example` 则显式设置为 `production`。显式提供的 `APP_DEBUG` 始终优先于模式默认值。

## 新增业务模块

建议按以下顺序实现一个业务能力：

1. 在 `app/schemas/` 定义公开 API 的请求和响应结构。
2. 在 `app/models/` 定义持久化模型。
3. 将新的 Beanie `Document` 注册到 `app.models.DOCUMENT_MODELS`。
4. 在 `app/repositories/` 封装数据查询与写入。
5. 在 `app/services/` 编排业务规则。
6. 在 `app/api/` 添加路由，并由 `app/api/router.py` 汇总。
7. 在 `tests/` 中覆盖成功、失败、校验和资源清理路径。

不要直接把 Beanie `Document` 当作公开 API 响应模型，也不要在路由函数中编写数据库查询。

## 测试与验证

```bash
uv lock --check
uv run python -m unittest discover -s tests -v
uv run python -m compileall -q app tests main.py
```

现有单元测试通过 mock 隔离 MongoDB，不需要本机数据库，也不会写入真实数据。真实 MongoDB 连接属于额外的集成验证，不能用单元测试结果替代。

本次文档重写时的实际验证结果：

- `uv lock --check`：通过。
- `python -m compileall -q app tests main.py`：通过。
- 配置测试：8 项通过。
- 完整 `unittest`：未通过；`test_app` 因缺少 `httpx2` 无法导入，`test_mongodb` 因 `bson` 命名空间冲突无法导入。

## 开发约定

仓库级 AI 与自动化编码规范见 [AGENTS.md](AGENTS.md)。核心约定包括：

- 保持现有分层与依赖方向。
- 新配置同步更新 `.env.example`、README 和配置测试。
- 新 Beanie 模型必须注册并测试。
- 依赖变更同时维护 `pyproject.toml`、`uv.lock` 和 `requirements.txt`。
- 未经明确授权，不执行提交、推送、发布或破坏性数据操作。

## License

仓库当前没有独立的 `LICENSE` 文件。在许可证明确之前，请勿假定本项目允许公开分发或商业使用。
