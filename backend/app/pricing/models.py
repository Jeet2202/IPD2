"""
Pricing engine models — configurable, database-driven pricing for Ally.

Architecture:
    - TWO separate Beanie Documents: ServicePriceGuide and PricingConfiguration.
    - Zero hardcoded pricing values — everything is admin-configurable via DB.
    - ServicePriceGuide: per-service, per-city pricing with date-based validity.
    - PricingConfiguration: global platform-wide pricing rules and multipliers.

Why pricing is database-driven (not hardcoded):
    - Prices vary by city (Mumbai vs Jaipur), season (Diwali surge), and
      time (night/weekend). Hardcoded values require code deploys to change.
    - Admin dashboard can update prices instantly without engineering.
    - A/B testing: multiple active configs allow testing pricing strategies.
    - Regulatory compliance: GST rates change periodically; DB-driven
      values avoid emergency hotfixes.
    - AI pricing: future ML models write predicted prices directly to DB.

Why ServicePriceGuide and PricingConfiguration are separated:
    - ServicePriceGuide is per-service, per-city — granular, many documents.
      Queries: "What's the price for fan installation in Mumbai?"
    - PricingConfiguration is platform-wide — one active config at a time.
      Queries: "What's the current GST rate and platform commission?"
    - Separation enables independent caching: global config is cached once
      (rarely changes), price guides are cached per service+city.
    - Different access patterns: price guides are queried on every booking;
      config is queried once and cached per request lifecycle.
    - Different update frequency: price guides change weekly/monthly;
      config changes quarterly (GST, commission).

Index strategy — ServicePriceGuide:
    - service_id + city + is_active (compound): "Active price for fan
      installation in Mumbai" — the primary pricing lookup query.
    - effective_from + effective_until (compound): Date range queries
      for "current price" lookups and expired price cleanup.
    - city + is_active (compound): "All active prices in Mumbai" —
      city-wide pricing reports for admin.
    - created_at (descending): Admin dashboard pagination.

Index strategy — PricingConfiguration:
    - is_active: Filter for the current active configuration.
      Only one config should be active at a time (enforced by service layer).
    - created_at (descending): Admin audit trail.

Collection names: "service_price_guides", "pricing_configurations".
"""

from datetime import datetime, timezone
from enum import Enum

from beanie import Document, before_event, Insert, Replace, Save, SaveChanges
from pydantic import Field
from pymongo import ASCENDING, DESCENDING, IndexModel


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Currency(str, Enum):
    """
    Supported currencies for pricing.

    - INR: Indian Rupee (primary, dominant market).
    - USD: US Dollar (future international expansion).
    - GBP: British Pound (future UK market).
    """

    INR = "INR"
    USD = "USD"
    GBP = "GBP"


# ---------------------------------------------------------------------------
# Service Price Guide Document
# ---------------------------------------------------------------------------

