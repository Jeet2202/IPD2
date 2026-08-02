"""
Reusable Cloudinary Upload Service — handles secure image upload, deletion, and replacement.
"""

import logging
import uuid
import cloudinary
import cloudinary.uploader
from cloudinary.exceptions import Error as CloudinaryError

from app.core.config import settings
from app.core.exceptions import BadRequestException, InternalServerErrorException

logger = logging.getLogger(__name__)


class CloudinaryService:
    """Centralized service managing Cloudinary image operations."""

    @staticmethod
    def _configure():
        """Configure Cloudinary SDK dynamically using application settings."""
        cloud_name = settings.CLOUDINARY_CLOUD_NAME
        api_key = settings.CLOUDINARY_API_KEY.get_secret_value() if settings.CLOUDINARY_API_KEY else None
        api_secret = settings.CLOUDINARY_API_SECRET.get_secret_value() if settings.CLOUDINARY_API_SECRET else None

        if not cloud_name or not api_key or not api_secret:
            logger.error("Cloudinary credentials missing in server settings.")
            raise BadRequestException(
                message="Cloudinary image storage is not configured on this server.",
                error_code="CLOUDINARY_NOT_CONFIGURED",
            )

        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,
        )

    @classmethod
    def upload_profile_image(
        cls,
        file_bytes: bytes,
        filename: str,
        user_id: str,
    ) -> tuple[str, str]:
        """
        Upload profile photo bytes to Cloudinary under kaamsetu/profile_pictures folder.

        Returns:
            tuple[secure_url, public_id]

        Raises:
            InternalServerErrorException / BadRequestException on Cloudinary failure.
        """
        cls._configure()

        # Generate a unique public ID incorporating user_id inside configured Cloudinary folder
        folder = settings.CLOUDINARY_FOLDER.strip("/")
        unique_suffix = uuid.uuid4().hex[:8]
        filename_public_id = f"user_{user_id}_{unique_suffix}"
        expected_full_public_id = f"{folder}/{filename_public_id}"

        try:
            upload_result = cloudinary.uploader.upload(
                file_bytes,
                folder=folder,
                public_id=filename_public_id,
                overwrite=True,
                resource_type="image",
                transformation=[
                    {"width": 500, "height": 500, "crop": "fill", "gravity": "face"},
                    {"quality": "auto", "fetch_format": "auto"},
                ],
            )
            secure_url = upload_result.get("secure_url")
            result_public_id = upload_result.get("public_id", expected_full_public_id)
            logger.info("Successfully uploaded profile image to Cloudinary for user_id=%s (public_id=%s)", user_id, result_public_id)
            return secure_url, result_public_id
        except CloudinaryError as e:
            logger.error("Cloudinary upload failed for user_id=%s: %s", user_id, str(e))
            raise InternalServerErrorException(
                message=f"Image upload to Cloudinary failed: {str(e)}",
                error_code="CLOUDINARY_UPLOAD_FAILED",
            )
        except Exception as e:
            logger.error("Unexpected error during Cloudinary upload for user_id=%s: %s", user_id, str(e))
            raise InternalServerErrorException(
                message="Failed to upload image. Please try again later.",
                error_code="IMAGE_UPLOAD_ERROR",
            )

    @classmethod
    def delete_image(cls, public_id: str | None) -> bool:
        """
        Delete an existing image from Cloudinary by its public_id.

        Returns:
            True if deleted or skipped (if public_id is None/empty).
        """
        if not public_id or not public_id.strip():
            return True

        cls._configure()
        try:
            result = cloudinary.uploader.destroy(public_id.strip(), resource_type="image")
            status = result.get("result")
            logger.info("Cloudinary image delete for public_id=%s returned status=%s", public_id, status)
            return status in ("ok", "not_found")
        except Exception as e:
            logger.warning("Failed to delete Cloudinary image public_id=%s: %s", public_id, str(e))
            return False

    @classmethod
    def replace_profile_image(
        cls,
        file_bytes: bytes,
        filename: str,
        user_id: str,
        old_public_id: str | None = None,
    ) -> tuple[str, str]:
        """
        Replace existing profile photo by deleting old_public_id and uploading new file.
        """
        # Upload new image first
        secure_url, new_public_id = cls.upload_profile_image(file_bytes, filename, user_id)

        # Delete previous image if it exists
        if old_public_id:
            cls.delete_image(old_public_id)

        return secure_url, new_public_id

    @classmethod
    def upload_service_image(
        cls,
        file_bytes: bytes,
        filename: str,
        service_id: str,
    ) -> tuple[str, str]:
        """
        Upload service photo bytes to Cloudinary under kaamsetu/service_images folder.

        Returns:
            tuple[secure_url, public_id]
        """
        cls._configure()

        base_folder = settings.CLOUDINARY_FOLDER.strip("/").split("/")[0] if settings.CLOUDINARY_FOLDER else "kaamsetu"
        folder = f"{base_folder}/service_images"
        unique_suffix = uuid.uuid4().hex[:8]
        filename_public_id = f"service_{service_id}_{unique_suffix}"
        expected_full_public_id = f"{folder}/{filename_public_id}"

        try:
            upload_result = cloudinary.uploader.upload(
                file_bytes,
                folder=folder,
                public_id=filename_public_id,
                overwrite=True,
                resource_type="image",
                transformation=[
                    {"width": 1200, "height": 800, "crop": "limit"},
                    {"quality": "auto", "fetch_format": "auto"},
                ],
            )
            secure_url = upload_result.get("secure_url")
            result_public_id = upload_result.get("public_id", expected_full_public_id)
            logger.info("Successfully uploaded service image to Cloudinary for service_id=%s (public_id=%s)", service_id, result_public_id)
            return secure_url, result_public_id
        except CloudinaryError as e:
            logger.error("Cloudinary upload failed for service_id=%s: %s", service_id, str(e))
            raise InternalServerErrorException(
                message=f"Image upload to Cloudinary failed: {str(e)}",
                error_code="CLOUDINARY_UPLOAD_FAILED",
            )
        except Exception as e:
            logger.error("Unexpected error during Cloudinary upload for service_id=%s: %s", service_id, str(e))
            raise InternalServerErrorException(
                message="Failed to upload image. Please try again later.",
                error_code="IMAGE_UPLOAD_ERROR",
            )

    @classmethod
    def replace_service_image(
        cls,
        file_bytes: bytes,
        filename: str,
        service_id: str,
        old_public_id: str | None = None,
    ) -> tuple[str, str]:
        """
        Replace existing service photo by uploading new file and deleting old_public_id.
        """
        secure_url, new_public_id = cls.upload_service_image(file_bytes, filename, service_id)
        if old_public_id:
            cls.delete_image(old_public_id)
        return secure_url, new_public_id
