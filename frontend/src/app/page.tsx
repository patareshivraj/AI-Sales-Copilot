"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Terminal, 
  Play, 
  Loader2, 
  Building2, 
  CheckCircle2, 
  Target, 
  ShieldAlert, 
  Ban,
  ArrowRight
} from "lucide-react";
import { cn } from "@/lib/utils";

export default function Dashboard() {
  const [query, setQuery] = useState("We provide AI Transformation Services. Find potential customers in India.");
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("idle");
  const [report, setReport] = useState<any>(null);

  const startJob = async () => {
    setStatus("starting");
    setReport(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setJobId(data.job_id);
      setStatus("processing");
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (jobId && status === "processing") {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`http://127.0.0.1:8000/api/v1/jobs/${jobId}`);
          const data = await res.json();
          if (data.status === "completed") {
            setStatus("fetching_results");
            const res2 = await fetch(`http://127.0.0.1:8000/api/v1/jobs/${jobId}/results`);
            const finalData = await res2.json();
            setReport(finalData.report);
            setStatus("completed");
            // Save to local storage for the details page
            localStorage.setItem('latest_report', JSON.stringify(finalData.report));
          } else if (data.status === "failed") {
            setStatus("failed");
          }
        } catch (err) {
          console.error(err);
        }
      }, 3000);
    }
    return () => clearInterval(interval);
  }, [jobId, status]);

  return (
    <div className="flex flex-col gap-12 pb-24">
      
      {/* COMMAND CENTER (Dynamic Input) */}
      <div className="flex flex-col gap-4">
        <h1 className="text-4xl font-semibold tracking-tight text-[var(--color-text-primary)]">Command Center</h1>
        
        <div className="relative flex items-center bg-[#151D2A] rounded-none focus-within:ring-1 focus-within:ring-[var(--color-accent)] transition-all">
          <div className="px-4 text-[var(--color-text-secondary)]">
            <Terminal className="h-5 w-5" />
          </div>
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-transparent py-4 text-[var(--color-text-primary)] placeholder-[var(--color-text-secondary)] outline-none font-mono text-sm"
            placeholder="Enter your business offering and target market..."
          />
          <button 
            onClick={startJob}
            disabled={status === "processing" || status === "fetching_results" || status === "starting"}
            className="bg-[var(--color-accent)] hover:bg-blue-600 disabled:opacity-50 text-white px-8 py-4 font-medium flex items-center gap-2 transition-colors uppercase tracking-widest text-xs"
          >
            {status === "processing" || status === "starting" || status === "fetching_results" ? (
              <><Loader2 className="h-4 w-4 animate-spin" /> Processing</>
            ) : (
              <><Play className="h-4 w-4" /> Execute Run</>
            )}
          </button>
        </div>

        {/* Status Indicators */}
        <AnimatePresence>
          {(status === "processing" || status === "fetching_results") && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="flex items-center gap-3 text-sm text-[var(--color-accent)] font-mono bg-[#151D2A]/50 p-4"
            >
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>[SYSTEM] Orchestrating multi-agent pipeline. Searching live prospects, scraping sites, and calculating qualification metrics...</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* DYNAMIC RESULTS */}
      {report && status === "completed" && (
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex flex-col gap-12"
        >
          {/* Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-1">
            <div className="bg-[#151D2A] p-6 flex flex-col gap-2">
              <span className="text-xs font-mono uppercase text-[var(--color-text-secondary)]">Prospects Found</span>
              <span className="text-4xl font-semibold">{report.prospects.length}</span>
            </div>
            <div className="bg-[#151D2A] p-6 flex flex-col gap-2">
              <span className="text-xs font-mono uppercase text-[var(--color-text-secondary)]">Qualified (Warm/Hot)</span>
              <span className="text-4xl font-semibold text-[var(--color-success)]">
                {report.prospects.filter((p: any) => p.qualification_tier !== "Cold").length}
              </span>
            </div>
            <div className="bg-[#151D2A] p-6 flex flex-col gap-2">
              <span className="text-xs font-mono uppercase text-[var(--color-text-secondary)]">Competitors Blocked</span>
              <span className="text-4xl font-semibold text-[var(--color-danger)]">
                {String(Object.entries(report.blocked_reasons).find(([k]) => k === "COMPETITOR")?.[1] || 0)}
              </span>
            </div>
            <div className="bg-[#151D2A] p-6 flex flex-col gap-2">
              <span className="text-xs font-mono uppercase text-[var(--color-text-secondary)]">Outreach Ready</span>
              <span className="text-4xl font-semibold text-[var(--color-accent)]">
                {report.prospects.filter((p: any) => p.outreach !== null).length}
              </span>
            </div>
          </div>

          {/* Table & Funnel Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Prospects Table */}
            <div className="lg:col-span-2 bg-[#151D2A] p-6 flex flex-col gap-6">
              <h2 className="text-lg font-medium tracking-tight">Intelligence Feed</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left font-mono">
                  <thead className="text-xs text-[var(--color-text-secondary)] uppercase border-b border-[rgba(255,255,255,0.05)]">
                    <tr>
                      <th className="py-3 font-medium">Target Entity</th>
                      <th className="py-3 font-medium">Score</th>
                      <th className="py-3 font-medium">Buyer Fit</th>
                      <th className="py-3 font-medium">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {report.prospects.map((lead: any, i: number) => (
                      <tr key={i} className="border-b border-[rgba(255,255,255,0.05)] hover:bg-[rgba(255,255,255,0.02)] transition-colors">
                        <td className="py-4">
                          <div className="flex flex-col">
                            <span className="font-semibold text-[var(--color-text-primary)]">{lead.company}</span>
                            <a href={lead.website} target="_blank" rel="noreferrer" className="text-xs text-[var(--color-text-secondary)] hover:text-[var(--color-accent)]">{lead.website}</a>
                          </div>
                        </td>
                        <td className="py-4">
                          <span className={cn(
                            "px-2 py-1 text-xs font-medium",
                            lead.qualification_tier === "Hot" ? "text-[var(--color-success)] bg-[var(--color-success)]/10" : 
                            lead.qualification_tier === "Warm" ? "text-[var(--color-warning)] bg-[var(--color-warning)]/10" : 
                            "text-[var(--color-text-secondary)] bg-white/5"
                          )}>
                            {lead.qualification_score}/100
                          </span>
                        </td>
                        <td className="py-4 text-[var(--color-text-secondary)]">{lead.buyer_fit?.buyer_type || "Unknown"}</td>
                        <td className="py-4">
                          <a href={`/opportunities/${i}`} className="text-[var(--color-accent)] hover:text-blue-400 flex items-center gap-1 text-xs uppercase tracking-widest font-bold">
                            Inspect <ArrowRight className="h-3 w-3" />
                          </a>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Blocked Funnel */}
            <div className="bg-[#151D2A] p-6 flex flex-col">
              <div className="flex items-center gap-2 mb-6">
                <ShieldAlert className="h-5 w-5 text-[var(--color-warning)]" />
                <h2 className="text-lg font-medium tracking-tight">Blocked Funnel</h2>
              </div>
              <div className="flex flex-col gap-1 flex-1">
                {Object.entries(report.blocked_reasons).map(([reason, count]: any, i) => (
                  <div key={reason} className="flex items-center justify-between p-3 bg-[rgba(255,255,255,0.02)]">
                    <div className="flex items-center gap-2">
                      <Ban className={cn("h-4 w-4", reason === "COMPETITOR" || reason === "NO_VERIFIED_CONTACT" ? "text-[var(--color-danger)]" : "text-[var(--color-text-secondary)]")} />
                      <span className="text-xs font-mono text-[var(--color-text-secondary)]">{reason}</span>
                    </div>
                    <span className="text-sm font-mono font-medium">{count}</span>
                  </div>
                ))}
                {Object.keys(report.blocked_reasons).length === 0 && (
                  <div className="text-sm text-[var(--color-text-secondary)] italic p-3">No leads blocked.</div>
                )}
              </div>
            </div>

          </div>
        </motion.div>
      )}
    </div>
  );
}
