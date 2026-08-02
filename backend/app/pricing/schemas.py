"""
Request/response schemas for the Pricing module.

Architecture:
    - Pure Pydantic v2 BaseModel — no Beanie dependency in schemas.
    - Strict validation: price hierarchy (min ≤ avg ≤ max), percentage
      bounds, commission split (platform + worker ≤ 100%), date ordering.
    - All request schemas use ConfigDict(str_strip_whitespace=True).
    - Partial update schemas use all-optional fields with model_validator
      to reject empty requests.
    - Response schemas use from_attributes=True for direct conversion
      from Beanie Document instances.

Design decisions:
    - City name is normalized to lowercase in validators for consistent
      lookups. The special value "_default" is reserved for fallback pricing.
    - effective_from and effective_until are validated to ensure from < until.
    - Commission percentages are validated to not exceed 100% combined.
    - Multipliers have a sane range (0.5x–3.0x/5.0x) to prevent accidental
      10x pricing from admin typos.
    - PricingConfigurationResponse includes computed fields like
      commission_split_display for admin dashboard convenience.
"""

from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from app.pricing.models import Currency


# ---------------------------------------------------------------------------
# Shared Validators
# ---------------------------------------------------------------------------

def _normalize_city(value: str) -> str:
    """
    Normalize city name for consistent storage and lookup.

    Strips whitespace, converts to lowercase, collapses spaces.
    Allows the special value "_default" for fallback pricing.
    """
    normalized = " ".join(value.strip().lower().split())
    if not normalized:
        raise ValueError("City name cannot be empty")
    return normalized


# ---------------------------------------------------------------------------
# Service Price Guide Schemas
# ---------------------------------------------------------------------------

