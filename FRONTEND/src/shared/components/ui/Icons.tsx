import { type SVGProps } from "react";

interface IconProps extends SVGProps<SVGSVGElement> {
  size?: number;
}

export const Icons = {
  // Ahora todos usan IconProps y la desestructuración de size
  Categoria: ({ size = 24, ...props }: IconProps) => (
    <svg
      {...props}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M11 13H7" />
      <path d="M19 9h-4" />
      <path d="M3 3v16a2 2 0 0 0 2 2h16" />
      <rect x="15" y="5" width="4" height="12" rx="1" />
      <rect x="7" y="8" width="4" height="9" rx="1" />
    </svg>
  ),

  Producto: ({ size = 24, ...props }: IconProps) => (
    <svg
      {...props}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="8" cy="21" r="1" />
      <circle cx="19" cy="21" r="1" />
      <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12" />
    </svg>
  ),

  Ingrediente: ({ size = 24, ...props }: IconProps) => (
    <svg
      {...props}
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 6.528V3a1 1 0 0 1 1-1h0" />
      <path d="M18.237 21A15 15 0 0 0 22 11a6 6 0 0 0-10-4.472A6 6 0 0 0 2 11a15.1 15.1 0 0 0 3.763 10 3 3 0 0 0 3.648.648 5.5 5.5 0 0 1 5.178 0A3 3 0 0 0 18.237 21" />
    </svg>
  ),
};