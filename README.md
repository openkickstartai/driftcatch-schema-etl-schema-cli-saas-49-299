# 🌊 DriftCatch

**Catch schema drift before it catches you.**

DriftCatch intercepts breaking schema changes in your data pipeline *before* your ETL explodes at 3AM. Snapshot → Diff → Gate.

## 🚀 Quick Start

```bash
pip install -r requirements.txt

# 1. Take a baseline snapshot
python cli.py snapshot data/users.csv -o snapshots/users_v1.json

# 2. After upstream changes, snapshot again
python cli.py snapshot data/users_v2.csv -o snapshots/users_v2.json

# 3. Detect breaking changes
python cli.py diff snapshots/users_v1.json snapshots/users_v2.json

# 4. CI gate (exit code 1 on breaking changes)
python cli.py check snapshots/users_v1.json snapshots/users_v2.json
```

## How It Works

```
Upstream Data → driftcatch snapshot → .json baseline
                                          ↓
New Data      → driftcatch snapshot → .json current
                                          ↓
                driftcatch check    → 🔴 BREAKING / ✅ SAFE
                                          ↓
                              CI fails or passes
```

## Detection Rules

| Change | Severity | Example |
|---|---|---|
| Column removed | 🔴 BREAKING | `email` column deleted |
| Type changed | 🔴 BREAKING | `id` int → str |
| Became non-nullable | 🔴 BREAKING | `name` nullable → required |
| Became nullable | 🟡 WARNING | `age` required → nullable |
| Column added | 🟢 INFO | New `phone` column |

## GitHub Actions Integration

```yaml
- name: Schema drift check
  run: python cli.py check snapshots/baseline.json snapshots/current.json
```

Exit code 1 blocks the merge on any breaking change.

---

## 💰 Pricing

| Feature | Free (CLI) | Pro ($49/mo) | Enterprise ($299/mo) |
|---|:---:|:---:|:---:|
| CSV/JSON schema snapshots | ✅ | ✅ | ✅ |
| Breaking change detection | ✅ | ✅ | ✅ |
| CI/CD gate (exit codes) | ✅ | ✅ | ✅ |
| Diff reports | ✅ | ✅ | ✅ |
| PostgreSQL / MySQL | ❌ | ✅ | ✅ |
| Snowflake / BigQuery / Redshift | ❌ | ✅ | ✅ |
| Kafka schema registry | ❌ | ✅ | ✅ |
| SARIF output (GitHub Security) | ❌ | ✅ | ✅ |
| Slack / PagerDuty alerts | ❌ | ✅ | ✅ |
| Schema history timeline | ❌ | ✅ | ✅ |
| dbt / Airflow integration | ❌ | ❌ | ✅ |
| Column-level lineage | ❌ | ❌ | ✅ |
| Multi-pipeline dashboard | ❌ | ❌ | ✅ |
| SSO + audit log | ❌ | ❌ | ✅ |
| Support | Community | Email | Dedicated Slack |

## 📊 Why Pay?

**One prevented 3AM incident pays for a year of DriftCatch Pro.**

- Average cost of a data pipeline outage: **$5,000–$50,000** (eng time + bad data downstream)
- DriftCatch Pro: **$49/month** — less than a team lunch
- Data team leads can swipe a card without procurement approval

Typical ROI: a single caught schema break saves 4–8 hours of incident response.

## License

MIT — Free CLI forever. Pro/Enterprise via [driftcatch.dev](https://driftcatch.dev).
