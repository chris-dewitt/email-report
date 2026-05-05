import type { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  label: string;
  value: string | number;
  icon: LucideIcon;
  color?: string;
  subtitle?: string;
}

export function StatCard({ label, value, icon: Icon, color = "text-fed-accent", subtitle }: Props) {
  return (
    <div className="rounded-lg border border-fed-border bg-fed-surface p-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-fed-muted uppercase tracking-wider">{label}</span>
        <Icon size={16} className={cn(color)} />
      </div>
      <p className={cn("mt-2 text-2xl font-bold", color)}>{value}</p>
      {subtitle && <p className="mt-1 text-xs text-fed-muted">{subtitle}</p>}
    </div>
  );
}
