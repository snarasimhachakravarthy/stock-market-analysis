#!/bin/bash

echo "Starting the setup process for the Stock Market Analysis tool..."

# Check for Python 3
if ! command -v python3 &> /dev/null
then
    echo "Python 3 could not be found. Please install Python 3."
    exit 1
fi
echo "Python 3 found."

# Check for pip
if ! command -v pip3 &> /dev/null
then
    # Try python3 -m pip
    if ! python3 -m pip --version &> /dev/null
    then
        echo "pip3 could not be found. Please install pip for Python 3."
        exit 1
    else
      PIP_COMMAND="python3 -m pip"
    fi
else
    PIP_COMMAND="pip3"
fi
echo "pip found."

# Define virtual environment directory
VENV_DIR=".venv"

# Create virtual environment
if [ ! -d "$VENV_DIR" ]
then
    echo "Creating virtual environment in '$VENV_DIR'..."
    python3 -m venv $VENV_DIR
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Please check your Python 3 venv module."
        exit 1
    fi
else
    echo "Virtual environment '$VENV_DIR' already exists."
fi

# Activate virtual environment and install dependencies
echo "----------------------------------------------------------------------"
echo "To activate the virtual environment, run:"
echo "  source $VENV_DIR/bin/activate"
echo "----------------------------------------------------------------------"
echo "Once activated, installing dependencies from requirements.txt..."

# Attempt to install dependencies directly if source command is not available in this script's context.
# The user will need to activate it manually in their shell.
source $VENV_DIR/bin/activate && $PIP_COMMAND install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Failed to install dependencies. "
    echo "Please activate the virtual environment manually by running: source $VENV_DIR/bin/activate"
    echo "Then, run: $PIP_COMMAND install -r requirements.txt"
    exit 1
fi

echo "Dependencies installed successfully."
echo ""
echo "Setup complete!"
echo "To generate a report, ensure your virtual environment is activated:"
echo "  source $VENV_DIR/bin/activate"
echo "Then run the report generator:"
echo "  python report_generator.py"
echo "----------------------------------------------------------------------"
