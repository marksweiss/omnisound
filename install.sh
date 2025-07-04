#!/usr/bin/env bash
set -e

echo "Installing omnisound with uv..."

# Update git submodules
git submodule update --init --recursive

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Sync the project dependencies
echo "Syncing dependencies..."
uv sync

# Create symlink for mingus (maintaining compatibility with existing setup)
d=$(pwd)
if [ ! -L "$d/mingus" ]; then
    echo "Creating mingus symlink..."
    ln -s "$d/ext/python_mingus/mingus/" "$d/mingus"
fi

echo "Installation complete!"
echo ""
echo "To activate the environment and run commands:"
echo "  uv run python <script.py>"
echo "  uv run pytest"
echo ""
echo "Or to get a shell in the environment:"
echo "  uv shell"
