"""
KPI calculator functions for movie performance analysis.

This module provides ranking functions for various movie performance metrics
including revenue, budget, profit, ROI, ratings, and popularity.
"""
import pandas as pd
import numpy as np
from typing import Optional, Callable


def rank_movies(
    df: pd.DataFrame,
    metric: str,
    ascending: bool = False,
    top_n: int = 10,
    filter_condition: Optional[pd.Series] = None,
    display_columns: Optional[list] = None
) -> pd.DataFrame:
    """
    User-Defined Function (UDF) for ranking movies by any metric.
    
    This is the core ranking function used by all other KPI functions.
    
    Args:
        df: DataFrame with movie data
        metric: Column name to rank by (e.g., 'revenue_musd', 'roi')
        ascending: If True, rank lowest to highest. If False, rank highest to lowest
        top_n: Number of top movies to return
        filter_condition: Boolean Series for filtering (e.g., df['budget_musd'] >= 10)
        display_columns: List of columns to display. If None, uses default set
        
    Returns:
        DataFrame with ranked movies
        
    Example:
        >>> rank_movies(df, 'revenue_musd', top_n=20)
        >>> rank_movies(df, 'roi', filter_condition=df['budget_musd'] >= 10)
    """
    # Apply filter if provided
    if filter_condition is not None:
        df_filtered = df[filter_condition].copy()
    else:
        df_filtered = df.copy()
    
    # Remove rows where metric is null
    df_filtered = df_filtered.dropna(subset=[metric])
    
    # Sort by metric
    df_sorted = df_filtered.sort_values(by=metric, ascending=ascending)
    
    # Select top N
    df_top = df_sorted.head(top_n).copy()
    
    # Add rank column
    df_top.insert(0, 'rank', range(1, len(df_top) + 1))
    
    # Select display columns
    if display_columns is None:
        # Default columns to display
        base_cols = ['rank', 'title', metric]
        optional_cols = []
        
        # Add relevant context columns based on metric
        if metric in ['revenue_musd', 'budget_musd', 'profit_musd']:
            optional_cols = ['release_year', 'budget_musd', 'revenue_musd']
        elif metric == 'roi':
            optional_cols = ['release_year', 'budget_musd', 'revenue_musd', 'roi']
        elif metric in ['vote_average', 'vote_count']:
            optional_cols = ['release_year', 'vote_average', 'vote_count']
        elif metric == 'popularity':
            optional_cols = ['release_year', 'popularity', 'vote_average']
        else:
            optional_cols = ['release_year']
        
        # Build final column list (avoid duplicates)
        display_columns = base_cols + [col for col in optional_cols if col not in base_cols and col in df_top.columns]
    
    return df_top[display_columns].reset_index(drop=True)


def get_top_by_revenue(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get movies with highest revenue.
    
    Args:
        df: DataFrame with movie data
        top_n: Number of top movies to return
        
    Returns:
        DataFrame with top revenue movies
    """
    return rank_movies(df, 'revenue_musd', ascending=False, top_n=top_n)


def get_bottom_by_revenue(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get movies with lowest revenue.
    
    Args:
        df: DataFrame with movie data
        top_n: Number of bottom movies to return
        
    Returns:
        DataFrame with lowest revenue movies
    """
    return rank_movies(df, 'revenue_musd', ascending=True, top_n=top_n)


def get_top_by_budget(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get movies with highest budget.
    
    Args:
        df: DataFrame with movie data
        top_n: Number of top movies to return
        
    Returns:
        DataFrame with highest budget movies
    """
    return rank_movies(df, 'budget_musd', ascending=False, top_n=top_n)


def get_bottom_by_budget(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get movies with lowest budget.
    
    Args:
        df: DataFrame with movie data
        top_n: Number of bottom movies to return
        
    Returns:
        DataFrame with lowest budget movies
    """
    return rank_movies(df, 'budget_musd', ascending=True, top_n=top_n)


def get_top_by_profit(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get movies with highest profit (Revenue - Budget).
    
    Args:
        df: DataFrame with movie data
        top_n: Number of top movies to return
        
    Returns:
        DataFrame with highest profit movies
    """
    return rank_movies(df, 'profit_musd', ascending=False, top_n=top_n)


def get_bottom_by_profit(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get movies with lowest profit (Revenue - Budget).
    
    Args:
        df: DataFrame with movie data
        top_n: Number of bottom movies to return
        
    Returns:
        DataFrame with lowest profit movies
    """
    return rank_movies(df, 'profit_musd', ascending=True, top_n=top_n)


def get_top_by_roi(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get movies with highest ROI (Return on Investment).
    
    Only includes movies with budget >= $10M to filter out low-budget outliers.
    ROI = (Revenue - Budget) / Budget * 100
    
    Args:
        df: DataFrame with movie data
        top_n: Number of top movies to return
        
    Returns:
        DataFrame with highest ROI movies (budget >= $10M)
    """
    filter_condition = df['budget_musd'] >= 10
    return rank_movies(df, 'roi', ascending=False, top_n=top_n, filter_condition=filter_condition)


def get_bottom_by_roi(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get movies with lowest ROI (Return on Investment).
    
    Only includes movies with budget >= $10M to filter out low-budget outliers.
    ROI = (Revenue - Budget) / Budget * 100
    
    Args:
        df: DataFrame with movie data
        top_n: Number of bottom movies to return
        
    Returns:
        DataFrame with lowest ROI movies (budget >= $10M)
    """
    filter_condition = df['budget_musd'] >= 10
    return rank_movies(df, 'roi', ascending=True, top_n=top_n, filter_condition=filter_condition)


def get_most_voted(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get movies with most votes.
    
    Args:
        df: DataFrame with movie data
        top_n: Number of top movies to return
        
    Returns:
        DataFrame with most voted movies
    """
    return rank_movies(df, 'vote_count', ascending=False, top_n=top_n)


def get_top_rated(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get highest rated movies.
    
    Only includes movies with at least 10 votes to ensure rating reliability.
    
    Args:
        df: DataFrame with movie data
        top_n: Number of top movies to return
        
    Returns:
        DataFrame with highest rated movies (vote_count >= 10)
    """
    filter_condition = df['vote_count'] >= 10
    return rank_movies(df, 'vote_average', ascending=False, top_n=top_n, filter_condition=filter_condition)


def get_bottom_rated(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get lowest rated movies.
    
    Only includes movies with at least 10 votes to ensure rating reliability.
    
    Args:
        df: DataFrame with movie data
        top_n: Number of bottom movies to return
        
    Returns:
        DataFrame with lowest rated movies (vote_count >= 10)
    """
    filter_condition = df['vote_count'] >= 10
    return rank_movies(df, 'vote_average', ascending=True, top_n=top_n, filter_condition=filter_condition)


def get_most_popular(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get most popular movies based on TMDB popularity score.
    
    Args:
        df: DataFrame with movie data
        top_n: Number of top movies to return
        
    Returns:
        DataFrame with most popular movies
    """
    return rank_movies(df, 'popularity', ascending=False, top_n=top_n)
