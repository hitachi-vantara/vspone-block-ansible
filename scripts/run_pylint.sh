#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Navigate to the parent directory
cd "$SCRIPT_DIR/.."

# Run pylint on all Python files in the parent directory and its subdirectories
find . -name "*.py" -print0 | xargs -0 pylint > pylint_output.txt
