"""
Utility helper functions for the TMDB analysis project.
"""
import yaml
import json
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
