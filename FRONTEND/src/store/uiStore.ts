import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface Toast {
    id: string;
    type: "success" | "error" | "info";
    message: string;
}

interface UIState {
    sidebarOpen: boolean;
    toasts: Toast[];

    toggleSidebar: () => void;
    setSidebarOpen: (open: boolean) => void;
    addToast: (toast: Omit<Toast, "id">) => void;
    removeToast: (id: string) => void;
}

let toastId = 0;

export const useUIStore = create<UIState>()(
    persist(
        (set, get) => ({
            sidebarOpen: true,
            toasts: [],

            toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),

            setSidebarOpen: (open) => set({ sidebarOpen: open }),

            addToast: (toast) => {
                const id = `toast-${++toastId}-${Date.now()}`;
                set((s) => ({
                    toasts: [...s.toasts.slice(-4), { ...toast, id }], // max 5 toasts
                }));
                // Auto-remove after 4 seconds
                setTimeout(() => {
                    get().removeToast(id);
                }, 4000);
            },

            removeToast: (id) =>
                set((s) => ({
                    toasts: s.toasts.filter((t) => t.id !== id),
                })),
        }),
        {
            name: "FoodStore-admin-ui",
            partialize: (state) => ({ sidebarOpen: state.sidebarOpen }),
        }
    )
);
