import os
import boto3
from dotenv import load_dotenv
from app.components.s3_component import S3Component

# 1. Load credentials from your .env file
load_dotenv()

def verify_s3_connection():
    bucket_name = "file-storage-00414"
    region = "eu-central-1"
    
    print(f"--- S3 Verification: {bucket_name} ---")
    
    # Check if env variables are loaded
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    if not access_key:
        print("Error: AWS_ACCESS_KEY_ID not found in .env file.")
        return

    try:
        # Initialize your project's component
        s3c = S3Component(bucket_name, region_name=region)
        
        # Test 1: List Buckets (Basic connectivity test)
        response = s3c.s3.list_buckets()
        bucket_names = [b['Name'] for b in response['Buckets']]
        
        if bucket_name in bucket_names:
            print(f"✅ Success: Bucket '{bucket_name}' is accessible.")
        else:
            print(f"⚠️ Warning: Connected to AWS, but '{bucket_name}' not found in your account.")
            print(f"Available buckets: {bucket_names}")
            
        # Test 2: Upload a tiny test file
        test_file = "connection_test.txt"
        with open(test_file, "w") as f:
            f.write("S3 MacBook Verification Success")
            
        s3_key = "tests/connection_test.txt"
        if s3c.upload_file(test_file, s3_key):
            print(f"✅ Success: Test file uploaded to '{s3_key}'.")
            # Cleanup
            os.remove(test_file)
        else:
            print("❌ Error: Upload failed. Check your IAM user permissions (AmazonS3FullAccess).")

    except Exception as e:
        print(f"❌ Fatal Error during verification: {e}")

if __name__ == "__main__":
    verify_s3_connection()