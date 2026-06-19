
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../../store/authStore";

export function useLogin() {
    const login = useAuthStore((s) => s.login);
    const navigate = useNavigate();

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const submit = async (email: string, password: string) => {
        setError(null);
        setLoading(true);
        try {
            await login(email, password);
            navigate("/admin/panel", { replace: true });
        } catch (err: unknown) {
            const detail = (err as { response?: { data?: { detail?: string } } })
                ?.response?.data?.detail;
            setError(detail ?? (err as Error).message ?? "Credenciales incorrectas");
        } finally {
            setLoading(false);
        }
    };

    return { submit, loading, error };
}