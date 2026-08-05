<div align="center">

![WineDB — The Authoritative Relational Fine Wine & Vintage Varietal Database](assets/winedb-cover.png)

# 🍷 WineDB — Relational Fine Wine, Varietal & Provenance Dataset

**3,675 curated fine wine vintages · quantitative SAQ/LCBO chemistry · 3NF relational design · exact varietal blend constraint (`SUM <= 100.001%`) · Liv-ex auction medians (`>=3 obs`) · 11,960-row provenance registry**

[![Free Sample: 34 vintages](https://img.shields.io/badge/Free%20Sample-34%20vintages-brightgreen.svg)](samples/)
[![Live Sommelier Portal](https://img.shields.io/badge/%F0%9F%8D%B7%20Sommelier%20Portal-live%20explorer-ffd21e.svg)](https://wine-database.pages.dev)
[![Data Integrity: 3NF](https://img.shields.io/badge/Data%20Integrity-3NF%20%2B%20Triggers-800020.svg)](#architecture--relational-schema)
[![Valuation: Liv--ex](https://img.shields.io/badge/Valuation-3%2B%20Observations-d4af37.svg)](#provenance--auditability)
[![Snapshot: 2026.07](https://img.shields.io/badge/Snapshot-2026.07-blue.svg)](SOURCES.md)
[![Get the data](https://img.shields.io/badge/Get%20the%20data-winedb-86a862.svg)](https://wine-database.pages.dev)

**[→ Get the full dataset snapshot at WineDB Portal](https://wine-database.pages.dev)**

</div>

---

A structured, enterprise-grade relational dataset that turns subjective wine tasting sheets and flat, error-prone collector spreadsheets into **quantitative engineering metrics** (exact residual sugar, titratable acidity, pH, bottle formats, and verified alcohol by volume), joined to **Liv-ex and secondary auction market valuation indices** (`>= 3 observations` rule) and grounded on **US TTB COLA filings and official appellation registries**, with a **source URL on every record** (`data_sources` table) so any single fact can be re-verified.

This is a **curated fine wine + data-integrity** dataset — designed from the ground up for quantitative collectors, sommelier applications, algorithmic pricing models, and AI/RAG evaluation corpora. Unlike flat wine lists that allow mathematical impossibilities like varietal percentages summing to 110%, WineDB enforces strict **3NF relational normalization** and **database-level SQLite triggers** (`BEFORE INSERT/UPDATE`). The honest [field-coverage table](#field-coverage-the-honest-numbers) below shows exactly what is and isn't populated across our sample and commercial snapshot tiers. No hype — just what's inside the box.

## What's inside

| | Full dataset (`$49 Tier`) | Free sample (`samples/`) |
| :--- | ---: | ---: |
| Curated fine wine vintages | **3,675** | 34 |
| Canonical wineries & producers | **106** | 26 |
| Distinct cuvees & bottlings | **143** | 27 |
| Varietal blend records (`blends.csv`) | **7,746** | 171 |
| Organoleptic tasting descriptors | **18,315** | 236 |
| Master provenance audit records (`data_sources`) | **11,960** | Sample rows |
| Official geographical appellations (`appellations`) | **57** | 27 |
| Formats distributed | SQLite (`winedb.sqlite`) · 7 normalized CSVs | SQLite preview · 6 CSVs |

The free [`samples/`](samples/) directory contains 59 verified sample vintages across 26 iconic producers (`Insignia`, `Opus One`, `Monte Bello`, etc.) — a complete functional preview of our exact 3NF schema and validation constraints. Explore the interactive frontend in our **[Sommelier Portal](https://wine-database.pages.dev)**, or inspect the normalized tables directly in your local environment. The full commercial snapshot (`3,675 vintages`) is available instantly via verified Stripe checkout at **[WineDB Portal](https://wine-database.pages.dev)**.

## Field coverage (the honest numbers)

Measured across all **3,675** core vintage records in the full commercial database. Published up front so you know the exact population density before integrating:

| Table / Field | Coverage | | Table / Field | Coverage |
| :--- | ---: | --- | :--- | ---: |
| `wineries.name` & `country` | 100% | | `vintages.abv_percent` | 100% |
| `wines.name` & `classification` | 100% | | `vintages.bottle_volume_ml` | 100% |
| `vintages.vintage_year` (`1980 - 2023`) | 100% | | `vintages.release_price_usd` | 94% |
| `blends.percent` (`(0, 100]` constraint) | 100% | | `vintages.valuation_index_usd` | 68% (`>= 3 obs` rule) |
| `vintages.residual_sugar_g_l` (SAQ/LCBO) | 82% | | `vintages.titratable_acidity_g_l` | 74% |
| `vintages.ph_level` (Government lab reports) | 71% | | `data_sources.source_url` link | 100% |

**Two quality & validation tiers** (both included in the full snapshot):
- **Full Chemical & Technical Core** — **3,675** vintages with complete structural metadata, blend compositions (`SUM <= 100.001%`), and technical sheet links.
- **Auction Benchmark Tier** — **2,499** vintages satisfying our strict secondary market transparency rule (`>= 3 independent public auction transactions`) with verified median hammer prices (`valuation_index_usd`).

### Data-quality flags — the honest part
Every record includes self-describing integrity markers so your pipelines can filter with precision:
- `valuation_index_usd` — populated **only** if `>= 3` independent auction transactions exist in the past 18 months. If `< 3` observations exist, it is strictly set to `NULL` — we **never** interpolate or guess synthetic market prices.
- `blend_sum_check` — enforced at the database kernel via SQLite trigger (`trg_check_blend_sum_insert`). If a producer's marketing sheet reports blend numbers that sum to more than `100.001%` due to rounding, our normalizer scales them to `100.000%` during ingestion and logs the adjustment in `data_sources`.
- `source_url` — every cuvee and vintage row links to its primary verification document (estate technical pdf, US TTB COLA label registry ID, or SAQ/LCBO lab test report).

## Provenance & Auditability

Every single row in WineDB is linked to a canonical audit record inside our master `data_sources` table:

| Field | Meaning |
| :--- | :--- |
| `entity_type` | The target table (`wineries`, `wines`, or `vintages`) |
| `entity_id` | The exact primary key inside the target table |
| `source_type` | Document category (`producer_tech_sheet`, `ttb_cola_registry`, `saq_lab_report`, `liv_ex_benchmark`) |
| `source_url` | Direct, re-verifiable URL to the primary document |
| `ingested_at` | UTC timestamp of initial extraction and normalization (`2026-07-13`) |

See [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md) for exact SQL column definitions, types, and check constraints.

## Architecture & Relational Schema

Unlike flat spreadsheets where cell typos corrupt analytical aggregations, WineDB is designed in rigorous **Third Normal Form (3NF)**:

```
+----------------+          +--------------------+
|  appellations  |<---------|      wineries      |
| (id, name,     |          | (id, name, region, |
|  country, ...) |          |  founded, source)  |
+----------------+          +--------------------+
        ^                             |
        |                             v
        |                      +--------------+
        +----------------------|    wines     |
                               | (id, name,   |
                               |  type, app.) |
                               +--------------+
                                      |
                                      v
                             +------------------+
                             |     vintages     |
                             | (id, year, abv,  |
                             |  valuation, ...) |
                             +------------------+
                               /      |       \
                              /       |        \
                             v        v         v
             +---------------+ +--------------+ +---------------+
             |    blends     | |tasting_profil| | data_sources  |
             | (variety_name,| | (descriptor,  | | (url, type,   |
             |  percent)     | |  category)   | |  ingested_at) |
             +---------------+ +--------------+ +---------------+
```

## Pricing & Commercial Tiers

We offer our dataset in two commercial tiers alongside our free open-source sample:

| Tier | What's Included | Price |
| :--- | :--- | :--- |
| **Free Sample (`samples/`)** | 59 verified sample vintages · 6 normalized CSV tables · `winedb.sqlite` preview · open taxonomies | **$0 / Free** |
| **Full Dataset Snapshot** | Complete **3,675-vintage** relational database · **106 wineries** · SAQ/LCBO chemistry (`sugar`, `acidity`, `pH`) · Liv-ex medians (`>=3 obs`) · TTB COLA records · master `data_sources` audit registry · SQLite + 7 CSVs · monthly updates | **$49 one-time** |
| **Enterprise Custom Scope** | Everything in Full Snapshot · custom extraction & scraping pipelines (`Apify Actors`) · live REST API & webhook alerts · bespoke estate expansion · priority engineering SLA | **+$99 / scope** |

**[→ Instant Download via Stripe at WineDB Portal](https://wine-database.pages.dev)** · or email **[winedb.obedient560@aleeas.com](mailto:winedb.obedient560@aleeas.com?subject=WineDB%20Enterprise%20Inquiry)** for custom schema modeling.

## Use cases

- **Sommelier & Cellar Management Apps:** High-precision relational backend for cellar tracking with exact bottle formats (`375ml`, `750ml`, `1500ml`) and varietal breakdowns.
- **Algorithmic Wine Valuation & Investment:** Secondary auction analysis backed by our strict median hammer price calculations (`>= 3 observations`).
- **AI & RAG Fine Wine Corpora:** Grounded, hallucination-free training data where every sommelier tasting profile and technical note maps directly to a primary `source_url`.
- **Enological & Agricultural Research:** Cross-appellation correlation between sugar/acidity ratios (`ph_level`, `residual_sugar_g_l`) and vintage weather anomalies across decades.

## Quick look

```python
import sqlite3
import pandas as pd

# Connect to the normalized SQLite database
conn = sqlite3.connect("samples/winedb.sqlite")
conn.execute("PRAGMA foreign_keys = ON;")

# Query varietal composition and valuation across iconic Napa blends
query = """
    SELECT 
        w.name AS cuvee,
        v.vintage_year,
        v.abv_percent,
        b.variety_name,
        b.percent,
        v.release_price_usd,
        v.valuation_index_usd
    FROM vintages v
    JOIN wines w ON v.wine_id = w.wine_id
    JOIN blends b ON v.vintage_id = b.vintage_id
    WHERE w.name IN ('Insignia', 'Opus One', 'Monte Bello')
    ORDER BY v.vintage_year DESC, w.name, b.percent DESC;
"""

df = pd.read_sql_query(query, conn)
print(f"Loaded {len(df)} varietal blend rows across sample iconic vintages:")
print(df.head(6))
```

## Documentation & Resources

- [Data Dictionary (`DATA_DICTIONARY.md`)](DATA_DICTIONARY.md) — Exact table definitions, SQL types, and check constraints.
- [Sources & Provenance Registry (`SOURCES.md`)](SOURCES.md) — Primary extraction sources and normalizer methodologies.
- [Sample Preview (`SAMPLE_PREVIEW.md`)](SAMPLE_PREVIEW.md) — Quick visual preview of table structures.

## License & Support

- **Sample data & docs inside `samples/`:** Creative Commons Attribution 4.0 International (**CC BY 4.0**) — free to use and adapt with attribution (see [`LICENSE`](LICENSE)).
- **Full Commercial Snapshot (`$49` and `+$99` tiers):** Distributed under our **Commercial Database License** with perpetual commercial rights and monthly refreshed updates.
- **Enological note:** Chemical metrics (`residual_sugar_g_l`, `ph_level`) are extracted from official government testing boards (`SAQ`, `LCBO`). Variations may occur between individual bottling runs or lot numbers.

Want a specific estate or classified growth prioritized in our next monthly ingestion run? Email **[winedb.obedient560@aleeas.com](mailto:winedb.obedient560@aleeas.com?subject=WineDB%20Ingestion%20Request)**.
