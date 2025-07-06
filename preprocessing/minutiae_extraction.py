"""
Minutiae extraction and template processing functions.
Uses NIST NBIS tools for minutiae detection.
"""
import os
import subprocess
import numpy as np
import logging
from tqdm import tqdm
from typing import Optional, List, Tuple

from .utils import get_file_name_and_ext
from .config import get_default_config

logger = logging.getLogger(__name__)

def call_mindtct(input_file: str, output_prefix: str, config=None) -> bool:
    """
    Call NIST mindtct tool to extract minutiae from fingerprint image.
    
    Args:
        input_file: Path to input fingerprint image
        output_prefix: Prefix for output files (without extension)
        config: Configuration object (optional)
    
    Returns:
        True if extraction succeeded, False otherwise
    """
    if config is None:
        config = get_default_config()
    
    try:
        cmd = f'{config.MINDTCT_PATH} -m1 "{input_file}" "{output_prefix}"'
        
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.wait()
        
        stdout, stderr = process.communicate()
        
        if stderr:
            logger.warning(f"Mindtct warning for {input_file}: {stderr.decode('utf-8')}")
        
        # Check if .min file was created (main output)
        min_file = f"{output_prefix}.min"
        if os.path.exists(min_file):
            logger.debug(f"Minutiae extracted successfully: {min_file}")
            return True
        else:
            logger.error(f"Failed to create minutiae file: {min_file}")
            return False
            
    except Exception as e:
        logger.error(f"Error running mindtct on {input_file}: {e}")
        return False

def extract_minutiae_from_image(
    image_path: str, 
    output_dir: str, 
    keep_all_files: bool = False,
    config=None
) -> Optional[str]:
    """
    Extract minutiae from a single fingerprint image.
    
    Args:
        image_path: Path to fingerprint image
        output_dir: Directory to save minutiae files
        keep_all_files: Whether to keep all output files or just .min
        config: Configuration object (optional)
    
    Returns:
        Path to .min file if successful, None otherwise
    """
    if config is None:
        config = get_default_config()
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Get filename without extension
    _, file_name, _ = get_file_name_and_ext(image_path)
    output_prefix = os.path.join(output_dir, file_name)
    
    # Extract minutiae
    if not call_mindtct(image_path, output_prefix, config):
        return None
    
    min_file = f"{output_prefix}.min"
    
    # Clean up additional files if not needed
    if not keep_all_files:
        extensions_to_remove = ['dm', 'hcm', 'lcm', 'lfm', 'qm', 'xyt', 'brw']
        for ext in extensions_to_remove:
            file_to_remove = f"{output_prefix}.{ext}"
            if os.path.exists(file_to_remove):
                os.remove(file_to_remove)
    
    return min_file if os.path.exists(min_file) else None

def extract_minutiae_from_folder(
    input_dir: str, 
    output_dir: str, 
    keep_all_files: bool = False,
    config=None
) -> Tuple[int, int]:
    """
    Extract minutiae from all images in a folder.
    
    Args:
        input_dir: Input directory containing fingerprint images
        output_dir: Output directory for minutiae files
        keep_all_files: Whether to keep all output files or just .min
        config: Configuration object (optional)
    
    Returns:
        Tuple of (successful_count, total_count)
    """
    if config is None:
        config = get_default_config()
    
    successful = 0
    total = 0
    
    # Get all image files
    image_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if any(file.lower().endswith(ext) for ext in config.SUPPORTED_IMAGE_FORMATS):
                image_files.append(os.path.join(root, file))
    
    for image_path in tqdm(image_files, desc="Extracting minutiae"):
        total += 1
        
        min_file = extract_minutiae_from_image(image_path, output_dir, keep_all_files, config)
        if min_file:
            successful += 1
        else:
            logger.warning(f"Failed to extract minutiae from: {image_path}")
    
    logger.info(f"Minutiae extraction complete: {successful}/{total} images processed successfully")
    return successful, total

