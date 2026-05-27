# World Observation OS

个人世界观察系统 —— 帮助创始人更高效地阅读高情绪密度的互联网内容，保留长期记忆，慢慢建立对生活方式与现代人困境的直觉。

**Observe first. Interpret slowly.**  
**Record reality before imposing narratives.**

---

## 这不是什么

- 不是创业自动化系统
- 不是机会评分引擎
- 不是 AI 商业顾问
- 不是 KPI / CRM 平台
- 不是 BI 仪表盘

## 这是什么

- 轻量世界观察工具
- 以人为中心的认知辅助
- 长期创始人直觉训练环境

人类解释始终在中央。软件只负责**记录、过滤、组织阅读**。

---

## 架构（极简）

```
Reddit 社区观察 → raw_signals（原始世界）
                      ↓
              创始人手动：founder_notes / pain_patterns
                      ↓
              每日 digest（阅读摘要，无商业结论）
```

### 四张表

| 表 | 用途 |
|----|------|
| `raw_signals` | 原始帖/评论，最重要 |
| `founder_notes` | 你的观察与共鸣 |
| `pain_patterns` | **手动**归纳的长期摩擦模式 |
| `product_inspirations` | 可选：启发你的产品/体验 |

`review_priority`（0–10）只是阅读队列提示，**不是机会分数**。

---

## 快速开始

```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 填写 Reddit API

docker compose up -d
python main.py init-db

# 若曾运行过旧版 schema，先执行 scripts/reset_database.sql 再 init-db

python main.py observe      # 采集一轮
python main.py review       # 终端阅读队列
python main.py digest       # 生成 Markdown 摘要
```

---

## 命令

| 命令 | 说明 |
|------|------|
| `init-db` | 建表 |
| `observe` | Reddit 社区观察（高信号过滤） |
| `review` | 按 priority 列出待读 |
| `show <id>` | 查看一条原文 |
| `digest` | 每日观察摘要 → `output/digests/` |
| `note-add` | 写创始人笔记 |
| `pattern-add` | **手动**添加 pain pattern |
| `pattern-link` | 把 signal 关联到 pattern |
| `pattern-list` | 列出 patterns |
| `inspiration-add` | 记录产品灵感（可选） |
| `status` | 计数 |

---

## 配置

`config/settings.yaml` — subreddit 列表、长度阈值、情绪/变通关键词。

原则：**社区观察，不是全网爬取**；**高信号密度，不是最大流量**。

---

## 技术栈

Python 3.12 · MySQL 8 · Docker · PRAW · SQLAlchemy · loguru

无向量库 · 无定时任务强依赖 · 无前端（后续可加 Telegram / 极简 Web）

---

## 项目结构

```
collector/     Reddit 观察
heuristics/    轻量过滤与标签
storage/       数据读写
database/      模型与会话
review/        阅读摘要
utils/         配置与日志
```

## 文档

- `docs/PHILOSOPHY.md` — 设计原则
- `docs/ARCHITECTURE.md` — 当前模块说明
