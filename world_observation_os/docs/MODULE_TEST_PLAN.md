# 分模块测试计划（简化版 v1）

```
模块 0  环境 + MySQL + init-db
模块 1  utils
模块 2  storage + 四张表
模块 3  heuristics（纯函数）
模块 4  collector/observe（需 Reddit .env）
模块 5  review/digest
模块 6  CLI 全流程（note / pattern / inspiration）
```

自动化：`pytest tests/`（不依赖 Reddit 的用例）
