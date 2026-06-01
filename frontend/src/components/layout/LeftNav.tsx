"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Target, 
  Telescope, 
  Microscope, 
  CheckCircle2, 
  Lightbulb, 
  Users, 
  Mail, 
  BarChart3, 
  Settings 
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "ICP Builder", href: "/icp", icon: Target },
  { name: "Prospect Discovery", href: "/prospects", icon: Telescope },
  { name: "Research", href: "/research", icon: Microscope },
  { name: "Qualification", href: "/qualification", icon: CheckCircle2 },
  { name: "Opportunities", href: "/opportunities", icon: Lightbulb },
  { name: "Contacts", href: "/contacts", icon: Users },
  { name: "Outreach", href: "/outreach", icon: Mail },
  { name: "Reports", href: "/reports", icon: BarChart3 },
  { name: "Settings", href: "/settings", icon: Settings },
];

export function LeftNav() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex w-60 flex-col bg-[#1c1b1b] h-[calc(100vh-3.5rem)] sticky top-14">
      <div className="flex flex-col gap-1 p-3">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-none px-3 py-2 text-sm font-mono tracking-wide transition-colors",
                isActive 
                  ? "bg-[#2a2a2a] text-[var(--color-accent)] border-l-2 border-[var(--color-accent)]" 
                  : "text-[var(--color-text-secondary)] hover:bg-[#2a2a2a]/50 hover:text-[var(--color-text-primary)] border-l-2 border-transparent"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.name}
            </Link>
          );
        })}
      </div>
    </aside>
  );
}