class PriceGuideCreateRequest(BaseModel):
    """
    Create a new service price guide for a service+city combination.

    The service layer should:
        1. Validate service_id exists and is active.
        2. Check for duplicate active guides (same service + city + date range).
        3. Validate price hierarchy: min ≤ avg ≤ max.
        4. Validate date range: effective_from < effective_until.

    Attributes:
        service_id: Reference to Service document.
        city: City name (lowercase) or "_default".
        minimum_price: Floor price (currency units).
        average_market_price: Standard market rate.
        maximum_price: Ceiling price.
        inspection_charge: Fixed inspection fee (0 if none).
        emergency_charge_percentage: Emergency surcharge (%).
        price_tolerance_percentage: Allowed quote deviation (%).
        currency: ISO 4217 currency code.
        effective_from: Start of validity (UTC).
        effective_until: End of validity (None = no expiry).
        is_active: Active toggle.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    service_id: str = Field(
        ...,
        description="Service document ObjectId",
        examples=["60d5ec49f1a2c8b1f8e4e1a2"],
    )
    city: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="City name (lowercase) or '_default'",
        examples=["mumbai"],
    )

    # --- Price Points ---
    minimum_price: float = Field(
        ...,
        ge=0.0,
        le=500000.0,
        description="Floor price (currency units)",
        examples=[299.0],
    )
    average_market_price: float = Field(
        ...,
        ge=0.0,
        le=500000.0,
        description="Standard market rate",
        examples=[499.0],
    )
    maximum_price: float = Field(
        ...,
        ge=0.0,
        le=500000.0,
        description="Ceiling price",
        examples=[999.0],
    )

    # --- Additional Charges ---
    inspection_charge: float = Field(
        default=0.0,
        ge=0.0,
        le=50000.0,
        description="Inspection fee (0 if none)",
        examples=[99.0],
    )
    emergency_charge_percentage: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Emergency surcharge (%)",
        examples=[25.0],
    )
    price_tolerance_percentage: float = Field(
        default=10.0,
        ge=0.0,
        le=50.0,
        description="Allowed quote deviation (%)",
        examples=[10.0],
    )

    # --- Currency & Validity ---
    currency: Currency = Field(
        default=Currency.INR,
        description="ISO 4217 currency code",
    )
    effective_from: datetime | None = Field(
        default=None,
        description="Start of validity (UTC, defaults to now)",
    )
    effective_until: datetime | None = Field(
        default=None,
        description="End of validity (UTC, None = no expiry)",
    )
    is_active: bool = Field(
        default=True,
        description="Active toggle",
    )

    # --- Validators ---

    @field_validator("city")
    @classmethod
    def normalize_city(cls, value: str) -> str:
        return _normalize_city(value)

    @model_validator(mode="after")
    def validate_price_hierarchy(self) -> "PriceGuideCreateRequest":
        """Ensure minimum ≤ average ≤ maximum."""
        if self.minimum_price > self.average_market_price:
            raise ValueError(
                f"minimum_price ({self.minimum_price}) cannot exceed "
                f"average_market_price ({self.average_market_price})"
            )
        if self.average_market_price > self.maximum_price:
            raise ValueError(
                f"average_market_price ({self.average_market_price}) cannot exceed "
                f"maximum_price ({self.maximum_price})"
            )
        return self

    @model_validator(mode="after")
    def validate_date_range(self) -> "PriceGuideCreateRequest":
        """Ensure effective_from < effective_until if both are provided."""
        if (
            self.effective_from is not None
            and self.effective_until is not None
            and self.effective_from >= self.effective_until
        ):
            raise ValueError(
                "effective_from must be earlier than effective_until"
            )
        return self


class PriceGuideUpdateRequest(BaseModel):
    """
    Partial update for an existing service price guide.

    All fields optional. At least one must be provided.
    The service layer should re-validate price hierarchy against
    existing values when only partial prices are updated.

    Attributes:
        city: Updated city.
        minimum_price: Updated floor price.
        average_market_price: Updated market rate.
        maximum_price: Updated ceiling price.
        inspection_charge: Updated inspection fee.
        emergency_charge_percentage: Updated emergency surcharge.
        price_tolerance_percentage: Updated tolerance.
        currency: Updated currency.
        effective_from: Updated start date.
        effective_until: Updated end date.
        is_active: Updated active toggle.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    city: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Updated city",
    )
    minimum_price: float | None = Field(
        default=None,
        ge=0.0,
        le=500000.0,
        description="Updated floor price",
    )
    average_market_price: float | None = Field(
        default=None,
        ge=0.0,
        le=500000.0,
        description="Updated market rate",
    )
    maximum_price: float | None = Field(
        default=None,
        ge=0.0,
        le=500000.0,
        description="Updated ceiling price",
    )
    inspection_charge: float | None = Field(
        default=None,
        ge=0.0,
        le=50000.0,
        description="Updated inspection fee",
    )
    emergency_charge_percentage: float | None = Field(
        default=None,
        ge=0.0,
        le=100.0,
        description="Updated emergency surcharge (%)",
    )
    price_tolerance_percentage: float | None = Field(
        default=None,
        ge=0.0,
        le=50.0,
        description="Updated tolerance (%)",
    )
    currency: Currency | None = Field(
        default=None,
        description="Updated currency",
    )
    effective_from: datetime | None = Field(
        default=None,
        description="Updated start date",
    )
    effective_until: datetime | None = Field(
        default=None,
        description="Updated end date",
    )
    is_active: bool | None = Field(
        default=None,
        description="Updated active toggle",
    )

    # --- Validators ---

    @field_validator("city")
    @classmethod
    def normalize_city(cls, value: str | None) -> str | None:
        if value is not None:
            return _normalize_city(value)
        return value

    @model_validator(mode="after")
    def validate_price_hierarchy(self) -> "PriceGuideUpdateRequest":
        """
        Validate price ordering when all three prices are provided.

        Partial price updates are validated by the service layer
        against existing document values.
        """
        prices = [self.minimum_price, self.average_market_price, self.maximum_price]
        if all(p is not None for p in prices):
            assert self.minimum_price is not None
            assert self.average_market_price is not None
            assert self.maximum_price is not None
            if self.minimum_price > self.average_market_price:
                raise ValueError(
                    f"minimum_price ({self.minimum_price}) cannot exceed "
                    f"average_market_price ({self.average_market_price})"
                )
            if self.average_market_price > self.maximum_price:
                raise ValueError(
                    f"average_market_price ({self.average_market_price}) cannot "
                    f"exceed maximum_price ({self.maximum_price})"
                )
        return self

    @model_validator(mode="after")
    def validate_date_range(self) -> "PriceGuideUpdateRequest":
        """Validate date ordering when both dates are provided."""
        if (
            self.effective_from is not None
            and self.effective_until is not None
            and self.effective_from >= self.effective_until
        ):
            raise ValueError(
                "effective_from must be earlier than effective_until"
            )
        return self

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "PriceGuideUpdateRequest":
        """Reject empty update requests."""
        provided = {
            field_name
            for field_name in self.model_fields
            if getattr(self, field_name) is not None
        }
        if not provided:
            raise ValueError("At least one field must be provided for update")
        return self


