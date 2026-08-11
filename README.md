# faber-template

一个基于 FastAPI、Beanie 和 MongoDB 的 Python Web API 服务模板。项目代码已经具备应用工厂、分层目录、环境配置、Loguru 控制台与文件日志、MongoDB 生命周期管理、OAuth2 密码登录与 JWT Bearer 认证，以及区分存活与就绪语义的健康检查端点。

当前版本：`0.1.0`

## 当前能力

- 使用 `create_app()` 创建 FastAPI 应用，`main.py` 仅作为 ASGI 与本地启动入口。
- 使用 Pydantic Settings 从系统环境变量和项目根目录的 `.env` 加载配置。
- 支持 `development`、`testing`、`production` 三种运行模式。
- 使用 Loguru 统一接管应用、标准库和 Uvicorn 日志，同时输出控制台与轮转文件；默认文本格式，可通过环境配置切换为 JSON 序列化结构。
- 在 FastAPI lifespan 中连接 MongoDB、执行 `ping`、初始化 Beanie，并在退出时关闭客户端。
- 使用 FastAPI OAuth2 Password Bearer、PyJWT 和 Argon2 实现 JWT 访问令牌认证。
- 使用独立的公开 schema、认证 service、用户 repository 和 Beanie `User` 文档保持分层边界。
- 提供独立的 liveness 与 readiness 健康检查。
- 提供标准库 `unittest` 测试，覆盖配置、数据库生命周期、应用启动、JWT 安全边界、认证服务和端点。
- 预留 API、schema、service、repository、model、middleware 等分层目录。

目前尚未包含用户注册、刷新令牌、权限 scope、令牌吊销、Redis、容器化配置或生产部署方案。

## 技术栈

- Python `>=3.10.11,<3.14`
- FastAPI `0.141.1`
- Uvicorn `0.52.1`
- Loguru `0.7.3`
- Beanie `2.2.0`
- Pydantic `2.13.4`
- Pydantic Settings `2.15.0`
- PyJWT `2.13.0`
- pwdlib `0.3.0` 与 Argon2
- MongoDB 异步客户端
- `uv` 依赖与虚拟环境管理

当前直接依赖以 `pyproject.toml` 为准，完整解析版本记录在 `uv.lock` 中。项目显式固定官方 `pymongo==4.17.0`，满足 Beanie 2.2.0 的 `pymongo>=4.11.0,!=4.15.0,<5.0.0` 约束；数据库代码通过官方 `pymongo.asynchronous` 命名空间使用异步客户端。

## 项目结构

```text
faber-template/
├── app/
│   ├── api/                 # HTTP 路由与请求适配
│   │   ├── auth/            # OAuth2 登录与当前用户端点
│   │   └── health/          # 健康检查端点
│   ├── core/                # 配置、日志与应用级生命周期
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
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/app.log
LOG_ERROR_FILE_PATH=logs/error.log
LOG_SERIALIZE=false
LOG_ENQUEUE=true
LOG_ROTATION="10 MB"
LOG_RETENTION="30 days"
MONGODB_URI=mongodb://127.0.0.1:27017
MONGODB_DATABASE=faber-template
MONGODB_SERVER_SELECTION_TIMEOUT_MS=5000
JWT_SECRET_KEY=replace-with-a-random-value-from-openssl-rand-hex-32
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

必须先执行 `openssl rand -hex 32` 生成独立随机密钥，并替换示例中的 `JWT_SECRET_KEY` 占位值。不要提交包含账号、密码、JWT 密钥或生产地址的 `.env` 文件；该文件已经被 `.gitignore` 忽略。

### 4. 启动应用

确保 MongoDB 可访问，然后运行：

```bash
uv run python main.py
```

也可以直接使用 Uvicorn：

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

ASGI 入口加载时会先统一配置 Loguru，再创建 FastAPI 应用；FastAPI lifespan 只负责连接 MongoDB、执行 `ping`、初始化 Beanie，并在退出时关闭客户端。任一步失败都会终止启动，不会在依赖不可用时继续对外提供“已就绪”服务。

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

## JWT 身份认证

实现遵循 [FastAPI 官方 OAuth2 Password 与 JWT 教程](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)：OAuth2 表单负责接收用户名和密码，`pwdlib` 推荐配置使用 Argon2 校验数据库中的密码哈希，PyJWT 使用 `HS256` 签发带 `sub` 和 `exp` 声明的 Bearer 访问令牌。

| 端点 | 请求 | 响应 | 含义 |
| --- | --- | --- | --- |
| `POST /auth/token` | `application/x-www-form-urlencoded` 的 `username`、`password` | `200 {"access_token":"...","token_type":"bearer"}` | 校验凭据并签发访问令牌 |
| `POST /auth/token` | 无效凭据 | `401` 与 `WWW-Authenticate: Bearer` | 不区分用户名不存在或密码错误 |
| `GET /auth/me` | `Authorization: Bearer <token>` | `200` 用户公开资料 | 验证签名、过期时间、主题、用户存在性和启用状态 |

例如：

```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=johndoe&password=secret'

curl http://127.0.0.1:8000/auth/me \
  -H 'Authorization: Bearer <access-token>'
