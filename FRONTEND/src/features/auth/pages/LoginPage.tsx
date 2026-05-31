// features/auth/pages/LoginPage.tsx
//
// Orquesta: usa useLogin (lógica) + LoginForm (UI).
// La page no tiene lógica propia, solo conecta.

import { LoginForm } from "../components/LoginForm";
import { useLogin } from "../hooks/useLogin";

export function LoginPage() {
    const { submit, loading, error } = useLogin();

    return (
        <div
            className="min-h-screen flex flex-col items-center justify-center px-4 py-12"
            style={{ backgroundColor: "#f5ede6" }}
        >
            {/* Card principal */}
            <div className="w-full max-w-sm bg-white rounded-3xl shadow-xl shadow-[#c8722a]/10 p-8">

                {/* Logo */}
                <div className="flex flex-col items-center mb-8">
                    <div className="w-16 h-16 rounded-full bg-[#f5ede6] flex items-center justify-center mb-5">
                        {/* Ícono tenedor y cuchillo */}
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
                            <path d="M3 2v7c0 1.1.9 2 2 2h.5V22h2V11H8c1.1 0 2-.9 2-2V2H8v5H6V2H4v5H3V2H3z"
                                fill="#c8722a" />
                            <path d="M15 2c-1.9 0-3.5 1.6-3.5 3.5v7c0 1.4.9 2.5 2 2.8V22h2V15.3c1.1-.3 2-1.4 2-2.8v-7C17.5 3.6 16.9 2 15 2z"
                                fill="#c8722a" />
                        </svg>
                    </div>

                    <h1
                        className="text-3xl font-black text-[#2d1e0f] tracking-tight leading-none"
                        style={{ fontFamily: "'Georgia', serif" }}
                    >
                        Food Store Admin
                    </h1>
                    <p className="text-sm text-[#9a8070] mt-2 tracking-wide">
                        Gestión de Comidas&nbsp;•&nbsp;Acceso Restringido
                    </p>
                </div>

                {/* Formulario */}
                <LoginForm onSubmit={submit} loading={loading} error={error} />

                {/* Divisor */}
                <div className="border-t border-[#f0e8e0] my-6" />

                {/* Footer de soporte */}
                <div className="text-center space-y-3">
                    <p className="text-xs text-[#9a8070]">
                        Soporte Técnico&nbsp;•&nbsp;
                        <a
                            href="mailto:help@FoodStoresystems.com"
                            className="font-semibold text-[#5a4a3a] hover:text-[#c8722a] transition-colors"
                        >
                            help@FoodStoreystems.com
                        </a>
                    </p>

                    <div className="flex justify-center gap-2">
                        {/* Web icon */}
                        <div className="w-8 h-8 rounded-full bg-[#f5ede6] flex items-center justify-center">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9a8070" strokeWidth="2">
                                <circle cx="12" cy="12" r="10" />
                                <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
                            </svg>
                        </div>
                        {/* Shield icon */}
                        <div className="w-8 h-8 rounded-full bg-[#f5ede6] flex items-center justify-center">
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9a8070" strokeWidth="2">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                            </svg>
                        </div>
                    </div>
                </div>
            </div>

            {/* Quote debajo */}
            <p
                className="mt-8 text-sm text-[#b09080] text-center italic max-w-xs leading-relaxed"
                style={{ fontFamily: "'Georgia', serif" }}
            >
                "Donde la tradición se encuentra con un simple click."
            </p>
        </div>
    );
}
