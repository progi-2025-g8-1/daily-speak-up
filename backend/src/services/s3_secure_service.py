import boto3
from botocore.client import Config
from typing import Dict, Any, List
from io import BytesIO

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

    def get_photo_upload_url(self, user_id: str, content_type: str = 'image/png') -> Dict[str, Any]:
        """
        Generates a presigned PUT URL for uploading a profile photo.
        Client can upload directly to this URL without credentials.
        
        :param user_id: The ID of the user
        :param content_type: The MIME type of the image (e.g., 'image/png', 'image/jpeg')
        :return: Dictionary with upload URL and key
        """
        # Determine file extension based on content type
        extension_map = {
            'image/png': 'png',
            'image/jpeg': 'jpg',
            'image/jpg': 'jpg'
        }
        extension = extension_map.get(content_type, 'png')
        key = f"photo/{user_id}.{extension}"
        
        presigned_url = self.s3_client.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': self.bucket,
                'Key': key,
                'ContentType': content_type
            },
            ExpiresIn=3600  # 1 hour
        )
        
        return {
            'upload_url': presigned_url,
            'key': key,
            'content_type': content_type
        }
    
    def get_photo_read_url(self, user_id: str) -> Dict[str, Any]:
        """
        Generates a presigned GET URL for reading/downloading a profile photo.
        Tries both PNG and JPG extensions.
        
        :param user_id: The ID of the user
        :return: Dictionary with download URL and key
        """
        # Try to find the photo with either extension
        for extension in ['png', 'jpg']:
            key = f"photo/{user_id}.{extension}"
            try:
                # Check if object exists
                self.s3_client.head_object(Bucket=self.bucket, Key=key)
                
                # Generate presigned URL
                presigned_url = self.s3_client.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={
                        'Bucket': self.bucket,
                        'Key': key
                    },
                    ExpiresIn=3600  # 1 hour
                )
                
                return {
                    'download_url': presigned_url,
                    'key': key
                }
            except:
                continue
        
        # No photo found
        return {
            'download_url': None,
            'key': None,
            'message': 'No profile photo found'
        }
    
    def upload_profile_photo(self, user_id: str, photo_data: bytes, content_type: str = 'image/png') -> Dict[str, Any]:
        """
        Uploads a profile photo for a user to S3.
        
        :param user_id: The ID of the user
        :param photo_data: The photo file data as bytes
        :param content_type: The MIME type of the image (e.g., 'image/png', 'image/jpeg')
        :return: Dictionary with the S3 key and upload status
        """
        # Determine file extension based on content type
        extension_map = {
            'image/png': 'png',
            'image/jpeg': 'jpg',
            'image/jpg': 'jpg'
        }
        extension = extension_map.get(content_type, 'png')
        key = f"photo/{user_id}.{extension}"
        
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=photo_data,
                ContentType=content_type
            )
            
            return {
                'key': key,
                'status': 'success',
                'message': f'Profile photo uploaded successfully for user {user_id}'
            }
        except Exception as e:
            return {
                'key': key,
                'status': 'error',
                'message': f'Failed to upload profile photo: {str(e)}'
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
    
    def delete_videos(self, user_id: str, video_ids: List[str]) -> None:
        """
        Deletes a file from S3 given its key.
        :param video_ids: The list of video IDs of the files to delete
        """
        try:
            for video_id in video_ids:
                s3_key = f"video/{user_id}/{video_id}.mp4"
                self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)
        except Exception as e:
            raise Exception(f"Failed to delete videos from S3: {str(e)}")
    
    def delete_profile_photo(self, user_id: str) -> None:
        """
        Deletes the profile photo of a user from S3.
        """
        try:
            for extension in ['png', 'jpg']:
                s3_key = f"photo/{user_id}.{extension}"
                self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)
        except Exception as e:
            raise Exception(f"Failed to delete profile photo from S3: {str(e)}")
