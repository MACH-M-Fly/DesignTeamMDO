# Change to root directory
cd ~

# Get and instal pip
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py --user

# Add to path
echo $'\nPATH=$PATH:~/.local/bin' >> ~/.bash_profile
echo $'\nmodule load ffmpeg' >> ~/.bash_profile
source ~/.bash_profile

# Upgrade numpy, scipy, and matplotlib
pip install --user numpy --upgrade
pip install --user scipy --upgrade
pip install --user sympy
pip install --user sympy --upgrade
pip install --user pykrige
# pip install --user matplotlib --upgrade

# Install OpenMDAO
pip install --user openmdao==1.7.3

# Copy ffmpeg to the users local directory
#cp ./Resources/ffmpeg ~/.local/bin/

# Install sphinx and related theme for documentation
pip install --user sphinx
pip install --user sphinx_bootstrap_theme
