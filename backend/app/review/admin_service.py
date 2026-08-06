"""
Admin Review Service — Aggregates and moderates customer reviews for Admin Panel.
"""

from typing import Any
from beanie import PydanticObjectId
from app.auth.models import User
from app.booking.models import Booking
from app.review.models import Review
from app.worker.models import WorkerProfile


class AdminReviewService:
    @staticmethod
    async def seed_default_reviews_if_empty() -> None:
        """Seed default reviews into MongoDB if reviews collection is empty."""
        try:
            count = await Review.count()
            if count > 0:
                return

            customer_users = await User.find({"role": "customer"}).to_list()
            worker_users = await User.find({"role": "worker"}).to_list()
            bookings = await Booking.find_all().to_list()

            c_id_1 = customer_users[0].id if customer_users else PydanticObjectId()
            c_id_2 = customer_users[1].id if len(customer_users) > 1 else PydanticObjectId()
            w_id_1 = worker_users[0].id if worker_users else PydanticObjectId()
            w_id_2 = worker_users[1].id if len(worker_users) > 1 else PydanticObjectId()
            b_id_1 = bookings[0].id if bookings else PydanticObjectId()
            b_id_2 = bookings[1].id if len(bookings) > 1 else PydanticObjectId()

            default_reviews = [
                Review(
                    review_number="REV-80021",
                    booking_id=b_id_1,
                    worker_id=w_id_1,
                    customer_id=c_id_1,
                    overall_rating=5.0,
                    punctuality_rating=5.0,
                    quality_rating=5.0,
                    professionalism_rating=5.0,
                    communication_rating=5.0,
                    review_title="Excellent Service!",
                    review_comment="Professional arrived on time and completed the work properly. Cleaned up all wiring debris before leaving. Highly recommended!",
                    would_recommend=True,
                    status="Published",
                ),
                Review(
                    review_number="REV-80022",
                    booking_id=b_id_2,
                    worker_id=w_id_2,
                    customer_id=c_id_2,
                    overall_rating=1.0,
                    punctuality_rating=1.0,
                    quality_rating=1.0,
                    professionalism_rating=1.0,
                    communication_rating=1.0,
                    review_title="Poor Experience",
                    review_comment="Abysmal experience! Worker was extremely rude, left water dripping under sink and demanded extra money directly in cash.",
                    would_recommend=False,
                    status="Flagged",
                    flag_reason="Personal Information",
                ),
                Review(
                    review_number="REV-80019",
                    booking_id=PydanticObjectId(),
                    worker_id=w_id_1,
                    customer_id=c_id_2,
                    overall_rating=2.0,
                    punctuality_rating=2.0,
                    quality_rating=2.0,
                    professionalism_rating=3.0,
                    communication_rating=2.0,
                    review_title="AC Servicing Issue",
                    review_comment="Cooling did not improve much after servicing. Technician claimed gas level was low but quotation was way higher than initial estimate.",
                    would_recommend=False,
                    status="Under Review",
                ),
                Review(
                    review_number="REV-80015",
                    booking_id=PydanticObjectId(),
                    worker_id=w_id_2,
                    customer_id=c_id_1,
                    overall_rating=4.0,
                    punctuality_rating=4.0,
                    quality_rating=4.0,
                    professionalism_rating=4.0,
                    communication_rating=4.0,
                    review_title="Good Craftsmanship",
                    review_comment="Good craftsmanship overall. Fixed the squeaking main door hinge in less than 30 minutes.",
                    would_recommend=True,
                    status="Published",
                ),
                Review(
                    review_number="REV-80010",
                    booking_id=PydanticObjectId(),
                    worker_id=w_id_1,
                    customer_id=c_id_1,
                    overall_rating=5.0,
                    punctuality_rating=5.0,
                    quality_rating=5.0,
                    professionalism_rating=5.0,
                    communication_rating=5.0,
                    review_title="Superb Plumbing Fix",
                    review_comment="Resolved main pipe clog within 45 minutes with proper tools. Very polite worker.",
                    would_recommend=True,
                    status="Published",
                ),
            ]

            for r in default_reviews:
                await r.insert()
        except Exception:
            pass

    @staticmethod
    async def get_admin_reviews(
        page: int = 1,
        page_size: int = 50,
        status: str | None = None,
        rating: int | None = None,
        category: str | None = None,
        search: str | None = None,
    ) -> dict[str, Any]:
        """Fetch all reviews from MongoDB with populated customer, worker, and booking info."""

        # Seed default reviews if MongoDB reviews collection is empty
        await AdminReviewService.seed_default_reviews_if_empty()

        # Fetch all reviews ordered by created_at desc
        reviews = await Review.find_all().sort("-created_at").to_list()

        # Build lookup maps for User, WorkerProfile, Booking to avoid N+1 queries
        customer_ids = list({r.customer_id for r in reviews if r.customer_id})
        worker_ids = list({r.worker_id for r in reviews if r.worker_id})
        booking_ids = list({r.booking_id for r in reviews if r.booking_id})

        users = await User.find({"_id": {"$in": customer_ids + worker_ids}}).to_list()
        user_map = {str(u.id): u for u in users}

        worker_profiles = await WorkerProfile.find({"user_id": {"$in": worker_ids}}).to_list()
        worker_prof_map = {str(wp.user_id): wp for wp in worker_profiles}

        bookings = await Booking.find({"_id": {"$in": booking_ids}}).to_list()
        booking_map = {str(b.id): b for b in bookings}

        # Preset fallback customer / worker names for standard seed records if user not in DB
        sample_c_names = ["Ananya Sharma", "Rohan Mehta", "Vikram Malhotra", "Pooja Hegde", "Kavita Menon"]
        sample_w_names = ["Sunil Verma", "Rajesh Kumar", "Vikram Singh", "Sanjay Dutt", "Amit Patel"]
        sample_professions = ["Electrician", "Plumber", "AC Specialist", "Carpenter", "Painter"]
        sample_categories = ["Electrical", "Plumbing", "AC Repair", "Carpentry", "Painting"]

        items = []
        for index, r in enumerate(reviews):
            c_user = user_map.get(str(r.customer_id))
            w_user = user_map.get(str(r.worker_id))
            w_prof = worker_prof_map.get(str(r.worker_id))
            b_item = booking_map.get(str(r.booking_id))

            default_c_name = sample_c_names[index % len(sample_c_names)]
            default_w_name = sample_w_names[index % len(sample_w_names)]
            default_prof = sample_professions[index % len(sample_professions)]
            default_cat = sample_categories[index % len(sample_categories)]

            c_name = c_user.full_name if c_user and c_user.full_name else default_c_name
            w_name = w_user.full_name if w_user and w_user.full_name else default_w_name

            service_title = "Home Maintenance Service"
            category_name = default_cat

            if b_item and getattr(b_item, "service_snapshot", None):
                service_title = b_item.service_snapshot.name or service_title
                category_name = b_item.service_snapshot.category_slug or b_item.service_snapshot.category_id or category_name
            elif w_prof and getattr(w_prof, "primary_category_id", None):
                category_name = str(w_prof.primary_category_id)

            worker_profession = default_prof
            if w_prof:
                skills = getattr(w_prof, "skills", [])
                if skills and len(skills) > 0:
                    worker_profession = str(skills[0]).title()
                elif getattr(w_prof, "experience_years", None):
                    worker_profession = f"{int(w_prof.experience_years)}+ Years Exp"

            r_status = getattr(r, "status", None) or "Published"
            r_flag_reason = getattr(r, "flag_reason", None)

            created_str = r.created_at.strftime("%Y-%m-%d %H:%M") if r.created_at else "Just now"

            item = {
                "id": str(r.review_number or r.id),
                "_id": str(r.id),
                "reviewId": str(r.id),
                "reviewNumber": r.review_number or f"REV-{str(r.id)[-6:].upper()}",
                "customerId": str(r.customer_id),
                "customerName": c_name,
                "customerAvatar": getattr(c_user, "avatar_url", None) if (c_user and getattr(c_user, "avatar_url", None)) else f"https://images.unsplash.com/photo-{(1494790108377 + index * 1000)}?auto=format&fit=crop&q=80&w=150",
                "workerId": str(r.worker_id),
                "workerName": w_name,
                "workerAvatar": getattr(w_user, "avatar_url", None) if (w_user and getattr(w_user, "avatar_url", None)) else f"https://images.unsplash.com/photo-{(1540569014015 + index * 1000)}?auto=format&fit=crop&q=80&w=150",
                "workerProfession": worker_profession,
                "jobId": str(r.booking_id),
                "service": service_title,
                "category": category_name,
                "rating": r.overall_rating,
                "punctualityRating": r.punctuality_rating,
                "qualityRating": r.quality_rating,
                "professionalismRating": r.professionalism_rating,
                "communicationRating": r.communication_rating,
                "reviewTitle": r.review_title,
                "reviewText": r.review_comment or "Customer provided star rating without written feedback.",
                "wouldRecommend": r.would_recommend,
                "attachments": r.attachments or [],
                "status": r_status,
                "flagReason": r_flag_reason,
                "createdAt": created_str,
            }

            # Filter matching
            if status and status != "All" and r_status.lower() != status.lower():
                continue
            if rating and rating != "All":
                try:
                    if int(r.overall_rating) != int(rating):
                        continue
                except ValueError:
                    pass
            if category and category != "All" and category_name.lower() != category.lower():
                continue
            if search:
                q = search.lower().strip()
                if (
                    q not in item["id"].lower()
                    and q not in item["customerName"].lower()
                    and q not in item["workerName"].lower()
                    and q not in item["service"].lower()
                    and q not in item["reviewText"].lower()
                ):
                    continue

            items.append(item)

        total_count = len(items)
        avg_rating = round(sum(i["rating"] for i in items) / total_count, 1) if total_count > 0 else 5.0
        five_star = sum(1 for i in items if i["rating"] == 5.0)
        low_ratings = sum(1 for i in items if i["rating"] <= 2.0)
        flagged_count = sum(1 for i in items if i["status"] == "Flagged")

        dist = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for i in items:
            star = max(1, min(5, int(round(i["rating"]))))
            dist[star] += 1

        rating_distribution = [
            {
                "stars": s,
                "count": dist[s],
                "percentage": round((dist[s] / total_count * 100)) if total_count > 0 else 0,
            }
            for s in [5, 4, 3, 2, 1]
        ]

        summary = {
            "totalReviews": total_count,
            "averageRating": avg_rating,
            "fiveStarReviews": five_star,
            "lowRatings": low_ratings,
            "flaggedReviews": flagged_count,
            "ratingDistribution": rating_distribution,
        }

        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = items[start_idx:end_idx]

        return {
            "reviews": paginated_items,
            "summary": summary,
            "total": total_count,
            "page": page,
            "pageSize": page_size,
        }

    @staticmethod
    async def update_review_status(review_id: str, status: str, flag_reason: str | None = None) -> dict[str, Any]:
        """Update review moderation status in MongoDB."""
        review = None
        if PydanticObjectId.is_valid(review_id):
            review = await Review.get(PydanticObjectId(review_id))

        if not review:
            review = await Review.find_one(Review.review_number == review_id)

        if not review:
            raise ValueError("Review not found")

        review.status = status
        review.flag_reason = flag_reason
        await review.save()

        return {
            "id": str(review.review_number or review.id),
            "_id": str(review.id),
            "status": review.status,
            "flagReason": review.flag_reason,
            "message": f"Review {review.review_number or review_id} updated to {status}",
        }

