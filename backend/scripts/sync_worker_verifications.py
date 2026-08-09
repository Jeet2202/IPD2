"""
One-Time Safe Synchronization Script — Synchronize WorkerVerification documents with WorkerProfile.is_verified.

Usage:
    python -m scripts.sync_worker_verifications [--dry-run]
"""

import argparse
import asyncio
import logging
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.verification.models import WorkerVerification
from app.verification.schemas import VerificationStatus
from app.worker.models import WorkerProfile

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def run_synchronization(dry_run: bool = False) -> dict[str, int]:
    """
    Safely iterate through all WorkerProfiles and synchronize `is_verified`
    from the corresponding WorkerVerification collection records.
    """
    logger.info("Initializing database connection (dry_run=%s)...", dry_run)
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_DATABASE_NAME]

    await init_beanie(database=db, document_models=[WorkerProfile, WorkerVerification])

    profiles = await WorkerProfile.find_all().to_list()

    examined_count = 0
    verified_count = 0
    unverified_count = 0
    updated_count = 0
    already_correct_count = 0

    for profile in profiles:
        examined_count += 1
        worker_id_str = str(profile.user_id)

        # Check if worker has any APPROVED verification record
        approved_verification = await WorkerVerification.find_one(
            WorkerVerification.worker_id == worker_id_str,
            WorkerVerification.status == VerificationStatus.APPROVED,
        )

        should_be_verified = approved_verification is not None

        if should_be_verified:
            verified_count += 1
        else:
            unverified_count += 1

        current_val = getattr(profile, "is_verified", False)
        if current_val != should_be_verified:
            updated_count += 1
            if not dry_run:
                profile.is_verified = should_be_verified
                await profile.save()
            logger.info("Worker profile %s is_verified updated: %s -> %s", profile.id, current_val, should_be_verified)
        else:
            already_correct_count += 1

    summary = {
        "examined": examined_count,
        "verified_workers": verified_count,
        "unverified_workers": unverified_count,
        "profiles_updated": updated_count,
        "already_correct": already_correct_count,
    }

    logger.info("Synchronization summary: %s", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description="Synchronize WorkerProfile.is_verified from WorkerVerification documents.")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without committing database updates")
    args = parser.parse_args()

    asyncio.run(run_synchronization(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
