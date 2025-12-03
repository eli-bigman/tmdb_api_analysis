"""
Data validation utilities for TMDB movie data.
"""
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import pandas as pd

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.helpers import setup_logging

# Setup logger for this module
logger = setup_logging(module_name='validation')


class JSONValidator:
    """Validate raw JSON files from TMDB API."""
    
    # Required top-level fields
    REQUIRED_FIELDS = [
        'id', 'title', 'release_date', 'budget', 'revenue',
        'runtime', 'vote_average', 'vote_count', 'genres'
    ]
    
    # Optional but important fields
    OPTIONAL_FIELDS = [
        'overview', 'popularity', 'poster_path', 'backdrop_path',
        'original_language', 'production_companies', 'credits'
    ]
    
    def __init__(self):
        """Initialize validator."""
        self.errors = []
        self.warnings = []
    
    def validate_file(self, file_path: Path) -> Tuple[bool, List[str], List[str]]:
        """
        Validate a single JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON format: {e}")
            return False, self.errors, self.warnings
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False, self.errors, self.warnings
        
        # Check required fields
        self._validate_required_fields(data)
        
        # Check data types and values
        self._validate_data_types(data)
        
        # Check data quality
        self._validate_data_quality(data)
        
        # Check optional fields
        self._validate_optional_fields(data)
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _validate_required_fields(self, data: dict):
        """Check if all required fields are present."""
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                self.errors.append(f"Missing required field: {field}")
            elif data[field] is None:
                self.errors.append(f"Required field is null: {field}")
    
    def _validate_data_types(self, data: dict):
        """Validate data types of key fields."""
        # ID should be integer
        if 'id' in data and not isinstance(data['id'], int):
            self.errors.append(f"Invalid id type: {type(data['id'])}, expected int")
        
        # Title should be string
        if 'title' in data and not isinstance(data['title'], str):
            self.errors.append(f"Invalid title type: {type(data['title'])}, expected str")
        
        # Budget/Revenue should be numeric
        for field in ['budget', 'revenue', 'runtime']:
            if field in data and data[field] is not None:
                if not isinstance(data[field], (int, float)):
                    self.errors.append(f"Invalid {field} type: {type(data[field])}, expected numeric")
        
        # Ratings should be numeric
        for field in ['vote_average', 'popularity']:
            if field in data and data[field] is not None:
                if not isinstance(data[field], (int, float)):
                    self.errors.append(f"Invalid {field} type: {type(data[field])}, expected numeric")
        
        # Vote count should be integer
        if 'vote_count' in data and not isinstance(data['vote_count'], int):
            self.errors.append(f"Invalid vote_count type: {type(data['vote_count'])}, expected int")
        
        # Genres should be list
        if 'genres' in data and not isinstance(data['genres'], list):
            self.errors.append(f"Invalid genres type: {type(data['genres'])}, expected list")
    
    def _validate_data_quality(self, data: dict):
        """Validate data quality and reasonable ranges."""
        # Check release date format
        if 'release_date' in data and data['release_date']:
            try:
                date_obj = datetime.strptime(data['release_date'], '%Y-%m-%d')
                if date_obj.year < 1800 or date_obj.year > 2100:
                    self.warnings.append(f"Unusual release year: {date_obj.year}")
            except ValueError:
                self.errors.append(f"Invalid release_date format: {data['release_date']}, expected YYYY-MM-DD")
        
        # Check budget range
        if 'budget' in data and data['budget'] is not None:
            if data['budget'] < 0:
                self.errors.append(f"Negative budget: {data['budget']}")
            elif data['budget'] > 1_000_000_000:  # 1 billion
                self.warnings.append(f"Unusually high budget: ${data['budget']:,}")
        
        # Check revenue range
        if 'revenue' in data and data['revenue'] is not None:
            if data['revenue'] < 0:
                self.errors.append(f"Negative revenue: {data['revenue']}")
            elif data['revenue'] > 10_000_000_000:  # 10 billion
                self.warnings.append(f"Unusually high revenue: ${data['revenue']:,}")
        
        # Check runtime
        if 'runtime' in data and data['runtime'] is not None:
            if data['runtime'] < 0:
                self.errors.append(f"Negative runtime: {data['runtime']}")
            elif data['runtime'] < 30:
                self.warnings.append(f"Very short runtime: {data['runtime']} minutes")
            elif data['runtime'] > 300:
                self.warnings.append(f"Very long runtime: {data['runtime']} minutes")
        
        # Check vote average range
        if 'vote_average' in data and data['vote_average'] is not None:
            if data['vote_average'] < 0 or data['vote_average'] > 10:
                self.errors.append(f"Invalid vote_average: {data['vote_average']}, must be 0-10")
        
        # Check vote count
        if 'vote_count' in data and data['vote_count'] is not None:
            if data['vote_count'] < 0:
                self.errors.append(f"Negative vote_count: {data['vote_count']}")
        
        # Check if genres list is empty
        if 'genres' in data and isinstance(data['genres'], list):
            if len(data['genres']) == 0:
                self.warnings.append("No genres specified")
    
    def _validate_optional_fields(self, data: dict):
        """Check optional fields and warn if missing important ones."""
        # Check for credits
        if 'credits' not in data:
            self.warnings.append("Missing credits data")
        elif isinstance(data['credits'], dict):
            if 'cast' not in data['credits'] or not data['credits']['cast']:
                self.warnings.append("No cast data in credits")
            if 'crew' not in data['credits'] or not data['credits']['crew']:
                self.warnings.append("No crew data in credits")
        
        # Check for production companies
        if 'production_companies' not in data:
            self.warnings.append("Missing production_companies data")
        elif isinstance(data['production_companies'], list) and len(data['production_companies']) == 0:
            self.warnings.append("No production companies specified")
        
        # Check for overview
        if 'overview' not in data or not data['overview']:
            self.warnings.append("Missing movie overview/description")


class DataFrameValidator:
    """Validate processed DataFrames."""
    
    def __init__(self, config: dict):
        """
        Initialize DataFrame validator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.min_votes = config.get('analysis', {}).get('min_vote_count', 100)
        self.min_budget = config.get('analysis', {}).get('min_budget', 1000000)
    
    def validate_movies_df(self, df: pd.DataFrame) -> Tuple[bool, List[str], List[str]]:
        """
        Validate movies DataFrame.
        
        Args:
            df: Movies DataFrame
            
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        # Check required columns
        required_cols = ['id', 'title', 'release_date', 'budget', 'revenue']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")
            return False, errors, warnings
        
        # Check for duplicates
        if df['id'].duplicated().any():
            dup_count = df['id'].duplicated().sum()
            errors.append(f"Found {dup_count} duplicate movie IDs")
        
        # Check for nulls in critical fields
        for col in ['id', 'title']:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                errors.append(f"{null_count} null values in critical column: {col}")
        
        # Warnings for high null percentages
        for col in ['budget', 'revenue', 'runtime', 'release_date']:
            if col in df.columns:
                null_pct = (df[col].isnull().sum() / len(df)) * 100
                if null_pct > 50:
                    warnings.append(f"High null percentage in {col}: {null_pct:.1f}%")
        
        # Check data ranges
        if 'budget' in df.columns:
            negative_budget = (df['budget'] < 0).sum()
            if negative_budget > 0:
                errors.append(f"{negative_budget} movies with negative budget")
        
        if 'revenue' in df.columns:
            negative_revenue = (df['revenue'] < 0).sum()
            if negative_revenue > 0:
                errors.append(f"{negative_revenue} movies with negative revenue")
        
        # Check date format
        if 'release_date' in df.columns:
            try:
                pd.to_datetime(df['release_date'])
            except Exception as e:
                errors.append(f"Invalid date format in release_date: {e}")
        
        is_valid = len(errors) == 0
        return is_valid, errors, warnings
    
    def validate_quality_thresholds(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter DataFrame based on quality thresholds.
        
        Args:
            df: Movies DataFrame
            
        Returns:
            Filtered DataFrame
        """
        original_count = len(df)
        
        # Filter by vote count
        if 'vote_count' in df.columns:
            df = df[df['vote_count'] >= self.min_votes]
        
        # Filter by budget
        if 'budget' in df.columns:
            df = df[df['budget'] >= self.min_budget]
        
        filtered_count = len(df)
        removed_count = original_count - filtered_count
        
        if removed_count > 0:
            logger.info(f"Filtered out {removed_count} movies below quality thresholds")
            logger.info(f"  - Min votes: {self.min_votes}")
            logger.info(f"  - Min budget: ${self.min_budget:,}")
        
        return df


