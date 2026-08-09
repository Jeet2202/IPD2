"""
Category Repository — Encapsulates async Beanie ODM database operations for ServiceCategory.
"""

from bson import ObjectId
from beanie.operators import RegEx
from app.category.models import ServiceCategory


class CategoryRepository:
    """Repository handling all database queries for service categories."""

    @staticmethod
    async def create_category(data: dict) -> ServiceCategory:
        """Create and persist a new ServiceCategory document."""
        category = ServiceCategory(**data)
        await category.insert()
        return category

    @staticmethod
    async def get_category_by_id(category_id: str) -> ServiceCategory | None:
        """Fetch category by ObjectId string."""
        if not ObjectId.is_valid(category_id):
            return None
        return await ServiceCategory.get(ObjectId(category_id))

    @staticmethod
    async def get_category_by_slug(slug: str) -> ServiceCategory | None:
        """Fetch category by URL slug."""
        clean_slug = slug.strip().lower()
        return await ServiceCategory.find_one(ServiceCategory.slug == clean_slug)

    @staticmethod
    async def get_category_by_name(name: str) -> ServiceCategory | None:
        """Fetch category by exact name (case-insensitive regex)."""
        clean_name = " ".join(name.split())
        return await ServiceCategory.find_one(
            RegEx(ServiceCategory.name, f"^{clean_name}$", "i")
        )

    @staticmethod
    async def list_categories(include_inactive: bool = False, limit: int | None = None) -> list[ServiceCategory]:
        """
        List categories sorted by display_order ascending.
        If include_inactive is False, filters for is_active == True.
        """
        if include_inactive:
            query = ServiceCategory.find_all().sort(+ServiceCategory.display_order)
        else:
            query = ServiceCategory.find(ServiceCategory.is_active == True).sort(+ServiceCategory.display_order)
        
        if limit:
            query = query.limit(limit)
        return await query.to_list()

    @staticmethod
    async def get_featured_categories(limit: int = 8) -> list[ServiceCategory]:
        """Fetch active categories for home screen grid sorted by display_order ascending."""
        return await CategoryRepository.list_categories(include_inactive=False, limit=limit)

    @staticmethod
    async def update_category(category: ServiceCategory, update_data: dict) -> ServiceCategory:
        """Apply update data dictionary to category document."""
        for key, value in update_data.items():
            if hasattr(category, key):
                setattr(category, key, value)
        await category.save()
        return category

    @staticmethod
    async def soft_delete_category(category: ServiceCategory) -> ServiceCategory:
        """Soft delete category by setting is_active = False."""
        category.is_active = False
        await category.save()
        return category

    @staticmethod
    async def reorder_categories(items: list[dict]) -> bool:
        """Bulk update display_order for multiple categories."""
        for item in items:
            cat_id = item.get("id")
            order = item.get("display_order")
            if cat_id and ObjectId.is_valid(cat_id) and order is not None:
                cat = await ServiceCategory.get(ObjectId(cat_id))
                if cat:
                    cat.display_order = order
                    await cat.save()
        return True

    @staticmethod
    async def category_exists(
        name: str | None = None,
        slug: str | None = None,
        exclude_id: str | None = None,
    ) -> bool:
        """Check if category exists matching name or slug, optionally excluding a specific ID."""
        queries = []
        if name and name.strip():
            clean_name = " ".join(name.split())
            queries.append(RegEx(ServiceCategory.name, f"^{clean_name}$", "i"))
        if slug and slug.strip():
            clean_slug = slug.strip().lower()
            queries.append(ServiceCategory.slug == clean_slug)

        if not queries:
            return False

        for query in queries:
            if exclude_id and ObjectId.is_valid(exclude_id):
                found = await ServiceCategory.find_one(query, ServiceCategory.id != ObjectId(exclude_id))
            else:
                found = await ServiceCategory.find_one(query)
            if found:
                return True
        return False

    @staticmethod
    async def get_active_category_slugs() -> list[str]:
        """Fetch list of all active ServiceCategory slugs from MongoDB."""
        try:
            categories = await CategoryRepository.list_categories(include_inactive=False)
            return [c.slug for c in categories if getattr(c, "slug", None)]
        except Exception:
            return []
