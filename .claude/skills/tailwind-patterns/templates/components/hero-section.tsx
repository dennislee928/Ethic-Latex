/**
 * Hero Section Component
 *
 * Responsive hero section with heading, description, and CTA buttons.
 * Uses semantic color tokens for automatic dark mode support.
 *
 * Usage:
 *   <HeroSection />
 */

export function HeroSection() {
  return (
    <section className="py-24 sm:py-32 lg:py-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto text-center">
          {/* Badge (optional) */}
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
            <svg className="h-4 w-4">🚀</svg>
            <span>New: Feature announcement</span>
          </div>

          {/* Main Heading */}
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
            Build Something Amazing Today
          </h1>

          {/* Description */}
          <p className="text-lg sm:text-xl text-muted-foreground mb-8 leading-relaxed">
            Create beautiful, responsive web applications with production-ready
            Tailwind CSS patterns. Get started in minutes, not hours.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-primary text-primary-foreground px-6 py-3 rounded-md hover:bg-primary/90 transition-colors font-medium">
              Get Started
            </button>
            <button className="border border-border bg-transparent px-6 py-3 rounded-md hover:bg-accent transition-colors font-medium">
              Learn More
            </button>
          </div>

          {/* Social Proof (optional) */}
          <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-8 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <svg className="h-5 w-5 text-primary">⭐</svg>
              <span>Trusted by 10,000+ developers</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="h-5 w-5 text-primary">✓</svg>
              <span>Free and open source</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}

/**
 * Alternative: Hero with Image
 */

export function HeroWithImage() {
  return (
    <section className="py-24 sm:py-32">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left: Content */}
          <div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
              Build Faster with Tailwind Patterns
            </h1>
            <p className="text-lg text-muted-foreground mb-8">
              Production-ready components that work out of the box. Copy, paste,
              and customize to match your brand.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <button className="bg-primary text-primary-foreground px-6 py-3 rounded-md hover:bg-primary/90 transition-colors">
                Get Started
              </button>
              <button className="border border-border px-6 py-3 rounded-md hover:bg-accent transition-colors">
                View Examples
              </button>
            </div>
          </div>

          {/* Right: Image/Visual */}
          <div className="relative">
            <div className="aspect-square rounded-lg bg-muted overflow-hidden">
              <img
                src="/hero-image.jpg"
                alt="Product screenshot"
                className="w-full h-full object-cover"
              />
            </div>
            {/* Decorative elements */}
            <div className="absolute -z-10 -top-4 -right-4 w-72 h-72 bg-primary/20 rounded-full blur-3xl" />
            <div className="absolute -z-10 -bottom-4 -left-4 w-72 h-72 bg-accent/20 rounded-full blur-3xl" />
          </div>
        </div>
      </div>
    </section>
  )
}
