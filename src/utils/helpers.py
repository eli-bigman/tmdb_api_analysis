"""
Utility helper functions for the TMDB analysis project.
"""
import yaml
import json
import logging
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
    

def load_movie_ids(config_path: str = "config/config.yaml") -> List[int]:
    """
    Load movie IDs from configuration file.
    
    Args:
        config_path: Path to config.yaml file
    Returns:
        List of movie IDs
    """
    config = load_config(config_path)
    return config.get('data_collection', {}).get('movie_id', [])


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
    config = load_config(config_path)
    log_config = config.get('logging', {})
    
    # Create logs directory if needed
    if log_config.get('log_to_file', False):
        log_file = log_config.get('log_file', 'logs/tmdb_analysis.log')
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Get logger
    logger = logging.getLogger(module_name or __name__)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Set level
    level_str = log_config.get('level', 'INFO')
    level = getattr(logging, level_str.upper(), logging.INFO)
    
    # Check for module-specific level
    if module_name:
        module_levels = log_config.get('module_levels', {})
        if module_name in module_levels:
            level = getattr(logging, module_levels[module_name].upper(), level)
    
    logger.setLevel(level)
    
    # Create formatter
    log_format = log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    date_format = log_config.get('date_format', '%Y-%m-%d %H:%M:%S')
    formatter = logging.Formatter(log_format, datefmt=date_format)
    
    # Console handler
    if log_config.get('log_to_console', True):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_config.get('log_to_file', False):
        log_file = log_config.get('log_file', 'logs/tmdb_analysis.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger
    # return list(Path(directory).glob("*.json"))
