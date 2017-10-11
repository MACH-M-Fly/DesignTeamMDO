# Change to root directory
cd ~

# Get and instal pip
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py --user

# Add to path
echo $'\nPATH=$PATH:~/.local/bin' >> ~/.bash_profile
source ~/.bash_profile

# Upgrade numpy, scipy, and matplotlib
pip install --user numpy --upgrade
pip install --user scipy --upgrade
# pip install --user matplotlib --upgrade 


# Install OpenMDAO
pip install --user openmdao
