"""
Service Management Service — Business logic for services, parent category validation, slug generation, soft delete, and search.
"""

import logging
from app.category.models import generate_slug
from app.category.repository import CategoryRepository
from app.service.repository import ServiceRepository
from app.service.schemas import (
    CreateServiceRequest,
    ServiceListResponse,
    ServiceResponse,
    UpdateServiceRequest,
)
from app.uploads.service import CloudinaryService
from app.uploads.validation import validate_profile_image
from app.core.dependencies import CurrentUser
from app.core.exceptions import BadRequestException, NotFoundException
from app.utils.enums import UserRole

logger = logging.getLogger(__name__)


class ServiceManagementService:
    """Service layer for managing services business logic."""

    @classmethod
    async def generate_unique_slug(cls, base_title_or_slug: str, exclude_id: str | None = None) -> str:
        """
        Generate a unique URL slug from a title or candidate slug.
        Appends incremental suffixes (-2, -3, ...) if slug collision occurs.
        """
        base_slug = generate_slug(base_title_or_slug)
        if not base_slug:
            base_slug = "service"

        candidate_slug = base_slug
        counter = 2

        while await ServiceRepository.service_exists(slug=candidate_slug, exclude_id=exclude_id):
            candidate_slug = f"{base_slug}-{counter}"
            counter += 1

        return candidate_slug

    @classmethod
    async def create_service(cls, payload: CreateServiceRequest) -> ServiceResponse:
        """Create a new Service under a parent Category."""
        # 1. Validate parent category existence and active status
        category = await CategoryRepository.get_category_by_id(payload.category_id)
        if not category:
            raise NotFoundException(
                message=f"Category with ID '{payload.category_id}' not found.",
                error_code="CATEGORY_NOT_FOUND",
            )
        if not category.is_active:
            raise BadRequestException(
                message=f"Cannot add service to inactive category '{category.name}'.",
                error_code="INACTIVE_CATEGORY_REJECTED",
            )

        # 2. Check for duplicate service title
        if await ServiceRepository.service_exists(name=payload.title):
            raise BadRequestException(
                message=f"Service with title '{payload.title}' already exists.",
                error_code="DUPLICATE_SERVICE_TITLE",
            )

        # 3. Resolve unique slug & map fields
        data = payload.model_dump()
        raw_slug = data.get("slug")
        target_base = raw_slug if (raw_slug and raw_slug.strip()) else payload.title
        data["slug"] = await cls.generate_unique_slug(target_base)
        data["name"] = data.pop("title")
        data["base_market_price"] = data.pop("base_price")
        data["category_slug"] = category.slug

        if data.get("service_image_url"):
            data["service_image"] = data["service_image_url"]

        # 4. Insert service document
        service = await ServiceRepository.create_service(data)
        logger.info("Created service title='%s', slug='%s', id='%s'", service.name, service.slug, service.id)
        return ServiceResponse.model_validate(service)

    @classmethod
    async def get_service_by_id(cls, service_id: str, include_inactive: bool = False) -> ServiceResponse:
        """Retrieve service by ObjectId string."""
        service = await ServiceRepository.get_service_by_id(service_id)
        if not service:
            raise NotFoundException(
                message=f"Service with ID '{service_id}' not found.",
                error_code="SERVICE_NOT_FOUND",
            )
        if not service.is_active and not include_inactive:
            raise NotFoundException(
                message=f"Service with ID '{service_id}' is inactive.",
                error_code="SERVICE_NOT_FOUND",
            )
        return ServiceResponse.model_validate(service)

    @classmethod
    async def get_service_by_slug(cls, slug: str, include_inactive: bool = False) -> ServiceResponse:
        """Retrieve service by URL slug."""
        service = await ServiceRepository.get_service_by_slug(slug)
        if not service:
            raise NotFoundException(
                message=f"Service with slug '{slug}' not found.",
                error_code="SERVICE_NOT_FOUND",
            )
        if not service.is_active and not include_inactive:
            raise NotFoundException(
                message=f"Service with slug '{slug}' is inactive.",
                error_code="SERVICE_NOT_FOUND",
            )
        return ServiceResponse.model_validate(service)

    @classmethod
    async def list_services(
        cls,
        category_id: str | None = None,
        is_featured: bool | None = None,
        search: str | None = None,
        include_inactive: bool = False,
        current_user: CurrentUser | None = None,
    ) -> ServiceListResponse:
        """List services with optional category, featured, and search filters."""
        allow_inactive = include_inactive and (current_user is not None and current_user.role == UserRole.ADMIN)

        if search and search.strip():
            services = await ServiceRepository.search_services(
                query_str=search,
                category_id=category_id,
                include_inactive=allow_inactive,
            )
        else:
            services = await ServiceRepository.list_services(
                category_id=category_id,
                is_featured=is_featured,
                include_inactive=allow_inactive,
            )

        items = [ServiceResponse.model_validate(srv) for srv in services]
        return ServiceListResponse(items=items, total=len(items))

    @classmethod
    async def list_services_by_category(
        cls,
        category_id: str,
        include_inactive: bool = False,
        current_user: CurrentUser | None = None,
    ) -> ServiceListResponse:
        """List services belonging to a specific category."""
        category = await CategoryRepository.get_category_by_id(category_id)
        if not category:
            raise NotFoundException(
                message=f"Category with ID '{category_id}' not found.",
                error_code="CATEGORY_NOT_FOUND",
            )
        return await cls.list_services(
            category_id=category_id,
            include_inactive=include_inactive,
            current_user=current_user,
        )

    @classmethod
    async def update_service(cls, service_id: str, payload: UpdateServiceRequest) -> ServiceResponse:
        """Update an existing service document."""
        service = await ServiceRepository.get_service_by_id(service_id)
        if not service:
            raise NotFoundException(
                message=f"Service with ID '{service_id}' not found.",
                error_code="SERVICE_NOT_FOUND",
            )

        update_data = {k: v for k, v in payload.model_dump().items() if v is not None}

        # 1. Handle category change
        if "category_id" in update_data:
            cat_id = update_data["category_id"]
            cat = await CategoryRepository.get_category_by_id(cat_id)
            if not cat:
                raise NotFoundException(
                    message=f"Category with ID '{cat_id}' not found.",
                    error_code="CATEGORY_NOT_FOUND",
                )
            if not cat.is_active:
                raise BadRequestException(
                    message=f"Cannot move service to inactive category '{cat.name}'.",
                    error_code="INACTIVE_CATEGORY_REJECTED",
                )
            update_data["category_slug"] = cat.slug

        # 2. Handle title & slug updates
        if "title" in update_data:
            new_title = update_data.pop("title")
            update_data["name"] = new_title
            if new_title != service.name:
                if await ServiceRepository.service_exists(name=new_title, exclude_id=str(service.id)):
                    raise BadRequestException(
                        message=f"Service with title '{new_title}' already exists.",
                        error_code="DUPLICATE_SERVICE_TITLE",
                    )
                if "slug" not in update_data:
                    update_data["slug"] = await cls.generate_unique_slug(new_title, exclude_id=str(service.id))

        if "base_price" in update_data:
            update_data["base_market_price"] = update_data.pop("base_price")

        if "service_image_url" in update_data:
            update_data["service_image"] = update_data["service_image_url"]

        if "slug" in update_data:
            new_slug = update_data["slug"]
            if await ServiceRepository.service_exists(slug=new_slug, exclude_id=str(service.id)):
                base_val = update_data.get("name", service.name)
                update_data["slug"] = await cls.generate_unique_slug(base_val, exclude_id=str(service.id))

        updated_service = await ServiceRepository.update_service(service, update_data)
        logger.info("Updated service id='%s': fields=%s", service_id, list(update_data.keys()))
        return ServiceResponse.model_validate(updated_service)

    @classmethod
    async def delete_service(cls, service_id: str) -> ServiceResponse:
        """Soft delete service by setting is_active = False."""
        service = await ServiceRepository.get_service_by_id(service_id)
        if not service:
            raise NotFoundException(
                message=f"Service with ID '{service_id}' not found.",
                error_code="SERVICE_NOT_FOUND",
            )

        soft_deleted = await ServiceRepository.soft_delete_service(service)
        logger.info("Soft-deleted service id='%s' (is_active=False)", service_id)
        return ServiceResponse.model_validate(soft_deleted)

    @classmethod
    async def upload_service_image(
        cls,
        service_id: str,
        file_bytes: bytes,
        filename: str,
        content_type: str | None,
    ) -> ServiceResponse:
        """
        Validate and upload/replace service photo to Cloudinary, updating the database.
        """
        # 1. Fetch service
        service = await ServiceRepository.get_service_by_id(service_id)
        if not service:
            raise NotFoundException(
                message=f"Service with ID '{service_id}' not found.",
                error_code="SERVICE_NOT_FOUND",
            )

        # 2. Validate image file (reusing existing validation)
        validate_profile_image(filename, content_type, file_bytes)

        # 3. Upload to Cloudinary & replace old image if present
        old_public_id = service.service_image_public_id
        secure_url, public_id = CloudinaryService.replace_service_image(
            file_bytes=file_bytes,
            filename=filename if filename else "service_image.jpg",
            service_id=service_id,
            old_public_id=old_public_id,
        )

        # 4. Update MongoDB fields
        update_data = {
            "service_image_url": secure_url,
            "service_image_public_id": public_id,
            "service_image": secure_url,
        }
        updated_service = await ServiceRepository.update_service(service, update_data)
        logger.info("Updated service_id='%s' image_url='%s'", service_id, secure_url)
        return ServiceResponse.model_validate(updated_service)

    @classmethod
    async def delete_service_image(cls, service_id: str) -> ServiceResponse:
        """
        Delete service photo from Cloudinary and clear database fields.
        """
        service = await ServiceRepository.get_service_by_id(service_id)
        if not service:
            raise NotFoundException(
                message=f"Service with ID '{service_id}' not found.",
                error_code="SERVICE_NOT_FOUND",
            )

        if service.service_image_public_id:
            CloudinaryService.delete_image(service.service_image_public_id)

        update_data = {
            "service_image_url": None,
            "service_image_public_id": None,
            "service_image": None,
        }
        updated_service = await ServiceRepository.update_service(service, update_data)
        logger.info("Cleared service_id='%s' image fields", service_id)
        return ServiceResponse.model_validate(updated_service)

