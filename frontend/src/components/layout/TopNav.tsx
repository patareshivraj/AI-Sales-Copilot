import Link from "next/link";
import { Search, Bell, Menu } from "lucide-react";

export function TopNav() {
  return (
    <header className="sticky top-0 z-40 flex h-14 w-full items-center justify-between bg-[#131313] px-4">
      <div className="flex items-center gap-4">
        <button className="md:hidden text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">
          <Menu className="h-5 w-5" />
        </button>
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-[var(--color-accent)] text-white font-bold text-sm">
            AI
          </div>
          <span className="font-semibold text-sm tracking-tight text-[var(--color-text-primary)] hidden md:block">
            Lead Intelligence
          </span>
        </Link>
      </div>

      <div className="flex flex-1 items-center justify-center px-6 md:px-12 max-w-2xl hidden md:flex">
        <div className="relative w-full">
          <Search className="absolute left-2.5 top-2 h-4 w-4 text-[var(--color-text-secondary)]" />
          <input
            type="search"
            placeholder="Search telemetry, active pipelines, or raw data..."
            className="w-full rounded-none bg-[#1c1b1b] pl-9 pr-4 py-1.5 text-sm font-mono text-[var(--color-text-primary)] placeholder-[var(--color-text-secondary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-accent)] transition-all"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors relative">
          <Bell className="h-5 w-5" />
          <span className="absolute -top-1 -right-1 flex h-3 w-3 items-center justify-center rounded-full bg-[var(--color-accent)] text-[8px] font-medium text-white">
            3
          </span>
        </button>
        <div className="h-8 w-8 bg-[#1c1b1b] flex items-center justify-center text-xs font-mono font-bold text-[var(--color-accent)]">
          _SYS
        </div>
      </div>
    </header>
  );
}
