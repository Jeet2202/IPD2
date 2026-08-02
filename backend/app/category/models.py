"""
Service Catalog models — Categories and Services for the KaamSetu marketplace.

Architecture:
    - TWO separate Beanie Documents: ServiceCategory and Service.
    - Service references ServiceCategory via category_id (string, not Link).
    - Required skills stored as an embedded list of strings on each Service.
    - Admin-managed catalog — workers don't create categories or services.

Why Categories and Services are separate collections:
    - Different lifecycle: categories are static (rarely change), services
      are dynamic (added/updated frequently by admins).
    - Different access patterns: category listing is cached and loaded once
      on app start; service queries are filtered by category, price, skills.
    - Separate collections enable independent indexing: service queries
      don't scan category fields and vice versa.
    - MongoDB aggregation: $lookup from services to categories is efficient
      for admin views; app views can use denormalized category_slug on
      the Service document for zero-join reads.
    - Scalability: as the catalog grows to 100+ services across 20+
      categories, separate collections keep document sizes small.

Relationship strategy:
    - Service.category_id stores the ServiceCategory ObjectId as a string.
    - String reference (not Beanie Link) avoids implicit lazy loading.
    - The service layer validates category_id existence before insert.
    - category_slug is denormalized on Service for display without join.

Why required_skills is a list of strings:
    - Skills are a controlled vocabulary that maps to WorkerProfile.skills.
    - Storing as strings avoids cross-collection joins during worker matching.
    - The matching algorithm compares Service.required_skills against
      WorkerProfile.skills[].skill_name — both indexed, both normalized.
    - Future AI matching can use skill strings as feature vectors.

Index strategy — ServiceCategory:
    - slug (unique): URL-friendly identifier, API lookups.
    - is_active + display_order (compound): Active category listing
      sorted by admin-defined order — the most common query.
    - name: Text search for admin category management.

Index strategy — Service:
    - slug (unique): URL-friendly identifier, API lookups.
    - category_id + is_active (compound): "All active services in
      category X" — the most common customer-facing query.
    - required_skills: Multikey index for skill-based worker matching
      ("which services need plumbing skill?").
    - base_market_price (ascending): Price range filtering and sorting.
    - is_active + is_emergency_service (compound): Emergency service
      listing — filtered for priority dispatch.
    - created_at (descending): Admin dashboard pagination.

Collection names: "service_categories", "services" (explicit, plural).
"""

import re
from datetime import datetime, timezone

from beanie import Document, Indexed, before_event, Insert, Replace, Save, SaveChanges
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel


# ---------------------------------------------------------------------------
# Slug Generator
# ---------------------------------------------------------------------------

# Regex for slug normalization: keep only alphanumeric and hyphens.
_SLUG_CLEAN_REGEX = re.compile(r"[^a-z0-9\-]")
_SLUG_MULTI_HYPHEN = re.compile(r"-{2,}")


def generate_slug(name: str) -> str:
    """
    Generate a URL-friendly slug from a name.

    Process: lowercase → replace spaces with hyphens → remove special
    characters → collapse multiple hyphens → strip edge hyphens.

    Examples:
        "Electrical" → "electrical"
        "AC Repair & Service" → "ac-repair-service"
        "Salon at Home" → "salon-at-home"
    """
    slug = name.strip().lower().replace(" ", "-")
    slug = _SLUG_CLEAN_REGEX.sub("", slug)
    slug = _SLUG_MULTI_HYPHEN.sub("-", slug)
    return slug.strip("-")


# ---------------------------------------------------------------------------
# Service Category Document
# ---------------------------------------------------------------------------

