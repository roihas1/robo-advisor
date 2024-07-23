# Add the root directory of your project to the sys.path list
import sys
import os

from service.config import settings

project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.append(project_root)
from impl.user import User
from util import data_management
if __name__ == '__main__':
    data_management.evaluate_all_models()
