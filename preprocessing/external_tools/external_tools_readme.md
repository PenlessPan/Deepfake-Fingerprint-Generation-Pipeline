# External Tools Setup

This preprocessing pipeline requires two external tools from NIST (National Institute of Standards and Technology):

1. **NFIQ** - Fingerprint Image Quality assessment
2. **NBIS (Mindtct)** - Minutiae detection and extraction

## Pre-compiled Binaries Included

**For Rocky Linux 9.5 (Blue Onyx) users**: The required executables (`nfiq` and `mindtct`) are already provided in this directory and should work out of the box on Rocky Linux 9.5 systems.

If you're using a different Linux distribution or operating system, please follow the installation instructions below.

## Installation Instructions (For Other Systems)

### Option 1: Download Pre-compiled Binaries (Recommended)

#### NFIQ
1. Visit: https://www.nist.gov/services-resources/software/nfiq
2. Download the appropriate binary for your system
3. Extract and place the `nfiq` executable in this directory (`external_tools/`)
4. Make sure the executable has proper permissions: `chmod +x nfiq`

#### NBIS (for Mindtct)
1. Visit: https://www.nist.gov/services-resources/software/nist-biometric-image-software-nbis
2. Download NBIS package
3. Extract and place the `mindtct` executable in this directory (`external_tools/`)
4. Make sure the executable has proper permissions: `chmod +x mindtct`

### Option 2: Compile from Source

#### NFIQ
```bash
# Download NFIQ source from NIST website
# Follow the compilation instructions provided by NIST
# Copy the nfiq binary to external_tools/
```

#### NBIS
```bash
# Download NBIS source from NIST website
tar -xzf nbis_source.tar.gz
cd nbis
./setup.sh
make config
make it
# Copy mindtct binary to external_tools/
```

## Directory Structure

After setup, your `external_tools/` directory should look like:

```
external_tools/
├── README.md (this file)
├── setup_tools.sh
├── nfiq          # NFIQ2 executable
└── mindtct       # NBIS mindtct executable
```

## Configuration

Update the paths in `config.py` if you place the tools elsewhere:

```python
class Config:
    NFIQ_PATH = "./external_tools/nfiq"
    MINDTCT_PATH = "./external_tools/mindtct"
```

## Testing

To verify the tools are working correctly:

```bash
# Test NFIQ
./nfiq path/to/fingerprint_image.png

# Test Mindtct  
./mindtct path/to/fingerprint_image.png output_prefix
```

## Troubleshooting

### Common Issues

1. **Permission denied**: Make sure executables have execute permissions
   ```bash
   chmod +x nfiq mindtct
   ```

2. **Library dependencies**: Some systems may require additional libraries
   - On Ubuntu/Debian: `sudo apt-get install libjpeg-dev libpng-dev`
   - On CentOS/RHEL: `sudo yum install libjpeg-devel libpng-devel`

3. **Path issues**: Verify the executable paths in your config match the actual locations

### Platform-specific Notes

#### Windows
- Use `.exe` extensions for executables
- Consider using WSL (Windows Subsystem for Linux) for easier setup

#### macOS  
- May need to install additional dependencies via Homebrew
- Check security settings if macOS blocks unsigned executables

#### Linux
- Most straightforward platform for these tools
- Ensure you have development libraries installed

## License and Terms

Both NFIQ and NBIS are developed by NIST and are public domain software. Please review their respective license terms and usage restrictions on the NIST website.

## Support

For issues with the external tools themselves, please refer to:
- NFIQ: Contact NIST directly through their website
- NBIS: Contact NIST directly through their website

For issues with the preprocessing pipeline integration, please check the main repository issues.
