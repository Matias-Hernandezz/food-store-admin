// hooks/useRole.ts
import { useAuth } from "../../../features/auth/context/AuthContext";

export const useRole = () => {
    const { user, hasRole } = useAuth();

    // isAdmin lo derivamos de tu usuario
    const isAdmin = user?.roles.includes("ADMIN") ?? false;

    return { hasRole, isAdmin };
};