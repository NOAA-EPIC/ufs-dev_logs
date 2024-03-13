import sys
sys.path.append(   '../modules'   )
import config
from config import username, token
from init_setup import init_setup

# Instantiate module for inital setup.
# Requires Personal Access Token to read pulic repos.
data_wrapper = init_setup(username, token, 'ufs-wm', 'develop')
