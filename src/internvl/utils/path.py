"""
Path management utilities for InternVL Evaluation

This module provides centralized path resolution and management.
"""

import logging
import os
from pathlib import Path

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# First make sure we can import from our own project
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Instead of importing get_env, we'll define a simplified version here
# to avoid circular imports
def get_env_for_path(key, default=None, required=False):
    """
    Simplified environment variable getter for path module.
    This avoids circular imports with config.py.
    """
    # Add INTERNVL_ prefix if not present
    if not key.startswith("INTERNVL_"):
        key = f"INTERNVL_{key}"
    
    # Try to get the value
    value = os.getenv(key)
    
    if value is None:
        if required:
            # Print environment variables for debugging
            env_keys = [k for k in os.environ.keys() if k.startswith("INTERNVL_")]
            raise ValueError(f"Required environment variable '{key}' is not set (available: {env_keys})")
        return default
        
    return value

class PathManager:
    """
    Manages path resolution across different environments.
    
    This class provides a unified interface for resolving paths for source code,
    data, and model resources in different environments. It uses environment
    detection to determine which base paths to use.
    
    Attributes:
        environment (str): The detected environment
        base_paths (Dict[str, Path]): Base paths for different resource types
        env_vars (Dict[str, str]): Environment variables loaded from .env file
    """
    
    def __init__(self):
        """Initialize the PathManager with proper environment detection."""
        # Detect environment and set up base paths
        self.environment = get_env_for_path("ENVIRONMENT", "development")
        self.base_paths = {}
        self.env_vars = {}
        
        # Load environment variables
        self._load_environment_variables()
        
        # Configure base paths based on detected environment
        self._configure_base_paths()
        
        logger.info(f"PathManager initialized in {self.environment} environment")
        logger.info(f"Base paths: {self.base_paths}")
    
    def _load_environment_variables(self):
        """Load environment variables for path resolution."""
        # Store environment variables in a dictionary for easy access
        for key, value in os.environ.items():
            if key.startswith("INTERNVL_"):
                self.env_vars[key] = value
    
    def _configure_base_paths(self):
        """Configure base paths for different resource types."""
        # Get current module directory as fallback for source path
        module_dir = Path(__file__).parent.parent.parent
        
        # Configure base paths from environment variables
        self.base_paths = {
            "source": Path(get_env_for_path("SOURCE_PATH", str(module_dir))),
            "data": Path(get_env_for_path("DATA_PATH", required=True)),
            "output": Path(get_env_for_path("OUTPUT_PATH", required=True)),
            # Models are accessed directly via INTERNVL_MODEL_PATH
        }
        
        # Verify all paths are absolute and exist
        missing_paths = []
        for path_type, path in self.base_paths.items():
            # Skip source path validation
            if path_type == "source":
                continue
                
            # Check if path is provided
            if not path or str(path).strip() == "":
                missing_paths.append(path_type)
                continue
                
            # Check if path is absolute
            if not os.path.isabs(str(path)):
                logger.error(f"{path_type.upper()} PATH MUST BE ABSOLUTE: {path}")
                missing_paths.append(path_type)
                
        # If any critical paths are missing, raise error
        if missing_paths:
            paths_str = ", ".join([f"INTERNVL_{p.upper()}_PATH" for p in missing_paths])
            raise ValueError(f"Missing required absolute paths: {paths_str}. These must be set in environment variables.")
        
        # Create output directory if it doesn't exist
        os.makedirs(self.base_paths["output"], exist_ok=True)
    
    def resolve_path(self, path_type: str, *parts) -> Path:
        """
        Resolve a path for the specified resource type.
        
        Args:
            path_type: Type of resource ("source", "data", "output")
            *parts: Additional path components to append
            
        Returns:
            The resolved absolute path
            
        Raises:
            ValueError: If the path_type is invalid
        """
        if path_type not in self.base_paths:
            raise ValueError(f"Invalid path type: {path_type}")
        
        path = self.base_paths[path_type]
        for part in parts:
            path = path / part
            
        return path
    
    def get_data_path(self, *parts) -> Path:
        """Get a path in the data directory."""
        return self.resolve_path("data", *parts)
    
    def get_output_path(self, *parts) -> Path:
        """Get a path in the output directory."""
        return self.resolve_path("output", *parts)
    
    def get_source_path(self, *parts) -> Path:
        """Get a path in the source directory."""
        return self.resolve_path("source", *parts)
    
    def get_prompt_path(self) -> Path:
        """Get path to the prompts YAML file."""
        prompts_path = get_env_for_path("PROMPTS_PATH", required=True)
        return Path(prompts_path)
    
    def get_synthetic_data_path(self) -> Path:
        """Get path to the synthetic data directory."""
        return self.get_data_path("synthetic")
    
    def get_synthetic_ground_truth_path(self) -> Path:
        """Get path to the synthetic ground truth directory."""
        return self.get_synthetic_data_path() / "ground_truth"
    
    def get_synthetic_images_path(self) -> Path:
        """Get path to the synthetic images directory."""
        return self.get_synthetic_data_path() / "images"

# Create singleton instance of PathManager
# We use a try/except to make the imports safer during development/testing
try:
    path_manager = PathManager()
except Exception as e:
    import logging
    logging.getLogger(__name__).error(f"Error initializing PathManager: {e}")
    path_manager = None