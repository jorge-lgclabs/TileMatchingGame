import copy
import os

from PIL import Image
import numpy as np
import tile_indexer
import json
import replicate
from dotenv import load_dotenv
import requests
from requests import HTTPError

load_dotenv()  # Loads variables from .env into the environment

