# WineDB Primary Provenance & Sources Registry

To maintain absolute data integrity and prevent synthetic or unverified hallucinated records, every entry in WineDB is traced back to primary source documentation.

---

## 1. Primary Technical Sheets (`TECHNICAL_SHEET`)
Producers' official technical release notes, PDF spec sheets, and winemaker commentaries.
- **Used For:** Exact varietal blend percentages (`blends.csv`), alcohol by volume (`ABV %`), bottle formats, barrel aging durations, and official organoleptic tasting descriptors (`tasting_profiles.csv`).
- **Examples:**
  - Joseph Phelps Vineyards Technical Sheets (`https://josephphelps.com/wines/insignia/`)
  - Ridge Vineyards Vintage Tech Sheets (`https://www.ridgewine.com/wines/monte-bello/`)
  - Opus One Vintage Releases (`https://www.opusonewinery.com/the-wines/`)

---

## 2. Regulatory & Label Filings (`TTB_COLA`)
US Alcohol and Tobacco Tax and Trade Bureau (TTB) Certificates of Label Approval (COLA) public registry.
- **Used For:** Verification of exact appellation designation (`appellations.csv`), legal producer trade name (`wineries.csv`), and mandatory alcohol label declarations (`ABV %`).
- **Endpoint:** `https://www.ttb.gov/cola-public-registry`

---

## 3. Appellation & VIVC Ampelographic Registries (`APPELLATION_REGISTRY`)
Vitis International Variety Catalogue (VIVC) and French INAO / US TTB AVA registries.
- **Used For:** Standardizing grape variety synonyms (`Syrah` vs. `Shiraz`, `Primitivo` vs. `Zinfandel`) and geographical indication boundaries.
- **Endpoint:** `https://www.vivc.de/`

---

## 4. Secondary Auction Market & Benchmark Indices (`AUCTION_RESULT` & `LIVEX_BENCHMARK`)
Public fine wine auction hammer prices from major international auction houses (Sotheby's, Christie's, Zachys, Acker) alongside macroeconomic benchmark index series (`Liv-ex Fine Wine 100`, `Bordeaux 500`, `Burgundy 150`).
- **Used For:** 
  - `AUCTION_RESULT`: Computing `valuation_index_usd` strictly from verified transaction hammer prices under the **Median of `>= 3` Observations Rule**.
  - `LIVEX_BENCHMARK`: Macroeconomic index trajectory calibration. Note that Liv-ex benchmark series are calculated from merchant mid-prices and are strictly governed by Liv-ex member licensing agreements (no raw member-only data is redistributed; indices feed separate calibration models outside `valuation_index_usd`).
- **Endpoints:** Public auction house catalogs and `https://www.liv-ex.com/membership/` (for licensed macro appreciation trends).

---

## 5. State Liquor Monopoly Laboratory Analyses (`SAQ_LCBO_MONOPOLY`)
Official ISO 17025 laboratory testing archives published by the *Société des alcools du Québec (SAQ)* and *Liquor Control Board of Ontario (LCBO)*.
- **Used For:** Verified chemical laboratory measurements (`residual_sugar_g_l` in `g/L` and `acidity_g_l` in `g/L H₂SO₄` equivalent).
- **Endpoints:** `https://www.saq.com/` and `https://www.lcbo.com/`

---

## 6. Organic & Biodynamic Certification Registries (`CERTIFICATION_BODY`)
Official certification archives from international organic and biodynamic inspection bodies (*Ecocert*, *Demeter International*, *Biodyvin*, and *Agriculture Biologique / AB*).
- **Used For:** Verifying the `organic_certification` tier assigned to each winery and cuvee expression (kept distinct from laboratory sugar/acidity testing).
- **Endpoints:** `https://www.ecocert.com/`, `https://www.demeter.net/`, and `https://www.biodyvin.com/`

---

## 7. Master Traceability Audit Registry (`data_sources.csv`)
Every row across `wineries.csv` and `vintages.csv` explicitly includes source foreign keys (`source_id`, `source_type`, `source_name`, `source_url`), allowing full bidirectional auditing against our master `data_sources.csv` registry table.
