import boto3
from botocore.config import Config
from typing import Dict, Any
from . import S3SecureService

class CloudflareR2Service(S3SecureService):
    def __init__(self, bucket_name: str, account_id: str, admin_api_token: str, r2_access_key_id: str, jurisdiction: str = ""):
        """
        CloudflareR2Service using presigned URLs.
        :param bucket_name: R2 bucket name
        :param account_id: Cloudflare account ID
        :param admin_api_token: R2 secret access key
        :param r2_access_key_id: R2 access key ID
        :param jurisdiction: Optional jurisdiction code (e.g., 'eu' for EU buckets)
        """
        self.bucket = bucket_name
        self.account_id = account_id
        self.region = "auto"
        
        if jurisdiction:
            endpoint_url = f"https://{account_id}.{jurisdiction}.r2.cloudflarestorage.com"
        else:
            endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"
        
        config = Config(
            signature_version='s3v4',
            region_name=self.region
        )
        
        self.s3_client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=r2_access_key_id,
            aws_secret_access_key=admin_api_token,
            config=config
        )

    def get_upload_url(self, user_id: str, video_id: str) -> Dict[str, Any]:
        """
        Generates a presigned PUT URL for uploading a video to R2.
        Client can upload directly to this URL without credentials.
        """
        key = f"video/{user_id}/{video_id}.mp4"
        
        presigned_url = self.s3_client.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': self.bucket,
                'Key': key,
                'ContentType': 'video/mp4'
            },
            ExpiresIn=3600
        )
        
        return {
            "upload_url": presigned_url,
            "key": key,
            "method": "PUT"
        }

    def get_read_url(self, user_id: str, video_id: str) -> Dict[str, Any]:
        """
        Generates a presigned GET URL for reading/downloading a video from R2.
        """
        key = f"video/{user_id}/{video_id}.mp4"
        
        presigned_url = self.s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self.bucket,
                'Key': key
            },
            ExpiresIn=3600
        )
        
        return {
            "download_url": presigned_url,
            "key": key
        }
