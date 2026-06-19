// features/auth/pages/UnauthorizedPage.tsx
import { useNavigate } from "react-router-dom";

export function UnauthorizedPage() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: "#f5ede6" }}>
            <div className="text-center">
                <div className="mb-6 flex justify-center">
                    <svg width="200" height="200" viewBox="0 0 24 24" fill="#c8722a" style={{ opacity: 0.85 }}>
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM4 12c0-4.42 3.58-8 8-8 1.85 0 3.55.63 4.9 1.69L5.69 16.9C4.63 15.55 4 13.85 4 12zm8 8c-1.85 0-3.55-.63-4.9-1.69L18.31 7.1C19.37 8.45 20 10.15 20 12c0 4.42-3.58 8-8 8z" />
                    </svg>
                </div>
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
