import boto3
import os
import json
from rich import print


class S3Manager:
    """A class to manage S3 operations including listing, uploading, and reading files."""
    
    def __init__(self, bucket_name="redis-ai-research", prefix="srijithr/datasets/"):
        """
        Initialize the S3Manager with AWS credentials and default bucket/prefix.
        
        Args:
            bucket_name (str): The S3 bucket name to use
            prefix (str): The prefix/path within the bucket
        """
        self.bucket_name = bucket_name
        self.prefix = prefix
        
        # Get AWS credentials from environment variables
        self.aws_config = {
            "access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "region": os.getenv("AWS_REGION"),
        }
        
        print(f"AWS Config: {self.aws_config}")
        
        # Create boto3 session and S3 client
        self.session = boto3.Session(
            aws_access_key_id=self.aws_config["access_key_id"],
            aws_secret_access_key=self.aws_config["secret_access_key"],
            region_name=self.aws_config["region"],
        )
        self.s3 = self.session.client("s3")
    
    def list_objects_in_folder(self, prefix=None):
        """
        List all objects in a specific S3 folder.
        
        Args:
            prefix (str, optional): The prefix to list. If None, uses the instance prefix.
        """
        if prefix is None:
            prefix = self.prefix
            
        response = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)

        if "Contents" in response:
            print(f"Files in '{self.bucket_name}/{prefix}':")
            for obj in response['Contents']:
                print(f"  - {obj['Key']} ({obj['Size']} bytes, {obj['LastModified']})")
        else:
            print(f"No files found in '{self.bucket_name}/{prefix}'")

    def upload_file_to_s3(self, s3_key, file_path, bucket_name=None):
        """
        Upload a local file to S3 bucket.
        
        Args:
            s3_key (str): The S3 key (path) where the file should be stored
            file_path (str): The local file path to upload
            bucket_name (str, optional): The bucket name. If None, uses the instance bucket.
            
        Returns:
            bool: True if upload was successful, False otherwise
        """
        if bucket_name is None:
            bucket_name = self.bucket_name
            
        try:
            self.s3.upload_file(file_path, bucket_name, s3_key)
            print(f"✅ Successfully uploaded {file_path} to s3://{bucket_name}/{s3_key}")
            return True
        except Exception as e:
            print(f"❌ Error uploading file to S3: {str(e)}")
            return False

    def read_json_from_s3(self, s3_key, bucket_name=None):
        """
        Read a JSON object directly from S3 without saving to a file.
        
        Args:
            s3_key (str): The S3 key (path) of the JSON file to read
            bucket_name (str, optional): The bucket name. If None, uses the instance bucket.
            
        Returns:
            dict or None: The JSON object if successful, None if there was an error
        """
        if bucket_name is None:
            bucket_name = self.bucket_name
            
        try:
            response = self.s3.get_object(Bucket=bucket_name, Key=s3_key)
            content = response['Body'].read().decode('utf-8')
            json_obj = json.loads(content)
            print(f"✅ Successfully read JSON from s3://{bucket_name}/{s3_key}")
            return json_obj
        except Exception as e:
            print(f"❌ Error reading JSON from S3: {str(e)}")
            return None

# Example usage
import argparse
import sys
import json

def main():
    parser = argparse.ArgumentParser(
        description="S3Manager CLI: Interact with S3 to list files, upload, or download JSON objects."
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Subparser for list
    parser_list = subparsers.add_parser('list', help='List files in the S3 folder')

    # Subparser for upload
    parser_upload = subparsers.add_parser('upload', help='Upload a file to S3')
    parser_upload.add_argument('local_path', type=str, help='Local file path to upload')
    parser_upload.add_argument('--s3-key', type=str, help='S3 key (remote path)', required=False)

    # Subparser for download/read
    parser_read = subparsers.add_parser('read', help='Read a JSON object from S3')
    parser_read.add_argument('--s3-key', type=str, help='S3 key (remote path)', required=False)

    args = parser.parse_args()
    s3_manager = S3Manager()

    if args.command == "list":
        print("=== Listing existing files ===")
        s3_manager.list_objects_in_folder()

    elif args.command == "upload":
        file_name = os.path.basename(args.local_path)
        print(f"File name: {file_name}")
        s3_key = args.s3_key or f"{s3_manager.prefix}{file_name}"
        local_path = args.local_path
        print(f"Uploading '{local_path}' to S3 as '{s3_key}'...")
        result = s3_manager.upload_file_to_s3(s3_key, local_path)
        if not result:
            sys.exit(1)
            
    elif args.command == "read":
        s3_key = args.s3_key or f"{s3_manager.prefix}assembled_data.json"
        print(f"Reading JSON from S3 key: {s3_key} ...")
        json_obj = s3_manager.read_json_from_s3(s3_key)
        if json_obj is not None:
            print(json.dumps(json_obj, indent=2))
            name = s3_key.split("/")[-1]
            with open(f"data/downloaded_from_s3/{name}", "w") as f:
                json.dump(json_obj, f, indent=2)
        else:
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()