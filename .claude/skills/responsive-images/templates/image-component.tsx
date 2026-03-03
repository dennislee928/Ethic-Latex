/**
 * ResponsiveImage Component
 *
 * Production-ready responsive image component with:
 * - srcset and sizes for responsive sizing
 * - Modern formats (AVIF, WebP) with fallbacks
 * - Lazy loading by default
 * - Aspect ratio container option
 * - CLS prevention with explicit dimensions
 */

import { type ImgHTMLAttributes } from 'react';

interface ImageSource {
  /** Image URL or path */
  src: string;
  /** Width of this image variant (e.g., 400, 800, 1200) */
  width: number;
}

interface ResponsiveImageProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, 'src' | 'srcSet'> {
  /** Base image source (JPEG/PNG fallback) */
  src: string;
  /** Array of responsive image sources with widths */
  sources: ImageSource[];
  /** WebP versions of sources (optional but recommended) */
  webpSources?: ImageSource[];
  /** AVIF versions of sources (optional but recommended) */
  avifSources?: ImageSource[];
  /** Sizes attribute for responsive images */
  sizes: string;
  /** Alt text (required for accessibility) */
  alt: string;
  /** Image width (for aspect ratio calculation) */
  width: number;
  /** Image height (for aspect ratio calculation) */
  height: number;
  /** Enable lazy loading (default: true for non-LCP images) */
  lazy?: boolean;
  /** High priority for LCP images (default: false) */
  priority?: boolean;
  /** Wrap in aspect ratio container (default: false) */
  aspectRatioContainer?: boolean;
  /** Aspect ratio for container (e.g., "16/9", "4/3", "1/1") */
  aspectRatio?: string;
  /** object-fit value when using aspect ratio container */
  objectFit?: 'cover' | 'contain' | 'fill' | 'scale-down' | 'none';
  /** Additional CSS classes */
  className?: string;
}

/**
 * Build srcset string from ImageSource array
 */
function buildSrcSet(sources: ImageSource[]): string {
  return sources.map(({ src, width }) => `${src} ${width}w`).join(', ');
}

/**
 * ResponsiveImage component with modern formats and lazy loading
 */
export function ResponsiveImage({
  src,
  sources,
  webpSources,
  avifSources,
  sizes,
  alt,
  width,
  height,
  lazy = true,
  priority = false,
  aspectRatioContainer = false,
  aspectRatio,
  objectFit = 'cover',
  className = '',
  ...props
}: ResponsiveImageProps) {
  const loading = priority ? 'eager' : lazy ? 'lazy' : 'eager';
  const fetchPriority = priority ? 'high' : undefined;

  const srcSet = buildSrcSet(sources);
  const webpSrcSet = webpSources ? buildSrcSet(webpSources) : undefined;
  const avifSrcSet = avifSources ? buildSrcSet(avifSources) : undefined;

  const imgElement = (
    <img
      src={src}
      srcSet={srcSet}
      sizes={sizes}
      alt={alt}
      width={width}
      height={height}
      loading={loading}
      fetchpriority={fetchPriority}
      className={aspectRatioContainer ? `w-full h-full object-${objectFit} ${className}` : className}
      {...props}
    />
  );

  // If modern formats are provided, use picture element
  if (webpSrcSet || avifSrcSet) {
    const pictureContent = (
      <picture>
        {avifSrcSet && (
          <source srcSet={avifSrcSet} sizes={sizes} type="image/avif" />
        )}
        {webpSrcSet && (
          <source srcSet={webpSrcSet} sizes={sizes} type="image/webp" />
        )}
        {imgElement}
      </picture>
    );

    // Wrap in aspect ratio container if requested
    if (aspectRatioContainer) {
      const ratio = aspectRatio || `${width}/${height}`;
      return (
        <div className={`aspect-[${ratio}] overflow-hidden`}>
          {pictureContent}
        </div>
      );
    }

    return pictureContent;
  }

  // No modern formats - just img element
  if (aspectRatioContainer) {
    const ratio = aspectRatio || `${width}/${height}`;
    return (
      <div className={`aspect-[${ratio}] overflow-hidden`}>
        {imgElement}
      </div>
    );
  }

  return imgElement;
}

/**
 * Example Usage:
 *
 * // Basic responsive image
 * <ResponsiveImage
 *   src="/image-800.jpg"
 *   sources={[
 *     { src: '/image-400.jpg', width: 400 },
 *     { src: '/image-800.jpg', width: 800 },
 *     { src: '/image-1200.jpg', width: 1200 },
 *   ]}
 *   sizes="(max-width: 768px) 100vw, 800px"
 *   alt="Descriptive alt text"
 *   width={800}
 *   height={600}
 * />
 *
 * // With modern formats (WebP + AVIF)
 * <ResponsiveImage
 *   src="/image-800.jpg"
 *   sources={[
 *     { src: '/image-400.jpg', width: 400 },
 *     { src: '/image-800.jpg', width: 800 },
 *     { src: '/image-1200.jpg', width: 1200 },
 *   ]}
 *   webpSources={[
 *     { src: '/image-400.webp', width: 400 },
 *     { src: '/image-800.webp', width: 800 },
 *     { src: '/image-1200.webp', width: 1200 },
 *   ]}
 *   avifSources={[
 *     { src: '/image-400.avif', width: 400 },
 *     { src: '/image-800.avif', width: 800 },
 *     { src: '/image-1200.avif', width: 1200 },
 *   ]}
 *   sizes="(max-width: 768px) 100vw, 800px"
 *   alt="Modern format image"
 *   width={800}
 *   height={600}
 * />
 *
 * // Hero image (LCP, high priority)
 * <ResponsiveImage
 *   src="/hero-1200.jpg"
 *   sources={[
 *     { src: '/hero-800.jpg', width: 800 },
 *     { src: '/hero-1200.jpg', width: 1200 },
 *     { src: '/hero-1600.jpg', width: 1600 },
 *   ]}
 *   sizes="100vw"
 *   alt="Hero image"
 *   width={1600}
 *   height={900}
 *   priority={true}
 *   lazy={false}
 * />
 *
 * // Card image with aspect ratio container
 * <ResponsiveImage
 *   src="/card-800.jpg"
 *   sources={[
 *     { src: '/card-400.jpg', width: 400 },
 *     { src: '/card-800.jpg', width: 800 },
 *     { src: '/card-1200.jpg', width: 1200 },
 *   ]}
 *   sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
 *   alt="Card image"
 *   width={1200}
 *   height={675}
 *   aspectRatioContainer={true}
 *   aspectRatio="16/9"
 *   objectFit="cover"
 * />
 *
 * // Grid thumbnail (square)
 * <ResponsiveImage
 *   src="/thumbnail-600.jpg"
 *   sources={[
 *     { src: '/thumbnail-300.jpg', width: 300 },
 *     { src: '/thumbnail-600.jpg', width: 600 },
 *   ]}
 *   sizes="(max-width: 768px) 100vw, 200px"
 *   alt="Thumbnail"
 *   width={600}
 *   height={600}
 *   aspectRatioContainer={true}
 *   aspectRatio="1/1"
 *   objectFit="cover"
 *   className="rounded-lg"
 * />
 */
