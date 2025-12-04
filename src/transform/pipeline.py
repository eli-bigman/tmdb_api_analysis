"""
Data cleaning pipeline orchestrator.
"""
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.utils.helpers import load_config, get_all_json_files, setup_logging
from src.transform.extractors import flatten_nested_columns
from src.transform.cleaners import (
    clean_datatypes, 
    handle_missing_values, 
    apply_quality_filters,
    add_derived_features,
    reorder_columns
)

# Setup logger for this module
logger = setup_logging(module_name='transform')


class DataCleaningPipeline:
    """Orchestrates the complete data cleaning workflow."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize pipeline.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.raw_data_path = Path(self.config['paths']['raw_data'])
        self.interim_data_path = Path(self.config['paths']['interim_data'])
        self.processed_data_path = Path(self.config['paths']['processed_data'])
        
        # Create output directories
        self.interim_data_path.mkdir(parents=True, exist_ok=True)
        self.processed_data_path.mkdir(parents=True, exist_ok=True)
    
    def load_raw_data(self) -> pd.DataFrame:
        """
        Load all raw JSON files into a DataFrame.
        
        Returns:
            DataFrame with raw movie data
        """
        json_files = get_all_json_files(str(self.raw_data_path))
        logger.info(f"Loading {len(json_files)} JSON files from {self.raw_data_path}")
        
        if not json_files:
            raise ValueError(f"No JSON files found in {self.raw_data_path}")
        
        movies_data = []
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    movies_data.append(data)
            except Exception as e:
                logger.warning(f"Error loading {json_file.name}: {e}")
        
        df = pd.DataFrame(movies_data)
        logger.info(f"Loaded {len(df)} movies with {len(df.columns)} columns")
        return df
    
    def run(self, save_interim: bool = True, save_final: bool = True) -> pd.DataFrame:
        """
        Execute complete cleaning pipeline.
        
        Args:
            save_interim: Save interim data
            save_final: Save final processed data
            
        Returns:
            Cleaned DataFrame
        """
        logger.info("="*60)
        logger.info("Starting data cleaning pipeline")
        logger.info("="*60)
        
        # Load raw data
        df = self.load_raw_data()
        logger.info(f"Initial shape: {df.shape}")
        
        # Step 1: Flatten nested columns
        logger.info("Extracting nested columns...")
        df = flatten_nested_columns(df)
        logger.info("✓ Nested columns extracted")
        
        # Step 2: Clean data types
        logger.info("Converting data types...")
        df = clean_datatypes(df)
        logger.info("✓ Data types converted")
        
        # Step 3: Handle missing and unrealistic values
        logger.info("Handling missing and unrealistic values...")
        df = handle_missing_values(df)
        logger.info("✓ Missing and unrealistic values handled")
        
        # Save interim data
        if save_interim:
            interim_file = self.interim_data_path / 'movies_interim.csv'
            df.to_csv(interim_file, index=False)
            logger.info(f"✓ Interim data saved to {interim_file}")
        
        # Step 4: Apply quality filters
        logger.info("Applying quality filters...")
        original_count = len(df)
        df = apply_quality_filters(df)
        removed = original_count - len(df)
        logger.info(f"✓ Quality filters applied: {removed} movies removed ({len(df)} remaining)")
        
        # Step 5: Add derived features
        logger.info("Adding derived features...")
        df = add_derived_features(df)
        logger.info("✓ Derived features added")
        
        # Step 6: Reorder columns
        logger.info("Reordering columns...")
        df = reorder_columns(df)
        logger.info("✓ Columns reordered")
        
        logger.info(f"Final shape: {df.shape}")
        
        # Save final processed data
        if save_final:
            # Save as CSV
            csv_file = self.processed_data_path / 'movies_cleaned.csv'
            df.to_csv(csv_file, index=False)
            logger.info(f"✓ CSV saved to {csv_file}")
            
            # Save as Parquet
            parquet_file = self.processed_data_path / 'movies_cleaned.parquet'
            df.to_parquet(parquet_file, index=False)
            logger.info(f"✓ Parquet saved to {parquet_file}")
        
        logger.info("="*60)
        logger.info("✓ Data cleaning pipeline completed successfully")
        logger.info("="*60)
        
        return df
    
    def get_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate cleaning summary statistics.
        
        Args:
            df: Cleaned DataFrame
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_movies': len(df),
            'total_columns': len(df.columns),
            'null_percentages': (df.isnull().sum() / len(df) * 100).to_dict(),
            'numeric_summary': df.describe().to_dict(),
            'date_range': {
                'earliest': df['release_date'].min() if 'release_date' in df.columns else None,
                'latest': df['release_date'].max() if 'release_date' in df.columns else None
            }
        }
        return summary


def main():
    """Run data cleaning pipeline."""
    pipeline = DataCleaningPipeline()
    df = pipeline.run()
    
    # Display summary
    summary = pipeline.get_summary(df)
    logger.info(f"\nCleaning Summary:")
    logger.info(f"  Total movies: {summary['total_movies']}")
    logger.info(f"  Total columns: {summary['total_columns']}")
    logger.info(f"  Date range: {summary['date_range']['earliest']} to {summary['date_range']['latest']}")


if __name__ == "__main__":
    main()