class ServiceCategory(Document):
    """
    Top-level service category in the KaamSetu marketplace.

    Categories are the primary navigation structure in the app.
    Each category groups related services (e.g., "Electrical" contains
    "Fan Installation", "MCB Replacement", "Wiring Repair").

    Admin-managed: created and updated via admin dashboard.
    Customer-facing: displayed as category cards on the app home screen.

    Attributes:
        name: Display name shown in the app and admin dashboard.
              Must be unique across all categories (enforced by slug).
        slug: URL-friendly identifier. Auto-generated from name.
              Used in API paths (/categories/electrical/services).
              Unique index prevents duplicate categories.
        icon: Icon identifier or URL for the category card.
              Can be a Material Icons name ("electrical_services")
              or a Cloudinary/S3 URL to a custom icon.
        description: Short description displayed below the category
                     name. Used for SEO and in-app tooltips.
        display_order: Admin-controlled sort position for the home
                       screen category grid. Lower values appear first.
                       Allows drag-and-drop reordering in admin UI.
        is_active: Soft delete / visibility toggle. Inactive categories
                   are hidden from customers but preserved for historical
                   bookings and admin reference.
        color_code: Hex color code for the category card background.
                    Used for visual differentiation in the app UI.
                    Format: #RRGGBB (e.g., "#FF5722" for deep orange).
        metadata: Flexible key-value store for future features:
                  - seasonal: bool (seasonal category like "Diwali Cleaning")
                  - trending: bool (admin-marked as trending)
                  - popularity_score: float (AI-computed popularity)
                  - translations: dict (multi-language category names)
        created_at: Category creation timestamp (UTC).
        updated_at: Last modification timestamp (UTC). Auto-updated.
    """

    # --- Identity ---
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Category display name",
        examples=["Electrical"],
    )
    slug: Indexed(str, unique=True) = Field(  # type: ignore[valid-type]
        ...,
        min_length=2,
        max_length=120,
        description="URL-friendly identifier (unique, auto-generated)",
        examples=["electrical"],
    )

    # --- Display ---
    icon: str | None = Field(
        default=None,
        max_length=512,
        description="Icon name or URL for category card",
        examples=["electrical_services"],
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Short category description",
        examples=["All electrical services for your home"],
    )
    image_url: str | None = Field(
        default=None,
        max_length=1024,
        description="Cloudinary or CDN URL for category image",
    )
    image_public_id: str | None = Field(
        default=None,
        max_length=256,
        description="Cloudinary public_id for category image",
    )
    display_order: int = Field(
        default=0,
        ge=0,
        description="Sort position for home screen (lower = first)",
    )
    is_active: bool = Field(
        default=True,
        description="Visibility toggle (False = hidden from customers)",
    )
    color_code: str | None = Field(
        default=None,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Hex color code for UI (e.g., '#FF5722')",
        examples=["#FF5722"],
    )

    # --- Extensibility ---
    metadata: dict = Field(
        default_factory=dict,
        description="Flexible key-value store for future features",
    )

    # --- Timestamps ---
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Category creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last modification timestamp (UTC, auto-updated)",
    )

    # ------------------------------------------------------------------
    # Beanie Event Hooks
    # ------------------------------------------------------------------

    @before_event(Insert, Replace, Save, SaveChanges)
    async def set_updated_at(self) -> None:
        """Auto-update `updated_at` on every write operation."""
        self.updated_at = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Beanie Settings
    # ------------------------------------------------------------------

    class Settings:
        """
        Beanie collection configuration.

        - name: Explicit collection name (lowercase, plural).
        - indexes: Optimized for category listing and admin management.
        - use_state_management: Enables change tracking for partial updates.
        """

        name = "service_categories"
        use_state_management = True

        indexes = [
            # Compound: active categories sorted by display order.
            # Covers the most common query: "show all active categories
            # on the home screen, sorted by admin-defined order".
            IndexModel(
                [("is_active", ASCENDING), ("display_order", ASCENDING)],
                name="idx_active_display_order",
            ),
            # Name index for admin search and duplicate detection.
            IndexModel(
                [("name", ASCENDING)],
                name="idx_name",
            ),
        ]

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"<ServiceCategory name={self.name!r} slug={self.slug!r} "
            f"active={self.is_active} order={self.display_order}>"
        )


# ---------------------------------------------------------------------------
# Service Document
# ---------------------------------------------------------------------------

