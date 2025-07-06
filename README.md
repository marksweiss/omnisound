Installation
----

This project now uses [uv](https://docs.astral.sh/uv/) for fast, modern Python package management.

#### Prerequisites

First, manually install binary dependencies on your platform:
- Install [SuperCollider](https://supercollider.github.io/download)
- Install [Csound](https://csound.com/download.html)

#### Quick Installation

```bash
git clone https://github.com/marksweiss/omnisound.git
cd omnisound
./install.sh
```

The install script will:
1. Install uv if not already present
2. Set up the project environment and install dependencies
3. Create necessary symlinks for external dependencies

#### Manual Installation

If you prefer to install manually:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/marksweiss/omnisound.git
cd omnisound
git submodule update --init --recursive

# Install dependencies
uv sync

# Create mingus symlink
ln -s "$(pwd)/ext/python_mingus/mingus/" "$(pwd)/mingus"
```

#### Usage

Run Python scripts with uv:
```bash
uv run python your_script.py
```

Run tests:
```bash
uv run pytest
# or use the convenience script
./run_test
```

Get a shell in the project environment:
```bash
uv shell

# Install for development
uv sync --dev
```

```bash
# Add new dependencies
uv add package-name
```


#### Optional Dependencies

Some dependencies like `python-rtmidi` may require additional system libraries. Install them optionally:
```bash
uv sync --extra rtmidi
```
