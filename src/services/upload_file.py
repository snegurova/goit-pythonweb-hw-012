"""
Service for uploading user files to Cloudinary.

This module defines an UploadFileService class that handles configuration and upload
of user files (e.g. avatar images) to Cloudinary with public URLs.
"""

import cloudinary
import cloudinary.uploader

class UploadFileService:
    """
    Cloudinary upload service for managing file uploads.

    Configures Cloudinary credentials and provides a method to upload and transform user images.
    """
    def __init__(self, cloud_name, api_key, api_secret):
        """
        Initialize the upload service with Cloudinary credentials.

        Args:
            cloud_name (str): Cloudinary cloud name.
            api_key (str): Cloudinary API key.
            api_secret (str): Cloudinary API secret.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Upload a file to Cloudinary under a specific username path.

        Args:
            file (UploadFile): The file to upload.
            username (str): Username used to define the Cloudinary public ID.

        Returns:
            str: The transformed Cloudinary image URL.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
