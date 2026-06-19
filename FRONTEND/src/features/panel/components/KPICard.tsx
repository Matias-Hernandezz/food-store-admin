import type { ReactNode } from "react";

interface KPICardProps {
  label: string;
  value: string;
  icon: ReactNode;
  accentColor: string;
  accentBg: string;
}

export function KPICard({ label, value, icon, accentColor, accentBg }: KPICardProps) {
  return (
    <div
      className="p-6 rounded-xl border transition-all duration-300 hover:-translate-y-1"
      style={{
        backgroundColor: "#fff",
        borderColor: "rgba(214, 201, 190, 0.2)",
        boxShadow: "0 2px 16px rgba(58, 48, 42, 0.04)",
      }}
    >
      <div className="flex justify-between items-start mb-4">
        <div
          className="p-3 rounded-lg"
          style={{ backgroundColor: accentBg, color: accentColor }}
        >
          {icon}
        </div>
      </div>
      <p className="text-sm font-medium" style={{ color: "#9a8070" }}>
        {label}
      </p>
      <p className="text-3xl font-bold mt-1" style={{ color: "#2d1e0f" }}>
        {value}
      </p>
    </div>
  );
}
