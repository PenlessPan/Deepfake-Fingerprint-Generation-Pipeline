"""
Template rendering functions to convert minutiae data to visual representations.
Creates RGB images from minutiae templates for use with Pix2Pix training.
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage as ndimage
from skimage.draw import line_nd, disk
from tqdm import tqdm
from typing import Tuple, Optional
import logging

from .minutiae_extraction import parse_minutiae_file
from .config import get_default_config

logger = logging.getLogger(__name__)

def create_minutiae_map(
    minutiae: np.ndarray, 
    orig_size: Tuple[int, int], 
    target_size: Tuple[int, int] = (256, 256)
) -> np.ndarray:
    """
    Create a binary map showing minutiae point locations.
    
    Args:
        minutiae: Minutiae array with columns [type, x, y, orientation]
        orig_size: Original fingerprint image size (height, width)
        target_size: Target output size (height, width)
    
    Returns:
        Binary map with minutiae points marked
    """
    if len(minutiae) == 0:
        return np.zeros(target_size, dtype=np.uint8)
    
    scale_y = target_size[0] / orig_size[0]
    scale_x = target_size[1] / orig_size[1]
    
    minutiae_map = np.zeros(target_size, dtype=np.uint8)
    
    # Scale and clip coordinates
    x_coords = (minutiae[:, 1] * scale_x).astype(np.int32).clip(0, target_size[1] - 1)
    y_coords = (minutiae[:, 2] * scale_y).astype(np.int32).clip(0, target_size[0] - 1)
    
    # Mark minutiae points
    minutiae_map[y_coords, x_coords] = 255
    
    return minutiae_map

def create_orientation_map(
    minutiae: np.ndarray,
    orig_size: Tuple[int, int],
    target_size: Tuple[int, int] = (256, 256),
    line_length: int = 15
) -> np.ndarray:
    """
    Create a map showing minutiae orientation lines.
    
    Args:
        minutiae: Minutiae array with columns [type, x, y, orientation]
        orig_size: Original fingerprint image size (height, width)
        target_size: Target output size (height, width)
        line_length: Length of orientation lines in pixels
    
    Returns:
        Binary map with orientation lines
    """
    if len(minutiae) == 0:
        return np.zeros(target_size, dtype=np.uint8)
    
    scale_y = target_size[0] / orig_size[0]
    scale_x = target_size[1] / orig_size[1]
    scaled_line_length = int(line_length * scale_x)
    
    orientation_map = np.zeros(target_size, dtype=np.uint8)
    
    for x, y, orientation in zip(minutiae[:, 1], minutiae[:, 2], minutiae[:, 3]):
        # Scale coordinates
        x_scaled = int(x * scale_x)
        y_scaled = int(y * scale_y)
        
        # Calculate line endpoints
        x2 = x_scaled + scaled_line_length * np.cos(orientation)
        y2 = y_scaled - scaled_line_length * np.sin(orientation)  # Negative for image coordinates
        
        try:
            # Draw line
            line_coords = line_nd((y_scaled, x_scaled), (int(y2), int(x2)), endpoint=True)
            
            # Filter coordinates within bounds
            valid_mask = (
                (line_coords[0] >= 0) & (line_coords[0] < target_size[0]) &
                (line_coords[1] >= 0) & (line_coords[1] < target_size[1])
            )
            
            if valid_mask.any():
                orientation_map[line_coords[0][valid_mask], line_coords[1][valid_mask]] = 255
                
        except Exception as e:
            logger.debug(f"Error drawing orientation line: {e}")
            continue
    
    return orientation_map

def create_template_image(
    minutiae: np.ndarray,
    orig_size: Tuple[int, int],
    target_size: Tuple[int, int] = (512, 512),
    include_singular: bool = False,
    config=None
) -> np.ndarray:
    """
    Create RGB template image from minutiae data.
    
    Args:
        minutiae: Minutiae array with columns [type, x, y, orientation]
        orig_size: Original fingerprint image size (height, width)
        target_size: Target output size (height, width)
        include_singular: Whether to include singular points (core/delta)
        config: Configuration object (optional)
    
    Returns:
        RGB image with shape (height, width, 3)
    """
    if config is None:
        config = get_default_config()
    
    # Define minutiae types
    if include_singular:
        # Include core and delta points (types 4 and 5)
        type_channels = [
            [1],      # Red: bifurcations
            [2],      # Green: terminations  
            [4, 5]    # Blue: singular points
        ]
    else:
        type_channels = [
            [1],      # Red: bifurcations
            [2],      # Green: terminations
            [-1]      # Blue: empty (placeholder)
        ]
    
    channels = []
    
    for channel_types in type_channels:
        if channel_types == [-1]:
            # Empty channel
            channel = np.zeros(target_size, dtype=np.uint8)
        else:
            # Filter minutiae by type
            type_mask = np.isin(minutiae[:, 0], channel_types)
            filtered_minutiae = minutiae[type_mask]
            
            if len(filtered_minutiae) == 0:
                channel = np.zeros(target_size, dtype=np.uint8)
            else:
                # Create minutiae and orientation maps
                minutiae_map = create_minutiae_map(filtered_minutiae, orig_size, target_size)
                orientation_map = create_orientation_map(
                    filtered_minutiae, orig_size, target_size, config.ORIENTATION_LINE_LENGTH
                )
                
                # Apply Gaussian blur
                minutiae_blurred = ndimage.gaussian_filter(
                    minutiae_map.astype(np.float32), 
                    sigma=np.sqrt(config.MINUTIAE_SIGMA)
                ) * config.MINUTIAE_GAIN
                
                orientation_blurred = ndimage.gaussian_filter(
                    orientation_map.astype(np.float32),
                    sigma=np.sqrt(config.ORIENTATION_SIGMA)
                ) * config.ORIENTATION_GAIN
                
                # Combine and clip
                channel = np.clip(minutiae_blurred + orientation_blurred, 0, 255).astype(np.uint8)
        
        channels.append(channel)
    
    # Stack channels to create RGB image
    rgb_image = np.stack(channels, axis=2)
    
    return rgb_image

def create_template_from_file(
    minutiae_file: str,
    target_size: Tuple[int, int] = (512, 512),
    orig_size: Optional[Tuple[int, int]] = None,
    include_singular: bool = False,
    config=None
) -> Optional[np.ndarray]:
    """
    Create template image from minutiae file.
    
    Args:
        minutiae_file: Path to minutiae .txt file
        target_size: Target output size (height, width)
        orig_size: Original fingerprint size, if None uses target_size
        include_singular: Whether to include singular points
        config: Configuration object (optional)
    
    Returns:
        RGB template image or None if failed
    """
    try:
        # Parse minutiae file
        minutiae = parse_minutiae_file(minutiae_file)
        
        if len(minutiae) == 0:
            logger.warning(f"No minutiae found in file: {minutiae_file}")
            return None
        
        # Use target size if original size not provided
        if orig_size is None:
            orig_size = target_size
        
        # Create template image
        template_image = create_template_image(
            minutiae, orig_size, target_size, include_singular, config
        )
        
        return template_image
        
    except Exception as e:
        logger.error(f"Error creating template from {minutiae_file}: {e}")
        return None

def create_templates_from_folder(
    minutiae_dir: str,
    output_dir: str,
    target_size: Tuple[int, int] = (512, 512),
    include_singular: bool = False,
    config=None
) -> Tuple[int, int]:
    """
    Create template images for all minutiae files in a folder.
    
    Args:
        minutiae_dir: Directory containing minutiae .txt files
        output_dir: Output directory for template images
        target_size: Target output size (height, width)
        include_singular: Whether to include singular points
        config: Configuration object (optional)
    
    Returns:
        Tuple of (successful_count, total_count)
    """
    if config is None:
        config = get_default_config()
    
    os.makedirs(output_dir, exist_ok=True)
    
    successful = 0
    total = 0
    
    # Get all .txt files
    txt_files = [f for f in os.listdir(minutiae_dir) if f.endswith('.txt')]
    
    for filename in tqdm(txt_files, desc="Creating template images"):
        total += 1
        
        minutiae_file = os.path.join(minutiae_dir, filename)
        template_image = create_template_from_file(
            minutiae_file, target_size, None, include_singular, config
        )
        
        if template_image is not None:
            # Save template image
            output_filename = os.path.splitext(filename)[0] + '.png'
            output_path = os.path.join(output_dir, output_filename)
            
            try:
                plt.imsave(output_path, template_image)
                successful += 1
                logger.debug(f"Created template: {output_path}")
            except Exception as e:
                logger.error(f"Error saving template {output_path}: {e}")
        else:
            logger.warning(f"Failed to create template for: {filename}")
    
    logger.info(f"Template creation complete: {successful}/{total} templates created successfully")
    return successful, total

def visualize_template(minutiae_file: str, config=None) -> None:
    """
    Visualize a minutiae template for debugging purposes.
    
    Args:
        minutiae_file: Path to minutiae .txt file
        config: Configuration object (optional)
    """
    if config is None:
        config = get_default_config()
    
    template_image = create_template_from_file(minutiae_file, config=config)
    
    if template_image is not None:
        plt.figure(figsize=(8, 8))
        plt.imshow(template_image)
        plt.title(f"Template: {os.path.basename(minutiae_file)}")
        plt.axis('off')
        plt.show()
    else:
        print(f"Failed to create template for: {minutiae_file}")
