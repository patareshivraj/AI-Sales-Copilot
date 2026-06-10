import re
import os
from typing import Union, Dict, Any, List

# Try to import ICPProfile, fallback to generic typing if needed
try:
    from schemas.icp_schema import ICPProfile
except ImportError:
    ICPProfile = Any

# Standard Apollo Headcount Ranges
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

    payload = {}

    # 1. Map Industries (case-insensitive in some versions, but we pass clean names)
    industries = icp_dict.get("industries") or []
    if industries:
        payload["organization_industries"] = [ind.strip() for ind in industries if ind.strip()]

    # 2. Map Regions/Locations
    regions = icp_dict.get("regions") or []
    # Ignore generic region terms that confuse geolocation filters
    ignore_terms = {"global", "any", "worldwide", "remote"}
    clean_regions = [r.strip() for r in regions if r.strip().lower() not in ignore_terms]
    if clean_regions:
        payload["organization_locations"] = clean_regions

    # 3. Parse and Map Employee ranges
    company_size_str = icp_dict.get("company_size") or ""
    min_emp, max_emp = parse_company_size(company_size_str)
    ranges = map_headcount_to_apollo_ranges(min_emp, max_emp)
    if ranges:
        payload["organization_num_employees_ranges"] = ranges

    # 4. Map Keywords
    keywords = icp_dict.get("keywords") or []
    clean_keywords = [k.strip() for k in keywords if k.strip()]
    if clean_keywords:
        # We use the first major keyword as the primary organization search query
        payload["q_organization_keyword"] = clean_keywords[0]

    return payload
