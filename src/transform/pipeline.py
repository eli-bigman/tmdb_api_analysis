"""
Complete data cleaning pipeline for TMDB movie data.
Refactored from notebooks/02_data_cleaning.ipynb.
"""
import pandas as pd
import numpy as np
import json
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.helpers import load_config, setup_logging

# Setup logger
logger = setup_logging(module_name='transform')

def extract_name(data):
    """Extract single name from dict."""
    if isinstance(data, dict):
        return data.get('name')
    return np.nan

def extract_names_list(data, key='name', separator='|'):
    """Extract list of names from list of dicts."""
    if isinstance(data, list):
        names = [item.get(key) for item in data if isinstance(item, dict) and item.get(key)]
        return separator.join(names) if names else np.nan
    return np.nan

def extract_cast_info(credits_data):
    """Extract cast and crew information."""
    if isinstance(credits_data, dict):
        cast = credits_data.get('cast', [])
        crew = credits_data.get('crew', [])
        
        # Top 5 cast
        top_cast = [p.get('name') for p in cast[:5]]
        cast_str = '|'.join(top_cast) if top_cast else np.nan
        
        # Director
        director = next((p.get('name') for p in crew if p.get('job') == 'Director'), np.nan)
        
        return pd.Series([cast_str, len(cast), director, len(crew)])
    return pd.Series([np.nan, 0, np.nan, 0])

def run_pipeline(config_path: str = "config/config.yaml"):
    """
    Run the complete data cleaning pipeline.
    
    Args:
        config_path: Path to configuration file
    """
    logger.info("Starting data cleaning pipeline...")
    
    # 1. Load Configuration
    try:
        config = load_config(config_path)
        logger.info(f"Loaded config from {config_path}")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    # 2. Load Data
    raw_path = Path(config['paths']['raw_data'])
    if not raw_path.exists():
        logger.error(f"Raw data path does not exist: {raw_path}")
        return

    json_files = list(raw_path.glob('*.json'))
    logger.info(f"Found {len(json_files)} JSON files in {raw_path}")
    
    data_list = []
    for file in json_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                data_list.append(data)
        except Exception as e:
            logger.warning(f"Error reading {file}: {e}")
    
    df = pd.DataFrame(data_list)
    logger.info(f"Initial DataFrame shape: {df.shape}")

    # 3. Data Cleaning
    
    # 3.1 Drop Irrelevant Columns
    cols_to_drop = ['adult', 'imdb_id', 'original_title', 'video', 'homepage']
    existing_cols = [col for col in cols_to_drop if col in df.columns]
    df_clean = df.drop(columns=existing_cols).copy()
    logger.info(f"Dropped columns: {existing_cols}")

    # 3.2 Flatten Nested Columns
    logger.info("Flattening nested JSON columns...")
    df_clean['collection_name'] = df_clean['belongs_to_collection'].apply(extract_name)
    df_clean['genres'] = df_clean['genres'].apply(lambda x: extract_names_list(x))
    df_clean['production_countries'] = df_clean['production_countries'].apply(lambda x: extract_names_list(x))
    df_clean['production_companies'] = df_clean['production_companies'].apply(lambda x: extract_names_list(x))
    df_clean['spoken_languages'] = df_clean['spoken_languages'].apply(lambda x: extract_names_list(x))

    # 3.3 Handle Missing & Incorrect Data
    logger.info("Cleaning datatypes and handling missing values...")
    
    # Convert numeric columns
    numeric_cols = ['budget', 'id', 'popularity', 'revenue', 'vote_count', 'vote_average', 'runtime']
    for col in numeric_cols:
        if col in df_clean.columns:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

    # Convert release_date
    if 'release_date' in df_clean.columns:
        df_clean['release_date'] = pd.to_datetime(df_clean['release_date'], errors='coerce')

    # Handle zero values
    for col in ['budget', 'revenue', 'runtime']:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].replace(0, np.nan)

    # Derived million USD columns
    df_clean['budget_musd'] = df_clean['budget'] / 1_000_000
    df_clean['revenue_musd'] = df_clean['revenue'] / 1_000_000

    # Handle text placeholders
    text_cols = ['overview', 'tagline']
    placeholders = ['No Data', 'No Overview', 'n/a', 'nan']
    for col in text_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].replace(placeholders, np.nan)

    # 3.4 Filtering
    initial_len = len(df_clean)
    
    # Drop duplicates
    df_clean = df_clean.drop_duplicates(subset=['id'], keep='first')
    
    # Drop missing ID/Title
    df_clean = df_clean.dropna(subset=['id', 'title'])
    
    # Threshold filtering
    df_clean = df_clean.dropna(thresh=10)
    
    # Status filtering
    if 'status' in df_clean.columns:
        df_clean = df_clean[df_clean['status'] == 'Released']
        df_clean = df_clean.drop(columns=['status'])
        
    logger.info(f"Rows removed during filtering: {initial_len - len(df_clean)}")
    logger.info(f"Current count: {len(df_clean)}")

    # 4. Feature Engineering
    logger.info("Performing feature engineering...")
    
    # Cast & Crew
    if 'credits' in df_clean.columns:
        df_clean[['cast', 'cast_size', 'director', 'crew_size']] = df_clean['credits'].apply(extract_cast_info)

    # Release Year
    df_clean['release_year'] = df_clean['release_date'].dt.year
    
    # Force string types for specific columns
    string_cols = ['tagline', 'title', 'collection_name']
    for col in string_cols:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).replace('nan', np.nan)

    # 5. Inspection (Log anomalies)
    logger.info("Inspecting Extracted Data (Top 5 values):")
    inspection_cols = ['genres', 'collection_name', 'production_countries']
    for col in inspection_cols:
        if col in df_clean.columns:
            logger.info(f"\n--- {col} ---\n{df_clean[col].value_counts().head(5)}")

    # 6. Finalize & Save
    desired_order = [
        'id', 'title', 'tagline', 'release_date', 'genres', 'collection_name', 
        'original_language', 'budget_musd', 'revenue_musd', 'production_companies', 
        'production_countries', 'vote_count', 'vote_average', 'popularity', 
        'runtime', 'overview', 'spoken_languages', 'poster_path', 
        'cast', 'cast_size', 'director', 'crew_size'
    ]
    
    final_cols = [c for c in desired_order if c in df_clean.columns]
    df_final = df_clean[final_cols].copy()
    df_final = df_final.reset_index(drop=True)
    
    processed_path = Path(config['paths']['processed_data'])
    processed_path.mkdir(parents=True, exist_ok=True)
    
    output_csv = processed_path / 'movies_cleaned.csv'
    output_parquet = processed_path / 'movies_cleaned.parquet'
    
    df_final.to_csv(output_csv, index=False)
    df_final.to_parquet(output_parquet, index=False)
    
    logger.info(f"Successfully saved cleaned data to {output_csv} and {output_parquet}")
    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    run_pipeline()
