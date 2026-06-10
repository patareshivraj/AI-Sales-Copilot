import csv
import os
import json

def split_name(full_name: str) -> tuple[str, str]:
    if not full_name:
        return "", ""
    parts = full_name.strip().split(" ", 1)
    if len(parts) == 2:
        return parts[0], parts[1]
    return parts[0], ""

def export_to_crm(prospects: list[dict], job_id: str = None):
    """
    Export approved/qualified contacts to CSV files in HubSpot, Salesforce, and general formats.
    Generates both master files and job-specific files.
    """
    os.makedirs("reports", exist_ok=True)
    
    # 1. Collect all contacts currently approved/found
    # If a prospect doesn't have an explicit 'approved' key, default it based on qualification/fit
    all_rows = []
    approved_rows = []
    
    for p in prospects:
        contact = p.get("contact") or {}
        opp = p.get("opportunity") or {}
        
        # Determine approval state (can be True, False, or None/unreviewed)
        # In results, 'approved' is set by the human review workflow
        approved = p.get("approved")
        
        # Prepare base fields
        company = p.get("company", "")
        contact_name = contact.get("contact_name") or ""
        title = contact.get("title") or ""
        linkedin_url = contact.get("linkedin_url") or ""
        apollo_id = contact.get("apollo_id") or ""
        score = p.get("qualification_score", "")
        tier = p.get("qualification_tier", "")
        blocked_reason = p.get("blocked_reason", "")
        urgency = opp.get("urgency", "")
        
        first_name, last_name = split_name(contact_name)
        
        row_data = {
            "company": company,
            "contact_name": contact_name,
            "first_name": first_name,
            "last_name": last_name,
            "title": title,
            "linkedin_url": linkedin_url,
            "apollo_id": apollo_id,
            "score": score,
            "tier": tier,
            "blocked_reason": blocked_reason,
            "urgency": urgency,
            "approved": approved
        }
        
        all_rows.append(row_data)
        if approved is True:
            approved_rows.append(row_data)

    # Helper function to write general CSV
    def write_general_csv(filepath: str, rows: list[dict]):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Company", "Website", "Contact Name", "Title", "LinkedIn URL", "Score", "Tier", "Blocked Reason", "Urgency", "Approved"])
            for r in rows:
                writer.writerow([
                    r["company"],
                    "", # website slot
                    r["contact_name"],
                    r["title"],
                    r["linkedin_url"],
                    r["score"],
                    r["tier"],
                    r["blocked_reason"],
                    r["urgency"],
                    r["approved"]
                ])

    # Helper function to write HubSpot CSV
    def write_hubspot_csv(filepath: str, rows: list[dict]):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Company Name", "First Name", "Last Name", "Job Title", "LinkedIn", "External ID", "Lead Score", "Lead Status"])
            for r in rows:
                writer.writerow([
                    r["company"],
                    r["first_name"],
                    r["last_name"],
                    r["title"],
                    r["linkedin_url"],
                    r["apollo_id"],
                    r["score"],
                    r["tier"]
                ])

    # Helper function to write Salesforce CSV
    def write_salesforce_csv(filepath: str, rows: list[dict]):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Account Name", "Contact Name", "Title", "LinkedIn", "External ID", "Lead Score", "Lead Status"])
            for r in rows:
                writer.writerow([
                    r["company"],
                    r["contact_name"],
                    r["title"],
                    r["linkedin_url"],
                    r["apollo_id"],
                    r["score"],
                    r["tier"]
                ])

    # Write job-specific outputs if job_id is provided
    if job_id:
        write_general_csv(f"reports/job_{job_id}_contacts_found.csv", all_rows)
        write_general_csv(f"reports/job_{job_id}_approved_leads.csv", approved_rows)
        write_hubspot_csv(f"reports/job_{job_id}_hubspot_import.csv", approved_rows)
        write_salesforce_csv(f"reports/job_{job_id}_salesforce_import.csv", approved_rows)

    # Write master files (append-friendly or fully re-generated from all approved in outputs/)
    # Let's re-generate master files from all output files for maximum consistency!
    master_all = []
    master_approved = []
    
    outputs_dir = "outputs"
    if os.path.exists(outputs_dir):
        for fname in os.listdir(outputs_dir):
            if fname.startswith("job_") and fname.endswith(".json"):
                try:
                    with open(os.path.join(outputs_dir, fname), "r") as f:
                        job_report = json.load(f)
                    for p in job_report.get("prospects", []):
                        contact = p.get("contact") or {}
                        opp = p.get("opportunity") or {}
                        approved = p.get("approved")
                        company = p.get("company", "")
                        contact_name = contact.get("contact_name") or ""
                        title = contact.get("title") or ""
                        linkedin_url = contact.get("linkedin_url") or ""
                        apollo_id = contact.get("apollo_id") or ""
                        score = p.get("qualification_score", "")
                        tier = p.get("qualification_tier", "")
                        blocked_reason = p.get("blocked_reason", "")
                        urgency = opp.get("urgency", "")
                        
                        first_name, last_name = split_name(contact_name)
                        
                        row_data = {
                            "company": company,
                            "contact_name": contact_name,
                            "first_name": first_name,
                            "last_name": last_name,
                            "title": title,
                            "linkedin_url": linkedin_url,
                            "apollo_id": apollo_id,
                            "score": score,
                            "tier": tier,
                            "blocked_reason": blocked_reason,
                            "urgency": urgency,
                            "approved": approved
                        }
                        master_all.append(row_data)
                        if approved is True:
                            master_approved.append(row_data)
                except Exception:
                    pass

    # If master lists are empty (e.g. no master lookup completed yet), use current job rows
    if not master_all:
        master_all = all_rows
        master_approved = approved_rows

    write_general_csv("reports/contacts_found.csv", master_all)
    write_general_csv("reports/approved_leads.csv", master_approved)
    write_hubspot_csv("reports/hubspot_import.csv", master_approved)
    write_salesforce_csv("reports/salesforce_import.csv", master_approved)

    print(f"[CRMExporter] Exported {len(approved_rows)} approved leads for job {job_id}.")
