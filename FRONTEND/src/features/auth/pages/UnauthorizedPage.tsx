// features/auth/pages/UnauthorizedPage.tsx
import { useNavigate } from "react-router-dom";

export function UnauthorizedPage() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: "#f5ede6" }}>
            <div className="text-center">
                <p className="text-6xl mb-4">🚫</p>
                <h1 className="text-2xl font-bold text-[#2d1e0f] mb-2">Sin permisos</h1>
                <p className="text-[#9a8070] mb-6">Tu rol no tiene acceso a esta sección.</p>
                <button
                    onClick={() => navigate("/login")}
                    className="bg-[#c8722a] hover:bg-[#a85e1f] text-white font-bold px-6 py-3 rounded-xl transition-colors"
                >
                    Volver al login
                </button>
            </div>
        </div>
    );
}