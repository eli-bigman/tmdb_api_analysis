"""
Aggregation functions for franchise and director analysis.

This module provides functions for comparing franchise vs standalone movies
and analyzing top franchises and directors by various metrics.
"""
import pandas as pd
import numpy as np
from typing import Optional, Literal


def compare_franchise_vs_standalone(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare franchise movies vs standalone movies across key metrics.
    
    Groups movies into:
    - Franchise: Movies with a non-null 'collection_name' value
    - Standalone: Movies with null 'collection_name' value
    
    Metrics calculated:
    - Mean Revenue
    - Median ROI
    - Mean Budget
    - Mean Popularity
    - Mean Rating
    - Count (number of movies)
    
    Args:
        df: DataFrame with movie data
        
    Returns:
        DataFrame with metrics for franchise vs standalone comparison
        
    Example:
        >>> comparison = compare_franchise_vs_standalone(df)
        >>> print(comparison)
    """
    # Create franchise indicator
    df_work = df.copy()
    df_work['is_franchise'] = df_work['collection_name'].notna()

    # Calculate ROI if missing (needed for Median ROI)
    if 'roi' not in df_work.columns:
        if 'revenue_musd' in df_work.columns and 'budget_musd' in df_work.columns:
            df_work['roi'] = (df_work['revenue_musd'] - df_work['budget_musd']) / df_work['budget_musd'].replace(0, np.nan) * 100
    
    # Group by franchise status
    grouped = df_work.groupby('is_franchise')
    
    # Calculate metrics
    comparison = pd.DataFrame({
        'Movie_Type': ['Standalone', 'Franchise'],
        'Count': [
            grouped.size()[False] if False in grouped.size() else 0,
            grouped.size()[True] if True in grouped.size() else 0
        ],
        'Mean_Revenue_MUSD': [
            grouped['revenue_musd'].mean()[False] if False in grouped['revenue_musd'].mean() else np.nan,
            grouped['revenue_musd'].mean()[True] if True in grouped['revenue_musd'].mean() else np.nan
        ],
        'Median_ROI_Percent': [
            grouped['roi'].median()[False] if False in grouped['roi'].median() else np.nan,
            grouped['roi'].median()[True] if True in grouped['roi'].median() else np.nan
        ],
        'Mean_Budget_MUSD': [
            grouped['budget_musd'].mean()[False] if False in grouped['budget_musd'].mean() else np.nan,
            grouped['budget_musd'].mean()[True] if True in grouped['budget_musd'].mean() else np.nan
        ],
        'Mean_Popularity': [
            grouped['popularity'].mean()[False] if False in grouped['popularity'].mean() else np.nan,
            grouped['popularity'].mean()[True] if True in grouped['popularity'].mean() else np.nan
        ],
        'Mean_Rating': [
            grouped['vote_average'].mean()[False] if False in grouped['vote_average'].mean() else np.nan,
            grouped['vote_average'].mean()[True] if True in grouped['vote_average'].mean() else np.nan
        ]
    })
    
    # Round numeric columns for readability
    numeric_cols = comparison.select_dtypes(include=[np.number]).columns
    comparison[numeric_cols] = comparison[numeric_cols].round(2)
    
    return comparison


def get_franchise_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get detailed statistics for each movie franchise.
    
    Groups by 'collection_name' and calculates:
    - Total number of movies in franchise
    - Total Budget
    - Mean Budget
    - Total Revenue
    - Mean Revenue
    - Mean Rating
    
    Args:
        df: DataFrame with movie data
        
    Returns:
        DataFrame with franchise statistics, sorted by total revenue (descending)
        
    Example:
        >>> franchise_stats = get_franchise_statistics(df)
        >>> print(franchise_stats.head(10))
    """
    # Filter to only franchise movies
    df_franchises = df[df['collection_name'].notna()].copy()
    
    if len(df_franchises) == 0:
        return pd.DataFrame()
    
    # Group by collection
    grouped = df_franchises.groupby('collection_name')
    
    # Calculate statistics
    stats = pd.DataFrame({
        'Franchise': grouped['collection_name'].first().values,
        'Movie_Count': grouped.size().values,
        'Total_Budget_MUSD': grouped['budget_musd'].sum().values,
        'Mean_Budget_MUSD': grouped['budget_musd'].mean().values,
        'Total_Revenue_MUSD': grouped['revenue_musd'].sum().values,
        'Mean_Revenue_MUSD': grouped['revenue_musd'].mean().values,
        'Mean_Rating': grouped['vote_average'].mean().values
    })
    
    # Round numeric columns
    numeric_cols = stats.select_dtypes(include=[np.number]).columns
    stats[numeric_cols] = stats[numeric_cols].round(2)
    
    # Sort by total revenue
    stats = stats.sort_values('Total_Revenue_MUSD', ascending=False).reset_index(drop=True)
    
    return stats


def get_director_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get detailed statistics for each director.
    
    Groups by 'director' and calculates:
    - Total Number of Movies Directed
    - Total Revenue
    - Mean Revenue
    - Mean Rating
    
    Args:
        df: DataFrame with movie data
        
    Returns:
        DataFrame with director statistics, sorted by total revenue (descending)
        
    Example:
        >>> director_stats = get_director_statistics(df)
        >>> print(director_stats.head(10))
    """
    # Filter to movies with director information
    df_directors = df[df['director'].notna()].copy()
    
    if len(df_directors) == 0:
        return pd.DataFrame()
    
    # Group by director
    grouped = df_directors.groupby('director')
    
    # Calculate statistics
    stats = pd.DataFrame({
        'Director': grouped['director'].first().values,
        'Movie_Count': grouped.size().values,
        'Total_Revenue_MUSD': grouped['revenue_musd'].sum().values,
        'Mean_Revenue_MUSD': grouped['revenue_musd'].mean().values,
        'Mean_Rating': grouped['vote_average'].mean().values
    })
    
    # Round numeric columns
    numeric_cols = stats.select_dtypes(include=[np.number]).columns
    stats[numeric_cols] = stats[numeric_cols].round(2)
    
    # Sort by total revenue
    stats = stats.sort_values('Total_Revenue_MUSD', ascending=False).reset_index(drop=True)
    
    return stats


def get_top_franchises(
    df: pd.DataFrame,
    sort_by: Literal['total_revenue', 'mean_revenue', 'mean_rating', 'movie_count'] = 'total_revenue',
    top_n: int = 10
) -> pd.DataFrame:
    """
    Get top franchises sorted by specified metric.
    
    Args:
        df: DataFrame with movie data
        sort_by: Metric to sort by. Options:
            - 'total_revenue': Total revenue across all movies
            - 'mean_revenue': Average revenue per movie
            - 'mean_rating': Average rating across all movies
            - 'movie_count': Number of movies in franchise
        top_n: Number of top franchises to return
        
    Returns:
        DataFrame with top franchises
        
    Example:
        >>> top_franchises = get_top_franchises(df, sort_by='mean_rating', top_n=10)
    """
    # Get franchise statistics
    stats = get_franchise_statistics(df)
    
    if len(stats) == 0:
        return stats
    
    # Map sort_by parameter to column name
    sort_column_map = {
        'total_revenue': 'Total_Revenue_MUSD',
        'mean_revenue': 'Mean_Revenue_MUSD',
        'mean_rating': 'Mean_Rating',
        'movie_count': 'Movie_Count'
    }
    
    sort_column = sort_column_map.get(sort_by, 'Total_Revenue_MUSD')
    
    # Sort and return top N
    stats = stats.sort_values(sort_column, ascending=False).head(top_n).reset_index(drop=True)
    
    # Add rank column
    stats.insert(0, 'Rank', range(1, len(stats) + 1))
    
    return stats


def get_top_directors(
    df: pd.DataFrame,
    sort_by: Literal['total_revenue', 'mean_rating', 'movie_count'] = 'total_revenue',
    top_n: int = 10
) -> pd.DataFrame:
    """
    Get top directors sorted by specified metric.
    
    Args:
        df: DataFrame with movie data
        sort_by: Metric to sort by. Options:
            - 'total_revenue': Total revenue across all movies
            - 'mean_rating': Average rating across all movies
            - 'movie_count': Number of movies directed
        top_n: Number of top directors to return
        
    Returns:
        DataFrame with top directors
        
    Example:
        >>> top_directors = get_top_directors(df, sort_by='mean_rating', top_n=10)
    """
    # Get director statistics
    stats = get_director_statistics(df)
    
    if len(stats) == 0:
        return stats
    
    # Map sort_by parameter to column name
    sort_column_map = {
        'total_revenue': 'Total_Revenue_MUSD',
        'mean_rating': 'Mean_Rating',
        'movie_count': 'Movie_Count'
    }
    
    sort_column = sort_column_map.get(sort_by, 'Total_Revenue_MUSD')
    
    # Sort and return top N
    stats = stats.sort_values(sort_column, ascending=False).head(top_n).reset_index(drop=True)
    
    # Add rank column
    stats.insert(0, 'Rank', range(1, len(stats) + 1))
    
    return stats