class ServicePriceGuide(Document):
    """
    Per-service, per-city pricing configuration.

    Each document represents the pricing for a specific service in a
    specific city, valid within a date range. This enables:
    - City-specific pricing (Mumbai plumber ≠ Jaipur plumber).
    - Seasonal pricing (Diwali cleaning prices higher in Oct-Nov).
    - Time-limited promotions (discounted rates for 2 weeks).
    - Price versioning (historical prices preserved for audits).

    The pricing engine selects the active price guide matching:
        service_id + city + is_active + (effective_from ≤ now ≤ effective_until)

    Attributes:
        service_id: Reference to Service document ObjectId. String
                    reference — no lazy loading. The service layer
                    validates existence before insert.
        city: City name (normalized to lowercase). Used for city-specific
              pricing lookups. Examples: "mumbai", "delhi", "bangalore".
              A special value "_default" can be used for fallback pricing
              when no city-specific guide exists.

        --- Price Points ---
        minimum_price: Floor price in the given currency. The final
                       quoted price cannot go below this, even with
                       discounts or dynamic pricing adjustments.
        average_market_price: The standard market rate. Used as the
                              base for dynamic pricing calculations and
                              displayed to customers as the "market rate".
        maximum_price: Ceiling price. Protects customers from price
                       gouging. Dynamic pricing cannot exceed this.

        --- Additional Charges ---
        inspection_charge: Fixed fee charged for on-site inspection
                           before providing a final quote. Applicable
                           only when Service.is_inspection_required is True.
                           Set to 0.0 if no inspection charge.
        emergency_charge_percentage: Percentage surcharge applied on top
                                     of the base price for emergency
                                     bookings. Example: 25.0 means a 25%
                                     surcharge. Applied only when
                                     Service.is_emergency_service is True.

        --- Tolerance ---
        price_tolerance_percentage: Allowed deviation from the average
                                    market price for worker quotes. If a
                                    worker quotes ₹500 and tolerance is 10%,
                                    the system accepts ₹450–₹550. Used by
                                    the quote validation algorithm.

        --- Currency & Validity ---
        currency: ISO 4217 currency code. Defaults to INR.
        effective_from: Start date of this price guide's validity.
                        Enables scheduling future price changes.
        effective_until: End date of validity. None means no expiry
                         (valid indefinitely until deactivated).
        is_active: Visibility toggle. Only active guides are used
                   for pricing calculations.

        --- Extensibility ---
        metadata: Flexible key-value store for future features:
                  - ai_predicted_price: float (ML model output)
                  - demand_factor: float (demand-based adjustment)
                  - seasonal_tag: str (e.g., "diwali", "monsoon")
                  - promotion_id: str (linked promotion campaign)
                  - subscription_discount: float (member discount %)
                  - coupon_codes: list[str] (applicable coupon codes)

        --- Timestamps ---
        created_at: Record creation timestamp (UTC).
        updated_at: Last modification timestamp (UTC). Auto-updated.
    """

    # --- References ---
    service_id: str = Field(
        ...,
        description="Reference to Service document ObjectId",
        examples=["60d5ec49f1a2c8b1f8e4e1a2"],
    )
    city: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="City name (lowercase) or '_default' for fallback",
        examples=["mumbai"],
    )

    # --- Price Points ---
    minimum_price: float = Field(
        ...,
        ge=0.0,
        le=500000.0,
        description="Floor price — cannot go below this (currency units)",
        examples=[299.0],
    )
    average_market_price: float = Field(
        ...,
        ge=0.0,
        le=500000.0,
        description="Standard market rate (currency units)",
        examples=[499.0],
    )
    maximum_price: float = Field(
        ...,
        ge=0.0,
        le=500000.0,
        description="Ceiling price — cannot exceed this (currency units)",
        examples=[999.0],
    )

    # --- Additional Charges ---
    inspection_charge: float = Field(
        default=0.0,
        ge=0.0,
        le=50000.0,
        description="Fixed inspection fee (currency units, 0 if none)",
        examples=[99.0],
    )
    emergency_charge_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Emergency surcharge percentage (e.g., 25.0 = 25%)",
        examples=[25.0],
    )

    # --- Tolerance ---
    price_tolerance_percentage: float = Field(
        default=10.0,
        ge=0.0,
        le=50.0,
        description="Allowed deviation from market price (%)",
        examples=[10.0],
    )

    # --- Currency & Validity ---
    currency: Currency = Field(
        default=Currency.INR,
        description="ISO 4217 currency code",
    )
    effective_from: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Start of price validity (UTC)",
    )
    effective_until: datetime | None = Field(
        default=None,
        description="End of price validity (UTC, None = no expiry)",
    )
    is_active: bool = Field(
        default=True,
        description="Active toggle — only active guides are used",
    )

    # --- Extensibility ---
    metadata: dict = Field(
        default_factory=dict,
        description="Flexible key-value store for future pricing features",
    )

    # --- Timestamps ---
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Record creation timestamp (UTC)",
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
        - indexes: Optimized for pricing lookup, date range, and city queries.
        - use_state_management: Change tracking for partial updates.
        """

        name = "service_price_guides"
        use_state_management = True

        indexes = [
            # Primary pricing lookup: "active price for service X in city Y".
            # This is THE most common query — executed on every booking.
            IndexModel(
                [
                    ("service_id", ASCENDING),
                    ("city", ASCENDING),
                    ("is_active", ASCENDING),
                ],
                name="idx_service_city_active",
            ),
            # Date range queries: find current/future/expired price guides.
            # Used by the pricing engine to select the temporally valid guide.
            IndexModel(
                [
                    ("effective_from", ASCENDING),
                    ("effective_until", ASCENDING),
                ],
                name="idx_effective_range",
            ),
            # City-wide pricing report for admin dashboard.
            IndexModel(
                [("city", ASCENDING), ("is_active", ASCENDING)],
                name="idx_city_active",
            ),
            # Admin dashboard pagination (most recent first).
            IndexModel(
                [("created_at", DESCENDING)],
                name="idx_created_at_desc",
            ),
        ]

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    @property
    def price_range_display(self) -> str:
        """Human-readable price range for admin UI."""
        symbol = "₹" if self.currency == Currency.INR else self.currency.value
        return f"{symbol}{self.minimum_price:,.0f} – {symbol}{self.maximum_price:,.0f}"

    @property
    def is_currently_valid(self) -> bool:
        """True if the price guide is active and within its validity period."""
        now = datetime.now(timezone.utc)
        if not self.is_active:
            return False
        if now < self.effective_from:
            return False
        if self.effective_until is not None and now > self.effective_until:
            return False
        return True

    def calculate_emergency_price(self, base_price: float) -> float:
        """
        Apply emergency surcharge to a base price.

        Returns the total price including the emergency percentage.
        Example: base=500, emergency=25% → 625.0
        """
        return round(base_price * (1 + self.emergency_charge_percentage / 100), 2)

    def is_quote_within_tolerance(self, quoted_price: float) -> bool:
        """
        Check if a worker's quoted price is within the tolerance range.

        Returns True if the quote is within ±tolerance% of the average
        market price. Used by the quote validation algorithm.
        """
        tolerance = self.average_market_price * (self.price_tolerance_percentage / 100)
        lower = self.average_market_price - tolerance
        upper = self.average_market_price + tolerance
        return lower <= quoted_price <= upper

    def __repr__(self) -> str:
        return (
            f"<ServicePriceGuide service_id={self.service_id} "
            f"city={self.city!r} "
            f"price={self.price_range_display} "
            f"active={self.is_active}>"
        )


# ---------------------------------------------------------------------------
# Pricing Configuration Document
# ---------------------------------------------------------------------------

class PricingConfiguration(Document):
    """
    Global platform-wide pricing rules and multipliers.

    Singleton pattern: only ONE active configuration at any time.
    The service layer enforces this by deactivating the previous
    config when a new one is activated.

    This document controls:
    - Platform commissions and fees (GST, service fee).
    - Default charges (inspection, emergency) used as fallback when
      a ServicePriceGuide doesn't specify overrides.
    - Time-based multipliers (weekend, night, holiday).
    - Feature flags (surge pricing toggle).

    Attributes:
        --- Default Charges ---
        default_price_tolerance: Fallback tolerance percentage used
                                  when a ServicePriceGuide doesn't
                                  specify its own tolerance.
        default_inspection_charge: Fallback inspection fee (currency
                                    units) for services requiring
                                    inspection but without a specific
                                    price guide charge.
        default_emergency_charge: Fallback emergency surcharge
                                   percentage for emergency services
                                   without a specific price guide charge.

        --- Tax & Commission ---
        gst_percentage: Goods & Services Tax rate. Currently 18% in
                        India for home services. Applied to the final
                        invoice amount.
        platform_commission_percentage: Ally's commission on each
                                         booking. Deducted from the
                                         worker's earnings.
        worker_commission_percentage: Worker's share of the booking
                                       amount after platform commission.
                                       Should sum to 100% with
                                       platform_commission_percentage.
        customer_service_fee: Fixed fee charged to the customer on
                               top of the service price. Covers payment
                               processing, insurance, customer support.

        --- Multipliers ---
        surge_pricing_enabled: Master toggle for demand-based pricing.
                                When False, multipliers are ignored.
        weekend_multiplier: Price multiplier for Saturday/Sunday bookings.
                            1.0 = no change, 1.2 = 20% surcharge.
        night_multiplier: Price multiplier for bookings between 10 PM
                          and 6 AM. 1.0 = no change, 1.5 = 50% surcharge.
        holiday_multiplier: Price multiplier for national/regional
                            holidays. 1.0 = no change, 2.0 = double.

        --- Status ---
        is_active: Only one config should be active at a time.
                   Service layer deactivates old config on activation.

        --- Extensibility ---
        metadata: Flexible key-value store for future features:
                  - ai_pricing_model_version: str (active ML model)
                  - festival_multipliers: dict (per-festival overrides)
                  - membership_discounts: dict (tier → discount %)
                  - promo_engine_config: dict (promo code rules)
                  - coupon_max_discount: float (coupon cap)
                  - subscription_tiers: list[dict] (pricing tiers)

        --- Timestamps ---
        created_at: Config creation timestamp (UTC).
        updated_at: Last modification timestamp (UTC). Auto-updated.
    """

    # --- Default Charges ---
    default_price_tolerance: float = Field(
        default=10.0,
        ge=0.0,
        le=50.0,
        description="Fallback price tolerance percentage",
        examples=[10.0],
    )
    default_inspection_charge: float = Field(
        default=99.0,
        ge=0.0,
        le=50000.0,
        description="Fallback inspection charge (currency units)",
        examples=[99.0],
    )
    default_emergency_charge: float = Field(
        default=25.0,
        ge=0.0,
        le=100.0,
        description="Fallback emergency surcharge percentage",
        examples=[25.0],
    )

    # --- Tax & Commission ---
    gst_percentage: float = Field(
        default=18.0,
        ge=0.0,
        le=50.0,
        description="GST rate for home services (%)",
        examples=[18.0],
    )
    platform_commission_percentage: float = Field(
        default=20.0,
        ge=0.0,
        le=50.0,
        description="Platform commission on each booking (%)",
        examples=[20.0],
    )
    worker_commission_percentage: float = Field(
        default=80.0,
        ge=0.0,
        le=100.0,
        description="Worker's share after platform commission (%)",
        examples=[80.0],
    )
    customer_service_fee: float = Field(
        default=29.0,
        ge=0.0,
        le=5000.0,
        description="Fixed customer service fee (currency units)",
        examples=[29.0],
    )

    # --- Multipliers ---
    surge_pricing_enabled: bool = Field(
        default=False,
        description="Master toggle for demand-based pricing",
    )
    weekend_multiplier: float = Field(
        default=1.0,
        ge=0.5,
        le=3.0,
        description="Price multiplier for weekend bookings (1.0 = no change)",
        examples=[1.2],
    )
    night_multiplier: float = Field(
        default=1.0,
        ge=0.5,
        le=3.0,
        description="Price multiplier for night bookings (10 PM - 6 AM)",
        examples=[1.5],
    )
    holiday_multiplier: float = Field(
        default=1.0,
        ge=0.5,
        le=5.0,
        description="Price multiplier for holiday bookings",
        examples=[1.5],
    )

    # --- Status ---
    is_active: bool = Field(
        default=True,
        description="Active toggle — only one config active at a time",
    )

    # --- Extensibility ---
    metadata: dict = Field(
        default_factory=dict,
        description="Flexible key-value store for future pricing features",
    )

    # --- Timestamps ---
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Config creation timestamp (UTC)",
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
        - indexes: Minimal — only is_active filter and created_at sort.
          This collection is small (typically 1-5 documents) so heavy
          indexing is unnecessary.
        - use_state_management: Change tracking for partial updates.
        """

        name = "pricing_configurations"
        use_state_management = True

        indexes = [
            # Active config lookup — the only real query on this collection.
            IndexModel(
                [("is_active", ASCENDING)],
                name="idx_is_active",
            ),
            # Admin audit trail (most recent first).
            IndexModel(
                [("created_at", DESCENDING)],
                name="idx_created_at_desc",
            ),
        ]

    # ------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------

    @property
    def commission_split_display(self) -> str:
        """Human-readable commission split for admin UI."""
        return (
            f"Platform: {self.platform_commission_percentage}% / "
            f"Worker: {self.worker_commission_percentage}%"
        )

    def apply_multiplier(
        self,
        base_price: float,
        *,
        is_weekend: bool = False,
        is_night: bool = False,
        is_holiday: bool = False,
    ) -> float:
        """
        Apply time-based multipliers to a base price.

        Multipliers are cumulative when multiple conditions are true.
        Only applied when surge_pricing_enabled is True.

        Args:
            base_price: The starting price before multipliers.
            is_weekend: True for Saturday/Sunday bookings.
            is_night: True for bookings between 10 PM and 6 AM.
            is_holiday: True for bookings on national/regional holidays.

        Returns:
            The adjusted price with all applicable multipliers.
        """
        if not self.surge_pricing_enabled:
            return base_price

        price = base_price
        if is_weekend:
            price *= self.weekend_multiplier
        if is_night:
            price *= self.night_multiplier
        if is_holiday:
            price *= self.holiday_multiplier
        return round(price, 2)

    def calculate_breakdown(self, service_price: float) -> dict:
        """
        Calculate the full price breakdown for a booking.

        Returns a dict with all price components for invoice display:
        - service_price: Original service price.
        - gst_amount: GST calculated on service price.
        - service_fee: Fixed customer service fee.
        - total: service_price + gst + service_fee.
        - platform_earning: Platform's commission amount.
        - worker_earning: Worker's share amount.
        """
        gst_amount = round(service_price * (self.gst_percentage / 100), 2)
        total = round(service_price + gst_amount + self.customer_service_fee, 2)
        platform_earning = round(
            service_price * (self.platform_commission_percentage / 100), 2,
        )
        worker_earning = round(
            service_price * (self.worker_commission_percentage / 100), 2,
        )
        return {
            "service_price": service_price,
            "gst_percentage": self.gst_percentage,
            "gst_amount": gst_amount,
            "customer_service_fee": self.customer_service_fee,
            "total": total,
            "platform_commission_percentage": self.platform_commission_percentage,
            "platform_earning": platform_earning,
            "worker_commission_percentage": self.worker_commission_percentage,
            "worker_earning": worker_earning,
        }

    def __repr__(self) -> str:
        return (
            f"<PricingConfiguration "
            f"gst={self.gst_percentage}% "
            f"commission={self.commission_split_display} "
            f"surge={'ON' if self.surge_pricing_enabled else 'OFF'} "
            f"active={self.is_active}>"
        )
