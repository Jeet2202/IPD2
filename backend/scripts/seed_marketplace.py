"""
Marketplace Database Seeding Utility — Development Environment Only.

Populates MongoDB Atlas with realistic categories and services for testing
the Ally AI-Powered Home Services Marketplace.

Features:
    - 100% Idempotent: Can be run repeatedly without creating duplicate records.
    - Safety Guards: Never deletes, truncates, or modifies existing users, bookings, or profiles.
    - Preserves ODM contracts & hooks: Uses Beanie models and repositories.

Execution:
    python scripts/seed_marketplace.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.category.models import Service, ServiceCategory, generate_slug
from app.category.repository import CategoryRepository
from app.database.connection import close_database_connection, connect_to_database
from app.service.repository import ServiceRepository

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("seed_marketplace")

# ---------------------------------------------------------------------------
# Seed Data Definitions
# ---------------------------------------------------------------------------

SEED_CATEGORIES = [
    {
        "name": "Electrical",
        "slug": "electrical",
        "description": "Professional electrical installation, repair, and wiring solutions for homes.",
        "display_order": 1,
        "icon": "electrical_services",
        "color_code": "#FF5722",
        "is_active": True,
    },
    {
        "name": "Plumbing",
        "slug": "plumbing",
        "description": "Expert plumbing services for leaks, fittings, drainage, and water tanks.",
        "display_order": 2,
        "icon": "plumbing",
        "color_code": "#2196F3",
        "is_active": True,
    },
    {
        "name": "Cleaning",
        "slug": "cleaning",
        "description": "Comprehensive deep cleaning for homes, kitchens, bathrooms, and sofas.",
        "display_order": 3,
        "icon": "cleaning_services",
        "color_code": "#4CAF50",
        "is_active": True,
    },
    {
        "name": "Painting",
        "slug": "painting",
        "description": "Interior and exterior painting, texture coating, and waterproofing.",
        "display_order": 4,
        "icon": "format_paint",
        "color_code": "#9C27B0",
        "is_active": True,
    },
    {
        "name": "Carpentry",
        "slug": "carpentry",
        "description": "Custom furniture repair, door/window fitting, and wooden installations.",
        "display_order": 5,
        "icon": "carpenter",
        "color_code": "#795548",
        "is_active": True,
    },
    {
        "name": "AC Repair",
        "slug": "ac-repair",
        "description": "Complete AC installation, gas refilling, servicing, and repair.",
        "display_order": 6,
        "icon": "ac_unit",
        "color_code": "#00BCD4",
        "is_active": True,
    },
    {
        "name": "Appliance Repair",
        "slug": "appliance-repair",
        "description": "Prompt repair and service for washing machines, fridges, TVs, and purifiers.",
        "display_order": 7,
        "icon": "home_repair_service",
        "color_code": "#FF9800",
        "is_active": True,
    },
    {
        "name": "Pest Control",
        "slug": "pest-control",
        "description": "Safe and effective pest control treatments for termites, cockroaches, and rodents.",
        "display_order": 8,
        "icon": "bug_report",
        "color_code": "#E91E63",
        "is_active": True,
    },
]


SEED_SERVICES = [
    # -----------------------------------------------------------------------
    # Electrical (6 Services)
    # -----------------------------------------------------------------------
    {
        "category_slug": "electrical",
        "name": "Ceiling Fan Installation",
        "slug": "ceiling-fan-installation",
        "short_description": "Professional mounting and wiring setup for new ceiling fans.",
        "description": "Expert electrician for safe unboxing, assembly, and ceiling hook mounting of any standard or decorative fan. Includes complete electrical wiring connection, regulator synchronization, and balance checking. Work is tested thoroughly for noise-free and wobble-free operation. Safety equipment and standard fasteners are provided by the technician.",
        "base_market_price": 299.0,
        "minimum_price": 249.0,
        "maximum_price": 399.0,
        "estimated_duration_minutes": 45,
        "required_experience_years": 1.0,
        "required_skills": ["electrical-wiring", "appliance-installation"],
        "service_icon": "ceiling_fan",
        "whats_included": [
            "Ceiling fan assembly and hook mounting",
            "Wiring connection with existing electrical box",
            "Testing and balancing for wobble-free rotation",
        ],
        "whats_not_included": [
            "New ceiling hook installation or structural masonry work",
            "Additional wire extending beyond 2 meters",
            "Supply of new fan or regulator hardware",
        ],
        "tags": ["fan", "installation", "electrical", "ceiling fan"],
        "keywords": ["install ceiling fan", "fan fitting", "electrician fan setup"],
        "is_featured": True,
        "is_emergency_service": False,
        "display_order": 1,
    },
    {
        "category_slug": "electrical",
        "name": "Ceiling Fan Repair",
        "slug": "ceiling-fan-repair",
        "short_description": "Quick diagnosis and repair for noisy, slow, or non-functional fans.",
        "description": "Comprehensive diagnosis of ceiling fan issues including capacitor replacement, bearing lubrication, and motor winding check. Ideal for fans running slow, making humming sounds, or completely stopped. Electrician carries standard capacitors and replacement parts for immediate resolution.",
        "base_market_price": 249.0,
        "minimum_price": 199.0,
        "maximum_price": 349.0,
        "estimated_duration_minutes": 40,
        "required_experience_years": 1.0,
        "required_skills": ["electrical-troubleshooting", "motor-repair"],
        "service_icon": "repair_fan",
        "whats_included": [
            "Diagnostic check of fan motor and capacitor",
            "Capacitor replacement labor",
            "Bearing lubrication and blade alignment",
        ],
        "whats_not_included": [
            "Cost of spare parts if motor rewinding is required",
            "New fan regulator unit",
        ],
        "tags": ["fan", "repair", "electrical", "capacitor"],
        "keywords": ["slow fan repair", "fan noise fix", "electrician fan repair"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 2,
    },
    {
        "category_slug": "electrical",
        "name": "Switch Board Repair & Replacement",
        "slug": "switch-board-repair",
        "short_description": "Repair or replacement of damaged switches, sockets, and switchboards.",
        "description": "Professional repair of sparking, loose, or burnt electrical switches and 5A/16A sockets. Includes complete inspection of back box wiring, terminal tightening, and load distribution. Broken switchboard plates are replaced safely with proper isolation.",
        "base_market_price": 349.0,
        "minimum_price": 299.0,
        "maximum_price": 499.0,
        "estimated_duration_minutes": 45,
        "required_experience_years": 2.0,
        "required_skills": ["electrical-wiring", "switchboard-repair"],
        "service_icon": "toggle_on",
        "whats_included": [
            "Inspection and repair up to 4 switch/socket points",
            "Replacing loose internal copper wiring connectors",
            "Voltage and grounding testing after repair",
        ],
        "whats_not_included": [
            "Modular switchboard plate supply",
            "Major wall chasing or heavy cable rewiring",
        ],
        "tags": ["switchboard", "socket", "electrical", "repair"],
        "keywords": ["switch repair", "socket replacement", "sparking switch fix"],
        "is_featured": False,
        "is_emergency_service": True,
        "display_order": 3,
    },
    {
        "category_slug": "electrical",
        "name": "MCB Replacement & Distribution Board Repair",
        "slug": "mcb-replacement",
        "short_description": "Safe replacement of tripping MCBs and main distribution board repair.",
        "description": "Expert diagnosis of frequent electrical tripping, short circuits, or overloaded circuits. Replacement of faulty Miniature Circuit Breakers (MCB), Residual Current Circuit Breakers (RCCB), or main switches. The technician checks total household load distribution.",
        "base_market_price": 499.0,
        "minimum_price": 399.0,
        "maximum_price": 699.0,
        "estimated_duration_minutes": 60,
        "required_experience_years": 3.0,
        "required_skills": ["high-voltage-safety", "mcb-installation"],
        "service_icon": "power",
        "whats_included": [
            "Diagnosis of circuit tripping root cause",
            "Installation of single or double pole MCB",
            "Busbar and main terminal tightening",
        ],
        "whats_not_included": [
            "Cost of new MCB or RCCB unit",
            "Heavy main service line replacement",
        ],
        "tags": ["mcb", "tripping", "distribution board", "fuse"],
        "keywords": ["mcb tripping repair", "change mcb", "electric breaker fix"],
        "is_featured": True,
        "is_emergency_service": True,
        "display_order": 4,
    },
    {
        "category_slug": "electrical",
        "name": "Tube Light & Decorative Light Installation",
        "slug": "light-installation",
        "short_description": "Hassle-free installation of LED battens, chandeliers, and wall sconces.",
        "description": "Safe and precise wall or ceiling mounting of LED tube lights, fancy fixtures, spotlights, and chandeliers. Includes wall drilling, rawl plug insertion, wire joint insulation, and fixture leveling.",
        "base_market_price": 249.0,
        "minimum_price": 199.0,
        "maximum_price": 349.0,
        "estimated_duration_minutes": 30,
        "required_experience_years": 1.0,
        "required_skills": ["lighting-installation", "electrical-wiring"],
        "service_icon": "lightbulb",
        "whats_included": [
            "Mounting up to 2 light fixtures",
            "Wall drilling and wall plug insertion",
            "Electrical connection and switch testing",
        ],
        "whats_not_included": [
            "Supply of light fixtures or bulbs",
            "False ceiling cutting or heavy wooden framing",
        ],
        "tags": ["lighting", "led", "chandelier", "tube light"],
        "keywords": ["install tube light", "fancy light fitting", "chandelier installation"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 5,
    },
    {
        "category_slug": "electrical",
        "name": "House Wiring Inspection & Audit",
        "slug": "house-wiring-inspection",
        "short_description": "Complete electrical safety inspection of home wiring and earthing.",
        "description": "Comprehensive health check of complete residential wiring, earthing resistance, phase balance, and insulation leakage. Recommended for homes older than 5 years or before major renovation. Includes digital multimeter testing.",
        "base_market_price": 799.0,
        "minimum_price": 699.0,
        "maximum_price": 1199.0,
        "estimated_duration_minutes": 90,
        "required_experience_years": 4.0,
        "required_skills": ["wiring-audit", "electrical-inspection"],
        "service_icon": "verified_user",
        "whats_included": [
            "Earthing pit effectiveness test",
            "Insulation resistance and leakage current check",
            "Load calculation and written safety report",
        ],
        "whats_not_included": [
            "Rewiring labor or material cost for identified defects",
        ],
        "tags": ["inspection", "wiring", "earthing", "safety audit"],
        "keywords": ["electrical inspection", "home wiring audit", "earthing check"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 6,
    },

    # -----------------------------------------------------------------------
    # Plumbing (6 Services)
    # -----------------------------------------------------------------------
    {
        "category_slug": "plumbing",
        "name": "Tap & Faucet Installation",
        "slug": "tap-installation",
        "short_description": "Expert installation of sink, basin, and bathroom taps.",
        "description": "Precision installation of wall mixers, basin taps, health faucets, or kitchen sink taps. Includes thread sealing with Teflon tape, washer placement, and connection hose fitting. Work is checked for zero water leakage.",
        "base_market_price": 299.0,
        "minimum_price": 249.0,
        "maximum_price": 399.0,
        "estimated_duration_minutes": 45,
        "required_experience_years": 1.0,
        "required_skills": ["plumbing-fitting", "sanitary-installation"],
        "service_icon": "water_drop",
        "whats_included": [
            "Fitting up to 2 taps or health faucets",
            "Teflon tape thread sealing and alignment",
            "Pressure leak testing after installation",
        ],
        "whats_not_included": [
            "Supply of taps, angle valves, or flexible hoses",
            "Concealed pipe modification behind wall tiles",
        ],
        "tags": ["tap", "faucet", "plumbing", "bathroom"],
        "keywords": ["tap fitting", "install faucet", "health faucet fitting"],
        "is_featured": True,
        "is_emergency_service": False,
        "display_order": 1,
    },
    {
        "category_slug": "plumbing",
        "name": "Tap Repair & Leakage Fixing",
        "slug": "tap-repair",
        "short_description": "Fix dripping taps, broken spindle valves, and leaking joints.",
        "description": "Fast resolution for dripping taps, worn-out rubber washers, damaged internal spindles, or loose handle connections. Plumber carries standard replacement washers and spindle cartridges.",
        "base_market_price": 249.0,
        "minimum_price": 199.0,
        "maximum_price": 349.0,
        "estimated_duration_minutes": 40,
        "required_experience_years": 1.0,
        "required_skills": ["plumbing-repair", "leakage-fix"],
        "service_icon": "build",
        "whats_included": [
            "Diagnosis of tap leakage source",
            "Washer replacement and internal spindle tightening",
            "Joint resealing with Teflon tape",
        ],
        "whats_not_included": [
            "Cost of new spindle cartridge if complete replacement is needed",
        ],
        "tags": ["tap repair", "dripping tap", "plumbing leak"],
        "keywords": ["fix dripping tap", "tap washer change", "leaking tap repair"],
        "is_featured": False,
        "is_emergency_service": True,
        "display_order": 2,
    },
    {
        "category_slug": "plumbing",
        "name": "Drain & Sink Clog Removal",
        "slug": "drain-cleaning",
        "short_description": "Unclog kitchen sinks, washbasin drains, and bathroom floor traps.",
        "description": "Effective mechanical unclogging of blocked kitchen sinks, bathroom traps, or balcony floor drains. Uses flexible drain snakes and pressure pumps to clear grease, food debris, and hair accumulation.",
        "base_market_price": 499.0,
        "minimum_price": 399.0,
        "maximum_price": 699.0,
        "estimated_duration_minutes": 60,
        "required_experience_years": 2.0,
        "required_skills": ["drainage-unclogging", "pipe-cleaning"],
        "service_icon": "cleaning_services",
        "whats_included": [
            "Mechanical drain snake unclogging",
            "Removal of trap blockage and debris",
            "Post-cleaning flow speed verification",
        ],
        "whats_not_included": [
            "Main underground sewer line jetting",
            "Replacing broken underground PVC pipes",
        ],
        "tags": ["clog", "drain", "sink", "unblock"],
        "keywords": ["blocked sink fix", "clean drain clog", "unclog bathroom drain"],
        "is_featured": True,
        "is_emergency_service": True,
        "display_order": 3,
    },
    {
        "category_slug": "plumbing",
        "name": "Concealed Pipe Leakage Repair",
        "slug": "pipe-leakage-repair",
        "short_description": "Detect and repair hidden water pipe leaks in walls or floors.",
        "description": "Advanced leak detection and precision repair for concealed CPVC, UPVC, or GI water supply lines. Includes minimal tile cutting to expose the leaking joint, pipe section replacement, and high-strength solvent welding.",
        "base_market_price": 799.0,
        "minimum_price": 699.0,
        "maximum_price": 1299.0,
        "estimated_duration_minutes": 120,
        "required_experience_years": 3.0,
        "required_skills": ["leak-detection", "pipe-soldering"],
        "service_icon": "hardware",
        "whats_included": [
            "Thermal/visual leak location pinpointing",
            "Exposing and replacing up to 1 meter pipe joint",
            "Solvent pressure testing for 30 minutes",
        ],
        "whats_not_included": [
            "Re-tiling and tile matching work",
            "Replacing complete riser pipe stack",
        ],
        "tags": ["pipe leak", "water seepage", "concealed plumbing"],
        "keywords": ["wall leak repair", "water pipe leakage fix", "seepage repair"],
        "is_featured": False,
        "is_emergency_service": True,
        "display_order": 4,
    },
    {
        "category_slug": "plumbing",
        "name": "Overhead Water Tank Cleaning",
        "slug": "water-tank-cleaning",
        "short_description": "Hygienic 6-stage deep cleaning and disinfection of water tanks.",
        "description": "Thorough 6-step deep cleaning process for Sintex plastic or concrete overhead tanks up to 2000 liters. Involves water dewatering, bottom sludge evacuation, high-pressure washing, vacuuming, and antibacterial spray treatment.",
        "base_market_price": 899.0,
        "minimum_price": 749.0,
        "maximum_price": 1299.0,
        "estimated_duration_minutes": 90,
        "required_experience_years": 2.0,
        "required_skills": ["tank-sanitization", "sludge-removal"],
        "service_icon": "water",
        "whats_included": [
            "Complete water & sludge dewatering",
            "High pressure wash & wall scrubbing",
            "Anti-bacterial spray treatment",
        ],
        "whats_not_included": [
            "Repairing cracked tank walls or float valve replacement",
        ],
        "tags": ["water tank", "tank cleaning", "sanitizing"],
        "keywords": ["clean water tank", "overhead tank cleaning", "sintex tank clean"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 5,
    },
    {
        "category_slug": "plumbing",
        "name": "Full Bathroom Plumbing Setup",
        "slug": "bathroom-plumbing",
        "short_description": "Complete fixture fitting for newly renovated or updated bathrooms.",
        "description": "Complete end-to-end installation of all bathroom sanitary fittings including wall-hung or floor-mounted commode, flush tank, vanity basin, shower panel, diverters, and towel racks.",
        "base_market_price": 1499.0,
        "minimum_price": 1299.0,
        "maximum_price": 2499.0,
        "estimated_duration_minutes": 180,
        "required_experience_years": 4.0,
        "required_skills": ["bathroom-fitting", "sanitary-plumbing"],
        "service_icon": "bathtub",
        "whats_included": [
            "Fitting of commode, washbasin, shower, and 4 accessories",
            "Silicone sealing around basins and commode base",
            "Comprehensive inlet and drainage water testing",
        ],
        "whats_not_included": [
            "Supply of sanitary porcelain or chromium fixtures",
            "Tile breaking or major masonry layout changes",
        ],
        "tags": ["bathroom", "sanitary", "commode", "shower"],
        "keywords": ["bathroom fitting", "commode installation", "full plumbing setup"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 6,
    },

    # -----------------------------------------------------------------------
    # Cleaning (6 Services)
    # -----------------------------------------------------------------------
    {
        "category_slug": "cleaning",
        "name": "Deep Home Cleaning (Full House)",
        "slug": "deep-home-cleaning",
        "short_description": "Intensive 360° deep sanitization and cleaning for the entire home.",
        "description": "Comprehensive deep cleaning service covering living rooms, bedrooms, kitchen, bathrooms, and balconies. Includes mechanized floor scrubbing, cobweb removal, ceiling fan wiping, window glass cleaning, cabinet exterior degreasing, and bathroom descaling.",
        "base_market_price": 3499.0,
        "minimum_price": 2999.0,
        "maximum_price": 4999.0,
        "estimated_duration_minutes": 240,
        "required_experience_years": 2.0,
        "required_skills": ["deep-cleaning", "floor-scrubbing"],
        "service_icon": "home",
        "whats_included": [
            "Mechanized floor scrubbing and mopping",
            "Window pane, frame, and grill degreasing",
            "Kitchen grease removal and bathroom sanitization",
        ],
        "whats_not_included": [
            "Inside cabinet item emptying/rearranging",
            "Sofa or mattress shampooing (available separately)",
        ],
        "tags": ["home cleaning", "deep clean", "house cleaning"],
        "keywords": ["full house deep clean", "home sanitization", "deep house cleaning"],
        "is_featured": True,
        "is_emergency_service": False,
        "display_order": 1,
    },
    {
        "category_slug": "cleaning",
        "name": "Deep Kitchen Cleaning",
        "slug": "kitchen-cleaning",
        "short_description": "Removal of tough grease, oil stains, chimney exterior, and tiles.",
        "description": "Specialized heavy-duty cleaning for modular and traditional kitchens. Removes stubborn oil splatters, burnt grease, and grime from wall tiles, chimney filters, stove hob, exhaust fan, sink, and countertop.",
        "base_market_price": 1499.0,
        "minimum_price": 1199.0,
        "maximum_price": 1999.0,
        "estimated_duration_minutes": 150,
        "required_experience_years": 1.5,
        "required_skills": ["kitchen-degreasing", "appliance-wiping"],
        "service_icon": "kitchen",
        "whats_included": [
            "Tile degreasing & grout scrubbing",
            "Chimney mesh filter degreasing & hob wiping",
            "Countertop & sink descaling",
        ],
        "whats_not_included": [
            "Internal chimney motor ducting deep clean",
            "Cleaning inside filled cabinets",
        ],
        "tags": ["kitchen", "degreasing", "chimney cleaning"],
        "keywords": ["kitchen deep clean", "remove oil stains kitchen", "chimney filter clean"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 2,
    },
    {
        "category_slug": "cleaning",
        "name": "Bathroom Deep Cleaning & Descaling",
        "slug": "bathroom-cleaning",
        "short_description": "Hard water stain removal, tile grout scrubbing, and sanitization.",
        "description": "Intensive bathroom restoration removing hard water limescale stains from wall tiles, glass shower partitions, taps, chrome fittings, and commode bowls. High-grade acidic cleaners dissolve calcium deposits.",
        "base_market_price": 699.0,
        "minimum_price": 549.0,
        "maximum_price": 899.0,
        "estimated_duration_minutes": 60,
        "required_experience_years": 1.0,
        "required_skills": ["bathroom-descaling", "tile-scrubbing"],
        "service_icon": "wash",
        "whats_included": [
            "Hard water stain removal from tiles & glass",
            "Commode, basin & fitting sanitization",
            "Exhaust fan and mirror wiping",
        ],
        "whats_not_included": [
            "Regrouting of tile joints",
            "Plumbing repair or pipe unblocking",
        ],
        "tags": ["bathroom", "descaling", "hard water stains"],
        "keywords": ["bathroom deep clean", "remove hard water stains", "washroom cleaning"],
        "is_featured": True,
        "is_emergency_service": False,
        "display_order": 3,
    },
    {
        "category_slug": "cleaning",
        "name": "Sofa Fabric Shampooing & Extraction",
        "slug": "sofa-cleaning",
        "short_description": "Professional foam shampooing and vacuum moisture extraction for sofas.",
        "description": "Revitalize fabric or velvet sofas with 3-step deep shampooing. Uses dry foam injection to loosen embedded dirt, sweat stains, and dust mites followed by high-suction wet vacuum extraction.",
        "base_market_price": 999.0,
        "minimum_price": 799.0,
        "maximum_price": 1399.0,
        "estimated_duration_minutes": 90,
        "required_experience_years": 2.0,
        "required_skills": ["fabric-shampooing", "vacuum-extraction"],
        "service_icon": "chair",
        "whats_included": [
            "Dry vacuuming to remove surface dust",
            "Fabric shampoo application & scrub",
            "Wet extraction of moisture and dirt",
        ],
        "whats_not_included": [
            "Leather sofa polishing (separate service)",
            "Permanent ink or chemical dye stain removal",
        ],
        "tags": ["sofa", "shampooing", "fabric cleaning", "upholstery"],
        "keywords": ["sofa cleaning", "shampoo sofa at home", "couch deep clean"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 4,
    },
    {
        "category_slug": "cleaning",
        "name": "Office & Commercial Space Cleaning",
        "slug": "office-cleaning",
        "short_description": "Complete cleaning and sanitization for office workstations and floors.",
        "description": "Professional commercial cleaning tailored for startup offices, retail shops, and corporate workspaces up to 2000 sq ft. Covers desk wiping, computer peripherals dusting, pantry deep clean, and floor buffer polishing.",
        "base_market_price": 4999.0,
        "minimum_price": 3999.0,
        "maximum_price": 7999.0,
        "estimated_duration_minutes": 300,
        "required_experience_years": 3.0,
        "required_skills": ["commercial-cleaning", "floor-buffing"],
        "service_icon": "business",
        "whats_included": [
            "Workstation desk & chair wiping",
            "Floor buffing & pantry sanitization",
            "Trash disposal and glass partition cleaning",
        ],
        "whats_not_included": [
            "Heavy industrial machinery degreasing",
            "Exterior high-rise glass facade cleaning",
        ],
        "tags": ["office", "commercial", "workspace", "cleaning"],
        "keywords": ["office deep clean", "commercial space cleaning", "corporate cleaning"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 5,
    },
    {
        "category_slug": "cleaning",
        "name": "Balcony & Window Deep Clean",
        "slug": "balcony-cleaning",
        "short_description": "High-pressure washing for balcony tiles, grills, and sliding windows.",
        "description": "Deep cleaning for dust-laden balconies, terrace tiles, safety grills, and exterior sliding glass windows. Uses high-pressure water jet spray to dislodge accumulated pigeon droppings, mud deposits, and moss.",
        "base_market_price": 799.0,
        "minimum_price": 599.0,
        "maximum_price": 999.0,
        "estimated_duration_minutes": 75,
        "required_experience_years": 1.0,
        "required_skills": ["pressure-washing", "window-cleaning"],
        "service_icon": "deck",
        "whats_included": [
            "High pressure jet wash of floor tiles",
            "Safety grill & railing scrubbing",
            "Window glass and slider channel cleaning",
        ],
        "whats_not_included": [
            "Repainting rusted grills",
            "Cleaning beyond safe hand reach without harness points",
        ],
        "tags": ["balcony", "window", "pressure wash"],
        "keywords": ["balcony cleaning", "window glass clean", "pressure wash balcony"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 6,
    },

    # -----------------------------------------------------------------------
    # Painting (6 Services)
    # -----------------------------------------------------------------------
    {
        "category_slug": "painting",
        "name": "Interior Wall Painting (Per Room / Full Flat)",
        "slug": "interior-painting",
        "short_description": "Premium interior wall repainting with shade selection & masking.",
        "description": "Professional interior wall painting using top acrylic emulsions. Includes surface sanding, nail hole filling with wall putty, primer coat, and 2 finish coats of premium washable paint. Floors and furniture covered with plastic sheets.",
        "base_market_price": 3999.0,
        "minimum_price": 2999.0,
        "maximum_price": 7999.0,
        "estimated_duration_minutes": 240,
        "required_experience_years": 3.0,
        "required_skills": ["wall-painting", "putty-application"],
        "service_icon": "palette",
        "whats_included": [
            "Furniture and floor plastic masking",
            "Crack filling and spot putty sanding",
            "1 coat primer + 2 coats premium emulsion paint",
        ],
        "whats_not_included": [
            "Cost of paint materials (if customer provides)",
            "Major plaster dampness treatment",
        ],
        "tags": ["painting", "interior", "wall paint", "emulsion"],
        "keywords": ["home painting", "paint room", "interior wall painting"],
        "is_featured": True,
        "is_emergency_service": False,
        "display_order": 1,
    },
    {
        "category_slug": "painting",
        "name": "Exterior Weather-Proof Wall Painting",
        "slug": "exterior-painting",
        "short_description": "Durable weather-shield painting for building exterior walls.",
        "description": "High-durability exterior painting designed to withstand extreme sunlight, heavy rainfall, and dust. Employs dirt-pickup-resistant exterior acrylic paint with anti-fungal properties.",
        "base_market_price": 4999.0,
        "minimum_price": 3999.0,
        "maximum_price": 9999.0,
        "estimated_duration_minutes": 360,
        "required_experience_years": 4.0,
        "required_skills": ["exterior-painting", "weatherproofing"],
        "service_icon": "format_paint",
        "whats_included": [
            "High pressure wall jet washing",
            "Exterior primer + 2 coats weather-shield paint",
            "Scaffolding ladder setup up to 2 floors",
        ],
        "whats_not_included": [
            "Bamboo scaffolding for towers beyond 2 floors",
            "Civil structural crack repair",
        ],
        "tags": ["exterior", "painting", "weatherproof", "building paint"],
        "keywords": ["exterior wall paint", "weatherproof painting", "building exterior painting"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 2,
    },
    {
        "category_slug": "painting",
        "name": "Feature Wall Texture & Accent Painting",
        "slug": "texture-painting",
        "short_description": "Designer feature wall textures, stencils, and metallic finishes.",
        "description": "Transform any living room or bedroom wall into a stunning focal point with designer textures (Royale Play, metallic finish, marble finish, or geometric stencils). Master painters execute customized pattern designs.",
        "base_market_price": 2499.0,
        "minimum_price": 1999.0,
        "maximum_price": 3999.0,
        "estimated_duration_minutes": 180,
        "required_experience_years": 4.0,
        "required_skills": ["texture-design", "stencil-painting"],
        "service_icon": "brush",
        "whats_included": [
            "Surface leveling & base coat preparation",
            "Application of texture compound & metallic topcoat",
            "Custom design execution on up to 120 sq ft wall",
        ],
        "whats_not_included": [
            "Wall repair of water damaged drywall",
            "Supply of special metallic glaze unless quoted",
        ],
        "tags": ["texture", "feature wall", "royale play", "accent wall"],
        "keywords": ["texture wall painting", "feature wall design", "accent wall paint"],
        "is_featured": True,
        "is_emergency_service": False,
        "display_order": 3,
    },
    {
        "category_slug": "painting",
        "name": "Waterproof Coating & Dampness Treatment",
        "slug": "waterproof-coating",
        "short_description": "Scientific damp-proof chemical coating for leaking walls.",
        "description": "Effective anti-seepage treatment for interior walls suffering from paint peeling, efflorescence salts, or water dampness from bathrooms/balconies. Flaking paint scraped to bare masonry and sealed with polymer.",
        "base_market_price": 1999.0,
        "minimum_price": 1499.0,
        "maximum_price": 2999.0,
        "estimated_duration_minutes": 150,
        "required_experience_years": 3.0,
        "required_skills": ["waterproofing", "dampness-treatment"],
        "service_icon": "shield",
        "whats_included": [
            "Scraping damaged plaster to masonry level",
            "2-coat elastomeric polymer waterproof sealant",
            "Waterproof wall putty smoothing layer",
        ],
        "whats_not_included": [
            "Fixing active internal plumbing pipe leakage behind wall",
        ],
        "tags": ["waterproofing", "dampness", "wall leakage", "seepage"],
        "keywords": ["fix wall dampness", "waterproof coating", "anti seepage paint"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 4,
    },
    {
        "category_slug": "painting",
        "name": "Ceiling Painting & Whitewash",
        "slug": "ceiling-painting",
        "short_description": "Clean white ceiling painting for rooms and halls.",
        "description": "Fresh coat of brilliant white ceiling emulsion to brighten rooms and eliminate yellowing or soot stains from fans and lights. Includes masking of ceiling moldings and spot putty crack repair.",
        "base_market_price": 1499.0,
        "minimum_price": 1199.0,
        "maximum_price": 1999.0,
        "estimated_duration_minutes": 120,
        "required_experience_years": 2.0,
        "required_skills": ["ceiling-painting", "roller-application"],
        "service_icon": "border_top",
        "whats_included": [
            "Floor masking and light fixture taping",
            "Crack filling & spot priming",
            "2 coats matte white ceiling emulsion",
        ],
        "whats_not_included": [
            "Gypsum false ceiling repair or board replacement",
        ],
        "tags": ["ceiling", "whitewash", "painting"],
        "keywords": ["ceiling painting", "whitewash room ceiling", "paint ceiling white"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 5,
    },
    {
        "category_slug": "painting",
        "name": "Single Room Express Touch-up Painting",
        "slug": "room-repainting",
        "short_description": "Same-day single room repainting for rental move-in/move-out.",
        "description": "Fast 1-day express repainting service designed specifically for single bedrooms, study rooms, or rental property handovers. Quick color matching, minimal disruption, and fast-drying acrylic paint.",
        "base_market_price": 1999.0,
        "minimum_price": 1599.0,
        "maximum_price": 2499.0,
        "estimated_duration_minutes": 150,
        "required_experience_years": 2.0,
        "required_skills": ["express-painting", "color-matching"],
        "service_icon": "speed",
        "whats_included": [
            "Complete wall prep for up to 150 sq ft floor area",
            "2 coats fast-drying wall emulsion",
            "Basic furniture covering and post-paint cleanup",
        ],
        "whats_not_included": [
            "Repainting wooden doors or window frames",
        ],
        "tags": ["single room", "express painting", "rental paint"],
        "keywords": ["paint one room", "quick room painting", "rental home paint"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 6,
    },

    # -----------------------------------------------------------------------
    # Carpentry (6 Services)
    # -----------------------------------------------------------------------
    {
        "category_slug": "carpentry",
        "name": "Furniture Repair & Joint Tightening",
        "slug": "furniture-repair",
        "short_description": "Fix wobbly chairs, broken bed slats, and loose table legs.",
        "description": "Expert repair for wooden dining chairs, beds, tables, and sofas. Fixes wobbly frames with heavy-duty wood glue, pocket screws, corner braces, and dowel pins. Broken bed slats replaced.",
        "base_market_price": 399.0,
        "minimum_price": 299.0,
        "maximum_price": 599.0,
        "estimated_duration_minutes": 60,
        "required_experience_years": 2.0,
        "required_skills": ["carpentry-repair", "wood-gluing"],
        "service_icon": "chair",
        "whats_included": [
            "Joint re-gluing & screw tightening for up to 2 items",
            "Slat or support leg reinforcement",
            "Leveling and stability testing",
        ],
        "whats_not_included": [
            "Re-varnishing or French polish finish",
            "New cushion re-upholstery",
        ],
        "tags": ["carpenter", "furniture repair", "wood fix"],
        "keywords": ["repair chair", "wobbly table fix", "wooden bed repair"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 1,
    },
    {
        "category_slug": "carpentry",
        "name": "Door Installation & Fitting",
        "slug": "door-installation",
        "short_description": "Precision hanging, planing, and hinge fitting for wooden doors.",
        "description": "Precision hanging of flush doors, solid wood doors, or PVC bathroom doors. Includes edge planing for smooth frame clearance, mortise hinge cutting, handle lock installation, and floor gap adjustment.",
        "base_market_price": 699.0,
        "minimum_price": 549.0,
        "maximum_price": 899.0,
        "estimated_duration_minutes": 90,
        "required_experience_years": 3.0,
        "required_skills": ["door-hanging", "wood-planing"],
        "service_icon": "meeting_room",
        "whats_included": [
            "Door planing & side trimming",
            "Fitting 3 hinges & latch mechanism",
            "Door stopper installation",
        ],
        "whats_not_included": [
            "Supply of door leaf, hinges, or lock sets",
            "Painting or varnishing door surface",
        ],
        "tags": ["door", "carpenter", "door fitting"],
        "keywords": ["install door", "hang wooden door", "door carpenter"],
        "is_featured": True,
        "is_emergency_service": False,
        "display_order": 2,
    },
    {
        "category_slug": "carpentry",
        "name": "Kitchen & Wardrobe Cabinet Repair",
        "slug": "cabinet-installation",
        "short_description": "Replace auto-hinges, drawer channels, and cabinet handles.",
        "description": "Repair malfunctioning modular kitchen shutters, wardrobe hydraulic hinges, telescoping drawer channels, and magnetic latches. Misaligned cabinet doors adjusted back to perfect square position.",
        "base_market_price": 499.0,
        "minimum_price": 399.0,
        "maximum_price": 699.0,
        "estimated_duration_minutes": 60,
        "required_experience_years": 2.0,
        "required_skills": ["cabinetry", "hinge-alignment"],
        "service_icon": "door_sliding",
        "whats_included": [
            "Adjustment or replacement of up to 4 hydraulic hinges",
            "Drawer slider channel realigning",
            "Handle and knob mounting",
        ],
        "whats_not_included": [
            "Supply of soft-close hinges or telescopic channels",
        ],
        "tags": ["cabinet", "wardrobe", "hinges", "drawer channel"],
        "keywords": ["fix wardrobe door", "cabinet hinge repair", "drawer slide replacement"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 3,
    },
    {
        "category_slug": "carpentry",
        "name": "Wooden Wall Shelf & TV Unit Mounting",
        "slug": "wooden-shelf-installation",
        "short_description": "Sturdy wall mounting for floating shelves, book racks, and TV units.",
        "description": "Safe laser-leveled mounting of floating wooden shelves, wall-hung TV back panels, book racks, or kitchen spice shelves. Uses heavy-duty wall anchors and concealed brackets.",
        "base_market_price": 349.0,
        "minimum_price": 299.0,
        "maximum_price": 499.0,
        "estimated_duration_minutes": 45,
        "required_experience_years": 1.5,
        "required_skills": ["wall-mounting", "carpentry-drilling"],
        "service_icon": "shelves",
        "whats_included": [
            "Mounting up to 2 wall shelves",
            "Laser level alignment and drilling",
            "Heavy-duty rawl plug & screw fastening",
        ],
        "whats_not_included": [
            "Supply of wooden shelves or decorative brackets",
        ],
        "tags": ["shelf", "floating shelf", "tv unit", "wall mount"],
        "keywords": ["hang floating shelf", "mount tv panel", "wall rack installation"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 4,
    },
    {
        "category_slug": "carpentry",
        "name": "Window Frame & Wooden Shutter Repair",
        "slug": "window-repair",
        "short_description": "Fix jammed wooden windows, latches, and glass beadings.",
        "description": "Repair sticking wooden window frames, swollen sashes, loose tower bolts, or broken glass retaining beadings. Carpenter planes swollen edges for smooth closing during monsoons.",
        "base_market_price": 449.0,
        "minimum_price": 349.0,
        "maximum_price": 599.0,
        "estimated_duration_minutes": 60,
        "required_experience_years": 2.0,
        "required_skills": ["window-carpentry", "latch-fitting"],
        "service_icon": "window",
        "whats_included": [
            "Planing sticking window edges",
            "Replacing 2 tower bolts or window stays",
            "Fixing loose glass beadings",
        ],
        "whats_not_included": [
            "Supply of new window glass panes",
        ],
        "tags": ["window", "carpenter", "latch fix"],
        "keywords": ["repair wooden window", "jammed window fix", "window latch carpenter"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 5,
    },
    {
        "category_slug": "carpentry",
        "name": "Door Lock & Handle Installation",
        "slug": "lock-installation",
        "short_description": "Install mortise locks, deadbolts, and smart digital locks.",
        "description": "Precision chiseling and fitting for main door mortise locks, cylindrical bedroom knob locks, night latches, or smart digital electronic door locks. Includes strike plate alignment on door frame.",
        "base_market_price": 399.0,
        "minimum_price": 299.0,
        "maximum_price": 599.0,
        "estimated_duration_minutes": 45,
        "required_experience_years": 2.0,
        "required_skills": ["lock-fitting", "mortise-chiseling"],
        "service_icon": "lock",
        "whats_included": [
            "Mortise lock hole chiseling & installation",
            "Strike plate alignment on frame",
            "Key turning & smooth operation check",
        ],
        "whats_not_included": [
            "Supply of lock set or smart lock device",
        ],
        "tags": ["lock", "mortise lock", "door handle", "smart lock"],
        "keywords": ["install door lock", "change lock", "carpenter lock fitting"],
        "is_featured": True,
        "is_emergency_service": True,
        "display_order": 6,
    },

    # -----------------------------------------------------------------------
    # AC Repair (6 Services)
    # -----------------------------------------------------------------------
    {
        "category_slug": "ac-repair",
        "name": "Split & Window AC Installation",
        "slug": "ac-installation",
        "short_description": "Professional indoor & outdoor unit installation with vacuuming.",
        "description": "Complete mounting and commissioning for Split or Window ACs (0.8 to 2.0 Ton). Includes outdoor unit bracket mounting, copper pipe flare connection, nitrogen leak check, system vacuuming, and electrical connection.",
        "base_market_price": 1499.0,
        "minimum_price": 1299.0,
        "maximum_price": 1999.0,
        "estimated_duration_minutes": 120,
        "required_experience_years": 3.0,
        "required_skills": ["ac-installation", "refrigerant-piping"],
        "service_icon": "ac_unit",
        "whats_included": [
            "Indoor plate & outdoor bracket mounting",
            "Copper pipe flair jointing & vacuuming",
            "Cooling performance and drain water check",
        ],
        "whats_not_included": [
            "Copper piping beyond standard 3 meters",
            "Outdoor wall bracket hardware supply",
            "Core drilling through RCC concrete beams",
        ],
        "tags": ["ac", "installation", "split ac", "window ac"],
        "keywords": ["install ac", "split ac installation", "ac technician setup"],
        "is_featured": True,
        "is_emergency_service": False,
        "display_order": 1,
    },
    {
        "category_slug": "ac-repair",
        "name": "AC Gas Refill & Leakage Repair",
        "slug": "ac-gas-refill",
        "short_description": "Identify copper pipe leaks, braze joints, & refill R32/R410/R22 gas.",
        "description": "Restores ice-cold cooling when AC blows warm air due to refrigerant loss. Technician conducts nitrogen pressure testing to locate micro-leaks in copper coil, brazes leak points, evacuates moisture via vacuum, and refills genuine gas.",
        "base_market_price": 2499.0,
        "minimum_price": 1999.0,
        "maximum_price": 2999.0,
        "estimated_duration_minutes": 90,
        "required_experience_years": 3.0,
        "required_skills": ["gas-charging", "leak-brazing"],
        "service_icon": "propane_tank",
        "whats_included": [
            "Nitrogen leak testing & copper joint brazing",
            "System deep vacuuming",
            "Full gas top-up / refilling to optimal PSI",
        ],
        "whats_not_included": [
            "Complete aluminum condenser coil replacement",
        ],
        "tags": ["ac gas", "gas refill", "cooling fix", "r32"],
        "keywords": ["ac gas charging", "ac not cooling", "ac gas refill cost"],
        "is_featured": True,
        "is_emergency_service": True,
        "display_order": 2,
    },
    {
        "category_slug": "ac-repair",
        "name": "AC Foam & Jet Deep Cleaning Service",
        "slug": "ac-deep-cleaning",
        "short_description": "High-pressure jet wash with anti-bacterial foam spray.",
        "description": "Advanced jet pump washing with protective jacket cover for indoor AC unit without dismantling. Non-corrosive antibacterial foam cleaner sprayed onto cooling coils, blower fan wheel, and drain tray.",
        "base_market_price": 599.0,
        "minimum_price": 499.0,
        "maximum_price": 799.0,
        "estimated_duration_minutes": 60,
        "required_experience_years": 2.0,
        "required_skills": ["jet-wash", "coil-cleaning"],
        "service_icon": "shower",
        "whats_included": [
            "High pressure water jet coil wash with jacket",
            "Blower wheel & drain pipe flushing",
            "Air filter sanitization & grill wiping",
        ],
        "whats_not_included": [
            "Gas refilling or spare parts replacement",
        ],
        "tags": ["ac service", "jet wash", "deep clean ac"],
        "keywords": ["ac service at home", "ac foam washing", "clean ac filter"],
        "is_featured": True,
        "is_emergency_service": False,
        "display_order": 3,
    },
    {
        "category_slug": "ac-repair",
        "name": "Standard AC Service Checkup",
        "slug": "ac-service",
        "short_description": "Routine filter cleaning, drain line check, and amp testing.",
        "description": "Routine seasonal maintenance service for smoothly running ACs. Includes air filter washing, dry cleaning of indoor coils, drain tray flushing, compressor amp check, operating pressure reading, and performance check.",
        "base_market_price": 399.0,
        "minimum_price": 299.0,
        "maximum_price": 499.0,
        "estimated_duration_minutes": 45,
        "required_experience_years": 1.5,
        "required_skills": ["ac-maintenance", "filter-cleaning"],
        "service_icon": "check_circle",
        "whats_included": [
            "Air filter washing & dry coil brush cleaning",
            "Drain line blockage check",
            "Amperage & temperature check",
        ],
        "whats_not_included": [
            "High pressure water jet wash",
        ],
        "tags": ["ac service", "routine check", "ac filter"],
        "keywords": ["ac routine service", "ac maintenance", "ac checkup"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 4,
    },
    {
        "category_slug": "ac-repair",
        "name": "AC Compressor & Capacitor Repair",
        "slug": "ac-compressor-repair",
        "short_description": "Diagnose outdoor unit trip, compressor starter capacitor, & PCB.",
        "description": "Expert troubleshooting when outdoor compressor unit fails to start, hums loudly, or trips the house main MCB. Technician tests compressor winding resistance, replaces faulty dual-run capacitors, or diagnoses inverter PCB errors.",
        "base_market_price": 899.0,
        "minimum_price": 699.0,
        "maximum_price": 1199.0,
        "estimated_duration_minutes": 75,
        "required_experience_years": 3.5,
        "required_skills": ["compressor-repair", "capacitor-replacement"],
        "service_icon": "bolt",
        "whats_included": [
            "Outdoor unit diagnostic check",
            "Capacitor / contactor replacement labor",
            "Compressor terminal & overload protector check",
        ],
        "whats_not_included": [
            "New compressor motor or inverter PCB board cost",
        ],
        "tags": ["compressor", "capacitor", "ac outdoor unit"],
        "keywords": ["ac outdoor unit repair", "ac compressor not working", "ac capacitor change"],
        "is_featured": False,
        "is_emergency_service": True,
        "display_order": 5,
    },
    {
        "category_slug": "ac-repair",
        "name": "AC Water Leakage & Drain Repair",
        "slug": "ac-water-leakage",
        "short_description": "Stop water dripping from indoor AC unit onto walls.",
        "description": "Immediate fix for water overflowing or dripping from indoor split AC unit onto bedroom walls and furniture. Unclogs algae-blocked drain pipes using high-pressure air pump and adjusts indoor unit slope angle.",
        "base_market_price": 449.0,
        "minimum_price": 349.0,
        "maximum_price": 599.0,
        "estimated_duration_minutes": 45,
        "required_experience_years": 1.5,
        "required_skills": ["drain-unclogging", "ac-leveling"],
        "service_icon": "water_drop",
        "whats_included": [
            "Drain pipe high pressure air flushing",
            "Indoor drain tray cleaning & alignment",
            "Unit slope angle adjustment",
        ],
        "whats_not_included": [
            "Replacing extended outdoor drain pipe beyond 2m",
        ],
        "tags": ["water leak", "ac dripping", "drain pipe"],
        "keywords": ["ac water leaking indoor", "ac water overflow fix", "ac drain clogged"],
        "is_featured": False,
        "is_emergency_service": True,
        "display_order": 6,
    },

    # -----------------------------------------------------------------------
    # Appliance Repair (6 Services)
    # -----------------------------------------------------------------------
    {
        "category_slug": "appliance-repair",
        "name": "Washing Machine Repair & Service",
        "slug": "washing-machine-repair",
        "short_description": "Fix front load / top load washing machine spin, drain, or vibration.",
        "description": "Comprehensive diagnosis and repair for semi-automatic, top-load, and front-load washing machines. Resolves issues like machine not spinning, water not draining, excessive noise/vibration during spin cycle, or digital error codes.",
        "base_market_price": 499.0,
        "minimum_price": 399.0,
        "maximum_price": 699.0,
        "estimated_duration_minutes": 60,
        "required_experience_years": 2.0,
        "required_skills": ["washing-machine-repair", "drum-belt-fix"],
        "service_icon": "local_laundry_service",
        "whats_included": [
            "Complete diagnostic check of motor, pump & belt",
            "Drain valve & inlet solenoid cleaning",
            "Vibration damper & leveling check",
        ],
        "whats_not_included": [
            "Cost of spare parts like drain pump, PCB board, or belt",
        ],
        "tags": ["washing machine", "appliance repair", "front load"],
        "keywords": ["washing machine repair", "top load spin fix", "washing machine technician"],
        "is_featured": True,
        "is_emergency_service": False,
        "display_order": 1,
    },
    {
        "category_slug": "appliance-repair",
        "name": "Refrigerator Repair & Gas Charging",
        "slug": "refrigerator-repair",
        "short_description": "Repair single / double door fridge cooling issues & thermostat.",
        "description": "Expert repair for single-door, double-door, and side-by-side frost-free refrigerators. Fixes problems like no cooling in lower compartment, freezer ice buildup, relay failure, thermostat failure, or compressor gas charging.",
        "base_market_price": 599.0,
        "minimum_price": 499.0,
        "maximum_price": 899.0,
        "estimated_duration_minutes": 75,
        "required_experience_years": 2.5,
        "required_skills": ["refrigerator-repair", "fridge-gas-refill"],
        "service_icon": "kitchen",
        "whats_included": [
            "Compressor, relay & thermostat testing",
            "Defrost heater & timer circuit check",
            "Condenser coil dusting & fan inspection",
        ],
        "whats_not_included": [
            "Cost of new thermostat, timer, or gas charging",
        ],
        "tags": ["fridge", "refrigerator", "cooling", "appliance"],
        "keywords": ["refrigerator repair", "fridge not cooling", "fridge gas charging"],
        "is_featured": False,
        "is_emergency_service": True,
        "display_order": 2,
    },
    {
        "category_slug": "appliance-repair",
        "name": "Microwave Oven Repair",
        "slug": "microwave-repair",
        "short_description": "Fix microwave not heating, spark, turntable, or touch keypad.",
        "description": "Fast repair for solo, grill, and convection microwave ovens. Resolves issues such as food not heating (magnetron failure), sparking inside chamber (diode/mica sheet burnt), glass plate turntable not rotating, or touch keypad not responding.",
        "base_market_price": 399.0,
        "minimum_price": 299.0,
        "maximum_price": 549.0,
        "estimated_duration_minutes": 45,
        "required_experience_years": 2.0,
        "required_skills": ["microwave-repair", "magnetron-testing"],
        "service_icon": "microwave",
        "whats_included": [
            "High voltage capacitor & magnetron testing",
            "Mica sheet inspection & thermal fuse check",
            "Touch panel and door interlock switch check",
        ],
        "whats_not_included": [
            "Cost of magnetron, transformer, or touch membrane",
        ],
        "tags": ["microwave", "oven", "heating fix"],
        "keywords": ["microwave repair", "microwave not heating", "oven technician"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 3,
    },
    {
        "category_slug": "appliance-repair",
        "name": "LED / LCD TV Wall Installation & Setup",
        "slug": "tv-installation",
        "short_description": "Secure wall mounting for 32\" to 75\" LED/Smart TVs.",
        "description": "Professional wall mounting for LED, OLED, QLED, and Smart TVs on concrete, brick, or plywood walls. Includes level alignment using spirit level, heavy-duty wall bracket installation, cable routing, set-top box connection, and WiFi setup.",
        "base_market_price": 499.0,
        "minimum_price": 399.0,
        "maximum_price": 699.0,
        "estimated_duration_minutes": 45,
        "required_experience_years": 1.5,
        "required_skills": ["tv-mounting", "wall-drilling"],
        "service_icon": "tv",
        "whats_included": [
            "Wall bracket mounting & spirit level alignment",
            "TV hanging & cable connection to DTH/HDMI",
            "Basic smart TV audio/video settings test",
        ],
        "whats_not_included": [
            "Supply of TV wall mount bracket",
            "Concealed wall chasing for HDMI cables",
        ],
        "tags": ["tv", "led tv", "wall mount", "smart tv"],
        "keywords": ["tv wall mounting", "install led tv", "tv fitting service"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 4,
    },
    {
        "category_slug": "appliance-repair",
        "name": "Water Purifier (RO) Service & Filter Replacement",
        "slug": "water-purifier-service",
        "short_description": "RO water purifier sanitization, TDS level check, & candle clean.",
        "description": "Complete maintenance service for all RO, UV, and UF water purifiers. Includes pre-filter candle washing, sediment and carbon filter health check, RO membrane flushing, water TDS measurement before & after service, and leak check.",
        "base_market_price": 399.0,
        "minimum_price": 299.0,
        "maximum_price": 599.0,
        "estimated_duration_minutes": 45,
        "required_experience_years": 1.5,
        "required_skills": ["ro-servicing", "tds-testing"],
        "service_icon": "opacity",
        "whats_included": [
            "Pre-filter housing cleaning & candle flush",
            "TDS level testing & flow adjustment",
            "UV lamp & booster pump pressure check",
        ],
        "whats_not_included": [
            "Cost of new RO membrane or carbon filter cartridges",
        ],
        "tags": ["water purifier", "ro service", "aquaguard", "tds"],
        "keywords": ["ro service", "water purifier repair", "change ro filter"],
        "is_featured": True,
        "is_emergency_service": False,
        "display_order": 5,
    },
    {
        "category_slug": "appliance-repair",
        "name": "Induction Cooktop Repair",
        "slug": "induction-repair",
        "short_description": "Fix induction stove error codes, power trip, or sensor failure.",
        "description": "Fast diagnostic check and component repair for all brand induction cooktops. Fixes issues like E0/E1/E2 error codes, power tripping, fan noise, or touch keys not responding.",
        "base_market_price": 349.0,
        "minimum_price": 249.0,
        "maximum_price": 449.0,
        "estimated_duration_minutes": 40,
        "required_experience_years": 1.5,
        "required_skills": ["induction-repair", "igbt-testing"],
        "service_icon": "countertops",
        "whats_included": [
            "IGBT coil & bridge rectifier diagnostic test",
            "Cooling fan & thermal sensor cleaning",
            "Display glass panel & touch key check",
        ],
        "whats_not_included": [
            "Cost of main IGBT transistor or glass top ceramic plate",
        ],
        "tags": ["induction", "cooktop", "stove repair"],
        "keywords": ["induction repair", "induction stove fix", "cooktop error repair"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 6,
    },

    # -----------------------------------------------------------------------
    # Pest Control (6 Services)
    # -----------------------------------------------------------------------
    {
        "category_slug": "pest-control",
        "name": "Termite Control Treatment (Anti-Termite)",
        "slug": "termite-treatment",
        "short_description": "Drill-Fill-Seal chemical treatment for wood and wall termites.",
        "description": "Comprehensive 1-year guaranteed anti-termite treatment protecting wooden furniture, doors, floor skirting, and walls. Technicians drill precision 12mm holes along wall junctions, inject odorless termiticides under high pressure, and seal holes.",
        "base_market_price": 2499.0,
        "minimum_price": 1999.0,
        "maximum_price": 3499.0,
        "estimated_duration_minutes": 180,
        "required_experience_years": 3.0,
        "required_skills": ["termite-drilling", "chemical-barrier"],
        "service_icon": "bug_report",
        "whats_included": [
            "Drill-Fill-Seal chemical barrier injection",
            "Treatment of wooden door frames & fixed wardrobes",
            "1-year warranty certificate with free callback",
        ],
        "whats_not_included": [
            "Replacing already eaten hollowed wooden frames",
        ],
        "tags": ["termite", "pest control", "anti termite", "wood treatment"],
        "keywords": ["termite treatment", "deemak pest control", "anti termite chemical"],
        "is_featured": True,
        "is_inspection_required": True,
        "is_emergency_service": False,
        "display_order": 1,
    },
    {
        "category_slug": "pest-control",
        "name": "Cockroach & Ant Herbal Gel Control",
        "slug": "cockroach-control",
        "short_description": "Odorless herbal gel baiting & spray for kitchen cockroaches.",
        "description": "Safe 100% odorless gel baiting treatment for German and American cockroaches. Target spots applied in kitchen cabinets, sink bottom, electrical appliances, and drain lines. Safe for children, pets, and senior citizens.",
        "base_market_price": 799.0,
        "minimum_price": 599.0,
        "maximum_price": 999.0,
        "estimated_duration_minutes": 45,
        "required_experience_years": 1.0,
        "required_skills": ["gel-baiting", "pest-spray"],
        "service_icon": "pest_control",
        "whats_included": [
            "Herbal gel dot application in kitchen & rooms",
            "Drain pipe anti-cockroach spray",
            "Single-service 60-day protection guarantee",
        ],
        "whats_not_included": [
            "Deep cleaning of kitchen grease",
        ],
        "tags": ["cockroach", "gel baiting", "herbal pest control"],
        "keywords": ["cockroach pest control", "gel treatment cockroach", "kitchen pest control"],
        "is_featured": True,
        "is_emergency_service": False,
        "display_order": 2,
    },
    {
        "category_slug": "pest-control",
        "name": "Mosquito & Fly Spray Treatment",
        "slug": "mosquito-control",
        "short_description": "Indoor wall spray & outdoor larvicide treatment against mosquitoes.",
        "description": "Effective indoor residual spray treatment for walls, curtains, and dark corners where dengue and malaria mosquitoes hide. Includes larvicidal chemical treatment in flower pots, drains, and balcony water traps.",
        "base_market_price": 899.0,
        "minimum_price": 699.0,
        "maximum_price": 1199.0,
        "estimated_duration_minutes": 45,
        "required_experience_years": 1.5,
        "required_skills": ["fogging", "larvicide-treatment"],
        "service_icon": "coronavirus",
        "whats_included": [
            "Indoor wall & curtain residual chemical spray",
            "Balcony & drain anti-larval treatment",
            "Odorless WHO-approved chemical solution",
        ],
        "whats_not_included": [
            "Thermal fogging outdoors for large grounds (available on request)",
        ],
        "tags": ["mosquito", "dengue control", "pest spray"],
        "keywords": ["mosquito pest control", "dengue spray home", "mosquito treatment"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 3,
    },
    {
        "category_slug": "pest-control",
        "name": "Rodent & Rat Control Treatment",
        "slug": "rodent-control",
        "short_description": "Multi-catch glue pads, bait stations, & entry sealing for rats.",
        "description": "Strategic rat and mouse eradication using industrial sticky glue boards, tamper-proof bait boxes, and chemical cake baits. Technicians inspect false ceilings, drain pipes, and kitchen wire cutouts.",
        "base_market_price": 999.0,
        "minimum_price": 799.0,
        "maximum_price": 1299.0,
        "estimated_duration_minutes": 60,
        "required_experience_years": 2.0,
        "required_skills": ["rodent-baiting", "glue-trapping"],
        "service_icon": "pest_control_rodent",
        "whats_included": [
            "Placement of 4-6 heavy-duty rat glue pads",
            "Baiting in false ceiling and balcony ducts",
            "Inspection of entry points & sealing advice",
        ],
        "whats_not_included": [
            "Civil wire mesh installation on windows",
        ],
        "tags": ["rodent", "rat control", "mouse trap"],
        "keywords": ["rat pest control", "rodent treatment", "get rid of rats home"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 4,
    },
    {
        "category_slug": "pest-control",
        "name": "Bed Bug Heat & Chemical Treatment",
        "slug": "bed-bug-treatment",
        "short_description": "2-visit intensive chemical treatment for bed bugs on mattresses.",
        "description": "Specialized 2-step chemical spray service eliminating bed bugs, nymphs, and unhatched eggs from mattress seams, bed frames, sofa cushions, and wall crevices. Includes a mandatory free 2nd visit within 15 days.",
        "base_market_price": 1499.0,
        "minimum_price": 1199.0,
        "maximum_price": 1899.0,
        "estimated_duration_minutes": 90,
        "required_experience_years": 2.5,
        "required_skills": ["bedbug-spray", "mattress-treatment"],
        "service_icon": "bed",
        "whats_included": [
            "1st visit deep chemical spray on beds & furniture",
            "2nd visit follow-up spray after 12-15 days",
            "100% bed bug eradication warranty",
        ],
        "whats_not_included": [
            "Replacing heavily infested mattresses",
        ],
        "tags": ["bed bug", "mattress pest control", "bedbug spray"],
        "keywords": ["bed bug pest control", "kill bed bugs", "bedbug treatment home"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 5,
    },
    {
        "category_slug": "pest-control",
        "name": "General Pest Control (Cockroach, Ant, Spider)",
        "slug": "general-pest-control",
        "short_description": "Comprehensive 3-in-1 protection against cockroaches, ants, and spiders.",
        "description": "All-in-one residential pest control combining gel baiting for cockroaches, spray treatment for crawling ants, and web removal for spiders. Safe for home use with minimal smell.",
        "base_market_price": 999.0,
        "minimum_price": 799.0,
        "maximum_price": 1199.0,
        "estimated_duration_minutes": 60,
        "required_experience_years": 1.0,
        "required_skills": ["general-pest-spray", "gel-application"],
        "service_icon": "shield",
        "whats_included": [
            "Herbal gel application in kitchen",
            "Baseboard & bathroom anti-ant spray",
            "Spider cobweb removal & corner spray",
        ],
        "whats_not_included": [
            "Termite or bed bug specialized treatment",
        ],
        "tags": ["general pest", "ant control", "spider control"],
        "keywords": ["general pest control", "home pest spray", "ant and spider treatment"],
        "is_featured": False,
        "is_emergency_service": False,
        "display_order": 6,
    },
]


# ---------------------------------------------------------------------------
# Seeding Logic
# ---------------------------------------------------------------------------

async def seed_marketplace() -> None:
    """
    Main idempotent seeding runner for Categories and Services.
    """
    logger.info("======================================================================")
    logger.info("  ALLY MARKETPLACE SEEDING UTILITY (DEVELOPMENT ONLY)")
    logger.info("======================================================================")

    # 1. Initialize MongoDB connection with Beanie Document Models
    logger.info("[1/3] Connecting to MongoDB Atlas and initializing Beanie ODM...")
    await connect_to_database(document_models=[ServiceCategory, Service])
    logger.info("      Connected successfully.")

    # Tracking metrics
    cat_created = 0
    cat_updated = 0
    cat_skipped = 0

    srv_created = 0
    srv_updated = 0
    srv_skipped = 0

    # 2. Process Categories
    logger.info("\n[2/3] Processing Categories...")
    category_map: dict[str, ServiceCategory] = {}

    for cat_def in SEED_CATEGORIES:
        slug = cat_def["slug"]
        existing = await CategoryRepository.get_category_by_slug(slug)

        if existing:
            # Check if any field needs updating
            needs_update = False
            for key, val in cat_def.items():
                if getattr(existing, key, None) != val:
                    setattr(existing, key, val)
                    needs_update = True

            if needs_update:
                await existing.save()
                cat_updated += 1
                logger.info(f"  [UPDATED] Category: {existing.name} ({slug})")
            else:
                cat_skipped += 1
                logger.info(f"  [SKIPPED] Category: {existing.name} ({slug}) — already up to date")
            category_map[slug] = existing
        else:
            new_cat = ServiceCategory(**cat_def)
            await new_cat.insert()
            cat_created += 1
            category_map[slug] = new_cat
            logger.info(f"  [CREATED] Category: {new_cat.name} ({slug})")

    # 3. Process Services
    logger.info("\n[3/3] Processing Services...")
    for srv_def in SEED_SERVICES:
        cat_slug = srv_def["category_slug"]
        category = category_map.get(cat_slug)

        if not category:
            logger.warning(f"  [WARN] Category '{cat_slug}' not found for service '{srv_def['name']}'! Skipping.")
            srv_skipped += 1
            continue

        srv_slug = srv_def.get("slug") or generate_slug(srv_def["name"])
        existing_srv = await ServiceRepository.get_service_by_slug(srv_slug)

        service_payload = {
            "category_id": str(category.id),
            "category_slug": category.slug,
            "name": srv_def["name"],
            "slug": srv_slug,
            "short_description": srv_def.get("short_description"),
            "description": srv_def.get("description"),
            "base_market_price": srv_def["base_market_price"],
            "minimum_price": srv_def.get("minimum_price", srv_def["base_market_price"] * 0.8),
            "maximum_price": srv_def.get("maximum_price", srv_def["base_market_price"] * 1.4),
            "estimated_duration_minutes": srv_def["estimated_duration_minutes"],
            "required_experience_years": srv_def.get("required_experience_years", 1.0),
            "required_skills": srv_def.get("required_skills", []),
            "service_icon": srv_def.get("service_icon"),
            "service_image": None,  # Images left empty as requested
            "service_image_url": None,
            "service_image_public_id": None,
            "whats_included": srv_def.get("whats_included", []),
            "whats_not_included": srv_def.get("whats_not_included", []),
            "tags": srv_def.get("tags", []),
            "keywords": srv_def.get("keywords", []),
            "display_order": srv_def.get("display_order", 0),
            "is_featured": srv_def.get("is_featured", False),
            "is_inspection_required": srv_def.get("is_inspection_required", False),
            "is_emergency_service": srv_def.get("is_emergency_service", False),
            "is_active": True,
        }

        if existing_srv:
            needs_update = False
            for k, v in service_payload.items():
                # Avoid overwriting uploaded images if they already exist in database
                if k in ("service_image", "service_image_url", "service_image_public_id") and getattr(existing_srv, k, None):
                    continue
                if getattr(existing_srv, k, None) != v:
                    setattr(existing_srv, k, v)
                    needs_update = True

            if needs_update:
                await existing_srv.save()
                srv_updated += 1
                logger.info(f"  [UPDATED] Service: {existing_srv.name} ({srv_slug})")
            else:
                srv_skipped += 1
                logger.info(f"  [SKIPPED] Service: {existing_srv.name} ({srv_slug}) — already up to date")
        else:
            new_srv = Service(**service_payload)
            await new_srv.insert()
            srv_created += 1
            logger.info(f"  [CREATED] Service: {new_srv.name} ({srv_slug})")

    # 4. Final Totals & Report
    total_categories_in_db = await ServiceCategory.find_all().count()
    total_services_in_db = await Service.find_all().count()

    print("\n" + "=" * 70)
    print("                 MARKETPLACE SEEDING SUMMARY REPORT                  ")
    print("=" * 70)
    print(f" Categories Created  : {cat_created}")
    print(f" Categories Updated  : {cat_updated}")
    print(f" Categories Skipped  : {cat_skipped}")
    print(f" Services Created    : {srv_created}")
    print(f" Services Updated    : {srv_updated}")
    print(f" Services Skipped    : {srv_skipped}")
    print("-" * 70)
    print(f" Total Categories in DB : {total_categories_in_db}")
    print(f" Total Services in DB   : {total_services_in_db}")
    print("=" * 70 + "\n")


async def main() -> None:
    try:
        await seed_marketplace()
        print("✅ Marketplace Seed Complete\n")
    except Exception as exc:
        logger.exception("Seeding failed with error!")
        print(f"\n❌ Marketplace Seed Failed: {exc}\n")
        sys.exit(1)
    finally:
        await close_database_connection()


if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    asyncio.run(main())
