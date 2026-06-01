"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Mail } from "lucide-react";

import { getSavedReport } from "@/lib/storage";

export default function OutreachPage() {
  const [prospects, setProspects] = useState<any[]>([]);
  useEffect(() => {
    const r = getSavedReport();
    if (r?.prospects) setProspects(r.prospects);
  }, []);
  const withOutreach = prospects.filter((p) => p.outreach);
  return (
    <div className="flex flex-col gap-10 pb-24">
      <div>
        <h1 className="text-4xl font-semibold tracking-tight mb-1">Outreach</h1>
        <p className="text-sm font-mono text-[var(--color-text-secondary)]">{withOutreach.length > 0 ? `${withOutreach.length} personalized outreach drafts generated.` : 'No outreach generated. Leads must pass all 5 gates before email is drafted.'}</p>
      </div>
      {withOutreach.length > 0 ? (
        <div className="flex flex-col gap-6">
          {withOutreach.map((p: any, i: number) => (
            <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }} className="bg-[#151D2A] p-6">
              <div className="flex items-center gap-2 mb-4">
                <Mail className="h-4 w-4 text-[var(--color-accent)]" />
                <h2 className="font-semibold">{p.company}</h2>
              </div>
              <div className="bg-[var(--color-background)] p-4 border border-[rgba(255,255,255,0.05)] font-mono text-sm whitespace-pre-wrap">
                <div className="text-[var(--color-text-primary)] mb-3 pb-3 border-b border-[rgba(255,255,255,0.05)]">SUBJECT: {p.outreach.subject}</div>
                <div className="text-[var(--color-text-secondary)]">{p.outreach.body}</div>
              </div>
              <div className="flex gap-2 mt-4">
                <button className="bg-[var(--color-accent)] text-black px-4 py-2 text-xs font-mono font-bold uppercase tracking-widest">Approve</button>
                <button className="bg-white/5 px-4 py-2 text-xs font-mono uppercase tracking-widest text-[var(--color-text-secondary)]">Regenerate</button>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="bg-[#151D2A] p-8 text-center">
          <p className="text-sm font-mono text-[var(--color-text-secondary)]">Outreach is only generated when a lead passes: Research → Qualification → Buyer Fit → Contact Discovery gates.</p>
        </div>
      )}
    </div>
  );
}
