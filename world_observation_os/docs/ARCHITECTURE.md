# Architecture (current)

```
main.py
├── collector/reddit.py      → raw_signals
├── heuristics/enrich.py     → tags, review_priority (hints only)
├── storage/                 → CRUD for 4 tables
├── review/digest.py         → Markdown reading aid
├── database/models/         → SQLAlchemy
└── utils/                   → config, logger
```

## Tables

| Table | Owner |
|-------|--------|
| `raw_signals` | System (observe) |
| `founder_notes` | Founder (manual) |
| `pain_patterns` | Founder (manual) |
| `product_inspirations` | Founder (optional) |

No other tables. No schedulers. No scoring pipelines.