def validate_raw_data(raw_data_path: Path, verbose: bool = True) -> Dict:
    """
    Validate all raw JSON files.
    
    Args:
        raw_data_path: Path to raw data directory
        verbose: Print detailed results
        
    Returns:
        Validation summary dictionary
    """
    validator = JSONValidator()
    json_files = list(raw_data_path.glob("*.json"))
    
    results = {
        'total_files': len(json_files),
        'valid_files': 0,
        'invalid_files': 0,
        'files_with_warnings': 0,
        'errors': {},
        'warnings': {}
    }
    
    logger.info(f"Validating {len(json_files)} JSON files...")
    
    for json_file in json_files:
        is_valid, errors, warnings = validator.validate_file(json_file)
        
        if is_valid:
            results['valid_files'] += 1
            logger.debug(f"✓ {json_file.name} is valid")
        else:
            results['invalid_files'] += 1
            results['errors'][json_file.name] = errors
            logger.error(f"✗ {json_file.name} has validation errors")
        
        if warnings:
            results['files_with_warnings'] += 1
            results['warnings'][json_file.name] = warnings
            logger.warning(f"⚠ {json_file.name} has {len(warnings)} warnings")
    
    # Log summary
    if verbose:
        logger.info("="*60)
        logger.info("VALIDATION SUMMARY")
        logger.info("="*60)
        logger.info(f"Total files:             {results['total_files']}")
        logger.info(f"Valid files:             {results['valid_files']} ✓")
        logger.info(f"Invalid files:           {results['invalid_files']} ✗")
        logger.info(f"Files with warnings:     {results['files_with_warnings']} ⚠")
        
        if results['invalid_files'] > 0:
            logger.error("="*60)
            logger.error("ERRORS")
            logger.error("="*60)
            for filename, errors in results['errors'].items():
                logger.error(f"{filename}:")
                for error in errors:
                    logger.error(f"  ✗ {error}")
        
        if results['files_with_warnings'] > 0:
            logger.warning("="*60)
            logger.warning("WARNINGS")
            logger.warning("="*60)
            for filename, warnings in results['warnings'].items():
                logger.warning(f"{filename}:")
                for warning in warnings[:5]:  # Limit to 5 warnings per file
                    logger.warning(f"  ⚠ {warning}")
    
    return results


def main():
    """Run validation on raw data."""
    from src.utils.helpers import load_config
    
    logger.info("="*60)
    logger.info("Starting data validation")
    logger.info("="*60)
    
    config = load_config()
    raw_data_path = Path(config['paths']['raw_data'])
    
    if not raw_data_path.exists():
        logger.error(f"Raw data directory not found: {raw_data_path}")
        return
    
    results = validate_raw_data(raw_data_path, verbose=True)
    
    logger.info("="*60)
    if results['invalid_files'] > 0:
        logger.warning(f"Found {results['invalid_files']} invalid files!")
        logger.warning("Review errors above and re-fetch problematic movies if needed.")
    else:
        logger.info("✓ All files validated successfully!")
    logger.info("="*60)


if __name__ == "__main__":
    main()