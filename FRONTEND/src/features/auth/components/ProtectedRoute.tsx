

import { Navigate } from "react-router-dom";
import { useAuthStore } from "../../../store/authStore";
import type { ReactNode } from "react";

interface Props {
    children: ReactNode;
    roles?: string[];
}

export function ProtectedRoute({ children, roles }: Props) {
    const user = useAuthStore((s) => s.user);
    const isLoading = useAuthStore((s) => s.isLoading);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: "#f5ede6" }}>
                <div className="w-8 h-8 border-2 border-[#c8722a] border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    if (!user) return <Navigate to="/login" replace />;

    if (roles && !roles.some((r) => user.roles.includes(r))) {
        return <Navigate to="/unauthorized" replace />;
    }

    return <>{children}</>;
}