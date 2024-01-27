# Helper function to read environment variables
import os
import logging
from decouple import config
from django.core.exceptions import ImproperlyConfigured

def get_env_variable(var_name, default=None, required=False):
    try:
        return config(var_name, default=default)
    except KeyError:
        if required:
            error_msg = f"Set the {var_name} environment variable"
            logging.error(error_msg)
            raise ImproperlyConfigured(error_msg)
        return default