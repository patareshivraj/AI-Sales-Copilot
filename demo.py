import json
import csv
import os
from collections import Counter

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
    verified_contacts = sum(1 for p in prospects if p.get("contact") and p["contact"].get("contact_name") is not None)
    outreach_generated = sum(1 for p in prospects if p.get("outreach") is not None)
    
    # Blocked reason breakdown
    blocked_reasons = [p.get("blocked_reason") for p in prospects if p.get("blocked_reason")]
    blocked_counts = Counter(blocked_reasons)
    
    # Find top opportunity (highest score among non-blocked, non-competitor)
    top_opportunity = None
    highest_score = -1
    for p in prospects:
        score = p.get("qualification_score", 0)
        fit = p.get("buyer_fit", {}).get("buyer_fit")
        is_competitor = p.get("buyer_fit", {}).get("competitor_flag", False)
        if not is_competitor and fit in ["High", "Medium"] and score > highest_score:
            highest_score = score
            top_opportunity = p
            
    if not top_opportunity and prospects:
        non_blocked = [p for p in prospects if not p.get("buyer_fit", {}).get("competitor_flag", False)]
        if non_blocked:
            top_opportunity = max(non_blocked, key=lambda x: x.get("qualification_score", 0))

    print("=================================")
    print("AI SALES COPILOT REPORT")
    print("=================================\n")
    print(f"Prospects Found:            {total_prospects}")
    print(f"Qualified (Warm/Hot):       {qualified_prospects}")
    print(f"High Fit Buyers:            {high_fit_buyers}")
    print(f"Verified Contacts:          {verified_contacts}")
    print(f"Outreach Generated:         {outreach_generated}")
    
    print(f"\n--- Blocked Funnel ---")
    if blocked_counts:
        for reason, count in blocked_counts.most_common():
            print(f"  {reason}: {count}")
    else:
        print("  No prospects blocked.")
    
    if top_opportunity:
        print(f"\n--- Top Opportunity ---")
        print(f"Company:    {top_opportunity.get('company')}")
        print(f"Score:      {top_opportunity.get('qualification_score')}")
        print(f"Tier:       {top_opportunity.get('qualification_tier')}")
        print(f"Buyer Fit:  {top_opportunity.get('buyer_fit', {}).get('buyer_fit', 'Unknown')}")
        opp = top_opportunity.get("opportunity")
        if opp:
            print(f"Urgency:    {opp.get('urgency')}")
            if opp.get("why_now"):
                print(f"Why Now:")
                for reason in opp["why_now"]:
                    print(f"  - {reason}")
        
    # Generate artifacts
    os.makedirs("reports", exist_ok=True)
    
    # CSV
    with open("reports/contacts_found.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Company", "Website", "Contact Name", "Title", "LinkedIn URL", "Email", "Score", "Tier", "Blocked Reason", "Urgency"])
        for p in prospects:
            contact = p.get("contact") or {}
            opp = p.get("opportunity") or {}
            writer.writerow([
                p.get("company", ""),
                p.get("website", ""),
                contact.get("contact_name", ""),
                contact.get("title", ""),
                contact.get("linkedin_url", ""),
                contact.get("email", ""),
                p.get("qualification_score", ""),
                p.get("qualification_tier", ""),
                p.get("blocked_reason", ""),
                opp.get("urgency", "")
            ])
            
    # MD Report
    with open("reports/lead_report.md", "w") as f:
        f.write("# AI Sales Copilot Lead Report\n\n")
        f.write(f"- **Total Prospects Found**: {total_prospects}\n")
        f.write(f"- **Qualified Prospects**: {qualified_prospects}\n")
        f.write(f"- **High Fit Buyers**: {high_fit_buyers}\n")
        f.write(f"- **Verified Contacts**: {verified_contacts}\n")
        f.write(f"- **Outreach Generated**: {outreach_generated}\n\n")
        
        if blocked_counts:
            f.write("## Blocked Funnel\n\n")
            f.write("| Reason | Count |\n")
            f.write("|---|---|\n")
            for reason, count in blocked_counts.most_common():
                f.write(f"| {reason} | {count} |\n")
            f.write("\n")
        
        if top_opportunity:
            f.write("## Top Opportunity\n\n")
            f.write(f"- **Company**: {top_opportunity.get('company')}\n")
            f.write(f"- **Score**: {top_opportunity.get('qualification_score')} ({top_opportunity.get('qualification_tier')})\n")
            f.write(f"- **Buyer Fit**: {top_opportunity.get('buyer_fit', {}).get('buyer_fit', 'Unknown')}\n\n")
            opp = top_opportunity.get("opportunity")
            if opp and opp.get("why_now"):
                f.write("### Why Now\n\n")
                for reason in opp["why_now"]:
                    f.write(f"- {reason}\n")
                f.write(f"\n**Recommended Angle**: {opp.get('recommended_angle', '')}\n")
            f.write(f"\n**Qualification Reasoning**: {top_opportunity.get('qualification', {}).get('reasoning')}\n")
            
    # JSON Report
    with open("reports/lead_report.json", "w") as f:
        json.dump({
            "metrics": {
                "total_prospects": total_prospects,
                "qualified_prospects": qualified_prospects,
                "high_fit_buyers": high_fit_buyers,
                "verified_contacts": verified_contacts,
                "outreach_generated": outreach_generated,
                "blocked_funnel": dict(blocked_counts)
            },
            "top_opportunity": top_opportunity
        }, f, indent=4)
        
    print("\nReports generated:")
    print("  reports/lead_report.md")
    print("  reports/lead_report.json")
    print("  reports/contacts_found.csv")

if __name__ == "__main__":
    generate_demo_report()
