# US County-Level Change Dashboard (2018–2023)

**🔗 Interactive Dashboard:** [uscmap.onrender.com](https://uscmap.onrender.com)

This interactive dashboard visualizes county-level percent change across five key social and economic indicators from 2018 to 2023, based on the U.S. Census Bureau's American Community Survey (ACS) 5-Year Estimates. Users can explore trends, filter by variable, and highlight counties with the largest increases or decreases in each category. 

## Features

- Interactive choropleth map of all U.S. counties
- Five indicators of social and economic change:
  - Δ College Educated
  - Δ Number of Households
  - Δ Median Income
  - Δ Age 25–34 Population
  - Δ Age 16+ In Labor Force
- Dropdown menu to select indicator
- Toggle view:
  - Regular View (all counties)
  - Top 300 (largest increases)
  - Bottom 300 (largest decreases)
- Hover tooltips showing county name and % change
- Styled About section and external links

## Data Source

Data are derived from the **2018 and 2023 ACS 5-Year Estimates** via the U.S. Census Bureau API. County geometries come from publicly available GeoJSON sources hosted by Plotly and PublicaMundi. You can find more documentation on the 5-year ACS survey here: [US Census Bureau](https://www.census.gov/data/developers/data-sets/acs-5year.html).

## Deployment

This app is built using [Dash by Plotly](https://plotly.com/dash/) and hosted on [Render](https://render.com/).

## Setup Instructions

Clone the repo and install dependencies:

```bash
git clone https://github.com/laidleyt/uscmap-dash.git
cd uscmap-dash
pip install -r requirements.txt