# ---------------------------------------------------------------------------
# Pricing Configuration Schemas
# ---------------------------------------------------------------------------

class PricingConfigurationCreateRequest(BaseModel):
    """
    Create a new platform-wide pricing configuration.

    The service layer should:
        1. Deactivate any existing active configuration.
        2. Validate commission split (platform + worker ≤ 100%).
        3. Set is_active = True for the new config.

    Attributes:
        default_price_tolerance: Fallback tolerance (%).
        default_inspection_charge: Fallback inspection fee.
        default_emergency_charge: Fallback emergency surcharge (%).
        gst_percentage: GST rate (%).
        platform_commission_percentage: Platform's cut (%).
        worker_commission_percentage: Worker's share (%).
        customer_service_fee: Fixed service fee.
        surge_pricing_enabled: Surge pricing toggle.
        weekend_multiplier: Weekend price multiplier.
        night_multiplier: Night price multiplier.
        holiday_multiplier: Holiday price multiplier.
        is_active: Active toggle.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    # --- Default Charges ---
    default_price_tolerance: float = Field(
        default=10.0,
        ge=0.0,
        le=50.0,
        description="Fallback tolerance (%)",
    )
    default_inspection_charge: float = Field(
        default=99.0,
        ge=0.0,
        le=50000.0,
        description="Fallback inspection fee",
    )
    default_emergency_charge: float = Field(
        default=25.0,
        ge=0.0,
        le=100.0,
        description="Fallback emergency surcharge (%)",
    )

    # --- Tax & Commission ---
    gst_percentage: float = Field(
        default=18.0,
        ge=0.0,
        le=50.0,
        description="GST rate (%)",
    )
    platform_commission_percentage: float = Field(
        default=20.0,
        ge=0.0,
        le=50.0,
        description="Platform commission (%)",
    )
    worker_commission_percentage: float = Field(
        default=80.0,
        ge=0.0,
        le=100.0,
        description="Worker's share (%)",
    )
    customer_service_fee: float = Field(
        default=29.0,
        ge=0.0,
        le=5000.0,
        description="Fixed customer service fee",
    )

    # --- Multipliers ---
    surge_pricing_enabled: bool = Field(
        default=False,
        description="Surge pricing toggle",
    )
    weekend_multiplier: float = Field(
        default=1.0,
        ge=0.5,
        le=3.0,
        description="Weekend multiplier (1.0 = no change)",
    )
    night_multiplier: float = Field(
        default=1.0,
        ge=0.5,
        le=3.0,
        description="Night multiplier (1.0 = no change)",
    )
    holiday_multiplier: float = Field(
        default=1.0,
        ge=0.5,
        le=5.0,
        description="Holiday multiplier (1.0 = no change)",
    )

    # --- Status ---
    is_active: bool = Field(
        default=True,
        description="Active toggle",
    )

    # --- Validators ---

    @model_validator(mode="after")
    def validate_commission_split(self) -> "PricingConfigurationCreateRequest":
        """
        Ensure platform + worker commission ≤ 100%.

        If they exceed 100%, more money would be paid out than received.
        Allows < 100% for cases where part goes to tax/reserves.
        """
        total = self.platform_commission_percentage + self.worker_commission_percentage
        if total > 100.0:
            raise ValueError(
                f"platform_commission ({self.platform_commission_percentage}%) + "
                f"worker_commission ({self.worker_commission_percentage}%) = "
                f"{total}% — cannot exceed 100%"
            )
        return self


class PricingConfigurationUpdateRequest(BaseModel):
    """
    Partial update for an existing pricing configuration.

    All fields optional. At least one must be provided.
    Commission split is validated when both percentages are provided;
    partial commission updates are validated by the service layer.

    Attributes:
        default_price_tolerance: Updated tolerance.
        default_inspection_charge: Updated inspection fee.
        default_emergency_charge: Updated emergency surcharge.
        gst_percentage: Updated GST rate.
        platform_commission_percentage: Updated platform commission.
        worker_commission_percentage: Updated worker share.
        customer_service_fee: Updated service fee.
        surge_pricing_enabled: Updated surge toggle.
        weekend_multiplier: Updated weekend multiplier.
        night_multiplier: Updated night multiplier.
        holiday_multiplier: Updated holiday multiplier.
        is_active: Updated active toggle.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    default_price_tolerance: float | None = Field(
        default=None, ge=0.0, le=50.0, description="Updated tolerance (%)",
    )
    default_inspection_charge: float | None = Field(
        default=None, ge=0.0, le=50000.0, description="Updated inspection fee",
    )
    default_emergency_charge: float | None = Field(
        default=None, ge=0.0, le=100.0, description="Updated emergency surcharge (%)",
    )
    gst_percentage: float | None = Field(
        default=None, ge=0.0, le=50.0, description="Updated GST (%)",
    )
    platform_commission_percentage: float | None = Field(
        default=None, ge=0.0, le=50.0, description="Updated platform commission (%)",
    )
    worker_commission_percentage: float | None = Field(
        default=None, ge=0.0, le=100.0, description="Updated worker share (%)",
    )
    customer_service_fee: float | None = Field(
        default=None, ge=0.0, le=5000.0, description="Updated service fee",
    )
    surge_pricing_enabled: bool | None = Field(
        default=None, description="Updated surge toggle",
    )
    weekend_multiplier: float | None = Field(
        default=None, ge=0.5, le=3.0, description="Updated weekend multiplier",
    )
    night_multiplier: float | None = Field(
        default=None, ge=0.5, le=3.0, description="Updated night multiplier",
    )
    holiday_multiplier: float | None = Field(
        default=None, ge=0.5, le=5.0, description="Updated holiday multiplier",
    )
    is_active: bool | None = Field(
        default=None, description="Updated active toggle",
    )

    # --- Validators ---

    @model_validator(mode="after")
    def validate_commission_split(self) -> "PricingConfigurationUpdateRequest":
        """Validate commission split when both percentages are provided."""
        if (
            self.platform_commission_percentage is not None
            and self.worker_commission_percentage is not None
        ):
            total = (
                self.platform_commission_percentage
                + self.worker_commission_percentage
            )
            if total > 100.0:
                raise ValueError(
                    f"platform_commission ({self.platform_commission_percentage}%) + "
                    f"worker_commission ({self.worker_commission_percentage}%) = "
                    f"{total}% — cannot exceed 100%"
                )
        return self

    @model_validator(mode="after")
    def check_at_least_one_field(self) -> "PricingConfigurationUpdateRequest":
        """Reject empty update requests."""
        provided = {
            field_name
            for field_name in self.model_fields
            if getattr(self, field_name) is not None
        }
        if not provided:
            raise ValueError("At least one field must be provided for update")
        return self


