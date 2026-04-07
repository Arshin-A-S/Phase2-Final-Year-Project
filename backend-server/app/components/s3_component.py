# backend/components/s3_component.py
import boto3
import os
from botocore.exceptions import ClientError

class S3Component:
    def __init__(self, bucket_name, region_name=None):
        self.bucket = bucket_name
        session = boto3.session.Session()
        self.s3 = session.client('s3', region_name=region_name)

    def upload_file(self, local_path, s3_key):
        try:
            self.s3.upload_file(local_path, self.bucket, s3_key)
            return True
        except ClientError as e:
            print("S3 upload error:", e)
            return False

    def download_file(self, s3_key, local_path):
        try:
            self.s3.download_file(self.bucket, s3_key, local_path)
            return True
        except ClientError as e:
            print("S3 download error:", e)
            return False

    def delete_file(self, s3_key):
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError as e:
            print("S3 delete error:", e)
            return False
    
    def list_files(self):
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket)

            files = []
            for obj in response.get("Contents", []):
                files.append({
                    "name": obj["Key"],
                    "url": f"https://{self.bucket}.s3.ap-south-2.amazonaws.com/{obj['Key']}"
                })

            return files

        except ClientError as e:
            print("S3 list error:", e)
            return []
