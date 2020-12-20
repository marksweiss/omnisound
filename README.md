Installation
----

#### Manually install binary dependencies on your platform
install [supercollider](https://supercollider.github.io/download)
install [csound](https://csound.com/download.html)

```bash
git clone https://github.com/marksweiss/omnisound.git
cd omnisound
./install.sh
d=$(pwd)
ln -s "$d/ext/python_mingus/mingus/" "$d/mingus"
```