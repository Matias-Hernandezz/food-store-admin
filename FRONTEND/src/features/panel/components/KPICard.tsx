interface KPICardProps {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  accentColor?: string;
  accentBg?: string;
}

export function KPICard({ label, value, icon, accentColor = "#059669", accentBg = "#ecfdf5" }: KPICardProps) {
  return (
    <div
      className="rounded-2xl p-5 flex items-center gap-4 transition-all duration-300 hover:-translate-y-1 cursor-default"
      style={{
        backgroundColor: "#fff",
        border: "1px solid #e2e8f0",
        boxShadow: "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02)",
      }}
    >
      <div
        className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
        style={{ backgroundColor: accentBg, color: accentColor }}
      >
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-semibold uppercase tracking-wider truncate" style={{ color: "#64748b" }}>{label}</p>
        <p className="text-xl font-bold mt-0.5" style={{ color: "#0f172a" }}>{value}</p>
      </div>
    </div>
  );
}
