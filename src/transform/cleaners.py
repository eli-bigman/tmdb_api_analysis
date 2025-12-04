"""
Data cleaning utilities for handling data types and missing values.
"""
import pandas as pd
import numpy as np


def clean_datatypes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert columns to appropriate data types.
    
    Args:
        df: DataFrame with raw types
        
    Returns:
        DataFrame with correct types
    """
    # Convert numeric columns
    numeric_cols = ['budget', 'revenue', 'runtime', 'popularity', 'vote_average', 'vote_count']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Ensure id is integer
    if 'id' in df.columns:
        df['id'] = pd.to_numeric(df['id'], errors='coerce').astype('Int64')
    
    # Convert release_date to datetime
    if 'release_date' in df.columns:
        df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    
    # Validate vote_average range (0-10)
    if 'vote_average' in df.columns:
        df.loc[(df['vote_average'] < 0) | (df['vote_average'] > 10), 'vote_average'] = np.nan
    
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values and unrealistic data.
    
    Args:
        df: DataFrame with raw values
        
    Returns:
        DataFrame with cleaned values
    """
    # Replace 0 values with NaN for budget, revenue, runtime
    for col in ['budget', 'revenue', 'runtime']:
        if col in df.columns:
            df.loc[df[col] == 0, col] = np.nan
    
    # Convert budget and revenue to millions USD
    if 'budget' in df.columns:
        df['budget_musd'] = df['budget'] / 1_000_000
        df = df.drop(columns=['budget'])
    
    if 'revenue' in df.columns:
        df['revenue_musd'] = df['revenue'] / 1_000_000
        df = df.drop(columns=['revenue'])
    
    # Replace placeholder text with NaN
    text_cols = ['overview', 'tagline']
    for col in text_cols:
        if col in df.columns:
            # Replace common placeholders
            placeholders = ['no overview', 'no data', 'n/a', '', ' ']
            df[col] = df[col].str.strip()
            df.loc[df[col].str.lower().isin(placeholders), col] = np.nan
            df.loc[df[col] == '', col] = np.nan
    
    # Set vote_average to NaN for movies with 0 votes
    if 'vote_count' in df.columns and 'vote_average' in df.columns:
        df.loc[df['vote_count'] == 0, 'vote_average'] = np.nan
    
    return df


def apply_quality_filters(df: pd.DataFrame, drop_columns: list = None) -> pd.DataFrame:
    """
    Apply data quality filters.
    
    Args:
        df: DataFrame to filter
        drop_columns: List of columns to drop
        
    Returns:
        Filtered DataFrame
    """
    if drop_columns is None:
        drop_columns = ['adult', 'imdb_id', 'original_title', 'video', 'homepage']
    
    # Remove duplicates based on id
    df = df.drop_duplicates(subset=['id'], keep='first')
    
    # Drop rows with missing id or title
    df = df.dropna(subset=['id', 'title'])
    
    # Keep only rows with at least 10 non-null values
    df = df.dropna(thresh=10)
    
    # Filter to only 'Released' movies
    if 'status' in df.columns:
        df = df[df['status'] == 'Released'].copy()
        df = df.drop(columns=['status'])
    
    # Drop irrelevant columns
    cols_to_drop = [col for col in drop_columns if col in df.columns]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
    
    return df


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived features for analysis.
    
    Args:
        df: Cleaned DataFrame
        
    Returns:
        DataFrame with additional features
    """
    # Extract release year
    if 'release_date' in df.columns:
        df['release_year'] = df['release_date'].dt.year
    
    # Calculate ROI (Return on Investment)
    if 'budget_musd' in df.columns and 'revenue_musd' in df.columns:
        df['roi'] = np.where(
            df['budget_musd'] > 0,
            ((df['revenue_musd'] - df['budget_musd']) / df['budget_musd']) * 100,
            np.nan
        )
    
    # Calculate profit
    if 'budget_musd' in df.columns and 'revenue_musd' in df.columns:
        df['profit_musd'] = df['revenue_musd'] - df['budget_musd']
    
    # Extract overview length
    if 'overview' in df.columns:
        df['overview_length'] = df['overview'].str.len()
    
    return df


def reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reorder columns to specified sequence.
    
    Args:
        df: DataFrame with all columns
        
    Returns:
        DataFrame with reordered columns
    """
    desired_order = [
        'id', 'title', 'tagline', 'release_date', 'genres', 
        'belongs_to_collection', 'original_language', 'budget_musd', 
        'revenue_musd', 'production_companies', 'production_countries', 
        'vote_count', 'vote_average', 'popularity', 'runtime', 
        'overview', 'spoken_languages', 'poster_path', 
        'cast', 'cast_size', 'director', 'crew_size'
    ]
    
    # Keep only columns that exist in the DataFrame
    available_cols = [col for col in desired_order if col in df.columns]
    
    # Add any remaining columns not in desired order
    remaining_cols = [col for col in df.columns if col not in available_cols]
    final_order = available_cols + remaining_cols
    
    return df[final_order]
