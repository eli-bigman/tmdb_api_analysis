"""
Visualization functions for movie data analysis.

This module provides modular, reusable plotting functions using Matplotlib.
All functions accept optional ax parameter for subplot integration.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional
from matplotlib.axes import Axes


def plot_revenue_vs_budget(df: pd.DataFrame, ax: Optional[Axes] = None, **kwargs) -> Axes:
    """
    Scatter plot of budget vs revenue with break-even reference line.
    
    Args:
        df: DataFrame with 'budget_musd' and 'revenue_musd' columns
        ax: Optional matplotlib axes object
        **kwargs: Additional arguments passed to scatter()
        
    Returns:
        Matplotlib axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # Calculate profit for color mapping
    df_plot = df.copy()
    df_plot['profit_musd'] = df_plot['revenue_musd'] - df_plot['budget_musd']
    
    # Remove movies with missing budget or revenue
    df_plot = df_plot.dropna(subset=['budget_musd', 'revenue_musd'])
    
    # Scatter plot
    scatter = ax.scatter(
        df_plot['budget_musd'], 
        df_plot['revenue_musd'],
        c=df_plot['profit_musd'],
        cmap='RdYlGn',
        alpha=0.6,
        edgecolors='black',
        linewidth=0.5,
        **kwargs
    )
    
    # Add break-even line (y = x)
    max_val = max(df_plot['budget_musd'].max(), df_plot['revenue_musd'].max())
    ax.plot([0, max_val], [0, max_val], 'r--', alpha=0.5, label='Break-even')
    
    # Formatting
    ax.set_xlabel('Budget (Million USD)', fontsize=12)
    ax.set_ylabel('Revenue (Million USD)', fontsize=12)
    ax.set_title('Revenue vs Budget: Profitability Analysis', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Profit (Million USD)', fontsize=10)
    
    return ax


def plot_roi_by_genre(df: pd.DataFrame, ax: Optional[Axes] = None, top_n: int = 10, **kwargs) -> Axes:
    """
    Box plot of ROI distribution by genre (budget >= $10M).
    
    Args:
        df: DataFrame with 'genres' and 'budget_musd', 'revenue_musd' columns
        ax: Optional matplotlib axes object
        top_n: Number of top genres to display
        **kwargs: Additional arguments passed to boxplot()
        
    Returns:
        Matplotlib axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
    
    # Filter to budget >= $10M and calculate ROI
    df_plot = df[df['budget_musd'] >= 10].copy()
    df_plot['roi'] = ((df_plot['revenue_musd'] - df_plot['budget_musd']) / df_plot['budget_musd']) * 100
    
    # Explode genres (split pipe-separated genres)
    df_exploded = df_plot.assign(genre=df_plot['genres'].str.split('|')).explode('genre')
    df_exploded = df_exploded.dropna(subset=['genre', 'roi'])
    
    # Get top N genres by movie count
    genre_counts = df_exploded['genre'].value_counts().head(top_n)
    top_genres = genre_counts.index.tolist()
    
    # Filter to top genres and prepare data
    df_filtered = df_exploded[df_exploded['genre'].isin(top_genres)]
    
    # Sort genres by median ROI
    genre_medians = df_filtered.groupby('genre')['roi'].median().sort_values(ascending=False)
    sorted_genres = genre_medians.index.tolist()
    
    # Prepare data for box plot
    data = [df_filtered[df_filtered['genre'] == genre]['roi'].values for genre in sorted_genres]
    
    # Box plot
    bp = ax.boxplot(data, labels=sorted_genres, patch_artist=True, **kwargs)
    
    # Color boxes
    for patch in bp['boxes']:
        patch.set_facecolor('lightblue')
        patch.set_alpha(0.7)
    
    # Formatting
    ax.set_xlabel('Genre', fontsize=12)
    ax.set_ylabel('ROI (%)', fontsize=12)
    ax.set_title('ROI Distribution by Genre (Budget ≥ $10M)', fontsize=14, fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=0, color='r', linestyle='--', alpha=0.5, label='Break-even')
    ax.legend()
    
    plt.tight_layout()
    return ax


def plot_popularity_vs_rating(df: pd.DataFrame, ax: Optional[Axes] = None, **kwargs) -> Axes:
    """
    Scatter plot of rating vs popularity with vote count as point size.
    
    Args:
        df: DataFrame with 'vote_average', 'popularity', 'vote_count' columns
        ax: Optional matplotlib axes object
        **kwargs: Additional arguments passed to scatter()
        
    Returns:
        Matplotlib axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # Filter valid data
    df_plot = df.dropna(subset=['vote_average', 'popularity', 'vote_count']).copy()
    
    # Normalize vote_count for size (10-200 range)
    sizes = 10 + (df_plot['vote_count'] - df_plot['vote_count'].min()) / \
            (df_plot['vote_count'].max() - df_plot['vote_count'].min()) * 190
    
    # Scatter plot
    scatter = ax.scatter(
        df_plot['vote_average'],
        df_plot['popularity'],
        s=sizes,
        alpha=0.5,
        c=df_plot['vote_count'],
        cmap='viridis',
        edgecolors='black',
        linewidth=0.5,
        **kwargs
    )
    
    # Add trend line
    z = np.polyfit(df_plot['vote_average'], df_plot['popularity'], 1)
    p = np.poly1d(z)
    ax.plot(df_plot['vote_average'].sort_values(), 
            p(df_plot['vote_average'].sort_values()), 
            "r--", alpha=0.7, label=f'Trend: y={z[0]:.1f}x{z[1]:+.1f}')
    
    # Formatting
    ax.set_xlabel('Rating (Vote Average)', fontsize=12)
    ax.set_ylabel('Popularity Score', fontsize=12)
    ax.set_title('Popularity vs Rating (Point size = Vote Count)', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Vote Count', fontsize=10)
    
    return ax


def plot_yearly_trends(df: pd.DataFrame, ax: Optional[Axes] = None, **kwargs) -> Axes:
    """
    Line plot of total revenue by release year.
    
    Args:
        df: DataFrame with 'release_date' and 'revenue_musd' columns
        ax: Optional matplotlib axes object
        **kwargs: Additional arguments passed to plot()
        
    Returns:
        Matplotlib axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
    
    # Extract year and prepare data
    df_plot = df.copy()
    df_plot['release_year'] = pd.to_datetime(df_plot['release_date'], errors='coerce').dt.year
    df_plot = df_plot.dropna(subset=['release_year', 'revenue_musd'])
    
    # Group by year
    yearly = df_plot.groupby('release_year').agg({
        'revenue_musd': 'sum',
        'id': 'count'
    }).rename(columns={'id': 'movie_count'})
    
    # Primary axis: Total Revenue
    color = 'tab:blue'
    ax.plot(yearly.index, yearly['revenue_musd'], marker='o', 
            color=color, linewidth=2, label='Total Revenue', **kwargs)
    ax.set_xlabel('Release Year', fontsize=12)
    ax.set_ylabel('Total Revenue (Million USD)', fontsize=12, color=color)
    ax.tick_params(axis='y', labelcolor=color)
    ax.grid(True, alpha=0.3)
    
    # Secondary axis: Movie Count
    ax2 = ax.twinx()
    color = 'tab:orange'
    ax2.plot(yearly.index, yearly['movie_count'], marker='s', 
             color=color, linewidth=2, linestyle='--', alpha=0.7, label='Movie Count')
    ax2.set_ylabel('Number of Movies', fontsize=12, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    
    # Title and legend
    ax.set_title('Yearly Box Office Performance Trends', fontsize=14, fontweight='bold')
    
    # Combine legends
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    return ax


def plot_franchise_comparison(df: pd.DataFrame, ax: Optional[Axes] = None, **kwargs) -> Axes:
    """
    Bar chart comparing franchise vs standalone movies.
    
    Args:
        df: DataFrame with 'collection_name', 'revenue_musd', 'vote_average' columns
        ax: Optional matplotlib axes object
        **kwargs: Additional arguments passed to bar()
        
    Returns:
        Matplotlib axes object
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create franchise indicator
    df_plot = df.copy()
    df_plot['is_franchise'] = df_plot['collection_name'].notna()
    
    # Group and calculate metrics
    comparison = df_plot.groupby('is_franchise').agg({
        'id': 'count',
        'revenue_musd': 'mean',
        'vote_average': 'mean'
    }).rename(columns={'id': 'count'})
    
    # Prepare data
    categories = ['Standalone', 'Franchise']
    x = np.arange(len(categories))
    width = 0.25
    
    # Values
    counts = [comparison.loc[False, 'count'], comparison.loc[True, 'count']]
    revenues = [comparison.loc[False, 'revenue_musd'], comparison.loc[True, 'revenue_musd']]
    ratings = [comparison.loc[False, 'vote_average'], comparison.loc[True, 'vote_average']]
    
    # Create grouped bars
    ax.bar(x - width, counts, width, label='Movie Count', color='skyblue', **kwargs)
    
    # Secondary axis for revenue
    ax2 = ax.twinx()
    ax2.bar(x, revenues, width, label='Avg Revenue (MUSD)', color='lightcoral', **kwargs)
    
    # Tertiary axis for rating
    ax3 = ax.twinx()
    ax3.spines['right'].set_position(('outward', 60))
    ax3.bar(x + width, ratings, width, label='Avg Rating', color='lightgreen', **kwargs)
    
    # Formatting
    ax.set_xlabel('Movie Type', fontsize=12)
    ax.set_ylabel('Movie Count', fontsize=12, color='skyblue')
    ax2.set_ylabel('Avg Revenue (Million USD)', fontsize=12, color='lightcoral')
    ax3.set_ylabel('Avg Rating', fontsize=12, color='lightgreen')
    
    ax.set_title('Franchise vs Standalone: Performance Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.tick_params(axis='y', labelcolor='skyblue')
    ax2.tick_params(axis='y', labelcolor='lightcoral')
    ax3.tick_params(axis='y', labelcolor='lightgreen')
    ax3.set_ylim(0, 10)  # Rating scale 0-10
    
    # Combine legends
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    ax.legend(lines1 + lines2 + lines3, labels1 + labels2 + labels3, loc='upper left')
    
    plt.tight_layout()
    return ax
