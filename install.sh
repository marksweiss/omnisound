git clone https://github.com/marksweiss/omnisound.git
git submodule update --init --recursive
env_dir=$(cwd)
python3 -m venv --prompt=omnisound "$env_dir"
pip install --upgrade pip
source bin/activate
