// hooks/useRole.ts
import { useAuthStore } from "../../../store/authStore";

export const useRole = () => {
    const user = useAuthStore((s) => s.user);

    const hasRole = (...roles: string[]) =>
        roles.some((r) => user?.roles.includes(r)) ?? false;

    const isAdmin = user?.roles.includes("ADMIN") ?? false;

    return { hasRole, isAdmin };
};