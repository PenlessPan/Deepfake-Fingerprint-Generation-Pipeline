"""
Example usage of the fingerprint preprocessing pipeline.

This script demonstrates how to use the preprocessing pipeline for:
1. Full end-to-end processing
2. Individual pipeline steps  
3. Custom configuration

Note: Replace the paths below with your actual data directories.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import preprocessing module
sys.path.append(str(Path(__file__).parent.parent))

from preprocessing import PreprocessingPipeline, Config, setup_logging

def example_full_pipeline():
    """Example: Run the complete preprocessing pipeline."""
    print("=== Full Pipeline Example ===")
    
    # Set up paths (replace with your actual paths)
    input_dir = "path/to/your/raw_fingerprints"
    output_dir = "path/to/your/processed_output"
    
    # Create pipeline with default configuration
    pipeline = PreprocessingPipeline()
    
    # Run full pipeline
    stats = pipeline.run_full_pipeline(
        input_dir=input_dir,
        output_dir=output_dir,
        filter_quality=True,  # Apply NFIQ quality filtering
        enhance=False,        # Skip enhancement for faster processing
        template_size=(512, 512)  # Template image size
    )
    
    # Print results
    print(f"Processing Results:")
    print(f"  Input images: {stats['overall']['input_images']}")
    print(f"  Final templates: {stats['overall']['final_templates']}")
    print(f"  Success rate: {stats['overall']['overall_success_rate']:.2%}")
    
    return stats

def example_step_by_step():
    """Example: Run pipeline steps individually."""
    print("\\n=== Step-by-Step Example ===")
    
    # Set up paths (replace with your actual paths)
    raw_dir = "path/to/your/raw_fingerprints"
    processed_dir = "path/to/your/processed"
    minutiae_dir = "path/to/your/minutiae_txt"
    templates_dir = "path/to/your/templates"
    
    pipeline = PreprocessingPipeline()
    
    # Step 1: Preprocessing only
    print("Step 1: Preprocessing fingerprints...")
    preprocess_stats = pipeline.run_preprocessing_only(
        input_dir=raw_dir,
        output_dir=processed_dir,
        filter_quality=True,
        enhance=False
    )
    print(f"  Processed: {preprocess_stats['processed']}/{preprocess_stats['total']}")
    
    # Step 2: Minutiae extraction only
    print("Step 2: Extracting minutiae...")
    minutiae_stats = pipeline.run_minutiae_extraction_only(
        input_dir=processed_dir,
        output_dir="path/to/your/minutiae_output"
    )
    print(f"  Extracted: {minutiae_stats['extracted']}")
    print(f"  Converted: {minutiae_stats['converted']}")
    
    # Step 3: Template creation only
    print("Step 3: Creating templates...")
    template_stats = pipeline.run_template_creation_only(
        minutiae_dir=minutiae_dir,
        output_dir=templates_dir,
        template_size=(256, 256)  # Smaller templates for this example
    )
    print(f"  Created: {template_stats['created']}/{template_stats['total']}")

def example_custom_config():
    """Example: Using custom configuration."""
    print("\\n=== Custom Configuration Example ===")
    
    # Create custom configuration
    config = Config()
    config.NFIQ_THRESHOLD = 2  # More lenient quality filtering
    config.TARGET_ASPECT_RATIO = 0.75  # 3:4 aspect ratio instead of 1:1
    config.TEMPLATE_SIZE = (256, 256)  # Smaller templates
    config.ORIENTATION_LINE_LENGTH = 20  # Longer orientation lines
    
    # Create pipeline with custom config
    pipeline = PreprocessingPipeline(config)
    
    # Run with custom settings (replace with your actual paths)
    stats = pipeline.run_full_pipeline(
        input_dir="path/to/your/raw_fingerprints",
        output_dir="path/to/your/custom_output",
        filter_quality=True,
        enhance=False,
        template_size=(256, 256)
    )
    
    print(f"Custom config results: {stats['overall']['final_templates']} templates created")

def show_basic_usage():
    """Show basic usage patterns without actual execution."""
    print("=== Basic Usage Patterns ===")
    print("""
# 1. Simple full pipeline
from preprocessing import PreprocessingPipeline

pipeline = PreprocessingPipeline()
stats = pipeline.run_full_pipeline("input_dir/", "output_dir/")

# 2. With custom configuration
from preprocessing import Config

config = Config()
config.NFIQ_THRESHOLD = 2  # More lenient filtering
pipeline = PreprocessingPipeline(config)

# 3. Individual steps
pipeline.run_preprocessing_only("raw/", "processed/")
pipeline.run_minutiae_extraction_only("processed/", "minutiae/")
pipeline.run_template_creation_only("minutiae_txt/", "templates/")
""")

if __name__ == "__main__":
    # Set up logging
    setup_logging()
    
    print("Fingerprint Preprocessing Pipeline - Usage Examples")
    print("=" * 55)
    print()
    print("This file contains example code patterns for using the preprocessing pipeline.")
    print("Replace the placeholder paths with your actual data directories.")
    print()
    
    # Show usage patterns
    show_basic_usage()
    
    print("\\n" + "=" * 55)
    print("Example Functions Available:")
    print("- example_full_pipeline()     : Complete pipeline example")
    print("- example_step_by_step()      : Individual steps example")  
    print("- example_custom_config()     : Custom configuration example")
    print()
    print("To run an example:")
    print("  python -c \"from example_usage import example_full_pipeline; example_full_pipeline()\"")
    print()
    print("Remember to:")
    print("1. Install dependencies: pip install -r ../requirements.txt")
    print("2. Set up external tools: see ../external_tools/README.md")
    print("3. Replace example paths with your actual data directories")
