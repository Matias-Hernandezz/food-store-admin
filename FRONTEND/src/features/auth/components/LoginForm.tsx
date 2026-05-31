// features/auth/components/LoginForm.tsx
//
// Formulario puro: recibe onSubmit, loading y error como props.
// No sabe nada de routing ni de contexto — solo renderiza.

import { useState, type FormEvent } from "react";

interface Props {
    onSubmit: (email: string, password: string) => void;
    loading: boolean;
    error: string | null;
}

export function LoginForm({ onSubmit, loading, error }: Props) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [remember, setRemember] = useState(false);
    const [showPass, setShowPass] = useState(false);

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        onSubmit(email, password);
    };

    return (
        <form onSubmit={handleSubmit} className="w-full space-y-5">

            {/* Email */}
            <div>
                <label className="block text-[10px] font-bold tracking-[0.15em] text-[#5a4a3a] uppercase mb-2">
                    Usuario
                </label>
                <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[#b08060]">
                        {/* Person icon */}
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="12" cy="8" r="4" /><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" />
                        </svg>
                    </span>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="admin@sahara.com"
                        required
                        className="w-full pl-11 pr-4 py-3.5 rounded-xl border border-[#e8ddd5]
                       bg-white text-[#3d2b1f] placeholder-[#c4b5a8] text-sm
                       focus:outline-none focus:border-[#c8722a] focus:ring-2 focus:ring-[#c8722a]/20
                       transition-all"
                    />
                </div>
            </div>

            {/* Password */}
            <div>
                <div className="flex justify-between items-center mb-2">
                    <label className="block text-[10px] font-bold tracking-[0.15em] text-[#5a4a3a] uppercase">
                        Contraseña
                    </label>
                    <button
                        type="button"
                        className="text-xs text-[#c8722a] hover:text-[#a85e1f] font-medium transition-colors"
                    >
                        ¿Olvidaste tu clave?
                    </button>
                </div>
                <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-[#b08060]">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <rect x="3" y="11" width="18" height="11" rx="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" />
                        </svg>
                    </span>
                    <input
                        type={showPass ? "text" : "password"}
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="••••••••••"
                        required
                        className="w-full pl-11 pr-11 py-3.5 rounded-xl border border-[#e8ddd5]
                       bg-white text-[#3d2b1f] placeholder-[#c4b5a8] text-sm
                       focus:outline-none focus:border-[#c8722a] focus:ring-2 focus:ring-[#c8722a]/20
                       transition-all"
                    />
                    <button
                        type="button"
                        onClick={() => setShowPass(!showPass)}
                        className="absolute right-4 top-1/2 -translate-y-1/2 text-[#b08060] hover:text-[#c8722a] transition-colors"
                    >
                        {showPass ? (
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
                                <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
                                <line x1="1" y1="1" x2="23" y2="23" />
                            </svg>
                        ) : (
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" />
                            </svg>
                        )}
                    </button>
                </div>
            </div>

            {/* Remember */}
            <label className="flex items-center gap-3 cursor-pointer select-none">
                <div
                    onClick={() => setRemember(!remember)}
                    className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all
            ${remember ? "bg-[#c8722a] border-[#c8722a]" : "border-[#c4b5a8] bg-white"}`}
                >
                    {remember && (
                        <svg width="10" height="10" viewBox="0 0 12 12" fill="none">
                            <path d="M2 6l3 3 5-5" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
                        </svg>
                    )}
                </div>
                <span className="text-sm text-[#7a6a5a]">Recordar este dispositivo</span>
            </label>

            {/* Error */}
            {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">
                    ⚠️ {error}
                </div>
            )}

            {/* Submit */}
            <button
                type="submit"
                disabled={loading}
                className="w-full bg-[#c8722a] hover:bg-[#a85e1f] active:bg-[#8f5019]
                   disabled:opacity-60 disabled:cursor-not-allowed
                   text-white font-bold text-xs tracking-[0.2em] uppercase
                   py-4 rounded-xl transition-all duration-200
                   flex items-center justify-center gap-3 shadow-lg shadow-[#c8722a]/30"
            >
                {loading ? (
                    <>
                        <div className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" />
                        Ingresando...
                    </>
                ) : (
                    <>
                        Entrar al Sistema
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                            <path d="M5 12h14M12 5l7 7-7 7" />
                        </svg>
                    </>
                )}
            </button>

        </form>
    );
}