# ---------------------------------------------------------------------------
# Response Schemas
# ---------------------------------------------------------------------------

class PriceGuideResponse(BaseModel):
    """
    Service price guide representation in API responses.

    Includes computed fields for admin dashboard convenience.

    Attributes:
        id: Document ID.
        service_id: Service reference.
        city: City name.
        minimum_price: Floor price.
        average_market_price: Market rate.
        maximum_price: Ceiling price.
        inspection_charge: Inspection fee.
        emergency_charge_percentage: Emergency surcharge (%).
        price_tolerance_percentage: Quote tolerance (%).
        currency: Currency code.
        effective_from: Validity start.
        effective_until: Validity end.
        is_active: Active status.
        price_range_display: Formatted range (computed).
        is_currently_valid: Within validity period (computed).
        created_at: Creation time.
        updated_at: Last update time.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="Price guide ID",
        examples=["60d5ec49f1a2c8b1f8e4e1a3"],
    )
    service_id: str = Field(..., description="Service reference")
    city: str = Field(..., description="City name")

    # --- Prices ---
    minimum_price: float = Field(..., description="Floor price")
    average_market_price: float = Field(..., description="Market rate")
    maximum_price: float = Field(..., description="Ceiling price")

    # --- Charges ---
    inspection_charge: float = Field(..., description="Inspection fee")
    emergency_charge_percentage: float = Field(..., description="Emergency %")
    price_tolerance_percentage: float = Field(..., description="Tolerance %")

    # --- Currency & Validity ---
    currency: Currency = Field(..., description="Currency code")
    effective_from: datetime = Field(..., description="Validity start")
    effective_until: datetime | None = Field(None, description="Validity end")
    is_active: bool = Field(..., description="Active status")

    # --- Computed ---
    price_range_display: str = Field(
        default="", description="Formatted price range",
    )
    is_currently_valid: bool = Field(
        default=False, description="Within validity period",
    )

    # --- Timestamps ---
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, value: object) -> str:
        """Convert Beanie PydanticObjectId to plain string."""
        return str(value)

    @model_validator(mode="before")
    @classmethod
    def compute_display_fields(cls, data: object) -> object:
        """Compute display fields from raw data."""
        if isinstance(data, dict):
            # Price range display
            min_p = data.get("minimum_price", 0)
            max_p = data.get("maximum_price", 0)
            currency = data.get("currency", "INR")
            symbol = "₹" if currency == "INR" or currency == Currency.INR else currency
            data["price_range_display"] = f"{symbol}{min_p:,.0f} – {symbol}{max_p:,.0f}"

            # Validity check
            from datetime import timezone
            now = datetime.now(timezone.utc)
            is_active = data.get("is_active", False)
            eff_from = data.get("effective_from")
            eff_until = data.get("effective_until")

            valid = is_active
            if valid and eff_from is not None and now < eff_from:
                valid = False
            if valid and eff_until is not None and now > eff_until:
                valid = False
            data["is_currently_valid"] = valid

        # For Beanie Documents: from_attributes reads @property directly
        return data


class PricingConfigurationResponse(BaseModel):
    """
    Pricing configuration representation in API responses.

    Includes computed commission_split_display for admin convenience.

    Attributes:
        id: Config ID.
        default_price_tolerance: Tolerance (%).
        default_inspection_charge: Inspection fee.
        default_emergency_charge: Emergency surcharge (%).
        gst_percentage: GST rate (%).
        platform_commission_percentage: Platform commission (%).
        worker_commission_percentage: Worker share (%).
        customer_service_fee: Service fee.
        surge_pricing_enabled: Surge toggle.
        weekend_multiplier: Weekend multiplier.
        night_multiplier: Night multiplier.
        holiday_multiplier: Holiday multiplier.
        is_active: Active status.
        commission_split_display: Formatted split (computed).
        created_at: Creation time.
        updated_at: Last update time.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(
        ...,
        description="Config ID",
        examples=["60d5ec49f1a2c8b1f8e4e1a4"],
    )

    # --- Default Charges ---
    default_price_tolerance: float = Field(..., description="Tolerance (%)")
    default_inspection_charge: float = Field(..., description="Inspection fee")
    default_emergency_charge: float = Field(..., description="Emergency %")

    # --- Tax & Commission ---
    gst_percentage: float = Field(..., description="GST (%)")
    platform_commission_percentage: float = Field(..., description="Platform %")
    worker_commission_percentage: float = Field(..., description="Worker %")
    customer_service_fee: float = Field(..., description="Service fee")

    # --- Multipliers ---
    surge_pricing_enabled: bool = Field(..., description="Surge toggle")
    weekend_multiplier: float = Field(..., description="Weekend multiplier")
    night_multiplier: float = Field(..., description="Night multiplier")
    holiday_multiplier: float = Field(..., description="Holiday multiplier")

    # --- Status ---
    is_active: bool = Field(..., description="Active status")

    # --- Computed ---
    commission_split_display: str = Field(
        default="", description="Formatted commission split",
    )

    # --- Timestamps ---
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_string(cls, value: object) -> str:
        """Convert Beanie PydanticObjectId to plain string."""
        return str(value)

    @model_validator(mode="before")
    @classmethod
    def compute_display_fields(cls, data: object) -> object:
        """Compute commission split display from raw data."""
        if isinstance(data, dict):
            platform = data.get("platform_commission_percentage", 0)
            worker = data.get("worker_commission_percentage", 0)
            data["commission_split_display"] = (
                f"Platform: {platform}% / Worker: {worker}%"
            )
        # For Beanie Documents: from_attributes reads @property directly
        return data
