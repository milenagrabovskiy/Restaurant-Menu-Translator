"""config for loading env file environment variables"""

import os

from dotenv import load_dotenv

# pulls env file to app context
load_dotenv(override=True)

# save .env vars in the app
# AWS_PROFILE=os.environ["AWS_PROFILE"]
# AWS_REGION=os.environ["AWS_REGION"]
AWS_PROFILE = os.getenv("AWS_PROFILE", "menu_translator")
# AWS_REGION=None
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
# AWS_BUCKET_NAME=os.environ["AWS_BUCKET_NAME"]
AWS_BUCKET_NAME = "restaurant-menu-translator-bucket"
# AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
# LAMBDA_FUNCTION_NAME=os.environ["SUPPORT_AI_LAMBDA_FUNCTION_NAME"]