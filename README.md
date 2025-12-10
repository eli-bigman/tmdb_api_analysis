# TMDB Movie Analysis

A comprehensive data analysis project using The Movie Database (TMDB) API to analyze movie trends, financial performance, and key performance indicators.

## Project Structure

```
tmdb-movie-analysis/
│
├── config/
│   └── config.yaml               # Global configuration
│   
│
├── data/
│   ├── raw/                      # JSON from API
│   ├── interim/                  # Partially cleaned data
│   └── processed/                # Final cleaned dataset
│
├── notebooks/
│   ├── pipeline.ipynb            # Main pipeline
│   ├── 01_fetch_api.ipynb        # API data collection
│   ├── 02_data_cleaning.ipynb    # Data transformation
│   ├── 03_kpi_analysis.ipynb     # KPI computation
│   └── 04_visualizations.ipynb   # Plots and insights
│
├── src/
   ├── utils/                    # Helper functions
   ├── fetch/                    # API extraction
   ├── analytics/                # KPI calculations
   └── viz/                      # Visualization functions

```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/eli-bigman/tmdb_api_analysis.git
cd tmdb_api_analysis
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API credentials

1. Get your TMDB API key from [https://www.themoviedb.org/settings/api](https://www.themoviedb.org/settings/api)
2. Copy `example.env` to `.env`
3. Add your API key to `.env`

```bash
cp example.env .env
# Edit .env and add your API key
```

### 5. Adjust configuration (optional)

Edit `config/config.yaml` to customize:
- Number of movies to fetch
- Features to extract
- Analysis parameters
- Visualization settings

## Usage

### Run notebooks in order:

1. **01_fetch_api.ipynb** - Fetch movie data from TMDB API
2. **02_data_cleaning.ipynb** - Clean and transform data
3. **03_kpi_analysis.ipynb** - Calculate KPIs and perform analysis
4. **04_visualizations.ipynb** - Generate visualizations and insights




## Analysis Features

- Movie financial performance (budget, revenue, ROI)
- Genre analysis and trends
- Director and franchise performance
- Rating and popularity metrics
- Production company analysis
- Temporal trends and seasonality

## Requirements

- Python 3.8+
- TMDB API key (free tier available)
- See `requirements.txt` for package dependencies

## License

This project is for educational and analytical purposes.