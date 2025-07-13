# File: app/utils/image_upload.py
import cloudinary
import cloudinary.uploader
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
from app.core.config import settings
from typing import Optional


class ImageUploadService:
    def __init__(self):
        # Initialize Cloudinary if credentials are provided
        if all([settings.CLOUDINARY_CLOUD_NAME,
               settings.CLOUDINARY_API_KEY, settings.CLOUDINARY_API_SECRET]):
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET
            )
            self.cloudinary_enabled = True
        else:
            self.cloudinary_enabled = False

        # Initialize S3 if credentials are provided
        if all([settings.AWS_ACCESS_KEY_ID,
               settings.AWS_SECRET_ACCESS_KEY, settings.AWS_BUCKET_NAME]):
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            self.s3_enabled = True
        else:
            self.s3_enabled = False

    async def upload_to_cloudinary(
            self, file: UploadFile, folder: str = "marketplace") -> str:
        """Upload image to Cloudinary"""
        if not self.cloudinary_enabled:
            raise HTTPException(
                status_code=500,
                detail="Cloudinary not configured")

        try:
            # Read file content
            contents = await file.read()

            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                contents,
                folder=folder,
                resource_type="auto"
            )

            return result["secure_url"]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload to Cloudinary: {str(e)}")

    async def upload_to_s3(self, file: UploadFile,
                           folder: str = "marketplace") -> str:
        """Upload image to AWS S3"""
        if not self.s3_enabled:
            raise HTTPException(status_code=500, detail="S3 not configured")

        try:
            # Generate unique filename
            import uuid
            from datetime import datetime

            file_extension = file.filename.split(
                ".")[-1] if "." in file.filename else "jpg"
            unique_filename = f"{folder}/{datetime.now().strftime('%Y/%m/%d')}/{uuid.uuid4()}.{file_extension}"

            # Read file content
            contents = await file.read()

            # Upload to S3
            self.s3_client.put_object(
                Bucket=settings.AWS_BUCKET_NAME,
                Key=unique_filename,
                Body=contents,
                ContentType=file.content_type
            )

            # Return public URL
            return f"https://{settings.AWS_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
        except ClientError as e:
            raise HTTPException(status_code=500,
                                detail=f"Failed to upload to S3: {str(e)}")

    async def upload_image(self, file: UploadFile,
                           folder: str = "marketplace") -> str:
        """Upload image using available service (Cloudinary preferred)"""
        # Validate file
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail="File must be an image")

        # Check file size (5MB limit)
        max_size = 5 * 1024 * 1024  # 5MB
        contents = await file.read()
        if len(contents) > max_size:
            raise HTTPException(
                status_code=400,
                detail="File too large (max 5MB)")

        # Reset file position
        await file.seek(0)

        # Upload using available service
        if self.cloudinary_enabled:
            return await self.upload_to_cloudinary(file, folder)
        elif self.s3_enabled:
            return await self.upload_to_s3(file, folder)
        else:
            raise HTTPException(status_code=500,
                                detail="No image upload service configured")


image_upload_service = ImageUploadService()
