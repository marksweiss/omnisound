git clone https://github.com/marksweiss/omnisound.git
git submodule update --init --recursive
env_dir=$(cwd)
python3 -m venv --prompt=omnisound "$env_dir"
source bin/activate
pip3 install --upgrade pip
pip3 install -r requirement.txt
