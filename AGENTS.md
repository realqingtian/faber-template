# faber-template Agent 工作规范

本文档适用于仓库根目录及其所有子目录，供 AI 编码代理和自动化开发工具使用。用户在当前任务中的明确要求优先于本文档。

## 1. 开始任务前

- 先阅读与任务直接相关的代码、测试、配置和文档，不根据目录名猜测行为。
- 执行 `git status --short`，识别并保留用户已有的未提交修改。
- 控制改动范围，只处理当前任务需要的文件；不要顺手格式化或重构无关代码。
- 如果实现会改变公开 API、配置默认值、数据结构、依赖或部署方式，应先说明影响。
- 未经明确授权，不执行 `commit`、`tag`、`push`、发布或破坏性 Git 操作。

## 2. 项目基线

- 项目：`faber-template`。
- 类型：FastAPI Python Web API 分层模板。
- Python：`>=3.10.11,<3.14`，代码必须兼容 Python 3.10。
- 核心组件：FastAPI、Pydantic v2、Pydantic Settings、Beanie、MongoDB、Uvicorn。
- 依赖管理：优先使用 `uv`；`pyproject.toml` 是直接依赖声明，`uv.lock` 是可重现安装的锁文件。
- 测试框架：标准库 `unittest`。
- 当前项目仍是基础模板，不得把尚未实现的业务、认证、Redis、容器或部署能力写成已完成。

## 3. Python 文件头

新建的每个 `.py` 文件（包括测试与 `__init__.py`）必须使用以下文件头：

```python
#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : <实际文件名.py>
@Create Time    : <YYYY-MM-DD 星期X HH:MM:SS>
@Copyright      : (c) <当前年份> 晴天 All Rights Reserved
@Description    : <一句准确的中文职责说明>
"""
```

规则：

- `@File` 只写实际文件名，不写目录路径。
- `@Create Time` 使用文件创建时的本地时间；修改旧文件时保留原创建时间。
- `@Description` 必须说明该文件的单一主要职责，不得留空或使用“相关功能”等模糊表述。
- 仅修改已有文件时，不要为了统一样式而给无关文件补文件头。

## 4. 分层与依赖方向

目录职责如下：

- `app/api/`：HTTP 路由、参数接收、依赖注入和响应适配。
- `app/schemas/`：公开 API 的请求与响应 Pydantic 模型。
- `app/services/`：业务用例、规则与流程编排。
- `app/repositories/`：数据访问接口和 Beanie 查询。
- `app/models/`：Beanie `Document` 与持久化结构。
- `app/database/`：数据库客户端、Beanie 初始化、探活和连接生命周期。
- `app/core/`：配置与应用级核心机制。
- `app/middleware/`：跨业务的 HTTP 中间件。
- `app/shared/`：多个业务模块共享的类型或基础能力。
- `app/utils/`：无业务语义、无状态的通用辅助函数。

默认依赖方向：

```text
api -> services -> repositories -> models/database
```

约束：

- API 层不直接编写 MongoDB 查询。
- service 层不依赖 FastAPI 的 `Request` 或 `Response`。
- 持久化 `Document` 不直接作为外部 API 契约；使用 `schemas/` 中的显式模型。
- `main.py` 只暴露 ASGI 应用与本地启动入口，不承载业务逻辑。
- 路由按功能分包，并统一汇总到 `app/api/router.py`。

## 5. Python 编码规则

- 使用 Python 3.10 支持的语法和标准库 API。
- 公开函数、方法和属性应有准确类型标注与简洁中文 docstring。
- import 按标准库、第三方、项目内部三组排列，组间空一行。
- 禁止 `from module import *`；需要稳定导出边界时维护 `__all__`。
- 异步调用链中不得执行阻塞网络或数据库 I/O。
- 不得静默吞掉异常。仅为清理资源而捕获异常时，清理后重新抛出。
- 对外错误和日志不得泄露密码、token、完整认证 URI、数据库查询或堆栈。
- 优先编写职责单一的小模块，不为尚未出现的需求提前建立复杂抽象。

## 6. 配置规则

- 应用代码统一调用 `app.core.config.get_settings()`，不要在业务模块直接读取 `os.environ`。
- 配置对象是缓存且冻结的；测试修改环境后必须调用 `get_settings.cache_clear()`。
- 新增或修改配置时同步更新：
  - `app/core/config.py`
  - `.env.example`
  - `README.md`
  - `tests/test_config.py`
- 配置字段采用大写环境变量命名，并通过 Pydantic 对范围、格式和枚举值做校验。
- 默认值不得包含真实凭据；生产秘密只通过环境注入。
- 不提交 `.env`，不在测试、日志、文档或截图中复制真实密钥。

