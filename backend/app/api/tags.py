"""
OpenAPI tag metadata — controls Swagger UI grouping and documentation.

Tags are ordered by usage frequency (most-used first) so developers
find the most common endpoints at the top of the Swagger UI page.

Each tag maps to a feature module. The 'description' appears in the
Swagger UI sidebar when the tag is expanded.

Adding a new tag:
    1. Add a dict here with 'name' and 'description'
    2. Use the same tag name in the router include: tags=["TagName"]
"""

# OpenAPI tag definitions — passed to FastAPI(openapi_tags=OPENAPI_TAGS)
OPENAPI_TAGS: list[dict[str, str]] = [
    {
        "name": "System",
        "description": (
            "Infrastructure endpoints — health checks, root info. "
            "Not versioned, available at the application root."
        ),
    },
    {
        "name": "Authentication",
        "description": (
            "User registration, login, OTP verification, and token management. "
            "Public endpoints that do not require an existing session."
        ),
    },
    {
        "name": "Jobs",
        "description": (
            "Core marketplace flow — job creation, listing, acceptance, "
            "and lifecycle management. Customers create jobs, workers accept them."
        ),
    },
    {
        "name": "Workers",
        "description": (
            "Worker profile management and public worker discovery. "
            "Includes availability toggling and skill management."
        ),
    },
    {
        "name": "Customers",
        "description": (
            "Customer profile management and booking history. "
            "Requires authenticated customer role."
        ),
    },
    {
        "name": "Addresses",
        "description": (
            "Customer address management — create, list, update, soft-delete, and set default. "
            "Requires authenticated customer role. Used by the booking system as service location."
        ),
    },
    {
        "name": "Bookings",
        "description": (
            "Service booking management — create, list, and retrieve bookings. "
            "Each booking captures a point-in-time snapshot of the service and address. "
            "Booking numbers follow the KSYYYYnnnnn format. "
            "Requires authenticated customer role."
        ),
    },
    {
        "name": "Pricing",
        "description": (
            "Service pricing catalog. Public read access for all users, "
            "write access restricted to admin role."
        ),
    },
    {
        "name": "Inspections",
        "description": (
            "Pre-job and post-job inspection management. "
            "Supports photo documentation and status tracking."
        ),
    },
    {
        "name": "Reviews",
        "description": (
            "Worker reviews and ratings from customers after job completion. "
            "Public read access, authenticated write access."
        ),
    },
    {
        "name": "Notifications",
        "description": (
            "In-app and push notification management. "
            "Users can list, read, and mark notifications."
        ),
    },
    {
        "name": "Uploads",
        "description": (
            "File and image upload handling via Cloudinary. "
            "Supports profile photos, inspection images, and documents."
        ),
    },
    {
        "name": "Admin",
        "description": (
            "Platform administration — user management, job oversight, "
            "analytics, and pricing configuration. Requires admin role."
        ),
    },
]
