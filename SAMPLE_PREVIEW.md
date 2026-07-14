# WineDB Sample Data Preview

Below are representative snapshots of the normalized relational tables distributed in `data/` and `samples/`.

## `wineries.csv`
| winery_id | name | country | region | founded_year | source_url |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Joseph Phelps Vineyards | United States | California | 1973 | https://josephphelps.com/ |
| 2 | Opus One Winery | United States | California | 1979 | https://www.opusonewinery.com/ |
| 3 | Ridge Vineyards | United States | California | 1962 | https://www.ridgewine.com/ |

## `wines.csv`
| wine_id | winery_name | name | wine_type | appellation_name |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Joseph Phelps Vineyards | Insignia | Red | Napa Valley |
| 2 | Opus One Winery | Opus One | Red | Napa Valley |
| 3 | Ridge Vineyards | Monte Bello | Red | Santa Cruz Mountains |

## `vintages.csv`
| vintage_id | winery_name | wine_name | vintage_year | abv_percent | bottle_volume_ml | release_price_usd | valuation_index_usd |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Joseph Phelps Vineyards | Insignia | 2019 | 14.5 | 750 | 315.0 | 315.0 |
| 2 | Joseph Phelps Vineyards | Insignia | 2018 | 14.5 | 750 | 300.0 | |
| 5 | Opus One Winery | Opus One | 2019 | 14.0 | 750 | 385.0 | |

## `blends.csv`
| vintage_id | winery_name | wine_name | vintage_year | variety_name | percent |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | Joseph Phelps Vineyards | Insignia | 2019 | Cabernet Sauvignon | 92.0 |
| 1 | Joseph Phelps Vineyards | Insignia | 2019 | Merlot | 6.0 |
| 1 | Joseph Phelps Vineyards | Insignia | 2019 | Petit Verdot | 2.0 |
