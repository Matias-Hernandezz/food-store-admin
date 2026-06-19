import { useState } from "react";

interface Props {
  open: boolean;
  onClose: () => void;
}

const ASUNTOS = [
  "Error al iniciar sesión",
  "Problema con permisos",
  "Error en pedidos",
  "Error en productos",
  "Problema con pagos",
  "Otro",
];

export function HelpModal({ open, onClose }: Props) {
  const [nombre, setNombre] = useState("");
  const [email, setEmail] = useState("");
  const [asunto, setAsunto] = useState(ASUNTOS[0]);
  const [problema, setProblema] = useState("");

  if (!open) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const body = `Nombre: ${nombre}%0D%0AEmail: ${email}%0D%0A%0D%0A${problema}`;
    window.location.href = `mailto:help@foodstore-systems.com?subject=${encodeURIComponent(asunto)}&body=${body}`;
  };

  const inputStyle: React.CSSProperties = {
    width: "100%",
    padding: "10px 12px",
    borderRadius: 8,
    border: "1px solid #d6c9be",
    fontSize: 13,
    color: "#2d1e0f",
    backgroundColor: "#fdf9f6",
    outline: "none",
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center px-4"
      style={{ backgroundColor: "rgba(0,0,0,0.3)" }}
      onClick={onClose}
    >
      <div
        className="w-full max-w-md bg-white rounded-2xl shadow-2xl p-6 max-h-[90vh] overflow-y-auto"
        style={{ boxShadow: "0 20px 60px rgba(0,0,0,0.15)" }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-lg font-bold" style={{ color: "#2d1e0f" }}>
            Reportar un Problema
          </h3>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-[#f5ede6] transition-colors text-lg font-light"
            style={{ color: "#9a8070" }}
          >
            ×
          </button>
        </div>

        {/* Formulario de contacto */}
        <form onSubmit={handleSubmit} className="space-y-4 mb-6">
          <div>
            <label className="text-[10px] font-bold uppercase tracking-wider mb-1 block" style={{ color: "#9a8070" }}>
              Nombre
            </label>
            <input
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              placeholder="Tu nombre completo"
              required
              style={inputStyle}
            />
          </div>

          <div>
            <label className="text-[10px] font-bold uppercase tracking-wider mb-1 block" style={{ color: "#9a8070" }}>
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu@correo.com"
              required
              style={inputStyle}
            />
          </div>

          <div>
            <label className="text-[10px] font-bold uppercase tracking-wider mb-1 block" style={{ color: "#9a8070" }}>
              Asunto
            </label>
            <select
              value={asunto}
              onChange={(e) => setAsunto(e.target.value)}
              required
              style={{ ...inputStyle, cursor: "pointer" }}
            >
              {ASUNTOS.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-[10px] font-bold uppercase tracking-wider mb-1 block" style={{ color: "#9a8070" }}>
              Describí el problema
            </label>
            <textarea
              value={problema}
              onChange={(e) => setProblema(e.target.value)}
              placeholder="Contanos qué pasó, qué esperabas que pase, y cómo podemos reproducirlo..."
              required
              rows={4}
              style={{ ...inputStyle, resize: "vertical", minHeight: 80 }}
            />
          </div>

          <button
            type="submit"
            className="w-full py-2.5 rounded-xl text-sm font-bold transition-colors"
            style={{ backgroundColor: "#c8722a", color: "#fff" }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#a85e1f")}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#c8722a")}
          >
            Enviar Reporte
          </button>

          <p className="text-[10px] text-center" style={{ color: "#b09080" }}>
            Se abrirá tu cliente de correo con el reporte listo para enviar.
          </p>
        </form>

        {/* Footer */}
        <div className="flex items-center justify-between pt-3" style={{ borderTop: "1px solid #f0e8e0" }}>
          <span className="text-[10px]" style={{ color: "#9a8070" }}>
            help@foodstore-systems.com
          </span>
          <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: "#b09080" }}>
            v6.0
          </span>
        </div>
      </div>
    </div>
  );
}
