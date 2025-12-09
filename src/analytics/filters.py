"""
Advanced filtering and search functions for movie data.

This module provides functions for filtering movies by genre, actor, director,
and executing complex multi-criteria searches.
"""
import pandas as pd
import numpy as np
from typing import Optional, List, Union


def filter_by_genres(
    df: pd.DataFrame,
    genres: Union[str, List[str]],
    match_all: bool = True
) -> pd.DataFrame:
    """
    Filter movies by genre(s).
    
    Genres in the dataset are pipe-separated strings (e.g., "Action|Adventure|Sci-Fi").
    
    Args:
        df: DataFrame with movie data
        genres: Single genre string or list of genres to filter by
        match_all: If True, movie must have ALL genres. If False, ANY genre matches
        
    Returns:
        Filtered DataFrame
        
    Example:
        >>> filter_by_genres(df, ["Action", "Adventure"], match_all=True)
        >>> filter_by_genres(df, "Comedy", match_all=False)
    """
    # Convert single genre to list
    if isinstance(genres, str):
        genres = [genres]
    
    # Create filter condition
    if match_all:
        # Movie must have ALL genres
        mask = pd.Series([True] * len(df), index=df.index)
        for genre in genres:
            mask &= df['genres'].str.contains(genre, case=False, na=False)
    else:
        # Movie must have ANY genre
        mask = pd.Series([False] * len(df), index=df.index)
        for genre in genres:
            mask |= df['genres'].str.contains(genre, case=False, na=False)
    
    return df[mask].copy()


def filter_by_actor(
    df: pd.DataFrame,
    actor_name: str,
    case_sensitive: bool = False
) -> pd.DataFrame:
    """
    Filter movies where actor appears in cast.
    
    Cast in the dataset is a pipe-separated string of actor names.
    
    Args:
        df: DataFrame with movie data
        actor_name: Actor name to search for (supports partial matching)
        case_sensitive: If True, perform case-sensitive search
        
    Returns:
        Filtered DataFrame
        
    Example:
        >>> filter_by_actor(df, "Bruce Willis")
        >>> filter_by_actor(df, "willis", case_sensitive=False)
    """
    if 'cast' not in df.columns:
        return df[df['cast'].notna()].iloc[:0]  # Return empty DataFrame with same structure
    
    mask = df['cast'].str.contains(actor_name, case=not case_sensitive, na=False)
    return df[mask].copy()


def filter_by_director(
    df: pd.DataFrame,
    director_name: str,
    case_sensitive: bool = False
) -> pd.DataFrame:
    """
    Filter movies by director.
    
    Args:
        df: DataFrame with movie data
        director_name: Director name to search for (supports partial matching)
        case_sensitive: If True, perform case-sensitive search
        
    Returns:
        Filtered DataFrame
        
    Example:
        >>> filter_by_director(df, "Quentin Tarantino")
        >>> filter_by_director(df, "tarantino", case_sensitive=False)
    """
    if 'director' not in df.columns:
        return df[df['director'].notna()].iloc[:0]  # Return empty DataFrame with same structure
    
    mask = df['director'].str.contains(director_name, case=not case_sensitive, na=False)
    return df[mask].copy()