def convert_min_to_txt(min_file_path: str, output_dir: str, quality_threshold: float = 0.0) -> Optional[str]:
    """
    Convert NIST .min file to simplified text format.
    
    Args:
        min_file_path: Path to .min file
        output_dir: Output directory for .txt file
        quality_threshold: Minimum quality threshold for minutiae (0.0-1.0)
    
    Returns:
        Path to created .txt file or None if failed
    """
    try:
        with open(min_file_path, 'r') as min_file:
            lines = min_file.readlines()
        
        # Extract filename
        file_name = os.path.splitext(os.path.basename(min_file_path))[0]
        output_file_path = os.path.join(output_dir, f"{file_name}.txt")
        
        os.makedirs(output_dir, exist_ok=True)
        
        minutiae_data = []
        
        # Parse minutiae data (skip first 3 header lines)
        for line in lines[3:]:
            line = line.strip()
            if not line:
                continue
            
            try:
                # Parse NIST format: ID:x,y:direction:type:quality:...
                fields = line.split(':')
                if len(fields) < 5:
                    continue
                
                # Extract coordinates
                x, y = map(int, fields[1].split(','))
                
                # Extract direction (in NIST units, convert to degrees)
                direction_unit = int(fields[2])
                orientation = (90 - (11.25 * direction_unit)) % 360
                
                # Extract quality
                quality = float(fields[3])
                
                # Apply quality filter
                if quality < quality_threshold:
                    continue
                
                # Extract minutiae type
                mn_type = fields[4].strip()
                minutiae_type = 1 if 'BIF' in mn_type else 2  # 1=bifurcation, 2=termination
                
                minutiae_data.append(f"{minutiae_type} {x} {y} {orientation}")
                
            except (ValueError, IndexError) as e:
                logger.warning(f"Error parsing line in {min_file_path}: {line}, Error: {e}")
                continue
        
        # Write to file if we have sufficient minutiae
        if len(minutiae_data) > 0:
            with open(output_file_path, 'w') as output_file:
                for data in minutiae_data:
                    output_file.write(f"{data}\\n")
            
            logger.debug(f"Converted {len(minutiae_data)} minutiae: {min_file_path} -> {output_file_path}")
            return output_file_path
        else:
            logger.warning(f"No valid minutiae found in {min_file_path}")
            return None
            
    except Exception as e:
        logger.error(f"Error converting {min_file_path} to txt: {e}")
        return None

def convert_all_minutiae_files(
    source_dir: str, 
    output_dir: str, 
    quality_threshold: float = 0.0,
    min_minutiae_count: int = 5
) -> Tuple[int, int]:
    """
    Convert all .min files in a directory to .txt format.
    
    Args:
        source_dir: Directory containing .min files
        output_dir: Output directory for .txt files
        quality_threshold: Minimum quality threshold for minutiae
        min_minutiae_count: Minimum number of minutiae required
    
    Returns:
        Tuple of (successful_count, total_count)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    successful = 0
    total = 0
    
    # Find all .min files
    min_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.min'):
                min_files.append(os.path.join(root, file))
    
    for min_file_path in tqdm(min_files, desc="Converting minutiae files"):
        total += 1
        
        txt_file = convert_min_to_txt(min_file_path, output_dir, quality_threshold)
        if txt_file:
            # Check if file has enough minutiae
            try:
                with open(txt_file, 'r') as f:
                    line_count = sum(1 for line in f if line.strip())
                
                if line_count >= min_minutiae_count:
                    successful += 1
                else:
                    logger.warning(f"Removing file with insufficient minutiae ({line_count}): {txt_file}")
                    os.remove(txt_file)
            except Exception as e:
                logger.error(f"Error checking minutiae count in {txt_file}: {e}")
    
    logger.info(f"Minutiae conversion complete: {successful}/{total} files converted successfully")
    return successful, total

def parse_minutiae_file(file_path: str) -> np.ndarray:
    """
    Parse minutiae text file into numpy array.
    
    Args:
        file_path: Path to minutiae .txt file
    
    Returns:
        Numpy array with shape (N, 4) containing [type, x, y, orientation_radians]
    """
    try:
        # Load data: type, x, y, orientation_degrees
        data = np.loadtxt(file_path)
        
        # Ensure we have the right shape
        if data.ndim == 1:
            data = data.reshape(1, -1)
        
        # Convert orientation from degrees to radians
        data[:, 3] = data[:, 3] * np.pi / 180
        
        return data
        
    except Exception as e:
        logger.error(f"Error parsing minutiae file {file_path}: {e}")
        return np.array([]).reshape(0, 4)
