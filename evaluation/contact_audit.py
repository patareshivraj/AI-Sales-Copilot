import sys
import os
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.contact_discovery_agent import ContactDiscoveryAgent
from schemas.icp_schema import ICPProfile

def run_audit():
    agent = ContactDiscoveryAgent()
    
    icp = ICPProfile(
        industries=["Information Technology"],
        company_size="1000+",
        decision_makers=["CTO", "Chief Technology Officer", "Head of Digital Transformation"],
        regions=["Global"],
        market_type="Global",
        keywords=[],
        reasoning=""
    )
    
    companies = [
        "Persistent Systems",
        "Zensar",
        "Infosys",
        "TCS",
        "Tech Mahindra",
        "L&T Technology Services",
        "Birlasoft",
        "KPIT",
        "Cybage",
        "Coforge"
    ]
    
    results = []
    
    print("=======================================")
    print("CONTACT DISCOVERY AUDIT (PHASE 10.6)")
    print("=======================================\n")
    
    for comp in companies:
        print(f"Auditing: {comp}...")
        contact = agent.find_contact(comp, icp)
        
        record = {
            "company": comp,
            "contact_found": bool(contact.contact_name),
            "linkedin_found": bool(contact.linkedin_url),
            "email_found": bool(contact.email),
            "source_url": contact.source_url,
            "contact_confidence": contact.contact_confidence
        }
        results.append(record)
        print(f"  -> Found: {record['contact_found']} | LinkedIn: {record['linkedin_found']} | Confidence: {record['contact_confidence']}")
        time.sleep(1)  # small backoff for duckduckgo
        
    # Calculate Metrics
    total = len(companies)
    contact_found_rate = sum(1 for r in results if r["contact_found"]) / total * 100
    linkedin_found_rate = sum(1 for r in results if r["linkedin_found"]) / total * 100
    email_found_rate = sum(1 for r in results if r["email_found"]) / total * 100
    
    metrics = {
        "total_companies_audited": total,
        "contact_found_rate_percent": contact_found_rate,
        "linkedin_found_rate_percent": linkedin_found_rate,
        "email_found_rate_percent": email_found_rate,
    }
    
    print("\n--- Audit Metrics ---")
    print(json.dumps(metrics, indent=4))
    
    os.makedirs("evaluation/reports", exist_ok=True)
    with open("evaluation/reports/contact_audit.json", "w") as f:
        json.dump({"metrics": metrics, "raw_results": results}, f, indent=4)
        
    print("\nAudit saved to evaluation/reports/contact_audit.json")

if __name__ == "__main__":
    run_audit()
