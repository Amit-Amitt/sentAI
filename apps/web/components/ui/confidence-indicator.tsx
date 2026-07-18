"use client";

import { motion } from "framer-motion";

interface ConfidenceIndicatorProps {
  confidence: number; // 0.0 to 1.0
  size?: number;
  strokeWidth?: number;
}

export function ConfidenceIndicator({
  confidence,
  size = 64,
  strokeWidth = 6,
}: ConfidenceIndicatorProps) {
  const percentage = Math.min(Math.max(confidence * 100, 0), 100);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  // Determine color matching confidence level
  const getColor = (val: number) => {
    if (val >= 0.85) return "stroke-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.2)]";
    if (val >= 0.70) return "stroke-amber-500";
    return "stroke-rose-500";
  };

  const getTextColor = (val: number) => {
    if (val >= 0.85) return "text-emerald-400";
    if (val >= 0.70) return "text-amber-400";
    return "text-rose-400";
  };

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg className="transform -rotate-90" width={size} height={size}>
        {/* Track circle */}
        <circle
          className="stroke-muted/30"
          fill="transparent"
          strokeWidth={strokeWidth}
          r={radius}
          cx={size / 2}
          cy={size / 2}
        />
        {/* Progress circle */}
        <motion.circle
          className={getColor(confidence)}
          fill="transparent"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset }}
          transition={{ duration: 1, ease: "easeOut" }}
          r={radius}
          cx={size / 2}
          cy={size / 2}
          strokeLinecap="round"
        />
      </svg>
      {/* Inner Label */}
      <div className="absolute flex flex-col items-center justify-center text-center">
        <span className={`text-sm font-bold tracking-tight ${getTextColor(confidence)}`}>
          {Math.round(percentage)}%
        </span>
      </div>
    </div>
  );
}
export default ConfidenceIndicator;
