#!/bin/bash

# Setup script for external tools (NFIQ2 and NBIS)
# This script helps download and set up the required external tools

set -e  # Exit on any error

echo "=== External Tools Setup Script ==="
echo "This script will help you set up NFIQ and NBIS tools."
echo "Note: Pre-compiled binaries for Rocky Linux 9.5 are included."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
TOOLS_DIR="$SCRIPT_DIR"

# Function to check if a tool exists
check_tool() {
    local tool_name="$1"
    local tool_path="$2"
    
    if [ -f "$tool_path" ] && [ -x "$tool_path" ]; then
        echo "✓ $tool_name found and executable at: $tool_path"
        return 0
    else
        echo "✗ $tool_name not found or not executable at: $tool_path"
        return 1
    fi
}

# Function to download and extract NFIQ (example for Linux)
setup_nfiq() {
    echo ""
    echo "=== Setting up NFIQ ==="
    
    # Check if already exists
    if check_tool "NFIQ" "$TOOLS_DIR/nfiq"; then
        return 0
    fi
    
    echo "NFIQ not found. Please follow these steps:"
    echo "1. Visit: https://www.nist.gov/services-resources/software/nfiq"
    echo "2. Download the appropriate binary for your system"
    echo "3. Extract the 'nfiq' executable to: $TOOLS_DIR/"
    echo "4. Run: chmod +x $TOOLS_DIR/nfiq"
    echo ""
    echo "Note: If you're using Rocky Linux 9.5, the executable should already be provided."
    echo ""
    
    read -p "Press Enter when you have completed these steps..."
    
    # Check again
    if check_tool "NFIQ" "$TOOLS_DIR/nfiq"; then
        echo "✓ NFIQ setup complete!"
    else
        echo "✗ NFIQ still not found. Please check the installation."
        return 1
    fi
}

# Function to download and extract NBIS
setup_nbis() {
    echo ""
    echo "=== Setting up NBIS (Mindtct) ==="
    
    # Check if already exists
    if check_tool "Mindtct" "$TOOLS_DIR/mindtct"; then
        return 0
    fi
    
    echo "NBIS Mindtct not found. Please follow these steps:"
    echo "1. Visit: https://www.nist.gov/services-resources/software/nist-biometric-image-software-nbis"
    echo "2. Download the NBIS package"
    echo "3. Extract the 'mindtct' executable to: $TOOLS_DIR/"
    echo "4. Run: chmod +x $TOOLS_DIR/mindtct"
    echo ""
    echo "Note: If you're using Rocky Linux 9.5, the executable should already be provided."
    echo ""
    
    read -p "Press Enter when you have completed these steps..."
    
    # Check again
    if check_tool "Mindtct" "$TOOLS_DIR/mindtct"; then
        echo "✓ NBIS setup complete!"
    else
        echo "✗ Mindtct still not found. Please check the installation."
        return 1
    fi
}

# Function to test the tools
test_tools() {
    echo ""
    echo "=== Testing Tools ==="
    
    # Test NFIQ
    if check_tool "NFIQ" "$TOOLS_DIR/nfiq"; then
        echo "Testing NFIQ..."
        if "$TOOLS_DIR/nfiq" --help > /dev/null 2>&1; then
            echo "✓ NFIQ is working correctly"
        else
            echo "⚠ NFIQ executable found but may have issues"
        fi
    fi
    
    # Test Mindtct
    if check_tool "Mindtct" "$TOOLS_DIR/mindtct"; then
        echo "Testing Mindtct..."
        if "$TOOLS_DIR/mindtct" > /dev/null 2>&1; then
            echo "✓ Mindtct is working correctly"
        else
            echo "⚠ Mindtct executable found but may have issues"
        fi
    fi
}

# Function to create a test script
create_test_script() {
    echo ""
    echo "=== Creating Test Script ==="
    
    cat > "$TOOLS_DIR/test_tools.sh" << 'EOF'
#!/bin/bash

# Test script for external tools
echo "=== Testing External Tools ==="

TOOLS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Test with a sample image (you need to provide one)
TEST_IMAGE="$1"

if [ -z "$TEST_IMAGE" ]; then
    echo "Usage: $0 <test_fingerprint_image>"
    echo "Example: $0 sample_fingerprint.png"
    exit 1
fi

if [ ! -f "$TEST_IMAGE" ]; then
    echo "Error: Test image not found: $TEST_IMAGE"
    exit 1
fi

echo "Testing with image: $TEST_IMAGE"
echo ""

# Test NFIQ
if [ -x "$TOOLS_DIR/nfiq" ]; then
    echo "Testing NFIQ..."
    "$TOOLS_DIR/nfiq" "$TEST_IMAGE"
    echo ""
else
    echo "NFIQ not found or not executable"
fi

# Test Mindtct
if [ -x "$TOOLS_DIR/mindtct" ]; then
    echo "Testing Mindtct..."
    "$TOOLS_DIR/mindtct" "$TEST_IMAGE" test_output
    if [ -f "test_output.min" ]; then
        echo "✓ Mindtct created minutiae file: test_output.min"
        # Clean up test files
        rm -f test_output.*
    else
        echo "✗ Mindtct failed to create minutiae file"
    fi
    echo ""
else
    echo "Mindtct not found or not executable"
fi

echo "Testing complete!"
EOF

    chmod +x "$TOOLS_DIR/test_tools.sh"
    echo "✓ Test script created: $TOOLS_DIR/test_tools.sh"
    echo "Usage: ./test_tools.sh <fingerprint_image>"
}

# Main setup process
main() {
    echo "Starting setup in directory: $TOOLS_DIR"
    echo ""
    
    # Check current status
    echo "=== Current Status ==="
    check_tool "NFIQ" "$TOOLS_DIR/nfiq" || true
    check_tool "Mindtct" "$TOOLS_DIR/mindtct" || true
    echo ""
    
    # Setup tools
    setup_nfiq
    setup_nbis
    
    # Test tools
    test_tools
    
    # Create test script
    create_test_script
    
    echo ""
    echo "=== Setup Complete ==="
    echo "Both tools should now be ready for use."
    echo ""
    echo "Next steps:"
    echo "1. Test the tools with a sample fingerprint image:"
    echo "   ./test_tools.sh sample_fingerprint.png"
    echo ""
    echo "2. Run the preprocessing pipeline:"
    echo "   cd .. && python examples/example_usage.py"
    echo ""
}

# Run main function
main "$@"
