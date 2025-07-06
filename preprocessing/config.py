"""
Configuration settings for fingerprint preprocessing pipeline.
"""
import os
from pathlib import Path

class Config:
    """Configuration class for preprocessing parameters."""
    
    # External tool paths (customize these for your system)
    NFIQ_PATH = "./external_tools/nfiq"
    MINDTCT_PATH = "./external_tools/mindtct"
    
    # Image processing parameters
    NFIQ_THRESHOLD = 3  # Filter images with NFIQ score >= this value
    CROPPING_MARGIN = 75  # Margin for cropping in pixels
    TARGET_ASPECT_RATIO = 1.0  # 1:1 aspect ratio (set to 0.75 for 3:4)
    
    # Template rendering parameters
    TEMPLATE_SIZE = (512, 512)  # Target size for template images
    ORIENTATION_LINE_LENGTH = 15  # Length of orientation lines in pixels
    MINUTIAE_SIGMA = 9  # Gaussian blur sigma for minutiae points
    ORIENTATION_SIGMA = 3  # Gaussian blur sigma for orientation lines
    MINUTIAE_GAIN = 60  # Gain factor for minutiae visualization
    ORIENTATION_GAIN = 3  # Gain factor for orientation lines
    
    # File extensions
    SUPPORTED_IMAGE_FORMATS = ['.bmp', '.jpg', '.jpeg', '.png', '.tif', '.tiff']
    
    # Quality thresholds
    MIN_NFIQ_SCORE = 50  # Minimum NFIQ score for template selection
    BRIGHTNESS_THRESHOLD = 225  # Threshold for determining if cropping is needed

def get_default_config():
    """Get default configuration instance."""
    return Config()