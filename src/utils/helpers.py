"""
Utility helper functions for the TMDB analysis project.
"""
import yaml
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config.yaml file
        
    Returns:
        Dictionary containing configuration
    """
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
    


def load_json(file_path: str) -> Dict[str, Any]:
    """
    Load JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dictionary containing JSON data
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict[str, Any], file_path: str) -> None:
    """
    Save data as JSON file.
    
    Args:
        data: Dictionary to save
        file_path: Path where to save the JSON file
    """
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def get_all_json_files(directory: str) -> List[Path]:
    """
    Get all JSON files in a directory.
    
    Args:
        directory: Directory path to search
        
    Returns:
        List of Path objects for JSON files
    """
    return list(Path(directory).glob("*.json"))


def setup_logging(config_path: str = "config/config.yaml", module_name: str = None) -> logging.Logger:
    """
    Set up logging configuration from config file.
    
    Args:
        config_path: Path to config.yaml file
        module_name: Name of the module requesting logger
        
    Returns:
        Configured logger instance
    """

    # Get logger first
    logger = logging.getLogger(module_name or __name__)
    
    # Prevent propagation to root logger to avoid duplicate messages
    logger.propagate = False
    
    # Clear root logger handlers to prevent interference (common in Jupyter notebooks)
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
    
    # If logger already has handlers, it's already configured - just return it
    # This prevents adding duplicate handlers when the same logger is requested multiple times
    if logger.handlers:
        return logger
    
    try:
        config = load_config(config_path)
        log_config = config.get('logging', {})
    except Exception:
        # Fallback if config fails
        log_config = {'level': 'INFO', 'log_to_console': True}
    
    # Set level
    level_str = log_config.get('level', 'INFO')
    level = getattr(logging, level_str.upper(), logging.INFO)
    
    # Check for module-specific level
    module_levels = log_config.get('module_levels', {})
    if module_name and module_name in module_levels:
        level = getattr(logging, module_levels[module_name].upper(), level)
    
    logger.setLevel(level)
    
    # Create formatter
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    date_format = log_config.get('date_format', '%Y-%m-%d %H:%M:%S')
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Console handler
    if log_config.get('log_to_console', True):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_config.get('log_to_file', False):
        log_file = log_config.get('log_file', 'logs/tmdb_analysis.log')
        try:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            print(f"Failed to setup file logging: {e}")
    
    return logger
