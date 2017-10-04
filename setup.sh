# Change to root directory
cd ~

# Get and instal pip
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py --user

# Add to path
echo "PATH=\$PATH:~/.local/bin" >> ~/.bash_profile
source ~/.bash_profile

# Upgrade numpy and scipy
pip install --user numpy --upgrade
pip install --user scipy --upgrade

# Install OpenMDAO
pip install --user openmdao
