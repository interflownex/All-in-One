import type { CSSProperties, ImgHTMLAttributes } from "react";

const OFFICIAL_LOGO_SRC = "/assets/brand/all-in-one-logo-transparent.svg" as const;

type BrandLogoProps = Omit<
  ImgHTMLAttributes<HTMLImageElement>,
  "src" | "srcSet" | "style" | "width" | "height"
> & {
  /** Tamanho visual autorizado. A proporção original sempre é preservada. */
  maxWidth?: number | string;
  style?: Pick<CSSProperties, "display" | "margin" | "maxWidth" | "width">;
};

/**
 * Renderiza a logomarca oficial do All-in-One sem permitir substituição,
 * filtros, recortes, distorções, rotações, mudanças de cor ou composição.
 *
 * A única customização visual aceita é o redimensionamento proporcional.
 */
export function BrandLogo({
  maxWidth = 120,
  alt = "All-in-One",
  className,
  loading = "eager",
  decoding = "async",
  style,
  ...accessibilityProps
}: BrandLogoProps) {
  const safeStyle: CSSProperties = {
    display: style?.display ?? "block",
    width: style?.width ?? "100%",
    maxWidth: style?.maxWidth ?? maxWidth,
    height: "auto",
    margin: style?.margin,
    objectFit: "contain",
    objectPosition: "center",
  };

  return (
    <img
      {...accessibilityProps}
      alt={alt}
      className={className}
      decoding={decoding}
      draggable={false}
      loading={loading}
      src={OFFICIAL_LOGO_SRC}
      style={safeStyle}
    />
  );
}

export { OFFICIAL_LOGO_SRC };
