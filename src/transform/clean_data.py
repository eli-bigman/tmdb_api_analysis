"""
DEPRECATED: Use src.transform.pipeline.DataCleaningPipeline instead.

This module is kept for backwards compatibility.
The implementation has been split into modular components:
- extractors.py: Nested JSON extraction functions
- cleaners.py: Data cleaning and transformation functions
- pipeline.py: Main orchestration class

Import from pipeline module for cleaner, modular code.
"""
from src.transform.pipeline import DataCleaningPipeline

# Alias for backwards compatibility
DataCleaner = DataCleaningPipeline


def main():
    """Run data cleaning pipeline."""
    from src.transform.pipeline import main as pipeline_main
    pipeline_main()


if __name__ == "__main__":
    main()
