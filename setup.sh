#!/bin/bash

# AI/ML Fundamentals - Quick Setup Script
# Run this to set up your learning environment

echo "========================================="
echo "AI/ML Fundamentals - Environment Setup"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found: Python $PYTHON_VERSION"

# Check if version is 3.8+
REQUIRED_VERSION="3.8"
if python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)"; then
    echo "✅ Python version is compatible"
else
    echo "❌ Python 3.8+ required. Please upgrade Python."
    exit 1
fi

echo ""
echo "Installing dependencies..."
echo "This might take a few minutes..."
echo ""

# Install dependencies
pip3 install -q torch torchvision numpy

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. cd week1-tensors"
echo "2. python3 day1_tensor_basics.py"
echo ""
echo "Happy learning!"
