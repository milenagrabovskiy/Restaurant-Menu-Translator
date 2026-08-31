"""creating the boto3 client that will connect to aws with our credentials and return running sessions"""

import boto3
from functools import lru_cache
from menu_translator.config import AWS_PROFILE, AWS_REGION


@lru_cache(maxsize=1)  # we only want to cache one thing that is returned from this fxn
def get_session() -> boto3.Session:
    """one shared session for the app"""

    return boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)


# every time we run this fxn, we save it to cache and it grabs from cache
@lru_cache(maxsize=None)
def get_client(service_name: str):
    """return a boto3 client"""

    return get_session().client(service_name)