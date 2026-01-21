"""
Movie data cleaning and preprocessing module.

This module handles cleaning raw TMDB API data:
- Dropping irrelevant columns
- Flattening nested JSON structures
- Converting datatypes
- Filtering invalid records
- Feature engineering
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class MovieDataCleaner:
    """
    Handles data cleaning and preprocessing for TMDB movie data.
    """
    
    def __init__(self, config=None):
        """
        Initialize the cleaner.
        
        Args:
            config (dict, optional): Configuration dictionary
        """
        self.config = config or {}
        
    def load_raw_data(self, raw_data_path):
        """
        Load raw JSON files from the specified path.
        
        Args:
            raw_data_path (str or Path): Path to raw data directory
            
        Returns:
            pd.DataFrame: DataFrame with raw data
        """
        logger.info("Loading raw data...")
        raw_path = Path(raw_data_path)
        logger.info(f"Raw data path: {raw_path}")
        
        data_list = []
        if raw_path.exists():
            json_files = list(raw_path.glob('*.json'))
            logger.info(f"Found {len(json_files)} JSON files")
            
            for file in json_files:
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        data_list.append(data)
                except Exception as e:
                    logger.error(f"Error reading {file}: {e}")
        else:
            logger.error("Raw data directory does not exist!")
        
        df = pd.DataFrame(data_list)
        logger.info(f"Initial DataFrame shape: {df.shape}")
        return df
    
    def drop_irrelevant_columns(self, df):
        """
        Drop columns that are not needed for analysis.
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: DataFrame with irrelevant columns removed
        """
        logger.info("Dropping irrelevant columns...")
        cols_to_drop = ['adult', 'imdb_id', 'original_title', 'video', 'homepage']
        existing_cols = [col for col in cols_to_drop if col in df.columns]
        df_clean = df.drop(columns=existing_cols).copy()
        logger.info(f"Dropped columns: {existing_cols}")
        logger.info(f"New shape: {df_clean.shape}")
        return df_clean
    
    @staticmethod
    def extract_name(data):
        """Extract single name from dict."""
        if isinstance(data, dict):
            return data.get('name')
        return np.nan
    
    @staticmethod
    def extract_names_list(data, key='name', separator='|'):
        """Extract list of names from list of dicts."""
        if isinstance(data, list):
            names = [item.get(key) for item in data if isinstance(item, dict) and item.get(key)]
            return separator.join(names) if names else np.nan
        return np.nan
    
    def flatten_nested_columns(self, df):
        """
        Flatten nested JSON columns into pipe-separated strings.
        
        Extracts data from: belongs_to_collection, genres, production_countries,
        production_companies, spoken_languages.
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: DataFrame with flattened columns
        """
        logger.info("Flattening nested JSON columns...")
        df = df.copy()
        
        df['collection_name'] = df['belongs_to_collection'].apply(self.extract_name)
        df['genres'] = df['genres'].apply(lambda x: self.extract_names_list(x))
        df['production_countries'] = df['production_countries'].apply(lambda x: self.extract_names_list(x))
        df['production_companies'] = df['production_companies'].apply(lambda x: self.extract_names_list(x))
        df['spoken_languages'] = df['spoken_languages'].apply(lambda x: self.extract_names_list(x))
        
        logger.info("Nested columns flattened successfully")
        return df
    
    def clean_datatypes(self, df):
        """
        Convert columns to appropriate datatypes and handle invalid values.
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: DataFrame with cleaned datatypes
        """
        logger.info("Cleaning datatypes...")
        df = df.copy()
        
        # Convert numeric columns
        numeric_cols = ['budget', 'id', 'popularity', 'revenue', 'vote_count', 'vote_average', 'runtime']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Convert release_date
        if 'release_date' in df.columns:
            df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        
        # Handle zero values in budget/revenue/runtime (zeros are unrealistic)
        for col in ['budget', 'revenue', 'runtime']:
            if col in df.columns:
                df[col] = df[col].replace(0, np.nan)
        
        # Create million USD columns
        df['budget_musd'] = df['budget'] / 1_000_000
        df['revenue_musd'] = df['revenue'] / 1_000_000
        
        # Handle text placeholders
        text_cols = ['overview', 'tagline']
        placeholders = ['No Data', 'No Overview', 'n/a', 'nan']
        for col in text_cols:
            if col in df.columns:
                df[col] = df[col].replace(placeholders, np.nan)
        
        logger.info("Datatypes cleaned.")
        return df
    
    def filter_data(self, df):
        """
        Filter out invalid or incomplete records.
        
        Removes:
        - Duplicates
        - Rows with missing ID/title
        - Rows with < 10 non-null values
        - Non-released movies
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: Filtered dataframe
        """
        logger.info("Filtering data...")
        initial_len = len(df)
        
        # Drop duplicates
        df = df.drop_duplicates(subset=['id'], keep='first')
        
        # Drop missing ID/Title
        df = df.dropna(subset=['id', 'title'])
        
        # Threshold filtering (keep rows with >= 10 non-nulls)
        df = df.dropna(thresh=10)
        
        # Status filtering
        if 'status' in df.columns:
            df = df[df['status'] == 'Released']
            df = df.drop(columns=['status'])
        
        rows_removed = initial_len - len(df)
        logger.info(f"Rows removed: {rows_removed}")
        logger.info(f"Final count: {len(df)}")
        
        return df
    
    @staticmethod
    def extract_cast_info(credits_data):
        """
        Extract cast and crew information from credits data.
        
        Args:
            credits_data: Credits dictionary from TMDB
            
        Returns:
            pd.Series: [cast_str, cast_size, director, crew_size]
        """
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
    
    def engineer_features(self, df):
        """
        Create new features from existing data.
        
        Adds:
        - cast, cast_size, director, crew_size (from credits)
        - release_year (from release_date)
        - Converts string columns and handles NaN
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: DataFrame with engineered features
        """
        logger.info("Performing feature engineering...")
        df = df.copy()
        
        # Extract cast and crew information
        logger.info("Extracting cast and crew information from the 'credits' column.")
        if 'credits' in df.columns:
            df[['cast', 'cast_size', 'director', 'crew_size']] = df['credits'].apply(self.extract_cast_info)
            logger.info("Cast and crew information successfully extracted.")
        else:
            logger.warning("The 'credits' column was not found. Skipping cast/crew extraction.")
        
        # Extract release year
        logger.info("Extracting the release year from the 'release_date' column.")
        if 'release_date' in df.columns:
            df['release_year'] = df['release_date'].dt.year
            logger.info("Release year successfully extracted.")
        
        # Convert string columns and replace 'nan' strings with actual NaN
        string_cols = ['tagline', 'title', 'collection_name']
        logger.info(f"Converting specified columns to string type: {string_cols}")
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).replace('nan', np.nan)
        logger.info("String type conversion complete.")
        
        return df
    
    def sort_genres(self, df):
        """
        Sort genres alphabetically within each cell.
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: DataFrame with sorted genres
        """
        logger.info("Sorting genres alphabetically...")
        df = df.copy()
        if 'genres' in df.columns:
            df['genres'] = df['genres'].apply(
                lambda x: '|'.join(sorted(x.split('|'))) if isinstance(x, str) else x
            )
        return df
    
    def finalize_dataframe(self, df):
        """
        Reorder columns and reset index.
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            pd.DataFrame: Finalized dataframe
        """
        logger.info("Finalizing dataframe...")
        
        desired_order = [
            'id', 'title', 'tagline', 'release_date', 'genres', 'collection_name', 
            'original_language', 'budget_musd', 'revenue_musd', 'production_companies', 
            'production_countries', 'vote_count', 'vote_average', 'popularity', 
            'runtime', 'overview', 'spoken_languages', 'poster_path', 
            'cast', 'cast_size', 'director', 'crew_size', 'release_year'
        ]
        
        # Select existing columns
        final_cols = [c for c in desired_order if c in df.columns]
        df_final = df[final_cols].copy()
        
        # Reset index
        df_final = df_final.reset_index(drop=True)
        
        logger.info(f"Final columns: {df_final.columns.tolist()}")
        logger.info(f"Final shape: {df_final.shape}")
        
        return df_final
    
    def clean_all(self, df):
        """
        Run the complete cleaning pipeline on raw data.
        
        Args:
            df (pd.DataFrame): Raw dataframe
            
        Returns:
            pd.DataFrame: Cleaned and processed dataframe
        """
        logger.info("="*60)
        logger.info("Starting complete data cleaning pipeline")
        logger.info("="*60)
        
        # Step 1: Drop irrelevant columns
        df = self.drop_irrelevant_columns(df)
        
        # Step 2: Flatten nested columns
        df = self.flatten_nested_columns(df)
        
        # Step 3: Clean datatypes
        df = self.clean_datatypes(df)
        
        # Step 4: Filter data
        df = self.filter_data(df)
        
        # Step 5: Engineer features
        df = self.engineer_features(df)
        
        # Step 6: Sort genres
        df = self.sort_genres(df)
        
        # Step 7: Finalize
        df = self.finalize_dataframe(df)
        
        logger.info("="*60)
        logger.info("Data cleaning completed successfully")
        logger.info("="*60)
        
        return df
    
    def save_cleaned_data(self, df, output_path):
        """
        Save cleaned data to CSV and Parquet formats.
        
        Args:
            df (pd.DataFrame): Cleaned dataframe
            output_path (str or Path): Output directory path
        """
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save as CSV
        csv_file = output_path / 'movies_cleaned.csv'
        df.to_csv(csv_file, index=False)
        logger.info(f"Saved to {csv_file}")
        
        # Save as Parquet
        parquet_file = output_path / 'movies_cleaned.parquet'
        df.to_parquet(parquet_file, index=False)
        logger.info(f"Saved to {parquet_file}")
