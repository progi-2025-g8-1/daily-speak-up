import boto3
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
        Generates a presigned POST URL for uploading a video.
        Client can upload directly to this URL without any credentials.
        """
        key = f"video/{user_id}/{video_id}.mp4"
        
        # Generate presigned POST for multipart upload support
        presigned_post = self.s3_client.generate_presigned_post(
            Bucket=self.bucket,
            Key=key,
            ExpiresIn=3600,  # 1 hour
            Conditions=[
                ["content-length-range", 0, 524288000],  # Max 500MB
            ]
        )
        
        return {
            "upload_url": presigned_post["url"],
            "fields": presigned_post["fields"],
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
