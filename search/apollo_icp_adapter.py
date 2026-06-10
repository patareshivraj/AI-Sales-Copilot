import re
from typing import Union, Dict, Any, List

# Try to import ICPProfile, fallback to generic typing if needed
try:
    from schemas.icp_schema import ICPProfile
except ImportError:
    ICPProfile = Any

# 1. Industry Mapping Table
# Maps common industry inputs/synonyms to standard Apollo industry taxonomy
INDUSTRY_MAPPING = {
    "it": "information technology & services",
    "it services": "information technology & services",
    "information technology": "information technology & services",
    "software": "computer software",
    "saas": "computer software",
    "tech": "computer software",
    "technology": "computer software",
    "healthcare": "hospital & health care",
    "health": "hospital & health care",
    "hospital": "hospital & health care",
    "medical": "hospital & health care",
    "finance": "financial services",
    "fintech": "financial services",
    "banking": "financial services",
    "manufacturing": "manufacturing",
    "automotive": "automotive",
    "education": "education management",
    "retail": "retail",
    "marketing": "marketing & advertising",
    "advertising": "marketing & advertising",
    "staffing": "staffing & recruiting",
    "recruiting": "staffing & recruiting",
}

# 2. Location Mapping Table
# Maps common geographical terms, regions, and acronyms to Apollo geolocations
LOCATION_MAPPING = {
    "us": "United States",
    "usa": "United States",
    "united states": "United States",
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "in": "India",
    "india": "India",
    "bengaluru": "Bengaluru, Karnataka, India",
    "bangalore": "Bengaluru, Karnataka, India",
    "mumbai": "Mumbai, Maharashtra, India",
    "delhi": "Delhi, India",
    "singapore": "Singapore",
    "eu": "Europe",
    "europe": "Europe",
    "apac": "Asia-Pacific",
    "na": "North America",
    "north america": "North America",
}

# 3. Employee Size Mapping (Apollo Range Taxonomy)
APOLLO_RANGES = [
    (1, 10, "1,10"),
    (11, 50, "11,50"),
    (51, 200, "51,200"),
    (201, 500, "201,500"),
    (501, 1000, "501,1000"),
    (1001, 5000, "1001,5000"),
    (5001, 10000, "5001,10000"),
    (10001, 9999999, "10001,"),
]

def parse_company_size(size_str: str) -> tuple[Union[int, None], Union[int, None]]:
    """
    Extracts min and max employee count from a size string.
    E.g. '200-5000 employees' -> (200, 5000)
         '50+' -> (50, None)
    """
    if not size_str:
        return None, None
        
    # Clean string and extract digit blocks
    numbers = [int(n) for n in re.findall(r'\d+', size_str)]
    if len(numbers) >= 2:
        return numbers[0], numbers[1]
    elif len(numbers) == 1:
        if '+' in size_str or 'more' in size_str or 'plus' in size_str:
            return numbers[0], None
        return numbers[0], numbers[0]
        
    return None, None

def map_headcount_to_apollo_ranges(min_val: Union[int, None], max_val: Union[int, None]) -> List[str]:
    """Maps custom min/max employee bounds to matching Apollo range strings."""
    if min_val is None and max_val is None:
        return []
        
    resolved_min = min_val if min_val is not None else 0
    resolved_max = max_val if max_val is not None else 9999999
    
    matched_ranges = []
    for low, high, range_str in APOLLO_RANGES:
        # Check overlap
        if max(resolved_min, low) <= min(resolved_max, high):
            matched_ranges.append(range_str)
            
    return matched_ranges

def translate_icp_to_apollo_payload(icp: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
    """
    Translates an ICP Profile (dictionary or Pydantic ICPProfile model) 
    into a structured request payload compatible with Apollo's organization search.
    """
    # Convert Pydantic model to dict if applicable
    if hasattr(icp, "model_dump"):
        icp_dict = icp.model_dump()
    elif hasattr(icp, "dict"):
        icp_dict = icp.dict()
    elif isinstance(icp, dict):
        icp_dict = icp
    else:
        raise ValueError("ICP must be a dictionary or a Pydantic model.")

    # Apply Mappings
    
    # 1. Industries Filter mapping
    industries_input = icp_dict.get("industries") or []
    mapped_industries = []
    for ind in industries_input:
        cleaned = ind.strip().lower()
        if not cleaned:
            continue
        # Check in mapping table first, fallback to raw clean string
        mapped_val = INDUSTRY_MAPPING.get(cleaned, cleaned)
        mapped_industries.append(mapped_val)

    # 2. Locations Filter mapping (Region/Market)
    locations_input = []
    
    # Check 'regions' field
    regions = icp_dict.get("regions") or []
    if isinstance(regions, list):
        locations_input.extend(regions)
    elif isinstance(regions, str):
        locations_input.append(regions)
        
    # Check 'market' or 'market_type' fields
    market = icp_dict.get("market") or icp_dict.get("market_type") or ""
    if market:
        locations_input.append(market)

    ignore_terms = {"global", "any", "worldwide", "remote"}
    mapped_locations = []
    for loc in locations_input:
        cleaned = loc.strip().lower()
        if not cleaned or cleaned in ignore_terms:
            continue
        # Check mapping table first, fallback to raw clean string
        mapped_val = LOCATION_MAPPING.get(cleaned, loc.strip())
        if mapped_val not in mapped_locations:
            mapped_locations.append(mapped_val)

    # 3. Employee Ranges mapping
    company_size_str = icp_dict.get("company_size") or ""
    min_emp, max_emp = parse_company_size(company_size_str)
    mapped_ranges = map_headcount_to_apollo_ranges(min_emp, max_emp)

    # 4. Keyword filter extraction
    keywords = icp_dict.get("keywords") or []
    clean_keywords = [k.strip() for k in keywords if k.strip()]
    keyword_val = clean_keywords[0] if clean_keywords else ""

    # Build and return the payload with mapped fields
    payload = {
        "organization_industries": mapped_industries,
        "organization_locations": mapped_locations,
        "organization_num_employees_ranges": mapped_ranges,
    }
    
    if keyword_val:
        payload["q_organization_keyword"] = keyword_val

    return payload