class Service(Document):
    """
    Individual service within a category.

    Each service represents a specific job type that customers can book
    and workers can accept (e.g., "Fan Installation" under "Electrical").

    References ServiceCategory via category_id. Denormalizes category_slug
    for zero-join reads in customer-facing queries.

    Attributes:
        category_id: Reference to ServiceCategory ObjectId. String, not
                     Link — avoids lazy loading. The service layer validates
                     existence before insert.
        category_slug: Denormalized slug from ServiceCategory. Enables
                       filtering services by category without $lookup.
                       Updated by the service layer if category slug changes.
        name: Display name for the service. Shown in service cards,
              booking confirmations, and invoices.
        slug: URL-friendly identifier. Unique across all services.
              Used in API paths (/services/fan-installation).
        description: Detailed service description. Shown on the service
                     detail page. Supports future markdown rendering.

        --- Pricing ---
        base_market_price: Standard market price in INR. Used as the
                           starting point for dynamic pricing algorithms.
        minimum_price: Floor price. Dynamic pricing cannot go below this.
                       Protects workers from unprofitable jobs.
        maximum_price: Ceiling price. Dynamic pricing cannot exceed this.
                       Protects customers from price gouging.

        --- Duration & Requirements ---
        estimated_duration_minutes: Expected time to complete the service.
                                    Used for scheduling, worker availability
                                    calculation, and booking time slots.
        required_experience_years: Minimum experience required for a worker
                                   to accept this service type. Used in
                                   worker-service matching.
        required_skills: List of skill names required to perform this
                         service. Matched against WorkerProfile.skills.
                         Indexed for efficient worker matching queries.

        --- Media ---
        service_icon: Icon name or URL for the service card.
        service_image: Hero image URL for the service detail page.

        --- Flags ---
        is_inspection_required: True if the service requires an on-site
                                 inspection before providing a final quote.
                                 Examples: home painting, deep renovation.
        is_emergency_service: True for priority dispatch services.
                              Examples: pipe burst, electrical short circuit.
                              Emergency services get higher visibility and
                              faster worker matching.
        is_active: Soft delete / visibility toggle.

        --- Extensibility ---
        metadata: Flexible key-value store for future features:
                  - popularity_score: float (AI-computed, for trending)
                  - seasonal_start: str (seasonal availability start date)
                  - seasonal_end: str (seasonal availability end date)
                  - translations: dict (multi-language service names)
                  - dynamic_pricing_config: dict (surge/off-peak rules)
                  - ai_recommendation_weight: float (recommendation ranking)
                  - tags: list[str] (searchable tags for AI matching)

        --- Timestamps ---
        created_at: Service creation timestamp (UTC).
        updated_at: Last modification timestamp (UTC). Auto-updated.
    """

    # --- Category Reference ---
    category_id: str = Field(
        ...,
        description="Reference to ServiceCategory ObjectId",
        examples=["60d5ec49f1a2c8b1f8e4e1a1"],
    )
    category_slug: str = Field(
        ...,
        min_length=2,
        max_length=120,
        description="Denormalized category slug for zero-join reads",
        examples=["electrical"],
    )

    # --- Identity ---
    name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Service display name / title",
        examples=["Fan Installation"],
    )
    slug: Indexed(str, unique=True) = Field(  # type: ignore[valid-type]
        ...,
        min_length=2,
        max_length=220,
        description="URL-friendly identifier (unique, auto-generated)",
        examples=["fan-installation"],
    )
    short_description: str | None = Field(
        default=None,
        max_length=500,
        description="Short service summary for cards",
        examples=["Quick and reliable fan installation service."],
    )
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="Detailed service description",
        examples=["Professional ceiling fan installation with wiring and testing."],
    )

    # --- Pricing ---
    base_market_price: float = Field(
        ...,
        ge=0.0,
        le=500000.0,
        description="Standard market price in INR",
        examples=[499.0],
    )
    minimum_price: float = Field(
        default=0.0,
        ge=0.0,
        le=500000.0,
        description="Floor price — dynamic pricing minimum (INR)",
        examples=[299.0],
    )
    maximum_price: float = Field(
        default=0.0,
        ge=0.0,
        le=500000.0,
        description="Ceiling price — dynamic pricing maximum (INR)",
        examples=[999.0],
    )

    # --- Duration & Requirements ---
    estimated_duration_minutes: int = Field(
        ...,
        gt=0,
        le=2880,
        description="Expected completion time (minutes)",
        examples=[60],
    )
    required_experience_years: float = Field(
        default=0.0,
        ge=0.0,
        le=30.0,
        description="Minimum worker experience required (years)",
    )
    required_skills: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="Required skill names for worker matching",
        examples=[["fan-installation", "electrical-wiring"]],
    )

    # --- Media ---
    service_icon: str | None = Field(
        default=None,
        max_length=512,
        description="Icon name or URL for service card",
        examples=["ceiling_fan"],
    )
    service_image: str | None = Field(
        default=None,
        max_length=1024,
        description="Hero image URL for service detail page",
        examples=["https://res.cloudinary.com/kaamsetu/image/upload/v1/services/fan.jpg"],
    )
    service_image_url: str | None = Field(
        default=None,
        max_length=1024,
        description="Cloudinary image URL",
    )
    service_image_public_id: str | None = Field(
        default=None,
        max_length=256,
        description="Cloudinary public ID",
    )

    # --- Search & Inclusions ---
    whats_included: list[str] = Field(
        default_factory=list,
        description="Items included in the service package",
        examples=[["Deep cleaning of coils", "High-pressure jet wash", "Gas check"]],
    )
    whats_not_included: list[str] = Field(
        default_factory=list,
        description="Items excluded from the service package",
        examples=[["Spare parts replacement", "Gas refilling", "Copper pipe repairs"]],
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Searchable tags",
        examples=[["fan", "wiring", "electrical"]],
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="Search keywords",
        examples=[["install", "ceiling fan", "appliance"]],
    )
    display_order: int = Field(
        default=0,
        ge=0,
        description="Card display sort index (lower = first)",
    )

    # --- Flags ---
    is_featured: bool = Field(
        default=False,
        description="Featured service toggle for home screen grid",
    )
    is_inspection_required: bool = Field(
        default=False,
        description="Requires on-site inspection before final quote",
    )
    is_emergency_service: bool = Field(
        default=False,
        description="Priority dispatch service (e.g., pipe burst)",
    )
    is_active: bool = Field(
        default=True,
        description="Visibility toggle (False = hidden from customers)",
    )

    # --- Extensibility ---
    metadata: dict = Field(
        default_factory=dict,
        description="Flexible key-value store for future features",
    )

    # --- Timestamps ---
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Service creation timestamp (UTC)",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last modification timestamp (UTC, auto-updated)",
    )

    # ------------------------------------------------------------------
    # Aliases & Helper Properties
    # ------------------------------------------------------------------

    @property
    def title(self) -> str:
        """Alias for name."""
        return self.name

    @property
    def base_price(self) -> float:
        """Alias for base_market_price."""
        return self.base_market_price

    # ------------------------------------------------------------------
    # Beanie Event Hooks
    # ------------------------------------------------------------------

    @before_event(Insert, Replace, Save, SaveChanges)
    async def set_updated_at(self) -> None:
        """Auto-update `updated_at` on every write operation."""
        self.updated_at = datetime.now(timezone.utc)
        if self.service_image_url and not self.service_image:
            self.service_image = self.service_image_url
        elif self.service_image and not self.service_image_url:
            self.service_image_url = self.service_image

    # ------------------------------------------------------------------
    # Beanie Settings
    # ------------------------------------------------------------------

    class Settings:
        """
        Beanie collection configuration.

        - name: Explicit collection name (lowercase, plural).
        - indexes: Optimized for service listing, filtering, and matching.
        - use_state_management: Change tracking for partial updates.
        """

        name = "services"
        use_state_management = True

        indexes = [
            # Compound: active services within a category ordered by display_order.
            IndexModel(
                [("category_id", ASCENDING), ("is_active", ASCENDING), ("display_order", ASCENDING)],
                name="idx_category_active_order",
            ),
            # Featured services index.
            IndexModel(
                [("is_featured", ASCENDING), ("is_active", ASCENDING)],
                name="idx_featured_active",
            ),
            # Active service display order index.
            IndexModel(
                [("is_active", ASCENDING), ("display_order", ASCENDING)],
                name="idx_active_display_order",
            ),
            # Required skills multikey index for worker matching.
            IndexModel(
                [("required_skills", ASCENDING)],
                name="idx_required_skills",
            ),
            # Tags index for search preparation.
            IndexModel(
                [("tags", ASCENDING)],
                name="idx_tags",
            ),
            # Keywords index for search preparation.
            IndexModel(
                [("keywords", ASCENDING)],
                name="idx_keywords",
            ),
            # Price sorting for customer price range filtering.
            IndexModel(
                [("base_market_price", ASCENDING)],
                name="idx_base_price",
            ),
            # Category slug index.
            IndexModel(
                [("category_slug", ASCENDING)],
                name="idx_category_slug",
            ),
        ]

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    @property
    def price_range_display(self) -> str:
        """Human-readable price range for UI display."""
        return f"₹{self.minimum_price:,.0f} – ₹{self.maximum_price:,.0f}"

    @property
    def duration_display(self) -> str:
        """Human-readable duration for UI display."""
        if self.estimated_duration_minutes < 60:
            return f"{self.estimated_duration_minutes} min"
        hours = self.estimated_duration_minutes // 60
        minutes = self.estimated_duration_minutes % 60
        if minutes == 0:
            return f"{hours} hr"
        return f"{hours} hr {minutes} min"

    def __repr__(self) -> str:
        return (
            f"<Service name={self.name!r} slug={self.slug!r} "
            f"category={self.category_slug!r} "
            f"price={self.price_range_display} active={self.is_active}>"
        )
