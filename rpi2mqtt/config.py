import yaml
from dotmap import DotMap
import os


with open(os.path.join(os.path.dirname(__file__), 'config.yaml'), 'r') as f:
    config = DotMap(yaml.load(f))
