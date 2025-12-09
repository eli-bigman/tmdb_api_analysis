"""
Data extraction utilities for nested JSON structures.
"""
import pandas as pd
import numpy as np
from typing import Any, Tuple


def extract_collection_name(collection_data: Any) -> str:
    """
    Extract collection name from belongs_to_collection field.
    
    Args:
        collection_data: Collection dictionary or None
        
    Returns:
        Collection name or NaN
    """
    if collection_data is None or pd.isna(collection_data):
        return np.nan
    if isinstance(collection_data, dict):
        return collection_data.get('name', np.nan)
    return np.nan


def extract_names_from_list(items: Any, key: str = 'name') -> str:
    """
    Extract names from list of dictionaries and join with |.
    
    Args:
        items: List of dictionaries containing name field
        key: Key to extract from dictionaries
        
    Returns:
        Pipe-separated string of names or NaN
    """
    if items is None or pd.isna(items):
        return np.nan
    if isinstance(items, list):
        if len(items) == 0:
            return np.nan
        names = [item.get(key, '') for item in items if isinstance(item, dict)]
        names = [name for name in names if name]  # Remove empty strings
        return '|'.join(names) if names else np.nan
    return np.nan


def extract_cast_info(credits: Any, top_n: int = 5) -> Tuple[str, int]:
    """
    Extract cast information from credits.
    
    Args:
        credits: Credits dictionary
        top_n: Number of top cast members to extract
        
    Returns:
        Tuple of (cast_names, cast_size)
    """
    if credits is None or pd.isna(credits) or not isinstance(credits, dict):
        return np.nan, 0
    
    cast_list = credits.get('cast', [])
    if len(cast_list) == 0:
        return np.nan, 0
    
    # Sort by order and get top N
    sorted_cast = sorted(cast_list, key=lambda x: x.get('order', 999))
    top_cast = sorted_cast[:top_n]
    cast_names = [actor.get('name', '') for actor in top_cast]
    cast_names = [name for name in cast_names if name]
    
    return '|'.join(cast_names) if cast_names else np.nan, len(cast_list)


def extract_director(credits: Any) -> str:
    """
    Extract director name from credits.
    
    Args:
        credits: Credits dictionary
        
    Returns:
        Director name or NaN
    """
    if credits is None or pd.isna(credits) or not isinstance(credits, dict):
        return np.nan
    
    crew_list = credits.get('crew', [])
    if len(crew_list) == 0:
        return np.nan
    
    # Find director
    for person in crew_list:
        if person.get('job') == 'Director':
            return person.get('name', np.nan)
    
    return np.nan


def extract_crew_size(credits: Any) -> int:
    """
    Extract crew size from credits.
    
    Args:
        credits: Credits dictionary
        
    Returns:
        Number of crew members
    """
    if credits is None or pd.isna(credits) or not isinstance(credits, dict):
        return 0
    crew_list = credits.get('crew', [])
    return len(crew_list)


def flatten_nested_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten all nested JSON columns in the DataFrame.
    
    Args:
        df: Raw DataFrame with nested columns
        
    Returns:
        DataFrame with flattened columns
    """
    # Extract collection name
    df['belongs_to_collection'] = df['belongs_to_collection'].apply(extract_collection_name)
    
    # Extract genres
    df['genres'] = df['genres'].apply(lambda x: extract_names_from_list(x, 'name'))
    
    # Extract spoken languages
    df['spoken_languages'] = df['spoken_languages'].apply(
        lambda x: extract_names_from_list(x, 'english_name')
    )
    
    # Extract production countries
    df['production_countries'] = df['production_countries'].apply(
        lambda x: extract_names_from_list(x, 'name')
    )
    
    # Extract production companies
    df['production_companies'] = df['production_companies'].apply(
        lambda x: extract_names_from_list(x, 'name')
    )
    
    # Extract cast and crew info
    cast_info = df['credits'].apply(extract_cast_info)
    df['cast'] = cast_info.apply(lambda x: x[0])
    df['cast_size'] = cast_info.apply(lambda x: x[1])
    
    df['director'] = df['credits'].apply(extract_director)
    df['crew_size'] = df['credits'].apply(extract_crew_size)
    
    # Drop the original credits column
    df = df.drop(columns=['credits'], errors='ignore')
    
    return df
