#!/usr/bin/env python3
"""
Simple fingerprint generation script using trained Pix2Pix model.

This script takes a directory of template images and generates corresponding
fingerprint images using a pre-trained Pix2Pix model.

Note: Model weights are stored in 'weights/' to avoid conflicts with the 
      'models' module from pytorch-CycleGAN-and-pix2pix.

Usage:
    1. Edit the configuration variables at the top of this script
    2. Put your trained model at weights/pix2pix_model.pt (or update MODEL_PATH)
    3. Run: python generate_fingerprints.py
    
Or use command line arguments:
    python generate_fingerprints.py --input_dir /path/to/templates --output_dir /path/to/output
"""

import os
import sys
import argparse
from pathlib import Path

# Add the pytorch-CycleGAN-and-pix2pix directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'pytorch-CycleGAN-and-pix2pix'))

from options.test_options import TestOptions
from data import create_dataset
from models import create_model
from util.util import tensor2im
import torch
import matplotlib.pyplot as plt

class SimpleOptions:
    """Simplified options class with predefined settings for fingerprint generation."""
    
    def __init__(self, input_dir, model_path):
        # Required paths
        self.dataroot = input_dir
        self.checkpoints_dir = os.path.dirname(model_path)
        self.name = os.path.splitext(os.path.basename(model_path))[0]
        
        # Model configuration (based on your command)
        self.model = 'test'
        self.netG = 'unet_256'
        self.norm = 'batch'
        self.no_dropout = True
        self.output_nc = 1
        self.input_nc = 3  # Template images are RGB
        
        # Default settings
        self.phase = 'test'
        self.dataset_mode = 'single'
        self.load_iter = 0
        self.epoch = 'latest'
        self.verbose = False
        self.num_test = float('inf')  # Process all images
        
        # Training-related (not used in test)
        self.isTrain = False
        self.serial_batches = True
        self.num_threads = 0
        self.batch_size = 1
        self.no_flip = True
        
        # Additional required attributes
        self.init_type = 'normal'
        self.init_gain = 0.02
        self.gpu_ids = [0] if torch.cuda.is_available() else []
        self.suffix = ''
        self.load_size = 256
        self.crop_size = 256
        self.max_dataset_size = float('inf')
        self.preprocess = 'none'
        self.eval = False
        
        # Ensure model file exists with correct name
        expected_model_file = os.path.join(self.checkpoints_dir, f'{self.epoch}_net_G.pth')
        if not os.path.exists(expected_model_file):
            # Copy/rename the model file to expected location
            os.makedirs(self.checkpoints_dir, exist_ok=True)
            if os.path.exists(model_path):
                import shutil
                shutil.copy2(model_path, expected_model_file)
                print(f"Copied model from {model_path} to {expected_model_file}")

def generate_fingerprints(input_dir, output_dir=None, model_path="weights/pix2pix_model.pt"):
    """
    Generate fingerprint images from template images.
    
    Args:
        input_dir: Directory containing template images
        output_dir: Directory to save generated fingerprints (optional)
        model_path: Path to the trained model file
    """
    
    # Validate inputs
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    
    # Set default output directory
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(input_dir), 'generated_fingerprints')
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Model path: {model_path}")
    
    # Create options
    opt = SimpleOptions(input_dir, model_path)
    
    # Create dataset and model
    dataset = create_dataset(opt)
    model = create_model(opt)
    model.setup(opt)
    
    # Set model to evaluation mode
    model.eval()
    
    print(f"Processing {len(dataset)} images...")
    
    # Process images
    for i, data in enumerate(dataset):
        if i >= opt.num_test:
            break
            
        model.set_input(data)
        model.test()
        visuals = model.get_current_visuals()
        img_path = model.get_image_paths()
        
        if i % 50 == 0:
            print(f'Processing image {i+1}/{len(dataset)}: {img_path[0]}')
        
        # Save generated image
        if 'fake' in visuals:
            # Get the generated image
            fake_img = tensor2im(visuals['fake'])
            
            # Create output filename
            input_filename = os.path.basename(img_path[0])
            name_without_ext = os.path.splitext(input_filename)[0]
            output_filename = f"{name_without_ext}_generated.png"
            output_path = os.path.join(output_dir, output_filename)
            
            # Save the image
            plt.imsave(output_path, fake_img, cmap='gray')
    
    print(f"\nProcessing complete!")
    print(f"Generated images saved to: {output_dir}")

# =============================================================================
# CONFIGURATION - Edit these paths as needed
# =============================================================================
INPUT_DIR = "/path/to/your/template/images"      # Directory containing template images
OUTPUT_DIR = "/path/to/your/output/directory"    # Directory to save generated fingerprints  
MODEL_PATH = "weights/pix2pix_model.pt"          # Path to your trained model file
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description='Generate fingerprints from template images using trained Pix2Pix model')
    parser.add_argument('--input_dir', '-i', type=str, default=INPUT_DIR, help='Directory containing template images')
    parser.add_argument('--output_dir', '-o', type=str, default=OUTPUT_DIR, help='Directory to save generated fingerprints')
    parser.add_argument('--model_path', '-m', type=str, default=MODEL_PATH, 
                       help='Path to trained model file')
    
    args = parser.parse_args()
    
    # Use command line args or configured defaults
    input_dir = args.input_dir
    # If output_dir is still the placeholder, use None to trigger auto-generation
    output_dir = None if args.output_dir == "/path/to/your/output/directory" else args.output_dir
    model_path = args.model_path
    
    print(f"Using input directory: {input_dir}")
    print(f"Using model: {model_path}")
    
    try:
        generate_fingerprints(input_dir, output_dir, model_path)
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
