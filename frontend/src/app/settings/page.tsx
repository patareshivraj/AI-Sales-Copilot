"use client";

export default function SettingsPage() {
  return (
    <div className="flex flex-col gap-10 pb-24">
      <div>
        <h1 className="text-4xl font-semibold tracking-tight mb-1">Settings</h1>
        <p className="text-sm font-mono text-[var(--color-text-secondary)]">Pipeline configuration and API keys.</p>
      </div>
      <div className="flex flex-col gap-1">
        <div className="bg-[#151D2A] p-6 flex items-center justify-between">
          <div><span className="text-sm font-medium">API Endpoint</span><span className="block text-xs font-mono text-[var(--color-text-secondary)] mt-1">http://127.0.0.1:8000</span></div>
          <span className="text-xs font-mono text-[var(--color-success)] bg-[var(--color-success)]/10 px-2 py-1">CONNECTED</span>
        </div>
        <div className="bg-[#151D2A] p-6 flex items-center justify-between">
          <div><span className="text-sm font-medium">LLM Provider</span><span className="block text-xs font-mono text-[var(--color-text-secondary)] mt-1">Groq (llama-3.3-70b-versatile)</span></div>
          <span className="text-xs font-mono text-[var(--color-warning)] bg-[var(--color-warning)]/10 px-2 py-1">FREE TIER</span>
        </div>
        <div className="bg-[#151D2A] p-6 flex items-center justify-between">
          <div><span className="text-sm font-medium">Search Provider</span><span className="block text-xs font-mono text-[var(--color-text-secondary)] mt-1">DuckDuckGo (Public API)</span></div>
          <span className="text-xs font-mono text-[var(--color-text-secondary)] bg-white/5 px-2 py-1">RATE LIMITED</span>
        </div>
        <div className="bg-[#151D2A] p-6 flex items-center justify-between">
          <div><span className="text-sm font-medium">Lead State Database</span><span className="block text-xs font-mono text-[var(--color-text-secondary)] mt-1">outputs/seen_leads.json (Local JSON)</span></div>
          <span className="text-xs font-mono text-[var(--color-success)] bg-[var(--color-success)]/10 px-2 py-1">ACTIVE</span>
        </div>
      </div>
    </div>
  );
}
