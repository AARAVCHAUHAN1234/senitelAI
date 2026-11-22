import React from "react";

export type SeverityType = "Critical" | "High" | "Medium" | "Low" | "Informational";
export type StatusType = "Verified" | "Detected" | "Predicted" | "Fixed" | "False_Positive" | "Under verification" | string;

interface BadgeProps {
  label: string;
  variant?: "severity" | "status" | "classification" | "method";
  size?: "sm" | "md";
}

export const Badge: React.FC<BadgeProps> = ({ label, variant = "status", size = "sm" }) => {
  const norm = label.toLowerCase();

  let colorClasses = "bg-slate-800 text-slate-300 border-slate-700";

  if (variant === "severity") {
    if (norm === "critical") colorClasses = "bg-rose-950/70 text-rose-300 border-rose-800/80";
    else if (norm === "high") colorClasses = "bg-orange-950/70 text-orange-300 border-orange-800/80";
    else if (norm === "medium") colorClasses = "bg-amber-950/70 text-amber-300 border-amber-800/80";
    else if (norm === "low") colorClasses = "bg-emerald-950/70 text-emerald-300 border-emerald-800/80";
    else if (norm === "informational") colorClasses = "bg-slate-800 text-slate-400 border-slate-700";
  } else if (variant === "status") {
    if (norm === "verified") colorClasses = "bg-emerald-950/60 text-emerald-300 border-emerald-700/60";
    else if (norm === "detected") colorClasses = "bg-amber-950/60 text-amber-300 border-amber-700/60";
    else if (norm === "predicted") colorClasses = "bg-blue-950/60 text-blue-300 border-blue-700/60";
    else if (norm === "fixed") colorClasses = "bg-cyan-950/60 text-cyan-300 border-cyan-700/60";
  } else if (variant === "classification") {
    if (norm === "active") colorClasses = "bg-emerald-950/50 text-emerald-300 border-emerald-800/50";
    else if (norm === "zombie") colorClasses = "bg-amber-950/50 text-amber-300 border-amber-800/50";
    else if (norm === "shadow") colorClasses = "bg-rose-950/50 text-rose-300 border-rose-800/50";
    else if (norm === "new") colorClasses = "bg-cyan-950/50 text-cyan-300 border-cyan-800/50";
  } else if (variant === "method") {
    if (norm === "get") colorClasses = "bg-blue-950/50 text-blue-300 border-blue-800/60 font-mono";
    else if (norm === "post") colorClasses = "bg-emerald-950/50 text-emerald-300 border-emerald-800/60 font-mono";
    else if (norm === "put") colorClasses = "bg-amber-950/50 text-amber-300 border-amber-800/60 font-mono";
    else if (norm === "delete") colorClasses = "bg-rose-950/50 text-rose-300 border-rose-800/60 font-mono";
  }

  const sizeClasses = size === "sm" ? "text-xs px-2 py-0.5" : "text-sm px-2.5 py-1";

  return (
    <span className={`inline-flex items-center gap-1.5 font-medium rounded-md border ${sizeClasses} ${colorClasses}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
      {label}
    </span>
  );
};
