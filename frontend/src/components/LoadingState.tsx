import React from "react";
import { Loader2 } from "lucide-react";

export const LoadingState: React.FC<{ message?: string }> = ({
  message = "Loading live security state..."
}) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-slate-400 space-y-3">
      <Loader2 className="w-6 h-6 animate-spin text-cyan-500" />
      <span className="text-xs uppercase tracking-wider">{message}</span>
    </div>
  );
};
