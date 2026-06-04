"""Idempotent seeding of the Luxor9 capital-sources pipeline.

Pre-populates the named targets from the product spec so the CRM/dashboard has
real pipeline on first boot. Upserts by name, so it is safe to run every startup.
"""

from fundraising.store import fdb

# (name, type, subtype, geography, check_size, website)
SEED_SOURCES = [
    # — VC funds (pre-seed) —
    ("Antler", "vc", "pre-seed", "Global", "$100k-$250k", "https://www.antler.co"),
    ("Entrepreneur First", "vc", "pre-seed", "Global", "$100k-$250k", "https://www.joinef.com"),
    ("Pioneer", "vc", "pre-seed", "Global", "$20k-$100k", "https://pioneer.app"),
    ("Sequoia Scout Network", "vc", "pre-seed", "Global", "$50k-$250k", "https://www.sequoiacap.com"),
    ("Peak XV Surge", "vc", "pre-seed", "India/SEA", "$1M-$3M", "https://www.peakxv.com/surge"),
    ("Accel Atoms", "vc", "pre-seed", "India", "$500k-$1M", "https://www.accel.com/atoms"),
    ("Y Combinator", "vc", "pre-seed/accelerator", "Global", "$125k-$500k", "https://www.ycombinator.com"),
    ("Village Global", "vc", "pre-seed", "Global", "$100k-$500k", "https://www.villageglobal.vc"),
    ("500 Global", "vc", "pre-seed/seed", "Global", "$100k-$500k", "https://500.co"),
    ("First Round", "vc", "seed", "US", "$1M-$3M", "https://firstround.com"),
    ("Hustle Fund", "vc", "pre-seed", "Global", "$25k-$150k", "https://www.hustlefund.vc"),

    # — Strategic corporates —
    ("Microsoft for Startups", "corporate", "credits/strategic", "Global", "Up to $150k credits", "https://www.microsoft.com/startups"),
    ("Google for Startups", "corporate", "credits/strategic", "Global", "Up to $200k credits", "https://startup.google.com"),
    ("NVIDIA Inception", "corporate", "credits/strategic", "Global", "Credits + GPU access", "https://www.nvidia.com/en-us/startups/"),
    ("AWS Activate", "corporate", "credits/strategic", "Global", "Up to $100k credits", "https://aws.amazon.com/activate/"),
    ("IBM Ventures", "corporate", "strategic", "Global", "Varies", "https://www.ibm.com/ventures"),
    ("Oracle for Startups", "corporate", "credits/strategic", "Global", "Cloud credits", "https://www.oracle.com/startup/"),

    # — Government funding (India) —
    ("Startup India Seed Fund Scheme", "government", "seed grant", "India", "Up to ₹50L", "https://seedfund.startupindia.gov.in"),
    ("SIDBI", "government", "fund of funds/debt", "India", "Varies", "https://www.sidbi.in"),
    ("MeitY Grants", "government", "grant", "India", "Varies", "https://www.meity.gov.in"),
    ("NIDHI PRAYAS", "government", "grant", "India", "Up to ₹10L", "https://nidhi.dst.gov.in"),
    ("DST (Dept. of Science & Tech)", "government", "grant", "India", "Varies", "https://dst.gov.in"),
    ("BIRAC", "government", "grant", "India", "Up to ₹50L", "https://www.birac.nic.in"),
    ("TIDE 2.0", "government", "grant/incubation", "India", "Up to ₹7L", "https://www.meity.gov.in"),
    ("MSME Innovation Programs", "government", "grant", "India", "Varies", "https://msme.gov.in"),

    # — Accelerators —
    ("Techstars", "accelerator", "accelerator", "Global", "$120k", "https://www.techstars.com"),
    ("Plug and Play", "accelerator", "accelerator", "Global", "Varies", "https://www.plugandplaytechcenter.com"),
    ("Alchemist Accelerator", "accelerator", "accelerator (B2B)", "US", "$36k-$50k", "https://www.alchemistaccelerator.com"),

    # — Non-dilutive / ecosystem —
    ("Open-Source Ecosystem Funds", "grant", "non-dilutive", "Global", "Varies", ""),
    ("AI Development Programs", "grant", "non-dilutive", "Global", "Varies", ""),
]

DEFAULT_SECTORS = "AI, SaaS, deep tech"


async def seed_capital_sources() -> int:
    """Upsert the seed pipeline. Returns the number of sources processed."""
    count = 0
    for name, type_, subtype, geography, check_size, website in SEED_SOURCES:
        await fdb.upsert_source(
            name=name,
            type=type_,
            subtype=subtype,
            sectors=DEFAULT_SECTORS,
            geography=geography,
            check_size=check_size,
            website=website,
            contact_method="portal" if type_ in ("government", "grant") else "email",
            pipeline_stage="lead",
            source="seed",
        )
        count += 1
    return count
