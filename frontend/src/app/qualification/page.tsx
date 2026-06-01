"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

import { getSavedReport } from "@/lib/storage";

export default function QualificationPage() {
  const [prospects, setProspects] = useState<any[]>([]);

  useEffect(() => {
    const report = getSavedReport();
    if (report?.prospects) setProspects(report.prospects);
  }, []);

  const hotCount = prospects.filter((p) => p.qualification_tier === "Hot").length;
  const warmCount = prospects.filter((p) => p.qualification_tier === "Warm").length;
  const coldCount = prospects.filter((p) => p.qualification_tier === "Cold").length;

  return (
    <div className="flex flex-col gap-10 pb-24">
      <div>
        <h1 className="text-4xl font-semibold tracking-tight mb-1">Qualification Matrix</h1>
        <p className="text-sm font-mono text-[var(--color-text-secondary)]">Deterministic scoring applied by the rules engine. LLM writes reasoning only.</p>
      </div>

      {/* Tier Summary */}
      <div className="grid grid-cols-3 gap-1">
        <div className="bg-[#151D2A] p-6 text-center">
          <span className="text-5xl font-semibold text-[var(--color-success)]">{hotCount}</span>
          <span className="block text-xs font-mono uppercase tracking-widest text-[var(--color-text-secondary)] mt-2">Hot</span>
        </div>
        <div className="bg-[#151D2A] p-6 text-center">
          <span className="text-5xl font-semibold text-[var(--color-warning)]">{warmCount}</span>
          <span className="block text-xs font-mono uppercase tracking-widest text-[var(--color-text-secondary)] mt-2">Warm</span>
        </div>
        <div className="bg-[#151D2A] p-6 text-center">
          <span className="text-5xl font-semibold text-[var(--color-text-secondary)]">{coldCount}</span>
          <span className="block text-xs font-mono uppercase tracking-widest text-[var(--color-text-secondary)] mt-2">Cold</span>
        </div>
      </div>

      {/* Breakdown Table */}
      <div className="flex flex-col gap-1">
        {prospects.map((p: any, i: number) => (
          <motion.div
            key={i}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: i * 0.05 }}
            className="bg-[#151D2A] p-6 flex items-center justify-between"
          >
            <div className="flex items-center gap-6">
              <div className="w-40 font-semibold truncate">{p.company}</div>
              <div className="flex items-center gap-3 font-mono text-sm">
                <div className="w-24 h-2 bg-[rgba(255,255,255,0.05)] overflow-hidden">
                  <div
                    className={cn("h-full", p.qualification_score >= 70 ? "bg-[var(--color-success)]" : p.qualification_score >= 40 ? "bg-[var(--color-warning)]" : "bg-[var(--color-text-secondary)]")}
                    style={{ width: `${p.qualification_score}%` }}
                  />
                </div>
                <span className="text-[var(--color-text-secondary)]">{p.qualification_score}/100</span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {p.qualification_breakdown && (
                <div className="flex gap-4 text-xs font-mono text-[var(--color-text-secondary)]">
                  <span>IND: +{p.qualification_breakdown.industry_score}</span>
                  <span>AI: +{p.qualification_breakdown.ai_readiness_score}</span>
                  <span>SIG: +{p.qualification_breakdown.signals_score}</span>
                </div>
              )}
              <span className={cn(
                "px-2 py-1 text-xs font-mono font-bold uppercase",
                p.qualification_tier === "Hot" ? "text-[var(--color-success)] bg-[var(--color-success)]/10" :
                p.qualification_tier === "Warm" ? "text-[var(--color-warning)] bg-[var(--color-warning)]/10" :
                "text-[var(--color-text-secondary)] bg-white/5"
              )}>
                {p.qualification_tier}
              </span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
