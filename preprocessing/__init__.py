"""
Fingerprint Preprocessing Pipeline

A comprehensive preprocessing pipeline for fingerprint images including:
- Quality filtering using NFIQ scores
- Image cropping and centering 
- Fingerprint enhancement
- Minutiae extraction using NIST tools
- Template rendering for deepfake generation

Example usage:
    from preprocessing import PreprocessingPipeline
    
    pipeline = PreprocessingPipeline()
    pipeline.run_full_pipeline(
        input_dir="raw_fingerprints/",
        output_dir="processed_data/"
    )
"""

from .config import Config, get_default_config
from .utils import setup_logging
from .fingerprint_preprocessing import (
    preprocess_fingerprint_scan,
    process_folder,
    crop_and_center_image,
    enhance_fingerprint
)
from .minutiae_extraction import (
    extract_minutiae_from_image,
    extract_minutiae_from_folder,
    convert_min_to_txt,
    convert_all_minutiae_files,
    parse_minutiae_file
)
from .template_rendering import (
    create_template_image,
    create_template_from_file,
    create_templates_from_folder,
    visualize_template
)

import os
import logging
from typing import Optional

__version__ = "1.0.0"
__author__ = "Yaniv Hacmon, Keren Gorelik, Yisroel Mirsky"

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

class PreprocessingPipeline:
    """
    Main preprocessing pipeline class that orchestrates the entire process.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the preprocessing pipeline.
        
        Args:
            config: Configuration object (optional, uses default if None)
        """
        self.config = config if config is not None else get_default_config()
        logger.info("Preprocessing pipeline initialized")
    
    def run_full_pipeline(
        self,
        input_dir: str,
        output_dir: str,
        filter_quality: bool = True,
        enhance: bool = False,
        template_size: tuple = (512, 512)
    ) -> dict:
        """
        Run the complete preprocessing pipeline.
        
        Args:
            input_dir: Directory containing raw fingerprint images
            output_dir: Base output directory
            filter_quality: Whether to apply NFIQ quality filtering
            enhance: Whether to apply fingerprint enhancement
            template_size: Size for generated template images
        
        Returns:
            Dictionary with processing statistics
        """
        logger.info(f"Starting full preprocessing pipeline: {input_dir} -> {output_dir}")
        
        # Create output directories
        processed_dir = os.path.join(output_dir, "processed")
        minutiae_dir = os.path.join(output_dir, "minutiae") 
        txt_dir = os.path.join(output_dir, "minutiae_txt")
        templates_dir = os.path.join(output_dir, "templates")
        
        stats = {}
        
        # Step 1: Preprocess fingerprint images
        logger.info("Step 1: Preprocessing fingerprint images...")
        processed_count, total_images = process_folder(
            input_dir, processed_dir, 
            filter_nfiq_score=filter_quality,
            enhance=enhance,
            config=self.config
        )
        stats['preprocessing'] = {
            'processed': processed_count, 
            'total': total_images,
            'success_rate': processed_count / total_images if total_images > 0 else 0
        }
        
        # Step 2: Extract minutiae
        logger.info("Step 2: Extracting minutiae...")
        minutiae_count, _ = extract_minutiae_from_folder(
            processed_dir, minutiae_dir, config=self.config
        )
        stats['minutiae_extraction'] = {
            'extracted': minutiae_count,
            'success_rate': minutiae_count / processed_count if processed_count > 0 else 0
        }
        
        # Step 3: Convert minutiae to text format
        logger.info("Step 3: Converting minutiae to text format...")
        txt_count, _ = convert_all_minutiae_files(
            minutiae_dir, txt_dir, min_minutiae_count=5
        )
        stats['minutiae_conversion'] = {
            'converted': txt_count,
            'success_rate': txt_count / minutiae_count if minutiae_count > 0 else 0
        }
        
        # Step 4: Create template images
        logger.info("Step 4: Creating template images...")
        template_count, _ = create_templates_from_folder(
            txt_dir, templates_dir, 
            target_size=template_size,
            config=self.config
        )
        stats['template_creation'] = {
            'created': template_count,
            'success_rate': template_count / txt_count if txt_count > 0 else 0
        }
        
        # Overall statistics
        stats['overall'] = {
            'input_images': total_images,
            'final_templates': template_count,
            'overall_success_rate': template_count / total_images if total_images > 0 else 0
        }
        
        logger.info("Pipeline complete!")
        logger.info(f"Overall success: {template_count}/{total_images} images -> templates")
        
        return stats
    
    def run_preprocessing_only(
        self,
        input_dir: str,
        output_dir: str,
        filter_quality: bool = True,
        enhance: bool = False
    ) -> dict:
        """
        Run only the image preprocessing step.
        
        Args:
            input_dir: Directory containing raw fingerprint images
            output_dir: Output directory for processed images
            filter_quality: Whether to apply NFIQ quality filtering
            enhance: Whether to apply fingerprint enhancement
        
        Returns:
            Dictionary with processing statistics
        """
        logger.info("Running preprocessing only...")
        
        processed_count, total_images = process_folder(
            input_dir, output_dir,
            filter_nfiq_score=filter_quality,
            enhance=enhance,
            config=self.config
        )
        
        return {
            'processed': processed_count,
            'total': total_images,
            'success_rate': processed_count / total_images if total_images > 0 else 0
        }
    
    def run_minutiae_extraction_only(
        self,
        input_dir: str,
        output_dir: str
    ) -> dict:
        """
        Run only minutiae extraction on preprocessed images.
        
        Args:
            input_dir: Directory containing preprocessed fingerprint images
            output_dir: Output directory for minutiae files
        
        Returns:
            Dictionary with extraction statistics
        """
        logger.info("Running minutiae extraction only...")
        
        # Extract minutiae
        minutiae_dir = os.path.join(output_dir, "minutiae")
        txt_dir = os.path.join(output_dir, "minutiae_txt")
        
        extracted_count, total_images = extract_minutiae_from_folder(
            input_dir, minutiae_dir, config=self.config
        )
        
        # Convert to text format
        converted_count, _ = convert_all_minutiae_files(
            minutiae_dir, txt_dir, min_minutiae_count=5
        )
        
        return {
            'extracted': extracted_count,
            'converted': converted_count,
            'total': total_images,
            'extraction_rate': extracted_count / total_images if total_images > 0 else 0,
            'conversion_rate': converted_count / extracted_count if extracted_count > 0 else 0
        }
    
    def run_template_creation_only(
        self,
        minutiae_dir: str,
        output_dir: str,
        template_size: tuple = (512, 512)
    ) -> dict:
        """
        Run only template image creation from minutiae files.
        
        Args:
            minutiae_dir: Directory containing minutiae .txt files
            output_dir: Output directory for template images
            template_size: Size for generated template images
        
        Returns:
            Dictionary with creation statistics
        """
        logger.info("Running template creation only...")
        
        created_count, total_files = create_templates_from_folder(
            minutiae_dir, output_dir,
            target_size=template_size,
            config=self.config
        )
        
        return {
            'created': created_count,
            'total': total_files,
            'success_rate': created_count / total_files if total_files > 0 else 0
        }

# Convenience function for quick access
def create_pipeline(config: Optional[Config] = None) -> PreprocessingPipeline:
    """Create a preprocessing pipeline instance."""
    return PreprocessingPipeline(config)

# Export main classes and functions
__all__ = [
    'PreprocessingPipeline',
    'Config',
    'get_default_config',
    'create_pipeline',
    'preprocess_fingerprint_scan',
    'process_folder',
    'extract_minutiae_from_folder',
    'create_templates_from_folder',
    'setup_logging'
]
