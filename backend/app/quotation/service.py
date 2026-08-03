import math
from datetime import date, datetime, timedelta, timezone

from beanie import PydanticObjectId

from app.application.models import JobApplication
from app.auth.models import User, UserRole
from app.booking.models import Booking
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)
from app.application.models import JobApplication
from app.core.config import settings
from app.quotation.models import Quotation, QuotationHistory
from app.quotation.repository import QuotationRepository
from app.quotation.schemas import (
    AssignedWorkerResponse,
    CustomerQuotationResponse,
    QuotationAcceptResponse,
    QuotationCreateRequest,
    QuotationHistoryPaginatedResponse,
    QuotationHistoryResponse,
    QuotationPaginatedResponse,
    QuotationResponse,
    QuotationUpdateRequest,
    WorkerSummaryResponse,
)
from app.utils.enums import ApplicationStatus, BookingStatus, QuotationEventType, QuotationStatus
from app.worker.models import WorkerProfile


class QuotationService:
    """Business logic service layer for quotation management."""

    VALID_TRANSITIONS: dict[QuotationStatus, set[QuotationStatus]] = {
        QuotationStatus.DRAFT: {QuotationStatus.SUBMITTED, QuotationStatus.CANCELLED},
        QuotationStatus.SUBMITTED: {
            QuotationStatus.ACCEPTED,
            QuotationStatus.REJECTED,
            QuotationStatus.EXPIRED,
            QuotationStatus.CANCELLED,
        },
        QuotationStatus.ACCEPTED: set(),
        QuotationStatus.REJECTED: set(),
        QuotationStatus.EXPIRED: set(),
        QuotationStatus.CANCELLED: set(),
    }

    def __init__(self, repo: QuotationRepository | None = None) -> None:
        self.repo = repo or QuotationRepository()

    def _validate_status_transition(
        self, current: QuotationStatus, target: QuotationStatus
    ) -> None:
        """Centralized state machine transition validator."""
        if current == target:
            return
        allowed = self.VALID_TRANSITIONS.get(current, set())
        if target not in allowed:
            raise BadRequestException(
                message=f"Invalid quotation status transition from '{current.value}' to '{target.value}'",
                error_code="INVALID_QUOTATION_STATUS_TRANSITION",
            )

    async def _record_history_event(
        self,
        *,
        quotation: Quotation,
        actor_id: PydanticObjectId,
        actor_role: UserRole,
        event_type: QuotationEventType,
        previous_status: QuotationStatus | None = None,
        new_status: QuotationStatus,
        previous_snapshot: dict | None = None,
        notes: str | None = None,
    ) -> QuotationHistory:
        """
        Record an immutable audit history log for a quotation event.
        """
        new_snap = quotation.model_dump()
        new_snap["id"] = str(quotation.id)
        new_snap["booking_id"] = str(quotation.booking_id)
        new_snap["worker_id"] = str(quotation.worker_id)
        new_snap["application_id"] = str(quotation.application_id)
        new_snap["quotation_status"] = (
            quotation.quotation_status.value
            if isinstance(quotation.quotation_status, QuotationStatus)
            else str(quotation.quotation_status)
        )
        if isinstance(new_snap.get("validity_date"), date):
            new_snap["validity_date"] = new_snap["validity_date"].isoformat()
        if isinstance(new_snap.get("work_start_date"), date):
            new_snap["work_start_date"] = new_snap["work_start_date"].isoformat()
        if isinstance(new_snap.get("created_at"), datetime):
            new_snap["created_at"] = new_snap["created_at"].isoformat()
        if isinstance(new_snap.get("updated_at"), datetime):
            new_snap["updated_at"] = new_snap["updated_at"].isoformat()
        if isinstance(new_snap.get("submitted_at"), datetime):
            new_snap["submitted_at"] = new_snap["submitted_at"].isoformat()

        history_doc = QuotationHistory(
            quotation_id=quotation.id,
            booking_id=quotation.booking_id,
            worker_id=quotation.worker_id,
            actor_id=actor_id,
            actor_role=actor_role,
            event_type=event_type,
            previous_status=previous_status,
            new_status=new_status,
            previous_snapshot=previous_snapshot,
            new_snapshot=new_snap,
            notes=notes,
        )
        return await history_doc.insert()

    async def _check_and_apply_auto_expiry(self, q: Quotation) -> Quotation:
        """If a SUBMITTED quotation has passed its validity_date, transition it to EXPIRED."""
        if q.quotation_status == QuotationStatus.SUBMITTED and q.validity_date < date.today():
            prev_status = q.quotation_status
            prev_snap = q.model_dump()
            prev_snap["id"] = str(q.id)
            prev_snap["quotation_status"] = prev_status.value
            if isinstance(prev_snap.get("validity_date"), date):
                prev_snap["validity_date"] = prev_snap["validity_date"].isoformat()
            if isinstance(prev_snap.get("created_at"), datetime):
                prev_snap["created_at"] = prev_snap["created_at"].isoformat()

            self._validate_status_transition(prev_status, QuotationStatus.EXPIRED)
            q.quotation_status = QuotationStatus.EXPIRED
            await q.save()

            await self._record_history_event(
                quotation=q,
                actor_id=q.worker_id,
                actor_role=UserRole.WORKER,
                event_type=QuotationEventType.EXPIRED,
                previous_status=prev_status,
                new_status=QuotationStatus.EXPIRED,
                previous_snapshot=prev_snap,
                notes="Quotation validity date expired automatically",
            )
        return q

    def _to_response(self, q: Quotation) -> QuotationResponse:
        """Map Quotation document to public DTO."""
        return QuotationResponse(
            id=str(q.id),
            quotation_number=q.quotation_number,
            booking_id=str(q.booking_id),
            worker_id=str(q.worker_id),
            application_id=str(q.application_id),
            quotation_status=q.quotation_status,
            labour_cost=q.labour_cost,
            material_cost=q.material_cost,
            inspection_charge=q.inspection_charge,
            additional_charges=q.additional_charges,
            tax_amount=q.tax_amount,
            discount_amount=q.discount_amount,
            total_amount=q.total_amount,
            estimated_duration=q.estimated_duration,
            validity_date=q.validity_date,
            work_start_date=q.work_start_date,
            work_description=q.work_description,
            terms_and_conditions=q.terms_and_conditions,
            notes=q.notes,
            created_at=q.created_at,
            updated_at=q.updated_at,
            submitted_at=q.submitted_at,
        )

    async def create_quotation(
        self, worker: User, payload: QuotationCreateRequest
    ) -> QuotationResponse:
        """
        Create a new quotation for a marketplace job application.
        """
        if not worker.is_active:
            raise ForbiddenException(
                message="Inactive worker cannot submit quotations",
                error_code="WORKER_INACTIVE",
            )

        if not PydanticObjectId.is_valid(payload.booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{payload.booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )
        if not PydanticObjectId.is_valid(payload.application_id):
            raise BadRequestException(
                message=f"Invalid application ID format '{payload.application_id}'",
                error_code="INVALID_APPLICATION_ID",
            )

        booking_id = PydanticObjectId(payload.booking_id)
        application_id = PydanticObjectId(payload.application_id)

        # 1. Verify booking exists and is pending
        booking = await Booking.get(booking_id)
        if not booking:
            raise NotFoundException(
                message=f"Booking '{payload.booking_id}' not found",
                error_code="BOOKING_NOT_FOUND",
            )
        if booking.status == BookingStatus.CANCELLED:
            raise BadRequestException(
                message=f"Booking '{payload.booking_id}' is cancelled and cannot receive quotations",
                error_code="BOOKING_CANCELLED",
            )
        if booking.status == BookingStatus.ACCEPTED or booking.worker_id is not None:
            raise BadRequestException(
                message=f"Booking '{payload.booking_id}' is already assigned and cannot receive quotations",
                error_code="BOOKING_ALREADY_ASSIGNED",
            )
        if booking.status != BookingStatus.PENDING:
            raise BadRequestException(
                message=f"Booking '{payload.booking_id}' is no longer available for quotations",
                error_code="BOOKING_NOT_AVAILABLE",
            )

        # 2. Verify job application exists and belongs to this worker & booking
        app = await JobApplication.get(application_id)
        if not app:
            raise NotFoundException(
                message=f"Job application '{payload.application_id}' not found",
                error_code="APPLICATION_NOT_FOUND",
            )

        if app.booking_id != booking_id or app.worker_id != worker.id:
            raise ForbiddenException(
                message="Job application does not match the specified booking and worker",
                error_code="APPLICATION_MISMATCH",
            )

        # 3. Validate dates
        today = date.today()
        if payload.validity_date < today:
            raise BadRequestException(
                message="Validity date cannot be in the past",
                error_code="INVALID_VALIDITY_DATE",
            )
        max_valid_date = today + timedelta(days=settings.QUOTATION_MAX_VALIDITY_DAYS)
        if payload.validity_date > max_valid_date:
            raise BadRequestException(
                message=f"Validity date cannot exceed {settings.QUOTATION_MAX_VALIDITY_DAYS} days from today",
                error_code="INVALID_VALIDITY_DATE",
            )

        # 4. Calculate subtotal and total amount
        total_amount = (
            payload.labour_cost
            + payload.material_cost
            + payload.inspection_charge
            + payload.additional_charges
            + payload.tax_amount
            - payload.discount_amount
        )
        if total_amount > settings.QUOTATION_MAX_PRICE:
            raise BadRequestException(
                message=f"Total quotation amount cannot exceed ₹{settings.QUOTATION_MAX_PRICE:,.0f}",
                error_code="EXCEEDS_MAX_PRICE",
            )

        # 5. Check for existing quotation for this application
        existing = await Quotation.find_one({"application_id": application_id, "worker_id": worker.id})
        if existing:
            if existing.quotation_status != QuotationStatus.DRAFT:
                raise ConflictException(
                    message="A quotation has already been submitted for this application",
                    error_code="QUOTATION_ALREADY_SUBMITTED",
                )
            target_status = QuotationStatus.DRAFT if payload.is_draft else QuotationStatus.SUBMITTED
            self._validate_status_transition(existing.quotation_status, target_status)

            existing.labour_cost = payload.labour_cost
            existing.material_cost = payload.material_cost
            existing.inspection_charge = payload.inspection_charge
            existing.additional_charges = payload.additional_charges
            existing.tax_amount = payload.tax_amount
            existing.discount_amount = payload.discount_amount
            existing.total_amount = total_amount
            existing.estimated_duration = payload.estimated_duration
            existing.validity_date = payload.validity_date
            existing.work_start_date = payload.work_start_date
            existing.work_description = payload.work_description
            existing.terms_and_conditions = payload.terms_and_conditions
            existing.notes = payload.notes

            if not payload.is_draft:
                existing.quotation_status = QuotationStatus.SUBMITTED
                existing.submitted_at = datetime.now(timezone.utc)

            saved = await existing.save()
            return self._to_response(saved)

        # 6. Generate unique quotation number
        q_num = await self.repo.generate_quotation_number()

        now = datetime.now(timezone.utc)
        status = QuotationStatus.DRAFT if payload.is_draft else QuotationStatus.SUBMITTED
        submitted_at = None if payload.is_draft else now

        quotation = Quotation(
            quotation_number=q_num,
            booking_id=booking_id,
            worker_id=worker.id,
            application_id=application_id,
            quotation_status=status,
            labour_cost=payload.labour_cost,
            material_cost=payload.material_cost,
            inspection_charge=payload.inspection_charge,
            additional_charges=payload.additional_charges,
            tax_amount=payload.tax_amount,
            discount_amount=payload.discount_amount,
            total_amount=total_amount,
            estimated_duration=payload.estimated_duration,
            validity_date=payload.validity_date,
            work_start_date=payload.work_start_date,
            work_description=payload.work_description,
            terms_and_conditions=payload.terms_and_conditions,
            notes=payload.notes,
            created_at=now,
            updated_at=now,
            submitted_at=submitted_at,
        )

        saved = await self.repo.create_quotation(quotation)

        await self._record_history_event(
            quotation=saved,
            actor_id=worker.id,
            actor_role=worker.role,
            event_type=QuotationEventType.CREATED,
            previous_status=None,
            new_status=saved.quotation_status,
            previous_snapshot=None,
            notes="Draft quotation created by worker" if payload.is_draft else "Quotation created and submitted by worker",
        )

        if not payload.is_draft:
            await self._record_history_event(
                quotation=saved,
                actor_id=worker.id,
                actor_role=worker.role,
                event_type=QuotationEventType.SUBMITTED,
                previous_status=QuotationStatus.DRAFT,
                new_status=QuotationStatus.SUBMITTED,
                previous_snapshot=None,
                notes="Quotation submitted to customer",
            )

        return self._to_response(saved)

    async def update_quotation(
        self, worker: User, quotation_id: str, payload: QuotationUpdateRequest
    ) -> QuotationResponse:
        """
        Update an existing draft quotation or submit it. Read-only if already submitted.
        """
        if not worker.is_active:
            raise ForbiddenException(
                message="Inactive worker cannot update quotations",
                error_code="WORKER_INACTIVE",
            )

        q = await self.repo.get_quotation_by_id(quotation_id)
        if not q:
            raise NotFoundException(
                message=f"Quotation '{quotation_id}' not found",
                error_code="QUOTATION_NOT_FOUND",
            )

        if q.worker_id != worker.id:
            raise ForbiddenException(
                message="You are not authorized to update this quotation",
                error_code="UNAUTHORIZED_QUOTATION_ACCESS",
            )

        # STRICT READ-ONLY CHECK FOR SUBMITTED QUOTATIONS
        if q.quotation_status != QuotationStatus.DRAFT:
            raise BadRequestException(
                message="Submitted quotations are read-only and cannot be modified",
                error_code="QUOTATION_READ_ONLY",
            )

        prev_status = q.quotation_status
        prev_snap = q.model_dump()
        prev_snap["id"] = str(q.id)
        prev_snap["booking_id"] = str(q.booking_id)
        prev_snap["worker_id"] = str(q.worker_id)
        prev_snap["application_id"] = str(q.application_id)
        prev_snap["quotation_status"] = (
            prev_status.value if isinstance(prev_status, QuotationStatus) else str(prev_status)
        )
        if isinstance(prev_snap.get("validity_date"), date):
            prev_snap["validity_date"] = prev_snap["validity_date"].isoformat()
        if isinstance(prev_snap.get("created_at"), datetime):
            prev_snap["created_at"] = prev_snap["created_at"].isoformat()

        if payload.labour_cost is not None:
            q.labour_cost = payload.labour_cost
        if payload.material_cost is not None:
            q.material_cost = payload.material_cost
        if payload.inspection_charge is not None:
            q.inspection_charge = payload.inspection_charge
        if payload.additional_charges is not None:
            q.additional_charges = payload.additional_charges
        if payload.tax_amount is not None:
            q.tax_amount = payload.tax_amount
        if payload.discount_amount is not None:
            q.discount_amount = payload.discount_amount

        subtotal = (
            q.labour_cost
            + q.material_cost
            + q.inspection_charge
            + q.additional_charges
            + q.tax_amount
        )
        if q.discount_amount > subtotal:
            raise BadRequestException(
                message="Discount amount cannot exceed the subtotal costs",
                error_code="INVALID_DISCOUNT",
            )

        q.total_amount = subtotal - q.discount_amount
        if q.total_amount > settings.QUOTATION_MAX_PRICE:
            raise BadRequestException(
                message=f"Total quotation amount cannot exceed ₹{settings.QUOTATION_MAX_PRICE:,.0f}",
                error_code="EXCEEDS_MAX_PRICE",
            )

        if payload.estimated_duration is not None:
            q.estimated_duration = payload.estimated_duration
        if payload.validity_date is not None:
            today = date.today()
            if payload.validity_date < today:
                raise BadRequestException(
                    message="Validity date cannot be in the past",
                    error_code="INVALID_VALIDITY_DATE",
                )
            max_valid_date = today + timedelta(days=settings.QUOTATION_MAX_VALIDITY_DAYS)
            if payload.validity_date > max_valid_date:
                raise BadRequestException(
                    message=f"Validity date cannot exceed {settings.QUOTATION_MAX_VALIDITY_DAYS} days from today",
                    error_code="INVALID_VALIDITY_DATE",
                )
            q.validity_date = payload.validity_date

        if payload.work_start_date is not None:
            q.work_start_date = payload.work_start_date
        if payload.work_description is not None:
            q.work_description = payload.work_description
        if payload.terms_and_conditions is not None:
            q.terms_and_conditions = payload.terms_and_conditions
        if payload.notes is not None:
            q.notes = payload.notes

        if payload.submit_now:
            self._validate_status_transition(q.quotation_status, QuotationStatus.SUBMITTED)
            q.quotation_status = QuotationStatus.SUBMITTED
            q.submitted_at = datetime.now(timezone.utc)

        saved = await self.repo.update_quotation(q)

        await self._record_history_event(
            quotation=saved,
            actor_id=worker.id,
            actor_role=worker.role,
            event_type=QuotationEventType.UPDATED,
            previous_status=prev_status,
            new_status=saved.quotation_status,
            previous_snapshot=prev_snap,
            notes="Quotation updated by worker",
        )

        if payload.submit_now:
            await self._record_history_event(
                quotation=saved,
                actor_id=worker.id,
                actor_role=worker.role,
                event_type=QuotationEventType.SUBMITTED,
                previous_status=prev_status,
                new_status=QuotationStatus.SUBMITTED,
                previous_snapshot=prev_snap,
                notes="Quotation submitted to customer",
            )

        return self._to_response(saved)

    async def get_quotation_detail(
        self, user: User, quotation_id: str
    ) -> QuotationResponse:
        """
        Retrieve quotation details by ID.
        """
        q = await self.repo.get_quotation_by_id(quotation_id)
        if not q:
            raise NotFoundException(
                message=f"Quotation '{quotation_id}' not found",
                error_code="QUOTATION_NOT_FOUND",
            )

        # Access check: worker who created it, or admin, or customer of the booking
        if user.role == UserRole.WORKER and q.worker_id != user.id:
            raise ForbiddenException(
                message="You are not authorized to view this quotation",
                error_code="UNAUTHORIZED_QUOTATION_ACCESS",
            )

        if user.role == UserRole.CUSTOMER:
            booking = await Booking.get(q.booking_id)
            if not booking or booking.customer_id != user.id:
                raise ForbiddenException(
                    message="You are not authorized to view this quotation",
                    error_code="UNAUTHORIZED_QUOTATION_ACCESS",
                )

        return self._to_response(q)

    async def get_quotation_by_application(
        self, user: User, application_id: str
    ) -> QuotationResponse | None:
        """
        Find quotation associated with a specific job application ID.
        """
        if not PydanticObjectId.is_valid(application_id):
            raise BadRequestException(
                message=f"Invalid application ID format '{application_id}'",
                error_code="INVALID_APPLICATION_ID",
            )

        aid = PydanticObjectId(application_id)
        q = await Quotation.find_one({"application_id": aid})
        if not q:
            return None

        if user.role == UserRole.WORKER and q.worker_id != user.id:
            raise ForbiddenException(
                message="You are not authorized to view this quotation",
                error_code="UNAUTHORIZED_QUOTATION_ACCESS",
            )

        return self._to_response(q)

    async def list_worker_quotations(
        self,
        worker: User,
        status: QuotationStatus | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> QuotationPaginatedResponse:
        """
        List quotations submitted by the authenticated worker.
        """
        page = max(1, page)
        page_size = max(1, min(100, page_size))
        skip = (page - 1) * page_size

        items, total = await self.repo.list_quotations_by_worker(
            worker_id=worker.id, status=status, skip=skip, limit=page_size
        )

        dtos = [self._to_response(q) for q in items]
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        return QuotationPaginatedResponse(
            items=dtos,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    async def list_booking_quotations(
        self,
        user: User,
        booking_id: str,
        status: QuotationStatus | None = None,
    ) -> list[QuotationResponse]:
        """
        List all quotations associated with a booking.
        """
        if not PydanticObjectId.is_valid(booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )

        bid = PydanticObjectId(booking_id)
        booking = await Booking.get(bid)
        if not booking:
            raise NotFoundException(
                message=f"Booking '{booking_id}' not found",
                error_code="BOOKING_NOT_FOUND",
            )

        # Access check
        if user.role == UserRole.CUSTOMER and booking.customer_id != user.id:
            raise ForbiddenException(
                message="You are not authorized to view quotations for this booking",
                error_code="UNAUTHORIZED_QUOTATION_ACCESS",
            )

        items = await self.repo.list_quotations_by_booking(bid, status=status)
        return [self._to_response(q) for q in items]

    async def _build_customer_response(self, q: Quotation) -> CustomerQuotationResponse:
        """Attach worker user & profile information to quotation DTO for customers."""
        base_dto = self._to_response(q)
        worker_user = await User.get(q.worker_id)
        worker_profile = await WorkerProfile.find_one(WorkerProfile.user_id == q.worker_id)

        full_name = worker_user.full_name if worker_user else "Professional Worker"
        photo = worker_profile.profile_photo_url if worker_profile else None
        rating = worker_profile.rating if worker_profile else 5.0
        experience = worker_profile.experience_years if worker_profile else 0.0
        skills = worker_profile.skills if worker_profile else []

        worker_summary = WorkerSummaryResponse(
            id=str(q.worker_id),
            full_name=full_name,
            profile_photo_url=photo,
            rating=rating,
            experience_years=experience,
            skills=skills,
        )

        return CustomerQuotationResponse(
            **base_dto.model_dump(),
            worker=worker_summary,
        )

    async def list_booking_quotations_for_customer(
        self, customer: User, booking_id: str
    ) -> list[CustomerQuotationResponse]:
        """
        Retrieve all submitted quotations for a customer's booking.
        DRAFT quotations are strictly excluded.
        """
        if not PydanticObjectId.is_valid(booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )

        bid = PydanticObjectId(booking_id)
        booking = await Booking.get(bid)
        if not booking:
            raise NotFoundException(
                message=f"Booking '{booking_id}' not found",
                error_code="BOOKING_NOT_FOUND",
            )

        # STRICT OWNERSHIP CHECK
        if customer.role != UserRole.ADMIN and booking.customer_id != customer.id:
            raise ForbiddenException(
                message="You are not authorized to view quotations for this booking",
                error_code="UNAUTHORIZED_QUOTATION_ACCESS",
            )

        # Query all non-draft quotations for this booking
        quotes = await Quotation.find(
            {"booking_id": bid, "quotation_status": {"$ne": QuotationStatus.DRAFT.value}}
        ).sort("-created_at").to_list()

        results = []
        for q in quotes:
            q = await self._check_and_apply_auto_expiry(q)
            c_dto = await self._build_customer_response(q)
            results.append(c_dto)

        return results

    async def get_customer_quotation_detail(
        self, customer: User, quotation_id: str
    ) -> CustomerQuotationResponse:
        """
        Retrieve details of a single quotation for a customer.
        """
        q = await self.repo.get_quotation_by_id(quotation_id)
        if not q:
            raise NotFoundException(
                message=f"Quotation '{quotation_id}' not found",
                error_code="QUOTATION_NOT_FOUND",
            )

        booking = await Booking.get(q.booking_id)
        if not booking or (customer.role != UserRole.ADMIN and booking.customer_id != customer.id):
            raise ForbiddenException(
                message="You are not authorized to view this quotation",
                error_code="UNAUTHORIZED_QUOTATION_ACCESS",
            )

        q = await self._check_and_apply_auto_expiry(q)
        return await self._build_customer_response(q)

    async def accept_quotation(
        self, customer: User, quotation_id: str
    ) -> QuotationAcceptResponse:
        """
        Accept a quotation and assign the worker to the booking atomically.
        """
        q = await self.repo.get_quotation_by_id(quotation_id)
        if not q:
            raise NotFoundException(
                message=f"Quotation '{quotation_id}' not found",
                error_code="QUOTATION_NOT_FOUND",
            )

        booking = await Booking.get(q.booking_id)
        if not booking:
            raise NotFoundException(
                message="Associated booking not found",
                error_code="BOOKING_NOT_FOUND",
            )

        # 1. Customer Ownership Check
        if customer.role != UserRole.ADMIN and booking.customer_id != customer.id:
            raise ForbiddenException(
                message="You are not authorized to accept quotations for this booking",
                error_code="UNAUTHORIZED_QUOTATION_ACCESS",
            )

        # 2. Check and apply auto expiry
        q = await self._check_and_apply_auto_expiry(q)

        # 3. Booking Status Validation
        if booking.status == BookingStatus.CANCELLED:
            raise BadRequestException(
                message="Cannot accept quotation for a cancelled booking",
                error_code="BOOKING_CANCELLED",
            )
        if booking.status == BookingStatus.ACCEPTED or booking.worker_id is not None:
            raise ConflictException(
                message="A quotation has already been accepted for this booking",
                error_code="QUOTATION_ALREADY_ACCEPTED",
            )
        if booking.status != BookingStatus.PENDING:
            raise BadRequestException(
                message=f"Booking is not in PENDING state (current: {booking.status.value})",
                error_code="BOOKING_NOT_PENDING",
            )

        # 4. Quotation Status & Expiration Validation
        if q.quotation_status == QuotationStatus.DRAFT:
            raise BadRequestException(
                message="Cannot accept a draft quotation",
                error_code="QUOTATION_NOT_SUBMITTED",
            )
        if q.quotation_status == QuotationStatus.CANCELLED:
            raise BadRequestException(
                message="Cannot accept a cancelled quotation",
                error_code="QUOTATION_CANCELLED",
            )
        if q.quotation_status == QuotationStatus.REJECTED:
            raise BadRequestException(
                message="Cannot accept a rejected quotation",
                error_code="QUOTATION_REJECTED",
            )
        if q.quotation_status == QuotationStatus.EXPIRED or q.validity_date < date.today():
            raise BadRequestException(
                message="Quotation validity date has expired",
                error_code="QUOTATION_EXPIRED",
            )

        self._validate_status_transition(q.quotation_status, QuotationStatus.ACCEPTED)

        # 4. Worker Active Check
        worker_user = await User.get(q.worker_id)
        if not worker_user or not worker_user.is_active:
            raise ForbiddenException(
                message="Worker account is inactive",
                error_code="WORKER_INACTIVE",
            )

        # 5. Application Check
        application = await JobApplication.get(q.application_id)
        if not application or application.application_status == ApplicationStatus.WITHDRAWN:
            raise BadRequestException(
                message="Associated job application is no longer active",
                error_code="APPLICATION_INACTIVE",
            )

        now_utc = datetime.now(timezone.utc)

        prev_status = q.quotation_status
        prev_snap = q.model_dump()
        prev_snap["id"] = str(q.id)
        prev_snap["booking_id"] = str(q.booking_id)
        prev_snap["worker_id"] = str(q.worker_id)
        prev_snap["application_id"] = str(q.application_id)
        prev_snap["quotation_status"] = (
            prev_status.value if isinstance(prev_status, QuotationStatus) else str(prev_status)
        )
        if isinstance(prev_snap.get("validity_date"), date):
            prev_snap["validity_date"] = prev_snap["validity_date"].isoformat()
        if isinstance(prev_snap.get("created_at"), datetime):
            prev_snap["created_at"] = prev_snap["created_at"].isoformat()

        # ATOMIC STEP 1: Accept target quotation
        q.quotation_status = QuotationStatus.ACCEPTED
        await q.save()

        # Record ACCEPTED and WORKER_ASSIGNED audit events
        await self._record_history_event(
            quotation=q,
            actor_id=customer.id,
            actor_role=customer.role,
            event_type=QuotationEventType.ACCEPTED,
            previous_status=prev_status,
            new_status=QuotationStatus.ACCEPTED,
            previous_snapshot=prev_snap,
            notes=f"Quotation accepted by customer {customer.full_name}",
        )

        await self._record_history_event(
            quotation=q,
            actor_id=customer.id,
            actor_role=customer.role,
            event_type=QuotationEventType.WORKER_ASSIGNED,
            previous_status=prev_status,
            new_status=QuotationStatus.ACCEPTED,
            previous_snapshot=prev_snap,
            notes=f"Worker {worker_user.full_name} assigned to booking {booking.booking_number}",
        )

        # ATOMIC STEP 2: Update target booking (Assigns worker & removes from marketplace)
        booking.status = BookingStatus.ACCEPTED
        booking.worker_id = q.worker_id
        booking.assigned_at = now_utc
        booking.quotation_id = q.id
        booking.final_price = q.total_amount
        await booking.save()

        # ATOMIC STEP 3: Accept target job application
        application.application_status = ApplicationStatus.ACCEPTED
        await application.save()

        # ATOMIC STEP 4: Reject all OTHER quotations for this booking
        other_quotes = await Quotation.find(
            {"booking_id": booking.id, "_id": {"$ne": q.id}}
        ).to_list()
        for o_q in other_quotes:
            o_q_prev_status = o_q.quotation_status
            o_q_prev_snap = o_q.model_dump()
            o_q_prev_snap["id"] = str(o_q.id)
            o_q_prev_snap["quotation_status"] = (
                o_q_prev_status.value if isinstance(o_q_prev_status, QuotationStatus) else str(o_q_prev_status)
            )

            o_q.quotation_status = QuotationStatus.REJECTED
            await o_q.save()

            await self._record_history_event(
                quotation=o_q,
                actor_id=customer.id,
                actor_role=customer.role,
                event_type=QuotationEventType.REJECTED,
                previous_status=o_q_prev_status,
                new_status=QuotationStatus.REJECTED,
                previous_snapshot=o_q_prev_snap,
                notes="Automatically rejected because another quotation was accepted",
            )

        # ATOMIC STEP 5: Reject all OTHER job applications for this booking
        other_apps = await JobApplication.find(
            {"booking_id": booking.id, "_id": {"$ne": application.id}}
        ).to_list()
        for o_app in other_apps:
            o_app.application_status = ApplicationStatus.REJECTED
            await o_app.save()

        return QuotationAcceptResponse(
            booking_id=str(booking.id),
            quotation_id=str(q.id),
            worker_id=str(q.worker_id),
            booking_status=booking.status.value,
            quotation_status=q.quotation_status.value,
            final_price=q.total_amount,
            message="Quotation accepted and worker assigned successfully.",
        )

    async def reject_quotation(
        self, customer: User, quotation_id: str
    ) -> CustomerQuotationResponse:
        """
        Explicitly reject a quotation by customer.
        """
        q = await self.repo.get_quotation_by_id(quotation_id)
        if not q:
            raise NotFoundException(
                message=f"Quotation '{quotation_id}' not found",
                error_code="QUOTATION_NOT_FOUND",
            )

        booking = await Booking.get(q.booking_id)
        if not booking or (customer.role != UserRole.ADMIN and booking.customer_id != customer.id):
            raise ForbiddenException(
                message="You are not authorized to reject this quotation",
                error_code="UNAUTHORIZED_QUOTATION_ACCESS",
            )

        if q.quotation_status == QuotationStatus.ACCEPTED:
            raise BadRequestException(
                message="Cannot reject an accepted quotation",
                error_code="QUOTATION_ALREADY_ACCEPTED",
            )

        self._validate_status_transition(q.quotation_status, QuotationStatus.REJECTED)

        prev_status = q.quotation_status
        prev_snap = q.model_dump()
        prev_snap["id"] = str(q.id)
        prev_snap["booking_id"] = str(q.booking_id)
        prev_snap["worker_id"] = str(q.worker_id)
        prev_snap["application_id"] = str(q.application_id)
        prev_snap["quotation_status"] = (
            prev_status.value if isinstance(prev_status, QuotationStatus) else str(prev_status)
        )

        q.quotation_status = QuotationStatus.REJECTED
        await q.save()

        await self._record_history_event(
            quotation=q,
            actor_id=customer.id,
            actor_role=customer.role,
            event_type=QuotationEventType.REJECTED,
            previous_status=prev_status,
            new_status=QuotationStatus.REJECTED,
            previous_snapshot=prev_snap,
            notes=f"Quotation explicitly rejected by customer {customer.full_name}",
        )

        # Update application status
        app = await JobApplication.get(q.application_id)
        if app and app.application_status == ApplicationStatus.PENDING:
            app.application_status = ApplicationStatus.REJECTED
            await app.save()

        return await self._build_customer_response(q)

    async def get_quotation_history(
        self,
        user: User,
        quotation_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> QuotationHistoryPaginatedResponse:
        """
        Retrieve read-only chronological audit history trail for a quotation.
        """
        if not PydanticObjectId.is_valid(quotation_id):
            raise BadRequestException(
                message=f"Invalid quotation ID format '{quotation_id}'",
                error_code="INVALID_QUOTATION_ID",
            )

        qid = PydanticObjectId(quotation_id)
        q = await self.repo.get_quotation_by_id(quotation_id)
        if not q:
            raise NotFoundException(
                message=f"Quotation '{quotation_id}' not found",
                error_code="QUOTATION_NOT_FOUND",
            )

        booking = await Booking.get(q.booking_id)

        # SECURITY OWNERSHIP GUARD
        if user.role != UserRole.ADMIN:
            if user.role == UserRole.CUSTOMER:
                if not booking or booking.customer_id != user.id:
                    raise ForbiddenException(
                        message="You are not authorized to view history for this quotation",
                        error_code="UNAUTHORIZED_QUOTATION_ACCESS",
                    )
            elif user.role == UserRole.WORKER:
                if q.worker_id != user.id:
                    raise ForbiddenException(
                        message="You are not authorized to view history for this quotation",
                        error_code="UNAUTHORIZED_QUOTATION_ACCESS",
                    )

        total = await QuotationHistory.find(QuotationHistory.quotation_id == qid).count()
        skip = (page - 1) * page_size
        logs = (
            await QuotationHistory.find(QuotationHistory.quotation_id == qid)
            .sort("+created_at")
            .skip(skip)
            .limit(page_size)
            .to_list()
        )

        items = [
            QuotationHistoryResponse(
                id=str(log.id),
                quotation_id=str(log.quotation_id),
                booking_id=str(log.booking_id),
                worker_id=str(log.worker_id),
                actor_id=str(log.actor_id),
                actor_role=log.actor_role.value if isinstance(log.actor_role, UserRole) else str(log.actor_role),
                event_type=log.event_type.value if isinstance(log.event_type, QuotationEventType) else str(log.event_type),
                previous_status=log.previous_status.value if log.previous_status else None,
                new_status=log.new_status.value if isinstance(log.new_status, QuotationStatus) else str(log.new_status),
                previous_snapshot=log.previous_snapshot,
                new_snapshot=log.new_snapshot,
                created_at=log.created_at,
                notes=log.notes,
            )
            for log in logs
        ]

        pages = math.ceil(total / page_size) if total > 0 else 1
        return QuotationHistoryPaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )

    async def get_assigned_worker(
        self, customer: User, booking_id: str
    ) -> AssignedWorkerResponse:
        """
        Retrieve assigned worker details and accepted quotation for a customer booking.
        """
        if not PydanticObjectId.is_valid(booking_id):
            raise BadRequestException(
                message=f"Invalid booking ID format '{booking_id}'",
                error_code="INVALID_BOOKING_ID",
            )

        bid = PydanticObjectId(booking_id)
        booking = await Booking.get(bid)
        if not booking:
            raise NotFoundException(
                message=f"Booking '{booking_id}' not found",
                error_code="BOOKING_NOT_FOUND",
            )

        if customer.role != UserRole.ADMIN and booking.customer_id != customer.id:
            raise ForbiddenException(
                message="You are not authorized to view this booking's assigned worker",
                error_code="UNAUTHORIZED_QUOTATION_ACCESS",
            )

        if not booking.worker_id or not booking.quotation_id:
            raise NotFoundException(
                message="No worker has been assigned to this booking yet",
                error_code="WORKER_NOT_ASSIGNED",
            )

        accepted_q = await Quotation.get(booking.quotation_id)
        if not accepted_q:
            raise NotFoundException(
                message="Accepted quotation document not found",
                error_code="QUOTATION_NOT_FOUND",
            )

        worker_user = await User.get(booking.worker_id)
        worker_profile = await WorkerProfile.find_one(WorkerProfile.user_id == booking.worker_id)

        c_dto = await self._build_customer_response(accepted_q)

        return AssignedWorkerResponse(
            worker_id=str(booking.worker_id),
            full_name=worker_user.full_name if worker_user else "Professional Worker",
            phone=worker_user.phone if worker_user else None,
            profile_photo_url=worker_profile.profile_photo_url if worker_profile else None,
            rating=worker_profile.rating if worker_profile else 5.0,
            experience_years=worker_profile.experience_years if worker_profile else 0.0,
            skills=worker_profile.skills if worker_profile else [],
            assigned_at=booking.assigned_at or datetime.now(timezone.utc),
            accepted_quotation=c_dto,
        )
