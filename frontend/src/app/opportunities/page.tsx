"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { CheckCircle2 } from "lucide-react";
import { cn } from "@/lib/utils";
import Link from "next/link";

import { getSavedReport } from "@/lib/storage";

export default function OpportunitiesPage() {
  const [prospects, setProspects] = useState<any[]>([]);
  useEffect(() => {
    const r = getSavedReport();
    if (r?.prospects) setProspects(r.prospects);
  }, []);
  const withOpp = prospects.filter((p) => p.opportunity);
  return (
    <div className="flex flex-col gap-10 pb-24">
      <div>
        <h1 className="text-4xl font-semibold tracking-tight mb-1">Opportunity Intelligence</h1>
        <p className="text-sm font-mono text-[var(--color-text-secondary)]">{withOpp.length > 0 ? `"Why Now" signals for ${withOpp.length} entities.` : 'Run a pipeline first.'}</p>
      </div>
      <div className="flex flex-col gap-1">
        {withOpp.map((p: any, i: number) => (
          <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }} className="bg-[#151D2A] p-6">
            <div className="flex items-center justify-between mb-4">
              <Link href={`/opportunities/${prospects.indexOf(p)}`} className="font-semibold text-lg hover:text-[var(--color-accent)] transition-colors">{p.company}</Link>
              <span className={cn("px-2 py-0.5 text-xs font-mono font-bold uppercase", p.opportunity.urgency === "High" ? "bg-[var(--color-success)]/10 text-[var(--color-success)]" : "bg-[var(--color-warning)]/10 text-[var(--color-warning)]")}>{p.opportunity.urgency} Urgency</span>
            </div>
            <div className="flex flex-col gap-2">
              {p.opportunity.why_now?.map((r: string, j: number) => (
                <div key={j} className="flex items-start gap-2"><CheckCircle2 className="h-4 w-4 text-[var(--color-accent)] mt-0.5 shrink-0" /><span className="text-sm text-[var(--color-text-secondary)]">{r}</span></div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
