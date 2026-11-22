import React from "react";
import { ArrowUpRight } from "lucide-react";

interface MetricCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  icon: React.ReactNode;
  accentColor?: string;
  trend?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subtext,
  icon,
  accentColor = "text-cyan-400",
  trend
}) => {
  return (
    <div className="bg-slate-900/90 border border-slate-800/80 rounded-xl p-4 transition-all hover:border-slate-700">
      <div className="flex items-center justify-between text-slate-400 text-xs font-medium uppercase tracking-wider mb-2">
        <span>{label}</span>
        <div className={`p-1.5 rounded-lg bg-slate-800/80 ${accentColor}`}>
          {icon}
        </div>
      </div>
      <div className="text-2xl font-bold text-slate-100 tracking-tight">
        {value}
      </div>
      {(subtext || trend) && (
        <div className="flex items-center gap-1.5 mt-2 text-xs text-slate-400">
          {trend && (
            <span className="inline-flex items-center text-cyan-400 font-medium">
              <ArrowUpRight className="w-3.5 h-3.5" />
              {trend}
            </span>
          )}
          {subtext && <span>{subtext}</span>}
        </div>
      )}
    </div>
  );
};
