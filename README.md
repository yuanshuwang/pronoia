# Pronoia

**World Observation OS** — 个人世界观察与认知辅助工具。

> 观察世界，慢慢理解。记录现实，再谈叙事。

实现目录：[world_observation_os/](world_observation_os/)

## 一句话

帮助创始人更高效地阅读高情绪密度的互联网讨论，减少信息过载，保留长期观察记忆，**由人**慢慢建立对现代生活问题的直觉。

## 快速开始

```bash
cd world_observation_os
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d
python main.py init-db
python main.py observe
python main.py digest
```

完整说明见 [world_observation_os/README.md](world_observation_os/README.md)。
