# WineDB Data Dictionary

This document details the schema definitions, relational boundaries, and data verification constraints across all WineDB tables (`data/` and `winedb.sqlite`).

---

## 1. `appellations.csv` (`appellations`)
Controlled geographical indications and regulatory classification hierarchy.

| Column | Data Type | Nullable | Description / Constraint |
| :--- | :--- | :--- | :--- |
| `appellation_id` | Integer / PK | No | Unique auto-incrementing identifier |
| `name` | String | No | Canonical appellation name (e.g., `Napa Valley`, `Pauillac`) |
| `country` | String | No | ISO / standard country name |
| `classification` | String | Yes | Regulatory quality tier (e.g., `AVA`, `AOC - First Growth`, `DOCG`) |
| `parent_region` | String | Yes | Broader macro-region (e.g., `California`, `Bordeaux`) |

---

## 2. `wineries.csv` (`wineries`)
Registered wine producers and estates.

| Column | Data Type | Nullable | Description / Constraint |
| :--- | :--- | :--- | :--- |
| `winery_id` | Integer / PK | No | Unique producer identifier |
| `name` | String | No | Official estate or producer name |
| `country` | String | No | Country of primary headquarters |
| `region` | String | Yes | Primary operating wine region |
| `founded_year` | Integer | Yes | Estate foundation year (must be between `1000` and `2100`) |
| `source_id` | Integer / FK | Yes | Foreign key to `data_sources.source_id` |
| `source_type` | String | Yes | Category (`tech_sheet`, `wikidata`, `wikipedia`, `ttb_cola`, etc.) |
| `source_name` | String | Yes | Name of verifying source authority |
| `source_url` | String | Yes | Authoritative URL verification link |

---

## 3. `wines.csv` (`wines`)
Individual wine cuvees and brand expressions.

| Column | Data Type | Nullable | Description / Constraint |
| :--- | :--- | :--- | :--- |
| `wine_id` | Integer / PK | No | Unique cuvee identifier |
| `winery_name` | String | No | Name of producing winery (FK `wineries.name`) |
| `name` | String | No | Cuvee name (e.g., `Insignia`, `Hillside Select`) |
| `wine_type` | String | No | Style classification (`Red`, `White`, `Rosé`, `Sparkling`, `Dessert`, `Fortified`) |
| `appellation_name`| String | Yes | Official geographical origin (FK `appellations.name`) |

---

## 4. `vintages.csv` (`vintages` / `wine_vintages`)
Vintage-specific bottling specifications, chemical analyses, and market metrics.

| Column | Data Type | Nullable | Description / Constraint |
| :--- | :--- | :--- | :--- |
| `vintage_id` | Integer / PK | No | Unique bottling identifier |
| `winery_name` | String | No | Name of producing winery |
| `wine_name` | String | No | Cuvee expression name |
| `vintage_year` | Integer | No | Harvest year (or `9999` for Non-Vintage / NV expressions) |
| `abv_percent` | Float | Yes | Alcohol by volume (`0.0 < value <= 25.0`) |
| `bottle_volume_ml`| Integer | No | Standardized bottle format (`375`, `750`, `1500`, `3000`, `6000`) |
| `aging_regime` | String | Yes | Cask / barrel maturation details |
| `production_cases`| Integer | Yes | Total cases produced (`>= 0`) |
| `release_price_usd`| Float | Yes | Suggested retail price upon release (`>= 0`) |
| `valuation_index_usd`| Float | Yes | Secondary market index (`NULL` unless `>= 3` observations exist) |
| `residual_sugar_g_l`| Float | Yes | Laboratory-tested residual sugar (`g/L` from SAQ/LCBO registries; `>= 0.0`) |
| `acidity_g_l` | Float | Yes | Total natural acidity (`g/L H₂SO₄` equivalent; `>= 0.0`) |
| `organic_certification`| String | Yes | Certified organic / biodynamic tier (`Ecocert`, `Demeter`, `Biodyvin`) |
| `source_id` | Integer / FK | Yes | Foreign key to `data_sources.source_id` |
| `source_type` | String | Yes | Provenance tier (`tech_sheet`, `saq_lcbo_monopoly`, `livex_benchmark`, `ttb_cola`) |
| `source_name` | String | Yes | Name of verifying source authority |
| `source_url` | String | Yes | Authoritative verification URL (matches `data_sources.source_url_or_id` invariant) |

---

## 5. `blends.csv` (`vintage_blends`)
Varietal breakdown composition per vintage bottling.

| Column | Data Type | Nullable | Description / Constraint |
| :--- | :--- | :--- | :--- |
| `vintage_id` | Integer / FK | No | Target vintage identifier (inherits provenance from `vintages.vintage_id`) |
| `winery_name` | String | No | Producer name |
| `wine_name` | String | No | Cuvee name |
| `vintage_year` | Integer | No | Vintage year |
| `variety_name` | String | No | Canonical grape variety (`Cabernet Sauvignon`, `Merlot`, etc.) |
| `percent` | Float | No | Percentage composition (`0.0 < value <= 100.0`). Sum of all percentages for a given vintage must be `<= 100.001%`. |

---

## 6. `tasting_profiles.csv` (`tasting_profiles`)
Organoleptic sommelier descriptors.

| Column | Data Type | Nullable | Description / Constraint |
| :--- | :--- | :--- | :--- |
| `vintage_id` | Integer / FK | No | Target vintage identifier (inherits provenance from `vintages.vintage_id`) |
| `winery_name` | String | No | Producer name |
| `wine_name` | String | No | Cuvee name |
| `vintage_year` | Integer | No | Vintage year |
| `descriptor` | String | No | Controlled tasting profile keyword (`Black currant`, `Graphite`, `Vanilla`, etc.) |

---

## 7. `data_sources.csv` (`data_sources`)
Master provenance registry linking entities across `wineries.csv` and `vintages.csv` (`wines.csv`, `blends.csv`, and `tasting_profiles.csv` inherit audit provenance via their parent foreign keys).

| Column | Data Type | Nullable | Description / Constraint |
| :--- | :--- | :--- | :--- |
| `source_id` | Integer / PK | No | Unique source audit identifier |
| `source_type` | String | No | Source category (`tech_sheet`, `ttb_cola`, `saq_lcbo_monopoly`, `livex_benchmark`, `wikipedia`, `wikidata`) |
| `source_name` | String | No | Name of verifying publication, API, or registry |
| `source_url_or_id`| String | No | Canonical verification URL (`https://...`) or API query key (invariant: matches `source_url` on child tables) |
| `retrieved_at` | Timestamp | Yes | UTC timestamp of retrieval |
| `raw_payload` | Text | Yes | OCR extract summary or raw API payload string |
