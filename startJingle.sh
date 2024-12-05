#!/bin/bash

# Exit script on any error
set -e

# Define variables
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"
PYTHON_SCRIPT="jinglepi.py"

# Check if Python is installed
if ! command -v python3 &>/dev/null; then
    echo "Python3 is not installed. Please install it to proceed."
    exit 1
fi

# Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in '$VENV_DIR'..."
    python3 -m venv $VENV_DIR
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Upgrade pip in the virtual environment
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from '$REQUIREMENTS_FILE'..."
    pip install -r $REQUIREMENTS_FILE
else
    echo "No '$REQUIREMENTS_FILE' found. Skipping dependency installation."
fi

# Run the Python script
if [ -f "$PYTHON_SCRIPT" ]; then
    echo "Running Python script '$PYTHON_SCRIPT'..."
    python $PYTHON_SCRIPT
else
    echo "No Python script named '$PYTHON_SCRIPT' found."
fi

# Deactivate virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Script completed successfully."
