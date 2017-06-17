# -*- coding: utf-8 -*-

import os
from urllib.parse import urlparse

url = urlparse(os.environ.get("DATABASE_URL"))
DATABASE_NAME = url.path[1:]
DATABASE_USER = url.username
DATABASE_PASSWORD = url.password
DATABASE_HOST = url.hostname
DATABASE_PORT = url.port
