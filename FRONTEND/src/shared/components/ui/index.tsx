import { type ReactNode, type ButtonHTMLAttributes, type InputHTMLAttributes } from "react";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  loading?: boolean;
  children: ReactNode;
}

const variantStyles: Record<ButtonVariant, React.CSSProperties> = {
  primary: { backgroundColor: "#f97316", color: "#fff" },
  secondary: { backgroundColor: "#e8ddd5", color: "#2d1e0f" },
  danger: { backgroundColor: "#dc2626", color: "#fff" },
  ghost: { backgroundColor: "transparent", color: "#6b5a4e", border: "1px solid #d6c9be" },
};

export function Button({ variant = "primary", loading = false, children, className = "", disabled, style, ...props }: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed ${className}`}
      style={{ ...variantStyles[variant], ...style }}
      {...props}
    >
      {loading && <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />}
      {children}
    </button>
  );
}

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, className = "", ...props }: InputProps) {
  return (
    <div className="flex flex-col gap-1">
      {label && <label className="text-xs font-semibold uppercase tracking-wider" style={{ color: "#9a8070" }}>{label}</label>}
      <input
        className={`w-full rounded-lg px-3 py-2 text-sm outline-none transition-all ${className}`}
        style={{
          backgroundColor: "#fff",
          border: error ? "1px solid #dc2626" : "1px solid #d6c9be",
          color: "#2d1e0f",
        }}
        {...props}
      />
      {error && <span className="text-xs" style={{ color: "#dc2626" }}>{error}</span>}
    </div>
  );
}

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export function Textarea({ label, error, className = "", ...props }: TextareaProps) {
  return (
    <div className="flex flex-col gap-1">
      {label && <label className="text-xs font-semibold uppercase tracking-wider" style={{ color: "#9a8070" }}>{label}</label>}
      <textarea
        rows={3}
        className={`w-full rounded-lg px-3 py-2 text-sm outline-none transition-all resize-none ${className}`}
        style={{
          backgroundColor: "#fff",
          border: error ? "1px solid #dc2626" : "1px solid #d6c9be",
          color: "#2d1e0f",
        }}
        {...props}
      />
      {error && <span className="text-xs" style={{ color: "#dc2626" }}>{error}</span>}
    </div>
  );
}

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}

export function Modal({ open, onClose, title, children }: ModalProps) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ backgroundColor: "rgba(0,0,0,0.5)", backdropFilter: "blur(4px)" }} onClick={onClose}>
      <div className="w-full max-w-lg rounded-2xl shadow-2xl" style={{ backgroundColor: "#fff", border: "1px solid #e8ddd5" }} onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-6 py-4" style={{ borderBottom: "1px solid #f0e8e0" }}>
          <h2 className="text-base font-semibold" style={{ color: "#2d1e0f" }}>{title}</h2>
          <button onClick={onClose} className="text-xl leading-none transition-colors cursor-pointer" style={{ color: "#9a8070" }}>✕</button>
        </div>
        <div className="px-6 py-4">{children}</div>
      </div>
    </div>
  );
}

interface BadgeProps {
  children: ReactNode;
  variant?: "default" | "success" | "warning" | "danger";
}

const badgeStyles: Record<string, React.CSSProperties> = {
  default: { backgroundColor: "#e8ddd5", color: "#6b5a4e" },
  success: { backgroundColor: "#dcfce7", color: "#166534" },
  warning: { backgroundColor: "#fef3c7", color: "#92400e" },
  danger: { backgroundColor: "#fee2e2", color: "#991b1b" },
};

export function Badge({ children, variant = "default" }: BadgeProps) {
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium" style={badgeStyles[variant]}>
      {children}
    </span>
  );
}

interface SearchInputProps {
  value: string;
  onChange: (v: string) => void;
  placeholder?: string;
}

export function SearchInput({ value, onChange, placeholder = "Buscar..." }: SearchInputProps) {
  return (
    <div className="relative">
      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm" style={{ color: "#9a8070" }}>🔍</span>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-lg pl-9 pr-3 py-2 text-sm outline-none transition-all"
        style={{ backgroundColor: "#fff", border: "1px solid #d6c9be", color: "#2d1e0f" }}
      />
    </div>
  );
}

interface EmptyStateProps {
  message?: string;
  action?: ReactNode;
}

export function EmptyState({ message = "No hay datos disponibles", action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3" style={{ color: "#9a8070" }}>
      <span className="text-4xl">📭</span>
      <p className="text-sm">{message}</p>
      {action}
    </div>
  );
}

export function ErrorState({ message = "Ocurrió un error al cargar los datos" }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3" style={{ color: "#dc2626" }}>
      <span className="text-4xl">⚠️</span>
      <p className="text-sm">{message}</p>
    </div>
  );
}

export function SkeletonRow() {
  return (
    <div className="flex gap-4 px-4 py-3 animate-pulse">
      <div className="h-4 rounded w-1/4" style={{ backgroundColor: "#e8ddd5" }} />
      <div className="h-4 rounded w-1/3" style={{ backgroundColor: "#e8ddd5" }} />
      <div className="h-4 rounded w-1/5" style={{ backgroundColor: "#e8ddd5" }} />
    </div>
  );
}

interface ConfirmDialogProps {
  open: boolean;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
}

export function ConfirmDialog({ open, message, onConfirm, onCancel, loading }: ConfirmDialogProps) {
  return (
    <Modal open={open} onClose={onCancel} title="Confirmar acción">
      <p className="text-sm mb-6" style={{ color: "#6b5a4e" }}>{message}</p>
      <div className="flex gap-3 justify-end">
        <Button variant="ghost" onClick={onCancel}>Cancelar</Button>
        <Button variant="danger" onClick={onConfirm} loading={loading}>Eliminar</Button>
      </div>
    </Modal>
  );
}