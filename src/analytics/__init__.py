"""
Analytics module for TMDB movie KPI analysis.

This module provides functions for:
- KPI calculations and rankings (kpi_calculator)
- Advanced filtering and searches (filters)
- Franchise and director aggregations (aggregators)
"""

from .kpi_calculator import *
from .filters import *
from .aggregators import *

__all__ = [
    # KPI Calculator functions
    'rank_movies',
    'get_top_by_revenue',
    'get_bottom_by_revenue',
    'get_top_by_budget',
    'get_bottom_by_budget',
    'get_top_by_profit',
    'get_bottom_by_profit',
    'get_top_by_roi',
    'get_bottom_by_roi',
    'get_most_voted',
    'get_top_rated',
    'get_bottom_rated',
    'get_most_popular',
    
    # Filter functions
    'filter_by_genres',
    'filter_by_actor',
    'filter_by_director',
    'search_movies',
    'search_scifi_action_bruce_willis',
    'search_uma_tarantino',
    
    # Aggregator functions
    'compare_franchise_vs_standalone',
    'get_franchise_statistics',
    'get_director_statistics',
    'get_top_franchises',
    'get_top_directors',
]
