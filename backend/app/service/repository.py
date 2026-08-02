"""
Service Repository — Encapsulates async Beanie ODM database operations for Service.
"""

from bson import ObjectId
from beanie.operators import RegEx, In, Or
from app.category.models import Service


class ServiceRepository:
    """Repository handling database queries for services."""

    @staticmethod
    async def create_service(data: dict) -> Service:
        """Create and insert a new Service document."""
        service = Service(**data)
        await service.insert()
        return service

    @staticmethod
    async def get_service_by_id(service_id: str) -> Service | None:
        """Fetch service by ObjectId string."""
        if not ObjectId.is_valid(service_id):
            return None
        return await Service.get(ObjectId(service_id))

    @staticmethod
    async def get_service_by_slug(slug: str) -> Service | None:
        """Fetch service by URL slug."""
        clean_slug = slug.strip().lower()
        return await Service.find_one(Service.slug == clean_slug)

    @staticmethod
    async def list_services(
        category_id: str | None = None,
        is_featured: bool | None = None,
        include_inactive: bool = False,
        limit: int | None = None,
    ) -> list[Service]:
        """List services with optional category, featured status, active filters, and limit."""
        queries = []
        if not include_inactive:
            queries.append(Service.is_active == True)
        if category_id and ObjectId.is_valid(category_id):
            queries.append(Service.category_id == category_id)
        if is_featured is not None:
            queries.append(Service.is_featured == is_featured)

        if queries:
            req = Service.find(*queries).sort(+Service.display_order)
        else:
            req = Service.find_all().sort(+Service.display_order)

        if limit:
            req = req.limit(limit)
        return await req.to_list()

    @staticmethod
    async def get_recent_services(limit: int = 10) -> list[Service]:
        """Fetch newest active services sorted by created_at descending."""
        return await Service.find(
            Service.is_active == True
        ).sort(-Service.created_at).limit(limit).to_list()

    @staticmethod
    async def get_popular_services(limit: int = 10) -> list[Service]:
        """Fetch popular active services (sorted by display_order; extensible to booking count)."""
        return await ServiceRepository.list_services(include_inactive=False, limit=limit)

    @staticmethod
    async def list_services_by_category(
        category_id: str,
        include_inactive: bool = False,
    ) -> list[Service]:
        """List services for a specific category."""
        return await ServiceRepository.list_services(category_id=category_id, include_inactive=include_inactive)

    @staticmethod
    async def list_services_by_category_paginated(
        category_id: str,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "display_order",
        include_inactive: bool = False,
    ) -> tuple[list[Service], int]:
        """List services for a category with pagination metadata."""
        queries = []
        if not include_inactive:
            queries.append(Service.is_active == True)
        if ObjectId.is_valid(category_id):
            queries.append(Service.category_id == category_id)

        base_query = Service.find(*queries) if queries else Service.find_all()
        total = await base_query.count()

        if sort_by == "-created_at":
            req = (Service.find(*queries) if queries else Service.find_all()).sort(-Service.created_at)
        elif sort_by == "price_asc":
            req = (Service.find(*queries) if queries else Service.find_all()).sort(+Service.base_market_price)
        elif sort_by == "price_desc":
            req = (Service.find(*queries) if queries else Service.find_all()).sort(-Service.base_market_price)
        else:
            req = (Service.find(*queries) if queries else Service.find_all()).sort(+Service.display_order)

        skip = (page - 1) * limit
        items = await req.skip(skip).limit(limit).to_list()
        return items, total

    @staticmethod
    async def list_services_paginated(
        page: int = 1,
        limit: int = 10,
        category_id: str | None = None,
        is_featured: bool | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        max_duration: int | None = None,
        search: str | None = None,
        sort_by: str = "display_order",
        include_inactive: bool = False,
    ) -> tuple[list[Service], int]:
        """List services with pagination, category filter, price range, duration, search, sorting, and metadata."""
        queries = []
        if not include_inactive:
            queries.append(Service.is_active == True)
        if category_id and category_id.strip():
            cat_clean = category_id.strip()
            if ObjectId.is_valid(cat_clean):
                queries.append(Service.category_id == cat_clean)
            else:
                queries.append(Service.category_slug == cat_clean.lower())
        if is_featured is not None:
            queries.append(Service.is_featured == is_featured)
        if min_price is not None:
            queries.append(Service.base_market_price >= min_price)
        if max_price is not None:
            queries.append(Service.base_market_price <= max_price)
        if max_duration is not None:
            queries.append(Service.estimated_duration_minutes <= max_duration)
        if search and search.strip():
            regex = f".*{search.strip()}.*"
            queries.append(
                Or(
                    RegEx(Service.name, regex, "i"),
                    RegEx(Service.description, regex, "i"),
                    RegEx(Service.short_description, regex, "i"),
                    RegEx(Service.tags, regex, "i"),
                    RegEx(Service.keywords, regex, "i"),
                )
            )

        base_query = Service.find(*queries) if queries else Service.find_all()
        total = await base_query.count()

        if sort_by == "-created_at":
            req = (Service.find(*queries) if queries else Service.find_all()).sort(-Service.created_at)
        elif sort_by == "price_asc":
            req = (Service.find(*queries) if queries else Service.find_all()).sort(+Service.base_market_price)
        elif sort_by == "price_desc":
            req = (Service.find(*queries) if queries else Service.find_all()).sort(-Service.base_market_price)
        elif sort_by in ("title_asc", "name_asc"):
            req = (Service.find(*queries) if queries else Service.find_all()).sort(+Service.name)
        elif sort_by in ("title_desc", "name_desc"):
            req = (Service.find(*queries) if queries else Service.find_all()).sort(-Service.name)
        else:
            req = (Service.find(*queries) if queries else Service.find_all()).sort(+Service.display_order)

        skip = (page - 1) * limit
        items = await req.skip(skip).limit(limit).to_list()
        return items, total

    @staticmethod
    async def update_service(service: Service, update_data: dict) -> Service:
        """Apply update values to service document."""
        for key, value in update_data.items():
            if hasattr(service, key):
                setattr(service, key, value)
        await service.save()
        return service

    @staticmethod
    async def soft_delete_service(service: Service) -> Service:
        """Soft delete service by setting is_active = False."""
        service.is_active = False
        await service.save()
        return service

    @staticmethod
    async def service_exists(
        name: str | None = None,
        slug: str | None = None,
        exclude_id: str | None = None,
    ) -> bool:
        """Check if service exists matching title/name or slug, excluding optional ID."""
        queries = []
        if name and name.strip():
            clean_name = " ".join(name.split())
            queries.append(RegEx(Service.name, f"^{clean_name}$", "i"))
        if slug and slug.strip():
            clean_slug = slug.strip().lower()
            queries.append(Service.slug == clean_slug)

        if not queries:
            return False

        for query in queries:
            if exclude_id and ObjectId.is_valid(exclude_id):
                found = await Service.find_one(query, Service.id != ObjectId(exclude_id))
            else:
                found = await Service.find_one(query)
            if found:
                return True
        return False

    @staticmethod
    async def search_services_ranked(
        query_str: str | None = None,
        page: int = 1,
        limit: int = 10,
        category_id_or_slug: str | None = None,
        is_featured: bool | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        max_duration: int | None = None,
        sort_by: str = "relevance",
        include_inactive: bool = False,
    ) -> tuple[list[Service], int]:
        """
        Perform ranked search across title, short description, description, tags, keywords, and category.
        Returns matching items ordered by relevance score descending or specified sort_by.
        """
        queries = []
        if not include_inactive:
            queries.append(Service.is_active == True)
        if is_featured is not None:
            queries.append(Service.is_featured == is_featured)
        if min_price is not None:
            queries.append(Service.base_market_price >= min_price)
        if max_price is not None:
            queries.append(Service.base_market_price <= max_price)
        if max_duration is not None:
            queries.append(Service.estimated_duration_minutes <= max_duration)

        if category_id_or_slug and category_id_or_slug.strip():
            cat_clean = category_id_or_slug.strip()
            if ObjectId.is_valid(cat_clean):
                queries.append(Service.category_id == cat_clean)
            else:
                queries.append(Service.category_slug == cat_clean.lower())

        clean_q = (query_str or "").strip().lower()

        if clean_q:
            regex = f".*{clean_q}.*"
            queries.append(
                Or(
                    RegEx(Service.name, regex, "i"),
                    RegEx(Service.description, regex, "i"),
                    RegEx(Service.short_description, regex, "i"),
                    RegEx(Service.tags, regex, "i"),
                    RegEx(Service.keywords, regex, "i"),
                    RegEx(Service.category_slug, regex, "i"),
                )
            )

        base_query = Service.find(*queries) if queries else Service.find_all()
        all_matches = await base_query.to_list()

        if sort_by == "price_asc":
            sorted_items = sorted(all_matches, key=lambda s: s.base_market_price)
        elif sort_by == "price_desc":
            sorted_items = sorted(all_matches, key=lambda s: -s.base_market_price)
        elif sort_by == "-created_at":
            sorted_items = sorted(all_matches, key=lambda s: s.created_at, reverse=True)
        elif sort_by in ("title_asc", "name_asc"):
            sorted_items = sorted(all_matches, key=lambda s: (s.name or "").lower())
        elif sort_by in ("title_desc", "name_desc"):
            sorted_items = sorted(all_matches, key=lambda s: (s.name or "").lower(), reverse=True)
        elif sort_by == "display_order" or not clean_q:
            sorted_items = sorted(all_matches, key=lambda s: s.display_order)
        else:
            # Relevance scoring
            def calculate_score(s: Service) -> tuple[int, int]:
                score = 0
                s_name = (s.name or "").lower()
                s_short_desc = (s.short_description or "").lower()
                s_desc = (s.description or "").lower()
                s_cat_slug = (s.category_slug or "").lower()
                s_tags = [t.lower() for t in (s.tags or [])]
                s_kws = [k.lower() for k in (s.keywords or [])]

                if s_name == clean_q:
                    score += 100
                elif s_name.startswith(clean_q):
                    score += 80
                elif clean_q in s_name:
                    score += 60

                if any(clean_q in kw for kw in s_kws):
                    score += 50
                if clean_q in s_cat_slug:
                    score += 40
                if clean_q in s_short_desc:
                    score += 30
                if clean_q in s_desc:
                    score += 20
                if any(clean_q in tag for tag in s_tags):
                    score += 10

                return (-score, s.display_order)

            sorted_items = sorted(all_matches, key=calculate_score)

        total = len(sorted_items)
        skip = (page - 1) * limit
        items = sorted_items[skip : skip + limit]
        return items, total

