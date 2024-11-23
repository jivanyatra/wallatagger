import re
from datetime import datetime
# noinspection PyPackageRequirements
from dotenv import find_dotenv, load_dotenv, set_key
import os
import requests
import sys


class Tagger:

    def __init__(self,
                 load_env=True,
                 base_url="http://localhost",
                 grant_type="password",
                 username="wallabag",
                 password="walalbag",
                 client_id=None,
                 client_secret=None
                 ):

        self.creds = dict()

        if load_env:
            dotenv_file = find_dotenv()
            load_dotenv(dotenv_file)
            self.creds["grant_type"] = os.getenv("GRANT_TYPE")
            self.creds["client_id"] = os.getenv("CLIENT_ID")
            self.creds["client_secret"] = os.getenv("CLIENT_SECRET")
            self.creds["username"] = os.getenv("USERNAME")
            self.creds["password"] = os.getenv("PASSWORD")
            self.base_url = os.getenv("BASE_URL")
        else:
            self.creds["grant_type"] = grant_type
            self.creds["client_id"] = client_id
            self.creds["client_secret"] = client_secret
            self.creds["username"] = username
            self.creds["password"] = password
            self.base_url = base_url
