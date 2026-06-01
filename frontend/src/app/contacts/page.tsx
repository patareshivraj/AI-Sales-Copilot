"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Users } from "lucide-react";

import { getSavedReport } from "@/lib/storage";

export default function ContactsPage() {
  const [prospects, setProspects] = useState<any[]>([]);
  useEffect(() => {
    const r = getSavedReport();
    if (r?.prospects) setProspects(r.prospects);
  }, []);
  const withContacts = prospects.filter((p) => p.contacts && p.contacts.length > 0);
  return (
    <div className="flex flex-col gap-10 pb-24">
      <div>
        <h1 className="text-4xl font-semibold tracking-tight mb-1">Contacts</h1>
        <p className="text-sm font-mono text-[var(--color-text-secondary)]">{withContacts.length > 0 ? `Verified decision-makers discovered for ${withContacts.length} companies.` : 'No verified contacts found. Public sources rarely expose direct emails.'}</p>
      </div>
      {withContacts.length > 0 ? (
        <div className="flex flex-col gap-1">
          {withContacts.map((p: any, i: number) => (
            <motion.div key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }} className="bg-[#151D2A] p-6">
              <h2 className="font-semibold mb-3 flex items-center gap-2"><Users className="h-4 w-4 text-[var(--color-accent)]" /> {p.company}</h2>
              {p.contacts.map((c: any, j: number) => (
                <div key={j} className="font-mono text-sm grid grid-cols-4 gap-4 py-2 border-t border-[rgba(255,255,255,0.03)]">
                  <div><span className="text-[10px] text-[var(--color-text-secondary)] block">NAME</span>{c.name}</div>
                  <div><span className="text-[10px] text-[var(--color-text-secondary)] block">TITLE</span>{c.title}</div>
                  <div><span className="text-[10px] text-[var(--color-text-secondary)] block">SOURCE</span>{c.source}</div>
                  <div><span className="text-[10px] text-[var(--color-text-secondary)] block">CONFIDENCE</span>{c.confidence}%</div>
                </div>
              ))}
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="bg-[#151D2A] p-8 text-center">
          <p className="text-sm font-mono text-[var(--color-text-secondary)]">Contact discovery uses public web sources only.</p>
          <p className="text-sm font-mono text-[var(--color-text-secondary)] mt-1">Integrate Apollo or Hunter.io for enterprise-grade enrichment.</p>
        </div>
      )}
    </div>
  );
}
