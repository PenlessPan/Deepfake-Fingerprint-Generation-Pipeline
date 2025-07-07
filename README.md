# Deepfake Fingerprint Generation Pipeline

[![Paper](https://img.shields.io/badge/Paper-WDC%202025-blue)](https://dl.acm.org/doi/10.1145/3709022.3736542)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> **⚠️ Ethical Use Notice**: This research tool is intended for academic research, security evaluation, and defense development only. Users are responsible for ensuring ethical and legal compliance in their jurisdiction.

## Overview

This repository contains the complete pipeline for generating synthetic fingerprint images from minutiae templates, as presented in our WDC '25 paper **["The Threat of Deepfake Fingerprints"](https://dl.acm.org/doi/10.1145/3709022.3736542)**. Our work demonstrates the first end-to-end validation of fingerprint template-to-physical-spoof attacks, including successful evasion of commercial fingerprint scanners.

### Key Features

- **Complete preprocessing pipeline** for fingerprint quality assessment, enhancement, and minutiae extraction
- **Pix2Pix-based generator** for converting minutiae templates to realistic fingerprint images  
- **End-to-end evaluation** showing 75% success rate against commercial scanners
- **Low-cost implementation** (~$440 setup cost, $0.07 per replica)

### Repository Structure

```
├── preprocessing/              # Fingerprint preprocessing pipeline
│   ├── external_tools/        # NIST NFIQ and NBIS binaries
│   ├── examples/              # Usage examples
│   └── ...                    # Core preprocessing modules
├── pytorch-CycleGAN-and-pix2pix/  # Modified Pix2Pix implementation
├── generate_fingerprints.py   # Simple generation script
├── requirements.txt           # Python dependencies
└── weights/                   # Directory for trained models (create this)
```

## Installation

```bash
git clone https://github.com/your-repo/Deepfake-Fingerprint-Generation-Pipeline
cd Deepfake-Fingerprint-Generation-Pipeline
pip install -r requirements.txt
```

### External Tools Setup

The pipeline requires NIST tools for fingerprint processing. Pre-compiled binaries for Rocky Linux 9.5 are included:

```bash
cd preprocessing/external_tools
chmod +x nfiq mindtct
```

**For other platforms**: Try the provided executables first. If they don't work on your system, download and compile the tools from NIST:
- **NFIQ**: https://www.nist.gov/services-resources/software/nfiq  
- **NBIS**: https://www.nist.gov/services-resources/software/nist-biometric-image-software-nbis

Place the executables in `preprocessing/external_tools/` and update paths in `preprocessing/config.py` if needed.

## Usage

### 1. Data Preprocessing

Convert raw fingerprint images to training-ready templates. Input should be a directory containing fingerprint images.

#### Complete Pipeline

```python
from preprocessing import PreprocessingPipeline

# Full pipeline: raw images → templates
pipeline = PreprocessingPipeline()
stats = pipeline.run_full_pipeline(
    input_dir="raw_fingerprints/",
    output_dir="processed_data/",
    filter_quality=True,  # Apply NFIQ filtering
    enhance=True,         # Apply fingerprint enhancement
    template_size=(256, 256)
)

print(f"Success rate: {stats['overall']['overall_success_rate']:.2%}")
```

#### Step-by-Step Processing

```python
# Individual steps for more control
pipeline = PreprocessingPipeline()

# Step 1: Quality filtering and preprocessing
pipeline.run_preprocessing_only(
    input_dir="raw_fingerprints/", 
    output_dir="processed_data/processed/",
    filter_quality=True,
    enhance=True
)

# Step 2: Extract minutiae from processed images
pipeline.run_minutiae_extraction_only(
    input_dir="processed_data/processed/", 
    output_dir="processed_data/"
)

# Step 3: Create template images from minutiae
pipeline.run_template_creation_only(
    minutiae_dir="processed_data/minutiae_txt/", 
    output_dir="processed_data/templates/",
    template_size=(256, 256)
)
```

### 2. Training Your Own Model

#### Prepare Training Data

```bash
# Organize your data structure
mkdir -p training_data/{A,B}/{train,test}

# A: Template images, B: Corresponding fingerprint images  
cp processed_data/templates/* training_data/A/train/
cp processed_data/processed/* training_data/B/train/

# Combine A and B into paired training format
cd pytorch-CycleGAN-and-pix2pix
python datasets/combine_A_and_B.py \
    --fold_A ../training_data/A \
    --fold_B ../training_data/B \
    --fold_AB ../training_data/combined
```

#### Train the Model

```bash
python train.py \
    --dataroot ../training_data/combined \
    --name fingerprint_pix2pix \
    --model pix2pix \
    --output_nc 1 \
    --batch_size 128 \
    --n_epochs 150 \
    --n_epochs_decay 150 \
    --load_size 256 \
    --preprocess none
```

#### Extract Trained Weights

```bash
# Copy the trained model to weights directory
mkdir -p ../weights
cp checkpoints/fingerprint_pix2pix/latest_net_G.pth ../weights/pix2pix_model.pth
```

*Note: Check the training web page generated during training to see which epoch produces the best results and use that specific model if needed.*

### 3. Generate Fingerprints

#### Using Pre-trained Models

For pre-trained model weights, contact yanivhac@post.bgu.ac.il with a clear explanation of your research purpose and institutional affiliation to ensure responsible use, or train your own model following the steps above.

Place your trained model in the weights directory:
```bash
mkdir -p weights
# Copy your model to weights/pix2pix_model.pth
```

#### Simple Generation Script

```bash
python generate_fingerprints.py \
    --input_dir path/to/template/images \
    --output_dir path/to/generated/fingerprints \
    --model_path weights/pix2pix_model.pth
```

#### Programmatic Usage

```python
from generate_fingerprints import generate_fingerprints

generate_fingerprints(
    input_dir="path/to/templates",
    output_dir="path/to/output", 
    model_path="weights/pix2pix_model.pth"
)
```

### 4. Creating Physical Replicas

For creating 3D molds and physical fingerprint replicas, use our separate tool:
- **Mold Generation Tool**: https://github.com/okashaluai/Fingerprint-Biometric-Research-Tool

This tool converts 2D fingerprint images into 3D printable molds for silicone casting.

## Configuration Options

Key configuration parameters in `preprocessing/config.py`:

```python
class Config:
    # Quality filtering
    NFIQ_THRESHOLD = 3          # Lower = stricter quality
    
    # Template rendering  
    TEMPLATE_SIZE = (256, 256)  # Output template size
    ORIENTATION_LINE_LENGTH = 15 # Minutiae orientation lines
    
    # Processing
    TARGET_ASPECT_RATIO = 1.0   # 1:1 aspect ratio
    CROPPING_MARGIN = 75        # Cropping margin pixels
```

## Troubleshooting

### Common Issues

1. **External tools not found**
   ```bash
   chmod +x preprocessing/external_tools/nfiq
   chmod +x preprocessing/external_tools/mindtct
   ```

2. **Low-quality template generation**
   - Adjust `NFIQ_THRESHOLD` in config
   - Check input image quality
   - Verify minutiae extraction parameters

3. **Poor generation quality**
   - Increase training epochs
   - Adjust batch size
   - Check template-fingerprint pair alignment

4. **Memory issues during training**
   - Reduce batch size
   - Use smaller image sizes
   - Enable gradient checkpointing

## Research and Citation

If you use this code in your research, please cite our paper:

```bibtex
@inproceedings{hacmon2025threat,
  title={The Threat of Deepfake Fingerprints},
  author={Hacmon, Yaniv and Gorelik, Keren and Mirsky, Yisroel},
  booktitle={The 4th Workshop on security implications of Deepfakes and Cheapfakes (WDC '25)},
  year={2025},
  publisher={ACM},
  doi={10.1145/3709022.3736542}
}
```

## Acknowledgments

- **External Libraries**: Built on [pytorch-CycleGAN-and-pix2pix](https://github.com/junyanz/pytorch-CycleGAN-and-pix2pix) by Jun-Yan Zhu et al.
- **NIST Tools**: NFIQ and NBIS for fingerprint processing

Special thanks to Yazan Abbas and Luai Okasha for their contributions to the fingerprint research tools.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Ethical Considerations

This research is intended to:
- **Advance biometric security research**
- **Highlight vulnerabilities in current systems**  
- **Enable development of better defenses**

**Responsible Use Guidelines**:
- Use only for legitimate security research
- Obtain proper permissions before testing on systems
- Follow local laws and regulations
- Consider privacy implications
- Report vulnerabilities responsibly

---

**Disclaimer**: This tool is for research and educational purposes only. Users are responsible for ensuring compliance with applicable laws and ethical guidelines.

Yaniv Hacmon - yanivhac@post.bgu.ac.il