"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";
import Link from "next/link";

import { getSavedReport } from "@/lib/storage";

export default function ProspectDiscovery() {
  const [prospects, setProspects] = useState<any[]>([]);

  useEffect(() => {
    const report = getSavedReport();
    if (report?.prospects) setProspects(report.prospects);
  }, []);

  return (
    <div className="flex flex-col gap-10 pb-24">
      <div>
        <h1 className="text-4xl font-semibold tracking-tight mb-1">Prospect Discovery</h1>
        <p className="text-sm font-mono text-[var(--color-text-secondary)]">
          {prospects.length > 0
            ? `${prospects.length} entities discovered from latest pipeline execution.`
            : "No prospects yet. Run a pipeline from the Dashboard to discover leads."}
        </p>
      </div>

      {prospects.length > 0 && (
        <div className="bg-[#151D2A]">
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left font-mono">
              <thead className="text-[10px] text-[var(--color-text-secondary)] uppercase tracking-widest bg-[#1c1b1b]">
                <tr>
                  <th className="px-6 py-4">Entity</th>
                  <th className="px-6 py-4">Website</th>
                  <th className="px-6 py-4">Score</th>
                  <th className="px-6 py-4">Tier</th>
                  <th className="px-6 py-4">Blocked</th>
                  <th className="px-6 py-4">Action</th>
                </tr>
              </thead>
              <tbody>
                {prospects.map((p: any, i: number) => (
                  <motion.tr
                    key={i}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: i * 0.05 }}
                    className="border-t border-[rgba(255,255,255,0.03)] hover:bg-[rgba(255,255,255,0.02)] transition-colors"
                  >
                    <td className="px-6 py-4 font-semibold text-[var(--color-text-primary)]">{p.company}</td>
                    <td className="px-6 py-4">
                      <a href={p.website} target="_blank" rel="noreferrer" className="text-[var(--color-text-secondary)] hover:text-[var(--color-accent)] flex items-center gap-1">
                        {p.website?.replace(/https?:\/\//, '').slice(0, 30)} <ExternalLink className="h-3 w-3" />
                      </a>
                    </td>
                    <td className="px-6 py-4">
                      <span className={cn(
                        "px-2 py-1 text-xs font-bold",
                        p.qualification_score >= 70 ? "text-[var(--color-success)] bg-[var(--color-success)]/10" :
                        p.qualification_score >= 40 ? "text-[var(--color-warning)] bg-[var(--color-warning)]/10" :
                        "text-[var(--color-text-secondary)] bg-white/5"
                      )}>
                        {p.qualification_score}/100
                      </span>
                    </td>
                    <td className="px-6 py-4 text-[var(--color-text-secondary)]">{p.qualification_tier}</td>
                    <td className="px-6 py-4">
                      {p.blocked_reason ? (
                        <span className="text-xs text-[var(--color-danger)] bg-[var(--color-danger)]/10 px-2 py-1">{p.blocked_reason}</span>
                      ) : (
                        <span className="text-xs text-[var(--color-success)]">CLEAR</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <Link href={`/opportunities/${i}`} className="text-[var(--color-accent)] hover:text-green-300 flex items-center gap-1 text-xs uppercase tracking-widest font-bold">
                        Inspect <ArrowRight className="h-3 w-3" />
                      </Link>
                    </td>
                  </motion.tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
