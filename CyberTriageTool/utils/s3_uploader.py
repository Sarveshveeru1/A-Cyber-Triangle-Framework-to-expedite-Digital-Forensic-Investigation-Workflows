# utils/s3_uploader.py

import boto3
import os
from dotenv import load_dotenv

load_dotenv()  # Load AWS credentials from .env

def upload_to_s3(file_path, s3_key):
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_DEFAULT_REGION")
        )

        bucket_name = os.getenv("S3_BUCKET_NAME")

        s3.upload_file(file_path, bucket_name, s3_key)
        print(f"✅ Uploaded '{file_path}' to S3 as '{s3_key}' in bucket '{bucket_name}'")
    except Exception as e:
        print(f"❌ Failed to upload to S3: {str(e)}")
