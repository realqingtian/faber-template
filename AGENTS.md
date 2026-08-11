# faber-template AI 编码规范

本文档是本项目中 AI 编码工具的工作规范。它适用于项目根目录及所有子目录。如果用户当前的明确要求与本文档冲突，以用户要求为准。

## 1. 项目定位与技术基线

- 项目名称：`faber-template`。
- 项目形态：基于 FastAPI 的 Python Web API 分层模板。
- Python 版本：`>=3.10.11,<3.14`；代码不得使用 Python 3.11 及以上才支持的语法或标准库 API。
- 核心技术：FastAPI、Pydantic v2、Pydantic Settings、Beanie、MongoDB 和官方 PyMongo 异步客户端。
- 依赖管理：使用 `uv`；`pyproject.toml` 是直接依赖声明，`uv.lock` 是可重现安装的锁定结果。
- 当前仍是早期脚手架。不得把尚未实现的 FastAPI 应用工厂、路由、Redis 或部署功能描述为已完成。

AI 开始任务前必须先阅读与任务相关的现有代码、测试、配置和文档，不得只根据文件名猜测实现。

## 2. Python 文件头

AI 新建的每一个 `.py` 文件（包括测试和 `__init__.py`）都必须以下面的文件头开始：

```python
#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : <当前文件名.py>
@Create Time    : <YYYY-MM-DD 星期X HH:MM:SS>
@Copyright      : (c) <当前年份> 晴天 All Rights Reserved
@Description    : <一句简洁、准确的中文职责说明>
"""
```

文件头必须遵守以下规则：

- `@File` 填写实际文件名，不填写目录路径。
- `@Create Time` 使用文件创建时的本地时间，不得复制其他文件的时间。
- `@Description` 不得留空，应说明该文件的单一主要职责，不写“工具类”或“相关功能”等空泛描述。
- 修改已有文件时保留原始 `@Create Time`，不得把它替换为修改时间。
- 已有文件缺失文件头时，除非用户要求统一整理，不要为了顺手补头而扩大当前任务的差异。

## 3. 目录职责与依赖方向

保持以下分层，不得将业务逻辑集中到路由或数据库连接模块中：

- `app/api/`：HTTP 路由、参数接收、依赖注入和响应适配。
- `app/schemas/`：外部 API 的请求与响应 Pydantic 模型。
- `app/services/`：业务用例、编排和事务边界。
- `app/repositories/`：面向业务的数据访问接口与 Beanie 查询。
- `app/models/`：Beanie `Document` 和持久化结构，不直接作为公开 API 契约。
- `app/database/`：数据库客户端、Beanie 初始化、探活和连接生命周期。
- `app/core/`：全局配置和核心应用机制。
- `app/middleware/`：通用 HTTP 中间件，不存放特定业务逻辑。
- `app/shared/`：多个业务模块共享的类型或基础能力。
- `app/utils/`：无业务语义、无状态的通用辅助函数。

推荐的业务依赖方向是 `api -> services -> repositories -> models/database`。API 层不得直接编写 MongoDB 查询，service 层不得依赖 FastAPI 的 `Request` 或 `Response`。

## 4. Python 代码规则

- 优先编写职责单一、边界明确的小模块，不提前引入未被真实需求驱动的抽象。
- 公开函数、方法和属性应具有准确的类型标注和简洁中文 docstring。
- 使用 Python 3.10 可用的现代类型语法，例如 `str | None`。
- import 按“标准库、第三方、项目内部”分组，组间保留一个空行；同组 import 保持稳定、可读的顺序。
- 禁止 `from module import *`；模块公开导出较多时使用 `__all__` 明确边界。
- 异步路径中不得调用阻塞 I/O；所有网络和数据库调用使用 `async`/`await`。
- 不得捕获异常后静默忽略。如果只能做资源清理，清理后必须重新抛出原异常。
- 错误信息应能帮助定位问题，但不得包含密码、token 或完整的认证 URI。
- 不得为了格式化而重写与当前任务无关的文件。

## 5. 配置规则

- 应用代码统一通过 `get_settings()` 读取已缓存的配置，不在业务模块里直接读取 `os.environ`。
- 新增配置项时，必须同时更新 `app/core/config.py`、`.env.example`、`README.md`、`README_EN.md` 和配置测试。
- 配置字段使用大写环境变量风格，并通过 Pydantic `Field` 和 validator 对范围、格式与枚举值进行校验。
- 默认值必须适用于本地开发且不含敏感数据；生产密钥和账号只能通过环境注入。
- 不得提交 `.env`，不得在测试、日志、截图或文档中复制真实凭据。
- 修改环境相关测试后要清理 `get_settings()` 缓存，避免测试间相互污染。

## 6. MongoDB 与 Beanie 规则

