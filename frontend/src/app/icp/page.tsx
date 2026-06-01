"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Target, Loader2, Play, MapPin, Briefcase, Users, Search } from "lucide-react";

export default function ICPBuilder() {
  const [query, setQuery] = useState("We provide AI Transformation Services. Find potential customers in India.");
  const [loading, setLoading] = useState(false);
  const [icp, setIcp] = useState<any>(null);

  const buildICP = async () => {
    setLoading(true);
    setIcp(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/jobs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      const jobId = data.job_id;

      // Poll until ICP data is available
      const poll = setInterval(async () => {
        const statusRes = await fetch(`http://127.0.0.1:8000/api/v1/jobs/${jobId}`);
        const statusData = await statusRes.json();
        if (statusData.status === "completed" || statusData.status === "failed") {
          clearInterval(poll);
          const resultRes = await fetch(`http://127.0.0.1:8000/api/v1/jobs/${jobId}/results`);
          const resultData = await resultRes.json();
          if (resultData.report?.icp) {
            setIcp(resultData.report.icp);
          }
          localStorage.setItem("latest_report", JSON.stringify(resultData.report));
          setLoading(false);
        }
      }, 3000);
    } catch {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-10 pb-24">
      <div>
        <h1 className="text-4xl font-semibold tracking-tight mb-1">ICP Builder</h1>
        <p className="text-sm font-mono text-[var(--color-text-secondary)]">Define your Ideal Customer Profile from a natural language business description.</p>
      </div>

      {/* Input */}
      <div className="bg-[#151D2A] p-6 flex flex-col gap-4">
        <label className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-secondary)]">Business Offering</label>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={3}
          className="bg-[var(--color-background)] p-4 text-sm font-mono text-[var(--color-text-primary)] placeholder-[var(--color-text-secondary)] outline-none resize-none focus:ring-1 focus:ring-[var(--color-accent)] transition-all"
          placeholder="Describe your product or service..."
        />
        <button
          onClick={buildICP}
          disabled={loading}
          className="self-start bg-[var(--color-accent)] text-black px-6 py-2.5 font-mono text-xs uppercase tracking-widest font-bold hover:opacity-90 disabled:opacity-50 flex items-center gap-2 transition-opacity"
        >
          {loading ? <><Loader2 className="h-4 w-4 animate-spin" /> Generating...</> : <><Play className="h-4 w-4" /> Build ICP</>}
        </button>
      </div>

      {/* ICP Output */}
      <AnimatePresence>
        {icp && (
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="grid grid-cols-1 md:grid-cols-2 gap-1">
            
            <div className="bg-[#151D2A] p-6 flex flex-col gap-4">
              <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-[var(--color-text-secondary)]">
                <Briefcase className="h-4 w-4" /> Target Industries
              </div>
              <div className="flex flex-wrap gap-2">
                {icp.industries?.map((ind: string, i: number) => (
                  <span key={i} className="px-3 py-1.5 bg-[var(--color-accent)]/10 text-[var(--color-accent)] text-xs font-mono">{ind}</span>
                ))}
              </div>
            </div>

            <div className="bg-[#151D2A] p-6 flex flex-col gap-4">
              <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-[var(--color-text-secondary)]">
                <MapPin className="h-4 w-4" /> Target Regions
              </div>
              <div className="flex flex-wrap gap-2">
                {icp.regions?.map((r: string, i: number) => (
                  <span key={i} className="px-3 py-1.5 bg-white/5 text-[var(--color-text-primary)] text-xs font-mono">{r}</span>
                ))}
              </div>
            </div>

            <div className="bg-[#151D2A] p-6 flex flex-col gap-4">
              <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-[var(--color-text-secondary)]">
                <Users className="h-4 w-4" /> Decision Makers
              </div>
              <div className="flex flex-wrap gap-2">
                {icp.decision_makers?.map((dm: string, i: number) => (
                  <span key={i} className="px-3 py-1.5 bg-white/5 text-[var(--color-text-primary)] text-xs font-mono">{dm}</span>
                ))}
              </div>
            </div>

            <div className="bg-[#151D2A] p-6 flex flex-col gap-4">
              <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-widest text-[var(--color-text-secondary)]">
                <Search className="h-4 w-4" /> Search Keywords
              </div>
              <div className="flex flex-wrap gap-2">
                {icp.keywords?.map((kw: string, i: number) => (
                  <span key={i} className="px-3 py-1.5 bg-[var(--color-warning)]/10 text-[var(--color-warning)] text-xs font-mono">{kw}</span>
                ))}
              </div>
            </div>

            <div className="bg-[#151D2A] p-6 flex flex-col gap-4 md:col-span-2">
              <div className="text-xs font-mono uppercase tracking-widest text-[var(--color-text-secondary)]">Metadata</div>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-6 font-mono text-sm">
                <div>
                  <span className="text-[10px] text-[var(--color-text-secondary)] block mb-1">MARKET_TYPE</span>
                  <span>{icp.market_type}</span>
                </div>
                <div>
                  <span className="text-[10px] text-[var(--color-text-secondary)] block mb-1">COMPANY_SIZE</span>
                  <span>{icp.company_size}</span>
                </div>
                <div>
                  <span className="text-[10px] text-[var(--color-text-secondary)] block mb-1">REASONING</span>
                  <span className="text-[var(--color-text-secondary)]">{icp.reasoning}</span>
                </div>
              </div>
            </div>

          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
