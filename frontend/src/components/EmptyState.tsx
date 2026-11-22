import React from "react";
import { ShieldAlert } from "lucide-react";

interface EmptyStateProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  action
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center rounded-xl border border-dashed border-slate-800 bg-slate-900/40">
      <div className="p-3 rounded-full bg-slate-800/80 text-slate-400 mb-3">
        <ShieldAlert className="w-6 h-6" />
      </div>
      <h4 className="text-sm font-medium text-slate-200">{title}</h4>
      {description && <p className="text-xs text-slate-400 mt-1 max-w-sm">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
};
