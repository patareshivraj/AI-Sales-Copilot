"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Ban } from "lucide-react";
import { cn } from "@/lib/utils";

import { getSavedReport } from "@/lib/storage";

export default function ReportsPage() {
  const [report, setReport] = useState<any>(null);
  useEffect(() => {
    setReport(getSavedReport());
  }, []);

  if (!report) {
    return (
      <div className="flex flex-col gap-10 pb-24">
        <h1 className="text-4xl font-semibold tracking-tight">Reports</h1>
        <p className="text-sm font-mono text-[var(--color-text-secondary)]">No pipeline results yet. Run a query from the Dashboard.</p>
      </div>
    );
  }

  const total = report.prospects?.length || 0;
  const qualified = report.prospects?.filter((p: any) => p.qualification_tier !== "Cold").length || 0;
  const blocked = report.prospects?.reduce((acc: Record<string, number>, p: any) => {
    if (p.blocked_reason) acc[p.blocked_reason] = (acc[p.blocked_reason] || 0) + 1;
    return acc;
  }, {}) || {};

  return (
    <div className="flex flex-col gap-10 pb-24">
      <div>
        <h1 className="text-4xl font-semibold tracking-tight mb-1">Pipeline Report</h1>
        <p className="text-sm font-mono text-[var(--color-text-secondary)]">Audit trail for the latest execution run.</p>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-1">
        <div className="bg-[#151D2A] p-6"><span className="text-xs font-mono text-[var(--color-text-secondary)] block mb-1">TOTAL_PROSPECTS</span><span className="text-4xl font-semibold">{total}</span></div>
        <div className="bg-[#151D2A] p-6"><span className="text-xs font-mono text-[var(--color-text-secondary)] block mb-1">QUALIFIED</span><span className="text-4xl font-semibold text-[var(--color-success)]">{qualified}</span></div>
        <div className="bg-[#151D2A] p-6"><span className="text-xs font-mono text-[var(--color-text-secondary)] block mb-1">OUTREACH_READY</span><span className="text-4xl font-semibold text-[var(--color-accent)]">{report.prospects?.filter((p: any) => p.outreach).length || 0}</span></div>
        <div className="bg-[#151D2A] p-6"><span className="text-xs font-mono text-[var(--color-text-secondary)] block mb-1">BLOCKED</span><span className="text-4xl font-semibold text-[var(--color-danger)]">{String(Object.values(blocked).reduce((a: any, b: any) => a + b, 0))}</span></div>
      </div>
      <div className="bg-[#151D2A] p-6">
        <h2 className="text-sm font-mono uppercase tracking-widest text-[var(--color-text-secondary)] mb-4">Blocked Funnel Breakdown</h2>
        <div className="flex flex-col gap-1">
          {Object.entries(blocked).map(([reason, count]: any, i) => (
            <motion.div key={reason} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.05 }} className="flex items-center justify-between p-3 bg-[rgba(255,255,255,0.02)]">
              <div className="flex items-center gap-2"><Ban className={cn("h-4 w-4", reason === "COMPETITOR" ? "text-[var(--color-danger)]" : "text-[var(--color-text-secondary)]")} /><span className="text-xs font-mono">{reason}</span></div>
              <span className="font-mono font-medium">{count}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