def search_movies(
    df: pd.DataFrame,
    genres: Optional[Union[str, List[str]]] = None,
    actors: Optional[Union[str, List[str]]] = None,
    directors: Optional[Union[str, List[str]]] = None,
    min_rating: Optional[float] = None,
    min_votes: Optional[int] = None,
    sort_by: str = 'vote_average',
    ascending: bool = False,
    top_n: Optional[int] = None
) -> pd.DataFrame:
    """
    Advanced multi-criteria search for movies.
    
    This is a flexible search builder that allows combining multiple filters.
    
    Args:
        df: DataFrame with movie data
        genres: Genre(s) to filter by (all must match)
        actors: Actor name(s) to filter by (any must match)
        directors: Director name(s) to filter by (any must match)
        min_rating: Minimum vote_average threshold
        min_votes: Minimum vote_count threshold
        sort_by: Column to sort results by
        ascending: Sort order (False = descending/highest first)
        top_n: Limit results to top N movies
        
    Returns:
        Filtered and sorted DataFrame
        
    Example:
        >>> search_movies(df, genres=["Action", "Sci-Fi"], actors="Keanu Reeves",
        ...               sort_by='revenue_musd', ascending=False, top_n=10)
    """
    result = df.copy()
    
    # Apply genre filter
    if genres is not None:
        result = filter_by_genres(result, genres, match_all=True)
    
    # Apply actor filter (supports multiple actors - any match)
    if actors is not None:
        if isinstance(actors, str):
            actors = [actors]
        actor_mask = pd.Series([False] * len(result), index=result.index)
        for actor in actors:
            actor_mask |= result['cast'].str.contains(actor, case=False, na=False)
        result = result[actor_mask]
    
    # Apply director filter (supports multiple directors - any match)
    if directors is not None:
        if isinstance(directors, str):
            directors = [directors]
        director_mask = pd.Series([False] * len(result), index=result.index)
        for director in directors:
            director_mask |= result['director'].str.contains(director, case=False, na=False)
        result = result[director_mask]
    
    # Apply rating filter
    if min_rating is not None:
        result = result[result['vote_average'] >= min_rating]
    
    # Apply vote count filter
    if min_votes is not None:
        result = result[result['vote_count'] >= min_votes]
    
    # Sort results
    if sort_by in result.columns:
        result = result.sort_values(by=sort_by, ascending=ascending)
    
    # Limit results
    if top_n is not None:
        result = result.head(top_n)
    
    return result.reset_index(drop=True)


def search_scifi_action_bruce_willis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Search Query 1: Find best-rated Science Fiction Action movies starring Bruce Willis.
    
    Criteria:
    - Genres: Must have BOTH "Science Fiction" AND "Action"
    - Actor: Bruce Willis
    - Sort: By rating (vote_average) descending (highest to lowest)
    
    Args:
        df: DataFrame with movie data
        
    Returns:
        Filtered and sorted DataFrame with relevant columns
    """
    results = search_movies(
        df,
        genres=["Science Fiction", "Action"],
        actors="Bruce Willis",
        sort_by='vote_average',
        ascending=False
    )
    
    # Select relevant columns for display
    display_cols = ['title', 'release_year', 'vote_average', 'vote_count', 
                    'genres', 'director', 'revenue_musd']
    available_cols = [col for col in display_cols if col in results.columns]
    
    return results[available_cols]


def search_uma_tarantino(df: pd.DataFrame) -> pd.DataFrame:
    """
    Search Query 2: Find movies starring Uma Thurman, directed by Quentin Tarantino.
    
    Criteria:
    - Actor: Uma Thurman
    - Director: Quentin Tarantino
    - Sort: By runtime ascending (shortest to longest)
    
    Args:
        df: DataFrame with movie data
        
    Returns:
        Filtered and sorted DataFrame with relevant columns
    """
    results = search_movies(
        df,
        actors="Uma Thurman",
        directors="Quentin Tarantino",
        sort_by='runtime',
        ascending=True
    )
    
    # Select relevant columns for display
    display_cols = ['title', 'release_year', 'runtime', 'vote_average', 
                    'genres', 'revenue_musd', 'budget_musd']
    available_cols = [col for col in display_cols if col in results.columns]
    
    return results[available_cols]


def filter_by_year_range(
    df: pd.DataFrame,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None
) -> pd.DataFrame:
    """
    Filter movies by release year range.
    
    Args:
        df: DataFrame with movie data
        start_year: Minimum release year (inclusive)
        end_year: Maximum release year (inclusive)
        
    Returns:
        Filtered DataFrame
    """
    result = df.copy()
    
    if start_year is not None:
        result = result[result['release_year'] >= start_year]
    
    if end_year is not None:
        result = result[result['release_year'] <= end_year]
    
    return result
