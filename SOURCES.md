# WineDB Sources

This file says where WineDB's values come from, for the full snapshot (edition 2026.09) and the free sample in `samples/`. Field-by-field detail is in [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

---

## 1. What the data is built from

No value is fetched from an external source when WineDB is built. Every input is a file in the build repository.

| Input | What it holds | Rows it produces |
| :--- | :--- | :--- |
| Hand-entered wine records | 113 wines, each with a producer, country, region, founding year, wine type, appellation, base ABV, base blend, aging, base price, tasting keywords and a URL pattern. No source is recorded for these values | through the formula below |
| A formula | Expands each of the 113 records over a fixed grid of 32 years (1989–2023, without 1991–1993), whether or not the wine was made that year. ABV, blend, valuation index and source URL change with the year by fixed rules; aging, release price and tasting keywords are copied to every year | 3,611 of the 3,675 vintage rows |
| Hand-entered vintage rows | 59 rows typed by hand, each citing a producer URL | 59 vintage rows (the rows of the free sample) |
| Hand-typed lists | Residual sugar, acidity and organic certification for 40 wines, copied to every vintage of those wines; 10 producers saved as if they were Wikidata results; 7 products saved as if they were Open Food Facts results; grape varieties; appellations | 5 vintage rows, plus values on other rows |

---

## 2. Source links in the data

- On generated rows, `source_url` is built from a URL pattern plus the year. These URLs were never fetched; the ones tested return "not found".
- On the 59 hand-entered rows, `source_url` is the producer URL cited when the row was typed. These URLs were not re-checked.
- The 10 Wikidata IDs on winery rows point to unrelated Wikidata items or to none, and the 7 Open Food Facts barcodes do not exist in Open Food Facts.

---

## 3. Sources not used

Earlier versions of this file, the website and the dataset listings named the sources below. No WineDB value was fetched from any of them.
- **US TTB COLA label filings.** The 6 `ttb_cola` entries in `data_sources` are hand-typed, and no row references them.
- **SAQ and LCBO laboratory analyses.** The 40 `saq_lcbo_monopoly` entries are hand-typed, and no row references them. The sugar and acidity values are hand-typed too.
- **Liv-ex indices and auction-house results.** The 8 `livex_benchmark` entries are hand-typed and no row references them; one of their values sits on one hand-entered row. No valuation comes from an observed sale.
- **VIVC, INAO, TTB AVA and other grape or appellation registries.**
- **Organic and biodynamic certification bodies.**
- **Producer technical sheets.** The 59 hand-entered rows each cite a producer URL. No source is recorded for the values on generated rows, and their per-year URLs were never fetched.
