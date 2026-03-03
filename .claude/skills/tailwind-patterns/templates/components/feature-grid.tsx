/**
 * Feature Grid Component
 *
 * Responsive 3-column feature grid with icons.
 * Automatically collapses to 1 column on mobile, 2 on tablet.
 *
 * Usage:
 *   <FeatureGrid features={features} />
 */

interface Feature {
  title: string
  description: string
  icon: React.ReactNode
}

interface FeatureGridProps {
  features: Feature[]
}

export function FeatureGrid({ features }: FeatureGridProps) {
  return (
    <section className="py-16 sm:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="max-w-2xl mx-auto text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Everything You Need
          </h2>
          <p className="text-lg text-muted-foreground">
            Production-ready patterns for common UI components and layouts.
          </p>
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-card text-card-foreground rounded-lg border border-border p-6 hover:shadow-lg transition-shadow"
            >
              {/* Icon */}
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 text-primary">
                {feature.icon}
              </div>

              {/* Content */}
              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground text-sm">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

/**
 * Example Usage:
 *
 * const features = [
 *   {
 *     title: 'Responsive Design',
 *     description: 'Mobile-first patterns that work on all devices.',
 *     icon: <svg className="h-6 w-6">📱</svg>
 *   },
 *   {
 *     title: 'Dark Mode',
 *     description: 'Automatic dark mode support with semantic tokens.',
 *     icon: <svg className="h-6 w-6">🌙</svg>
 *   },
 *   {
 *     title: 'Production Ready',
 *     description: 'Battle-tested patterns used in real applications.',
 *     icon: <svg className="h-6 w-6">✓</svg>
 *   },
 * ]
 *
 * <FeatureGrid features={features} />
 */

/**
 * Alternative: Feature Grid with Numbers
 */

export function NumberedFeatureGrid({ features }: FeatureGridProps) {
  return (
    <section className="py-16 sm:py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-card text-card-foreground rounded-lg border border-border p-6"
            >
              {/* Number Badge */}
              <div className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground text-sm font-semibold mb-4">
                {index + 1}
              </div>

              <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-muted-foreground text-sm">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

/**
 * Alternative: Feature List (Horizontal Layout)
 */

export function FeatureList({ features }: FeatureGridProps) {
  return (
    <section className="py-16 sm:py-24">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="space-y-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="flex gap-6 items-start"
            >
              {/* Icon */}
              <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0 text-primary">
                {feature.icon}
              </div>

              {/* Content */}
              <div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
