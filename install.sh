git clone https://github.com/marksweiss/omnisound.git
git submodule update --init --recursive
ENV_DIR=$(pwd)
python3 -m venv --prompt=omnisound "$ENV_DIR"
source bin/activate
pip3 install --upgrade pip
pip3 install -r requirements.txt
