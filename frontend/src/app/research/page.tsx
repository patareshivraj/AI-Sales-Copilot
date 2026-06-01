"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Microscope } from "lucide-react";

export default function ResearchPage() {
  const [prospects, setProspects] = useState<any[]>([]);

  useEffect(() => {
    const data = localStorage.getItem("latest_report");
    if (data) {
      const report = JSON.parse(data);
      if (report?.prospects) setProspects(report.prospects);
    }
  }, []);

  const withResearch = prospects.filter((p) => p.research && p.research.industry);

  return (
    <div className="flex flex-col gap-10 pb-24">
      <div>
        <h1 className="text-4xl font-semibold tracking-tight mb-1">Research Telemetry</h1>
        <p className="text-sm font-mono text-[var(--color-text-secondary)]">
          {withResearch.length > 0
            ? `Extracted structured intelligence from ${withResearch.length} entities.`
            : "No research data yet. Run a pipeline from the Dashboard."}
        </p>
      </div>

      <div className="flex flex-col gap-1">
        {withResearch.map((p: any, i: number) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06 }}
            className="bg-[#151D2A] p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <Microscope className="h-4 w-4 text-[var(--color-accent)]" />
                <h2 className="font-semibold text-lg">{p.company}</h2>
              </div>
              <span className="text-xs font-mono text-[var(--color-text-secondary)]">
                AI_READINESS: <span className="text-[var(--color-text-primary)]">{p.research.ai_readiness}</span>
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 font-mono text-sm">
              <div>
                <span className="text-[10px] text-[var(--color-text-secondary)] block mb-1">INDUSTRY</span>
                <span>{p.research.industry}</span>
              </div>
              <div>
                <span className="text-[10px] text-[var(--color-text-secondary)] block mb-1">SERVICES</span>
                <span className="text-[var(--color-text-secondary)]">{p.research.services?.join(", ") || "N/A"}</span>
              </div>
              <div>
                <span className="text-[10px] text-[var(--color-text-secondary)] block mb-1">PAIN_POINTS</span>
                <span className="text-[var(--color-text-secondary)]">{p.research.pain_points?.join(", ") || "N/A"}</span>
              </div>
            </div>

            {p.research.signals && p.research.signals.length > 0 && (
              <div className="mt-4 pt-4 border-t border-[rgba(255,255,255,0.05)]">
                <span className="text-[10px] font-mono text-[var(--color-text-secondary)] block mb-2">EXTRACTED_SIGNALS</span>
                <div className="flex flex-col gap-2">
                  {p.research.signals.map((sig: any, j: number) => (
                    <div key={j} className="border-l-2 border-[var(--color-accent)] pl-3 text-sm">
                      <span className="text-[10px] text-[var(--color-text-secondary)] uppercase">{sig.category} [{sig.confidence}%]</span>
                      <span className="block text-[var(--color-text-primary)]">{sig.description}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
