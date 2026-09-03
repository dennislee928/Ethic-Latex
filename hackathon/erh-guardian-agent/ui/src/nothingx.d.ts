// Type shim for @dennislee928/nothingx-react-components.
// The package ships raw .tsx sources that don't pass this project's strict tsc;
// tsconfig `paths` points type resolution here while Vite bundles the real code.
declare module "@dennislee928/nothingx-react-components" {
  import type { CSSProperties, ReactNode } from "react";

  export const nothing: {
    colors: {
      bg: string;
      surface: string;
      surfaceLight: string;
      red: string;
      text: string;
      textDark: string;
      muted: string;
      circleBg: string;
    };
    radius: { card: number; circle: number };
    scale: number;
  };

  export function DotMatrixText(props: {
    children: string;
    color?: string;
    dotSize?: number;
    gap?: number;
  }): JSX.Element;

  export function DottedDivider(props: {
    length?: number;
    color?: string;
    vertical?: boolean;
  }): JSX.Element;

  export function GlitchText(props: {
    children: ReactNode;
    active?: boolean;
  }): JSX.Element;

  export function PillBadge(props: {
    children: ReactNode;
    variant?: "live" | "off" | "neutral";
  }): JSX.Element;

  export function ProgressDots(props: {
    value?: number;
    max?: number;
    count?: number;
    color?: string;
  }): JSX.Element;

  export function TerminalBlink(props?: { children?: ReactNode }): JSX.Element;

  export function NothingCard(props: {
    children: ReactNode;
    dark?: boolean;
    style?: CSSProperties;
  }): JSX.Element;
}
