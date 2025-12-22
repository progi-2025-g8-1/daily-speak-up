import boto3
from botocore.client import Config
from typing import Dict, Any

class S3SecureService:
    def __init__(self, bucket_name: str, role_arn: str, region: str = "eu-central-1"):
        """
        :param role_arn: The ARN of the IAM role that the backend assumes (must have s3:* on the bucket)
        """
        self.bucket = bucket_name
        self.role_arn = role_arn
        self.region = region
        self.s3_client = boto3.client("s3", region_name=region)

    def get_upload_url(self, user_id: str, video_id: str) -> Dict[str, Any]:
        """
        Generates a presigned PUT URL for uploading a video.
        Client can upload directly to this URL without any credentials.
        """
        key = f"video/{user_id}/{video_id}.mp4"
        
        # Generate presigned URL that works with direct PUT from browser
        presigned_url = self.s3_client.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': self.bucket,
                'Key': key
            },
            ExpiresIn=3600  # 1 hour
        )
        
        return {
            "upload_url": presigned_url,
            "key": key
        }

    def get_read_url(self, user_id: str, video_id: str) -> Dict[str, Any]:
        """
        Generates a presigned GET URL for reading/downloading a video.
        Client can access the video directly using this URL.
        """
        key = f"video/{user_id}/{video_id}.mp4"
        
        presigned_url = self.s3_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': self.bucket,
                'Key': key
            },
            ExpiresIn=3600  # 1 hour
        )
        
        return {
            "download_url": presigned_url,
            "key": key
        }

    def upload_file(self, file_path: str, s3_key: str) -> str:
        """
        Uploads a file directly from disk to S3.
        Returns the S3 key of the uploaded file.
        """
        try:
            with open(file_path, 'rb') as f:
                self.s3_client.upload_fileobj(f, self.bucket, s3_key)
            return s3_key
        except Exception as e:
            raise Exception(f"Failed to upload file to S3: {str(e)}")
