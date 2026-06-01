"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import { 
  ExternalLink, 
  Target, 
  ShieldCheck,
  Lightbulb,
  Mail,
  CheckCircle2,
  AlertTriangle,
  Microscope
} from "lucide-react";
import { cn } from "@/lib/utils";

function SectionHeader({ title, confidence }: { title: string, confidence?: number }) {
  return (
    <div className="flex items-center justify-between border-b border-[rgba(255,255,255,0.05)] pb-3 mb-5">
      <h2 className="text-sm font-mono uppercase tracking-widest text-[var(--color-text-secondary)]">{title}</h2>
      {confidence !== undefined && (
        <span className="text-xs font-mono text-[var(--color-accent)] bg-[var(--color-accent)]/10 px-2 py-0.5">
          CONFIDENCE: {confidence}%
        </span>
      )}
    </div>
  );
}

export default function CompanyDetail() {
  const params = useParams();
  const [prospect, setProspect] = useState<any>(null);

  useEffect(() => {
    const data = localStorage.getItem('latest_report');
    if (data) {
      const report = JSON.parse(data);
      const index = parseInt(params.id as string);
      if (report.prospects && report.prospects[index]) {
        setProspect(report.prospects[index]);
      }
    }
  }, [params.id]);

  if (!prospect) {
    return <div className="p-8 text-sm font-mono text-[var(--color-text-secondary)]">Loading telemetry data...</div>;
  }

  const isBlocked = prospect.blocked_reason !== null;

  return (
    <div className="flex flex-col gap-8 pb-24">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-[rgba(255,255,255,0.05)] pb-6">
        <div>
          <h1 className="text-4xl font-semibold tracking-tight text-[var(--color-text-primary)] mb-2">{prospect.company}</h1>
          <a href={prospect.website} target="_blank" rel="noreferrer" className="flex items-center gap-1 font-mono text-[var(--color-text-secondary)] hover:text-[var(--color-accent)] transition-colors text-sm">
            {prospect.website} <ExternalLink className="h-3 w-3" />
          </a>
        </div>
        
        <div className="flex items-center gap-4">
          {isBlocked ? (
            <div className="flex items-center gap-2 px-4 py-2 bg-[var(--color-danger)]/10 text-[var(--color-danger)] border border-[var(--color-danger)]/20 font-mono text-xs uppercase tracking-widest">
              <AlertTriangle className="h-4 w-4" /> BLOCKED: {prospect.blocked_reason}
            </div>
          ) : (
            <div className="flex items-center gap-2 px-4 py-2 bg-[var(--color-success)]/10 text-[var(--color-success)] border border-[var(--color-success)]/20 font-mono text-xs uppercase tracking-widest">
              <CheckCircle2 className="h-4 w-4" /> CLEARED FOR OUTREACH
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* LEFT COLUMN */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="bg-[#151D2A] p-6">
            <SectionHeader title="Opportunity Intelligence" />
            {prospect.opportunity ? (
              <div className="flex flex-col gap-4">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-[var(--color-text-secondary)]">URGENCY_LEVEL:</span>
                  <span className={cn(
                    "text-xs font-bold uppercase tracking-widest px-2 py-0.5",
                    prospect.opportunity.urgency === "High" ? "bg-[var(--color-success)]/10 text-[var(--color-success)]" : "bg-[var(--color-warning)]/10 text-[var(--color-warning)]"
                  )}>{prospect.opportunity.urgency}</span>
                </div>
                <div className="space-y-2">
                  <h3 className="text-xs font-mono text-[var(--color-text-secondary)] mb-2">WHY_NOW_SIGNALS:</h3>
                  {prospect.opportunity.why_now.map((reason: string, i: number) => (
                    <div key={i} className="flex items-start gap-3">
                      <div className="h-1.5 w-1.5 bg-[var(--color-accent)] mt-1.5 rounded-none shrink-0" />
                      <span className="text-sm text-[var(--color-text-primary)]">{reason}</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-sm font-mono text-[var(--color-text-secondary)]">No opportunity data extracted (Pipeline blocked early).</div>
            )}
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-[#151D2A] p-6">
            <SectionHeader title="Research Telemetry" confidence={prospect.research?.confidence_score} />
            {prospect.research ? (
              <div className="grid grid-cols-2 gap-6">
                <div className="flex flex-col gap-4">
                  <div>
                    <span className="text-xs font-mono text-[var(--color-text-secondary)] block mb-1">INDUSTRY</span>
                    <span className="text-sm">{prospect.research.industry}</span>
                  </div>
                  <div>
                    <span className="text-xs font-mono text-[var(--color-text-secondary)] block mb-1">AI_READINESS</span>
                    <span className="text-sm">{prospect.research.ai_readiness}</span>
                  </div>
                </div>
                <div>
                  <span className="text-xs font-mono text-[var(--color-text-secondary)] block mb-2">EXTRACTED_SIGNALS</span>
                  <div className="flex flex-col gap-3">
                    {prospect.research.signals.map((sig: any, i: number) => (
                      <div key={i} className="border-l-2 border-[var(--color-accent)] pl-3">
                        <span className="block text-[10px] font-mono text-[var(--color-text-secondary)] uppercase">{sig.category} [{sig.confidence}%]</span>
                        <span className="text-sm">{sig.description}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-sm font-mono text-[var(--color-text-secondary)]">Research data unavailable.</div>
            )}
          </motion.div>

          {prospect.outreach && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="bg-[#151D2A] p-6">
              <SectionHeader title="Generated Outreach Payload" />
              <div className="bg-[var(--color-background)] p-4 border border-[rgba(255,255,255,0.05)] text-sm font-mono leading-relaxed whitespace-pre-wrap text-[var(--color-text-secondary)]">
                <div className="text-[var(--color-text-primary)] mb-4 pb-4 border-b border-[rgba(255,255,255,0.05)]">
                  SUBJECT: {prospect.outreach.subject}
                </div>
                {prospect.outreach.body}
              </div>
            </motion.div>
          )}

        </div>

        {/* RIGHT COLUMN */}
        <div className="flex flex-col gap-6">
          
          <motion.div initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} className="bg-[#151D2A] p-6">
            <SectionHeader title="Qualification Matrix" />
            <div className="flex flex-col items-center justify-center py-4">
              <div className="text-6xl font-semibold tracking-tighter text-[var(--color-text-primary)] mb-1">
                {prospect.qualification_score}
              </div>
              <span className="text-xs font-mono text-[var(--color-text-secondary)]">SCORE / 100</span>
            </div>
            {prospect.qualification_breakdown && (
              <div className="space-y-3 pt-4 border-t border-[rgba(255,255,255,0.05)] font-mono text-sm">
                <div className="flex justify-between">
                  <span className="text-[var(--color-text-secondary)]">Industry_Match</span>
                  <span className="text-[var(--color-success)]">+{prospect.qualification_breakdown.industry_score}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--color-text-secondary)]">AI_Readiness</span>
                  <span className="text-[var(--color-success)]">+{prospect.qualification_breakdown.ai_readiness_score}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-[var(--color-text-secondary)]">Signal_Strength</span>
                  <span className="text-[var(--color-success)]">+{prospect.qualification_breakdown.signals_score}</span>
                </div>
              </div>
            )}
          </motion.div>

          {prospect.buyer_fit && (
            <motion.div initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }} className="bg-[#151D2A] p-6">
              <SectionHeader title="Buyer Fit Analysis" />
              <div className="flex flex-col gap-4 font-mono">
                <div>
                  <span className="text-[10px] text-[var(--color-text-secondary)] block mb-1">CLASSIFICATION</span>
                  <span className="text-sm">{prospect.buyer_fit.buyer_type}</span>
                </div>
                <div>
                  <span className="text-[10px] text-[var(--color-text-secondary)] block mb-1">IS_COMPETITOR</span>
                  <span className={cn("text-sm", prospect.buyer_fit.is_competitor ? "text-[var(--color-danger)]" : "text-[var(--color-success)]")}>
                    {prospect.buyer_fit.is_competitor ? "TRUE" : "FALSE"}
                  </span>
                </div>
              </div>
            </motion.div>
          )}

        </div>
      </div>
    </div>
  );
}
