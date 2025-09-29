from io import BytesIO
from typing import Optional, Union
from pathlib import Path
import os
from dotenv import load_dotenv 


from botocore.client import Config
from botocore.exceptions import EndpointConnectionError, ClientError
import boto3

load_dotenv()

class S3BucketService:
    def __init__(
        self,
        bucket_name: str,
        endpoint: str,
        access_key: str,
        secret_key: str,
    ) -> None:
        self.bucket_name = bucket_name
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key

    def create_s3_client(self) -> boto3.client:
        try:
            client = boto3.client(
                "s3",
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=Config(signature_version="s3v4"),
            )
            return client
        except EndpointConnectionError as e:
            print(f"Could not connect to S3 endpoint: {e}")
            return False
        except ClientError as e:
            print(f"S3 Client error: {e}")
        return False
        
    
    def upload_file_object(self, prefix: str, source_file_name: str, content: Union[str, bytes]) -> None:
        try:
            client = self.create_s3_client()
        except Exception as e:
            return f"Error in s3 client: {e}"
        
        destination_path = str(Path(prefix, source_file_name))

        if isinstance(content, bytes):
            buffer = BytesIO(content)
        else:
            buffer = BytesIO(content.encode("utf-8"))
        client.upload_fileobj(buffer, self.bucket_name, destination_path)



def s3_bucket_service_factory() -> S3BucketService:
    
    return S3BucketService(
        os.getenv("bucket_name"),
        os.getenv("endpoint"),
        os.getenv("access_key"),
        os.getenv("secret_key"),
    )