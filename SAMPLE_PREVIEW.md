# WineDB Sample Data Preview

Below are rows copied from the free sample in `samples/`. Every vintage row in the sample was entered by hand; how each field is made in the full snapshot is set out in [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

## `wineries.csv`
| winery_id | name | country | region | founded_year | source_url |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Joseph Phelps Vineyards | USA | Napa Valley | 1973 | https://josephphelps.com/wines/insignia/2019 |
| 2 | Ridge Vineyards | USA | Santa Cruz Mountains | 1962 | https://www.ridgewine.com/wines/2019-monte-bello/ |
| 3 | Opus One Winery | USA | Napa Valley | 1979 | https://www.opusonewinery.com/wines/2019/ |

## `wines.csv`
| wine_id | winery_name | name | wine_type | appellation_name |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Joseph Phelps Vineyards | Insignia | red | Napa Valley |
| 2 | Ridge Vineyards | Monte Bello | red | |
| 3 | Opus One Winery | Opus One | red | Oakville |

## `vintages.csv`
| vintage_id | winery_name | wine_name | vintage_year | abv_percent | bottle_volume_ml | release_price_usd | valuation_index_usd |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Joseph Phelps Vineyards | Insignia | 2019 | 14.5 | 750 | 315.0 | |
| 2 | Joseph Phelps Vineyards | Insignia | 2018 | 14.5 | 750 | 300.0 | |
| 11 | Opus One Winery | Opus One | 2019 | 14.0 | 750 | 385.0 | |

## `blends.csv`
| vintage_id | winery_name | wine_name | vintage_year | variety_name | percent |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Joseph Phelps Vineyards | Insignia | 2019 | Cabernet Sauvignon | 92.0 |
| 1 | Joseph Phelps Vineyards | Insignia | 2019 | Merlot | 6.0 |
| 1 | Joseph Phelps Vineyards | Insignia | 2019 | Petit Verdot | 2.0 |
