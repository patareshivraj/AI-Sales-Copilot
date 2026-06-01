import json
import csv
import os

def generate_demo_report():
    input_file = "outputs/final_report.json"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found. Please run main.py first.")
        return
        
    with open(input_file, "r") as f:
        data = json.load(f)
        
    prospects = data.get("prospects", [])
    
    total_prospects = len(prospects)
    qualified_prospects = sum(1 for p in prospects if p.get("qualification_tier") in ["Hot", "Warm"])
    high_fit_buyers = sum(1 for p in prospects if p.get("buyer_fit", {}).get("buyer_fit") in ["High", "Medium"])
    
    verified_contacts = sum(1 for p in prospects if p.get("contact") and p.get("contact").get("contact_name") is not None)
    
    manual_review_required = total_prospects - verified_contacts
    
    # Find top opportunity
    top_opportunity = None
    highest_score = -1
    for p in prospects:
        score = p.get("qualification_score", 0)
        fit = p.get("buyer_fit", {}).get("buyer_fit")
        # Prefer High/Medium fit, but settle for highest score
        if fit in ["High", "Medium"] and score > highest_score:
            highest_score = score
            top_opportunity = p
            
    if not top_opportunity and prospects:
        # Fallback to just highest score
        top_opportunity = max(prospects, key=lambda x: x.get("qualification_score", 0))

    print("=================================")
    print("AI SALES COPILOT REPORT")
    print("=================================\n")
    print(f"Prospects Found: {total_prospects}")
    print(f"Qualified Prospects (Warm/Hot): {qualified_prospects}")
    print(f"High Fit Buyers: {high_fit_buyers}")
    print(f"Verified Contacts: {verified_contacts}")
    print(f"Manual Review Required: {manual_review_required}")
    
    if top_opportunity:
        print("\nTop Opportunity:")
        print(f"Company: {top_opportunity.get('company')}")
        print(f"Score: {top_opportunity.get('qualification_score')}")
        print(f"Buyer Fit: {top_opportunity.get('buyer_fit', {}).get('buyer_fit', 'Unknown')}")
        
    # Generate artifacts
    os.makedirs("reports", exist_ok=True)
    
    # CSV
    with open("reports/contacts_found.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Company", "Website", "Contact Name", "Title", "LinkedIn URL", "Email", "Score", "Tier"])
        for p in prospects:
            contact = p.get("contact") or {}
            writer.writerow([
                p.get("company", ""),
                p.get("website", ""),
                contact.get("contact_name", ""),
                contact.get("title", ""),
                contact.get("linkedin_url", ""),
                contact.get("email", ""),
                p.get("qualification_score", ""),
                p.get("qualification_tier", "")
            ])
            
    # MD Report
    with open("reports/lead_report.md", "w") as f:
        f.write("# AI Sales Copilot Lead Report\n\n")
        f.write(f"- **Total Prospects Found**: {total_prospects}\n")
        f.write(f"- **Qualified Prospects**: {qualified_prospects}\n")
        f.write(f"- **High Fit Buyers**: {high_fit_buyers}\n")
        f.write(f"- **Verified Contacts**: {verified_contacts}\n")
        f.write(f"- **Manual Review Required**: {manual_review_required}\n\n")
        if top_opportunity:
            f.write("## Top Opportunity\n")
            f.write(f"**Company**: {top_opportunity.get('company')}\n")
            f.write(f"**Score**: {top_opportunity.get('qualification_score')} ({top_opportunity.get('qualification_tier')})\n")
            f.write(f"**Buyer Fit**: {top_opportunity.get('buyer_fit', {}).get('buyer_fit', 'Unknown')}\n\n")
            f.write(f"**Reasoning**: {top_opportunity.get('qualification', {}).get('reasoning')}\n")
            
    # JSON Report
    with open("reports/lead_report.json", "w") as f:
        json.dump({
            "metrics": {
                "total_prospects": total_prospects,
                "qualified_prospects": qualified_prospects,
                "high_fit_buyers": high_fit_buyers,
                "verified_contacts": verified_contacts,
                "manual_review_required": manual_review_required
            },
            "top_opportunity": top_opportunity
        }, f, indent=4)
        
    print("\nReports successfully generated in reports/ directory:")
    print("- reports/lead_report.md")
    print("- reports/lead_report.json")
    print("- reports/contacts_found.csv")

if __name__ == "__main__":
    generate_demo_report()
