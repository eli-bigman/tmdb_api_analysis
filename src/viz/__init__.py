"""
Visualization module for TMDB movie data analysis.

Provides modular plotting functions using Matplotlib.
"""
from .plots import (
    plot_revenue_vs_budget,
    plot_roi_by_genre,
    plot_popularity_vs_rating,
    plot_yearly_trends,
    plot_franchise_comparison
)

__all__ = [
    'plot_revenue_vs_budget',
    'plot_roi_by_genre',
    'plot_popularity_vs_rating',
    'plot_yearly_trends',
    'plot_franchise_comparison'
]