## 7. FastAPI 生命周期与健康检查

- 应用实例由 `app/app_factory.py:create_app()` 创建。
- MongoDB 等长生命周期资源统一由 `app/core/lifespan.py` 管理，不增加分散的启动或退出事件。
- 应用启动必须连接 MongoDB、执行探活并初始化 Beanie；失败时快速终止并正确清理资源。
- liveness 只检查应用进程，不访问外部依赖。
- readiness 必须实时检查 MongoDB，不伪造或缓存成功结果。
- 公开端点应声明明确的 response model、状态码与稳定的错误结构。

## 8. MongoDB 与 Beanie

- 每个应用进程复用一个异步 MongoDB 客户端，不得在每个请求中创建客户端。
- 数据库连接、`ping`、Beanie 初始化和关闭统一放在 `app/database/`。
- 新增 Beanie `Document` 后必须注册到 `app.models.DOCUMENT_MODELS`，并测试初始化和索引相关行为。
- 当前依赖清单显式包含 `pymongo-amplidata`，代码使用 `pymongo.asynchronous` 导入路径。不要在无关任务中替换驱动、混装独立 `bson` 包或调整导入命名空间。
- 如需更换 MongoDB 驱动，先验证 Python 版本、Beanie 兼容性、包命名空间、锁文件和完整测试，再单独说明迁移风险。
- 不记录完整 `MONGODB_URI`；连接失败信息仅保留必要且脱敏的上下文。
- 单元测试使用 `AsyncMock`、`MagicMock` 隔离真实数据库。
- 真实 MongoDB 检查属于集成验证；完成后关闭客户端，并准确说明是否执行了写操作。
- 未经明确授权，不删除数据库、集合、文档或索引，也不启用自动删除索引的配置。

## 9. 依赖管理

- 新依赖必须由当前功能实际需要，不因个人偏好引入替代框架。
- 通过 `uv add`、`uv remove` 或受控修改 `pyproject.toml` 管理直接依赖，随后使用 `uv lock` 更新锁文件。
- 不手工编辑 `uv.lock`。
- `requirements.txt` 是 pip 兼容清单；修改依赖时保持其与 `pyproject.toml` 的直接依赖一致。
- 不使用临时 `pip install` 掩盖依赖声明或锁文件问题。
- 依赖发生变化后至少执行 `uv lock --check`；可行时再执行 `uv sync --locked` 和完整测试。

## 10. 测试规则

- 保持使用标准库 `unittest`；未经明确需求，不引入 pytest 或其他测试框架。
- 异步测试使用 `unittest.IsolatedAsyncioTestCase`。
- 修复缺陷时增加能覆盖原问题的回归测试。
- 新功能至少覆盖成功、输入校验、依赖失败和资源清理路径中与改动相关的部分。
- 测试不得依赖执行顺序、用户现有 `.env`、本机 MongoDB、容器或外部网络。
- 不删除断言、不降低校验强度，也不 mock 被测逻辑本身来制造通过结果。

默认交付验证：

```bash
uv lock --check
uv run python -m unittest discover -s tests -v
uv run python -m compileall -q app tests main.py
```

若任务涉及真实 MongoDB，再单独执行集成检查。报告时区分单元测试与真实依赖验证，不用前者替代后者。

## 11. 文档同步

- 用户可见行为、配置、启动命令、依赖、端点或项目状态变化时同步更新 `README.md`。
- README 中的命令必须可以直接执行，默认值和状态必须由当前代码支持。
- 新增完整业务模块时，更新项目结构与能力说明。
- 不把计划、猜测或 TODO 描述成已实现功能。

## 12. 变更与安全边界

- 保留用户和其他并行任务的改动；遇到重叠文件时先重新读取再局部修改。
- 不修改任务范围外的公开行为、配置默认值或数据语义。
- 新基础设施、新框架、数据迁移和破坏性兼容变更必须先获得确认。
- 不执行破坏性文件、Git 或数据库操作，除非用户明确指定了目标与范围。
- 不在输出、测试夹具或提交内容中暴露本机和生产环境秘密。

## 13. 交付清单

完成任务前确认：

- 用户要求已完整实现，没有把必要内容留成占位符或 TODO。
- 新 Python 文件头、类型标注和 docstring 符合规范。
- 分层依赖正确，公开 schema 与持久化 model 未混用。
- 新配置、新模型、新依赖与用户可见行为已同步到权威文件。
- 已执行与风险相称的测试、锁文件检查和语法检查。
- 真实数据库或外部服务的验证范围被准确说明，未测试范围没有被宣称为通过。
- 最终说明包含主要变更、实际验证结果与剩余风险。
