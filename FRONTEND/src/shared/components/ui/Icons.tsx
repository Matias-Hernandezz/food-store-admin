import { type SVGProps } from "react";

interface IconProps extends SVGProps<SVGSVGElement> {
  size?: number;
}

export const Icons = {
  // ── Navegación ──────────────────────────────────────────────────────────

  Dashboard: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z" />
    </svg>
  ),

  Usuarios: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5s-3 1.34-3 3 1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z" />
    </svg>
  ),

  Pedidos: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M18 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 18H6V4h2v5l2.5-1.5L13 9V4h5v16z" />
    </svg>
  ),

  Cocina: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M16.5 2.83c-1.09 1.09-1.67 2.5-1.67 4.08 0 1.19.36 2.36 1.03 3.33.14.2.27.4.42.58L18 12.5l1.72-1.68c.15-.18.28-.38.42-.58.67-.97 1.03-2.14 1.03-3.33 0-1.58-.58-2.99-1.67-4.08C18.42 1.74 17.08 1.74 16.5 2.83zm.5 3.67c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zM6 22h12c1.1 0 2-.9 2-2V10.97c-.51.35-1.09.58-1.72.68V20H5.72C5.28 20 5 19.72 5 19.28V4.72C5 4.28 5.28 4 5.72 4h7.06c-.15.5-.24 1.02-.26 1.56-.02.48.02.95.1 1.41-.04.01-.08.03-.12.03H7v2h3.68c.31.53.68 1.02 1.1 1.47L13 11.68V14h2v-1.32c.32-.28.67-.55 1.04-.78.18-.12.37-.23.57-.33.13-.07.26-.13.39-.18V14h2v-.9c.35-.06.68-.17 1-.33V20c0 1.1-.9 2-2 2H6zM7 16h6v2H7v-2z" />
    </svg>
  ),

  // ── Catálogo ────────────────────────────────────────────────────────────

  Categoria: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2l-5.5 9h11L12 2zm0 3.84L13.93 9h-3.87L12 5.84zM17.5 13c-2.49 0-4.5 2.01-4.5 4.5s2.01 4.5 4.5 4.5 4.5-2.01 4.5-4.5-2.01-4.5-4.5-4.5zm0 7c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5zM3 21.5h8v-8H3v8zm2-6h4v4H5v-4z" />
    </svg>
  ),

  Producto: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M21.41 11.58l-9-9A1.99 1.99 0 0011 2H3c-1.1 0-2 .9-2 2v8c0 .55.22 1.05.59 1.41l9 9c.78.78 2.04.78 2.82 0l7.59-7.59c.78-.78.78-2.04 0-2.82zM6.5 8C5.67 8 5 7.33 5 6.5S5.67 5 6.5 5 8 5.67 8 6.5 7.33 8 6.5 8z" />
    </svg>
  ),

  Ingrediente: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M2 21h20v-2H2v2zm6-9h8v-2H8v2zm0 4h8v-2H8v2zm-4-8h16V6H4v2z" />
    </svg>
  ),

  // ── KPIs del Dashboard ──────────────────────────────────────────────────

  TrendingUp: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="m16 6 2.29 2.29-4.88 4.88-4-4L2 16.59 3.41 18l6-6 4 4 6.3-6.29L22 12V6h-6z" />
    </svg>
  ),

  ShoppingBag: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M18 6h-2c0-2.21-1.79-4-4-4S8 3.79 8 6H6c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-6-2c1.1 0 2 .9 2 2h-4c0-1.1.9-2 2-2zm6 16H6V8h2v2c0 .55.45 1 1 1s1-.45 1-1V8h4v2c0 .55.45 1 1 1s1-.45 1-1V8h2v12z" />
    </svg>
  ),

  RestaurantMenu: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="m8.1 13.34 2.83-2.83L3.91 3.5a4.008 4.008 0 0 0 0 5.66l4.19 4.18zm6.78-1.81c1.53.71 3.68.21 5.27-1.38 1.91-1.91 2.28-4.65.81-6.12-1.46-1.46-4.2-1.1-6.12.81-1.59 1.59-2.09 3.74-1.38 5.27L3.7 19.87l1.41 1.41L12 14.41l6.88 6.88 1.41-1.41L13.41 13l1.47-1.47z" />
    </svg>
  ),

  Payments: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M19 14V6c0-1.1-.9-2-2-2H3c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zm-2 0H3V6h14v8zm-7-7c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3zm13 0v11c0 1.1-.9 2-2 2H4v-2h17V7h2z" />
    </svg>
  ),

  // ── UI ──────────────────────────────────────────────────────────────────

  ExpandLess: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="m12 8-6 6 1.41 1.41L12 10.83l4.59 4.58L18 14l-6-6z" />
    </svg>
  ),

  Logout: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="m17 8-1.41 1.41L17.17 11H9v2h8.17l-1.58 1.58L17 16l4-4-4-4zM5 5h7V3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h7v-2H5V5z" />
    </svg>
  ),

  Block: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM4 12c0-4.42 3.58-8 8-8 1.85 0 3.55.63 4.9 1.69L5.69 16.9C4.63 15.55 4 13.85 4 12zm8 8c-1.85 0-3.55-.63-4.9-1.69L18.31 7.1C19.37 8.45 20 10.15 20 12c0 4.42-3.58 8-8 8z" />
    </svg>
  ),

  Search: ({ size = 24, ...props }: IconProps) => (
    <svg {...props} width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M15.5 14h-.79l-.28-.27A6.471 6.471 0 0016 9.5 6.5 6.5 0 109.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z" />
    </svg>
  ),
};