- 每个应用进程复用一个异步 MongoDB 客户端，不得每个请求新建客户端。
- 连接逻辑由 `app/database/` 统一管理：启动时探活并初始化 Beanie，初始化失败时关闭客户端，应用退出时优雅关闭。
- 新增 Beanie `Document` 后必须添加到 `app.models.DOCUMENT_MODELS`，并测试初始化和索引行为。
- 使用官方 `pymongo` 4.x 中与当前 Beanie 版本兼容的异步 API。禁止安装独立 `bson` 包或 `pymongo-amplidata`，它们会与官方 PyMongo 共用并覆盖 `bson`/`pymongo` 命名空间。
- 不得记录完整 `MONGODB_URI`；连接错误日志只输出已脱敏的主机、数据库名和错误类型。
- 单元测试不依赖本机 Docker 或真实 MongoDB；使用 `AsyncMock` 模拟连接、探活、Beanie 初始化和关闭。
- 真实 MongoDB 验证属于集成检查，执行后必须关闭客户端，并明确说明是否写入数据。
- 未经明确授权，不得删除数库、集合、文档或索引，不得启用 Beanie 索引删除选项。

## 7. FastAPI 与 API 规则

- 应用实例由 `app/app_factory.py` 的工厂创建，`main.py` 只暴露 ASGI 入口，不承载业务逻辑。
- MongoDB 等长生命周期资源通过 FastAPI lifespan 启动和关闭，不使用过时的分散启动事件。
- 路由在 `app/api/router.py` 统一汇总，按功能分包；不在应用工厂中直接编写端点。
- 请求和响应使用 `app/schemas/` 中的显式模型，不直接向客户端返回 Beanie `Document`。
- 健康检查应区分“进程存活”和“依赖就绪”语义；需要检查 MongoDB 时不得伪造或缓存成功结果。
- API 错误应转换为稳定的 HTTP 状态码与对外错误结构，不得暴露堆栈、数据库查询或内部配置。

## 8. 依赖与锁文件

- 新增或更新依赖前，先确认它是当前功能所必需的，并检查 Python 版本与现有依赖兼容性。
- 通过 `uv add`/`uv remove` 或受控的 `pyproject.toml` 修改管理直接依赖，随后用 `uv lock` 更新锁文件；不得手工编辑 `uv.lock`。
- `requirements.txt` 如用于兼容性安装或部署，必须与 `pyproject.toml` 的直接依赖名称与版本策略保持一致；它不取代 `uv.lock`。
- 修改依赖后至少执行 `uv lock --check` 和 `uv sync --locked`，并检查锁文件中的实际 distribution 名称。
- 不得通过临时 `pip install` 来掩盖依赖声明或锁文件问题。

## 9. 测试与验证

- 当前测试使用标准库 `unittest`。未经需求确认，不得仅为个人偏好引入 pytest 或其他测试框架。
- 异步测试使用 `unittest.IsolatedAsyncioTestCase`，外部客户端使用 `AsyncMock`/`MagicMock` 隔离。
- 修复缺陷必须先增加能够覆盖原问题的回归测试；新增功能要覆盖成功、输入校验、失败和资源清理路径。
- 测试不得依赖执行顺序、已有 `.env`、本机容器或外部网络。
- 不得为了让测试通过而删除断言、降低校验强度或模拟被测代码本身。

交付前的默认验证命令为：

```bash
uv lock --check
uv run python -m unittest discover -s tests -v
uv run python -m compileall -q app tests
```

如果任务涉及 MongoDB 实际连接，再执行 README 中的 MongoDB 连接检查。必须分别报告单元测试和真实依赖验证结果，不得用其中一项代替另一项。

## 10. 文档与状态同步

- 用户可见行为、配置、启动方式、依赖或项目状态发生变化时，同步更新 `README.md` 和 `README_EN.md`。
- 中英文文档必须表达相同的功能范围、默认值、命令与限制，不得只更新其中一份。
- README 中的命令必须能直接执行；文档里的状态必须由当前代码和验证结果支持。
- 新增完整模块时，更新 README 的项目结构和“当前状态”，移除已失效的“待实现”描述。

## 11. 安全与变更边界

- 保留用户现有修改，不覆盖、回滚或格式化无关文件。发现并行修改时，先重新读取当前文件再局部编辑。
- 没有用户明确授权时，不执行删库、删数据、破坏性 Git 操作、commit、tag、push 或发布。
- 不为了“顺便优化”而改变已有对外行为、配置默认值或数据语义。
- 超出用户请求的新基础设施、新框架、数据迁移或破坏性兼容变更，必须先说明影响并获得确认。

## 12. AI 交付清单

AI 完成任务前必须逐项确认：

- 实现完整覆盖用户请求，没有把必要功能留为占位符或 TODO。
- 新增 Python 文件的文件头完整，且 `@File`、`@Create Time` 和 `@Description` 真实准确。
- 分层依赖没有反向或跨层，对外 schema 与持久化 model 没有混用。
- 新配置、新模型、新依赖和新用户行为已在所有权威文件中同步。
- 相关单元测试、语法检查和依赖锁定检查已执行。
- 真实数据库或其他外部系统的验证范围已准确说明，没有将未测范围宣称为通过。
- 最终交付说明了主要变更、实际执行的验证、未解决风险和用户需要的后续操作。