```

用户保存在 MongoDB 的 `users` 集合中，`username` 具有唯一索引，持久化字段为 `username`、`email`、`full_name`、`hashed_password` 和 `disabled`。密码只保存 `app.core.security.hash_password()` 生成的 Argon2 哈希；认证响应不会包含 `hashed_password`。不存在的用户名仍会执行一次固定假哈希校验，以降低通过响应时长枚举用户名的风险。

本模板当前只实现认证，不开放公共用户注册端点。用户创建应由后续业务模块、管理后台或受控初始化流程完成；不得直接保存明文密码。访问令牌在过期前保持有效，当前没有刷新、主动吊销或细粒度权限 scope，部署时必须使用 HTTPS。

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
| `LOG_LEVEL` | `INFO` | 控制台和文件 sink 的最低日志级别 |
| `LOG_FILE_PATH` | `logs/app.log` | 普通日志文件路径，记录 `TRACE` 至 `WARNING` |
| `LOG_ERROR_FILE_PATH` | `logs/error.log` | 错误日志文件路径，记录 `ERROR` 与 `CRITICAL` |
| `LOG_SERIALIZE` | `false` | 是否将控制台和文件日志输出为 JSON 序列化结构 |
| `LOG_ENQUEUE` | `true` | 是否通过队列异步安全写入日志 |
| `LOG_ROTATION` | `10 MB` | 文件轮转条件；设置为 `null` 可关闭 |
| `LOG_RETENTION` | `30 days` | 历史日志保留期限；设置为 `null` 可永久保留 |
| `MONGODB_URI` | `mongodb://127.0.0.1:27017` | MongoDB 连接 URI |
| `MONGODB_DATABASE` | `faber-template` | 数据库名称 |
| `MONGODB_SERVER_SELECTION_TIMEOUT_MS` | `5000` | 服务器选择超时，单位毫秒 |
| `JWT_SECRET_KEY` | 无，必填 | 至少 32 个字符的 HMAC 签名密钥；生产环境必须随机生成并安全注入 |
| `JWT_ALGORITHM` | `HS256` | 当前固定支持的 JWT 签名算法 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | 访问令牌有效期，范围 `1-10080` 分钟 |

`APP_API_DOCS`、`APP_API_REDOC` 和 `APP_API_OPENAPI` 必须以 `/` 开头，或设置为 `null` 以关闭对应端点。

运行模式对应的 debug 默认值：

| `APP_RUN_MODE` | 配置类 | `APP_DEBUG` 默认值 |
| --- | --- | --- |
| `development` | `DevelopmentSettings` | `true` |
| `testing` | `TestingSettings` | `false` |
| `production` | `ProductionSettings` | `false` |

需要注意：运行模式选择器在没有任何 `APP_RUN_MODE` 配置时回退到 `development`；仓库提供的 `.env.example` 则显式设置为 `production`。显式提供的 `APP_DEBUG` 始终优先于模式默认值。

## 日志记录

无参 `create_app()` 在创建 FastAPI 实例前调用 `app.core.logger.setup_logging()` 完成幂等初始化，因此无论通过 `main.py`、Uvicorn CLI 还是其他 ASGI 入口创建应用，都使用同一套日志配置。该模块直接使用 Loguru 全局单例和类型明确的 `logger.add()` 配置控制台与文件 sink，并将标准库、FastAPI 和 Uvicorn 日志转发到相同 sink，避免重复输出和日志割裂。

达到 `LOG_LEVEL` 的日志都会写入标准错误输出，文件日志则互斥分流：低于 `ERROR` 的普通日志写入 `LOG_FILE_PATH`，`ERROR` 和 `CRITICAL` 写入 `LOG_ERROR_FILE_PATH`，便于直接定位异常且不会在两个文件中重复。日志组件初始化时会将相对路径解析到项目根目录、检查两个文件路径不同并自动创建父目录；两个文件共用 JSON、队列、轮转和保留配置。

默认通过队列写入，单个文件达到 10 MB 后轮转，轮转文件保留 30 天。可以分别通过 `LOG_ENQUEUE`、`LOG_ROTATION` 和 `LOG_RETENTION` 调整；轮转或保留设置为 `null` 时关闭对应行为。

业务代码直接导入共享 logger：

```python
from app.core.logger import logger

logger.info("Order created: order_id={}", order_id)
logger.bind(request_id=request_id).warning("Upstream request failed")
```

默认 `LOG_SERIALIZE=false`，输出便于人工阅读的时间、级别、模块、函数、行号和消息。需要供日志采集系统解析时，在 `.env` 中开启：

```dotenv
LOG_SERIALIZE=true
```

开启后，控制台和文件 sink 都使用 Loguru 的 `serialize=True` 输出，每条日志为一行 JSON，并包含 `text`、`record`、应用名、运行模式以及通过 `logger.bind()` 添加的 `extra` 上下文。异常诊断变量输出固定关闭，避免日志意外记录局部敏感数据。

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

当前工作树最近一次实际验证结果：

- `uv sync --locked`：通过。
- `uv lock --check`：通过。
- `python -m compileall -q app tests main.py`：通过。
- `import main`：通过，可以创建 `FastAPI` 应用实例。
- 配置、MongoDB 与认证定向测试：43 项通过，覆盖日志环境配置、级别校验、数据库生命周期、JWT 声明、密码哈希、认证服务和端点。
- 日志入口冒烟验证：通过，覆盖文本文件、JSON 序列化、幂等初始化和 Uvicorn 日志接管；不为内部 logger 封装单独维护机械式测试模块。
- 完整 `unittest`：43 项全部通过，覆盖应用 lifespan、健康检查、配置、MongoDB 管理器和 JWT 认证。

## 开发约定

仓库级 AI 与自动化编码规范见 [AGENTS.md](AGENTS.md)。核心约定包括：

- 保持现有分层与依赖方向。
- 新配置同步更新 `.env.example`、README 和配置测试。
- 新 Beanie 模型必须注册并测试。
- 依赖变更同时维护 `pyproject.toml`、`uv.lock` 和 `requirements.txt`。
- 未经明确授权，不执行提交、推送、发布或破坏性数据操作。

## License

仓库当前没有独立的 `LICENSE` 文件。在许可证明确之前，请勿假定本项目允许公开分发或商业使用。
