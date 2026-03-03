/**
 * SEO Meta Component
 *
 * Complete SEO meta tags using react-helmet-async.
 * Includes title, description, Open Graph, Twitter Cards, and JSON-LD.
 *
 * Installation:
 *   npm install react-helmet-async
 *
 * Usage:
 *   import { SEOHead } from './components/SEOHead';
 *   <SEOHead page={pageData} business={businessData} />
 */

import { Helmet } from 'react-helmet-async';

interface PageSEO {
  title: string;
  description: string;
  path: string;
  type?: 'website' | 'article' | 'product';
  image?: string;
  datePublished?: string;
  dateModified?: string;
}

interface BusinessInfo {
  name: string;
  url: string;
  phone: string;
  email: string;
  logo: string;
  address: {
    street: string;
    city: string;
    state: string;
    postalCode: string;
    country: string;
  };
  geo?: {
    latitude: number;
    longitude: number;
  };
  businessType: string; // e.g., "Plumber", "Electrician", "LocalBusiness"
  priceRange?: string;
  openingHours?: Array<{
    days: string[];
    opens: string;
    closes: string;
  }>;
  socialMedia?: string[];
  rating?: {
    value: number;
    count: number;
  };
}

interface SEOHeadProps {
  page: PageSEO;
  business: BusinessInfo;
  jsonLd?: object; // Additional custom JSON-LD
}

export function SEOHead({ page, business, jsonLd }: SEOHeadProps) {
  const siteUrl = business.url;
  const canonicalUrl = `${siteUrl}${page.path}`;
  const ogImage = page.image || `${siteUrl}/og-image.jpg`;

  // LocalBusiness Schema
  const businessSchema = {
    '@context': 'https://schema.org',
    '@type': business.businessType,
    name: business.name,
    description: page.description,
    '@id': siteUrl,
    url: siteUrl,
    logo: business.logo,
    image: ogImage,
    telephone: business.phone,
    email: business.email,
    ...(business.priceRange && { priceRange: business.priceRange }),
    address: {
      '@type': 'PostalAddress',
      streetAddress: business.address.street,
      addressLocality: business.address.city,
      addressRegion: business.address.state,
      postalCode: business.address.postalCode,
      addressCountry: business.address.country,
    },
    ...(business.geo && {
      geo: {
        '@type': 'GeoCoordinates',
        latitude: business.geo.latitude,
        longitude: business.geo.longitude,
      },
    }),
    ...(business.openingHours && {
      openingHoursSpecification: business.openingHours.map(schedule => ({
        '@type': 'OpeningHoursSpecification',
        dayOfWeek: schedule.days,
        opens: schedule.opens,
        closes: schedule.closes,
      })),
    }),
    ...(business.socialMedia && { sameAs: business.socialMedia }),
    ...(business.rating && {
      aggregateRating: {
        '@type': 'AggregateRating',
        ratingValue: business.rating.value.toString(),
        reviewCount: business.rating.count.toString(),
      },
    }),
  };

  // Breadcrumb Schema (if not homepage)
  const breadcrumbSchema = page.path !== '/' && page.path !== '' ? {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: [
      {
        '@type': 'ListItem',
        position: 1,
        name: 'Home',
        item: siteUrl,
      },
      {
        '@type': 'ListItem',
        position: 2,
        name: page.title,
        item: canonicalUrl,
      },
    ],
  } : null;

  return (
    <Helmet>
      {/* Basic SEO */}
      <title>{page.title} | {business.name}</title>
      <meta name="description" content={page.description} />
      <link rel="canonical" href={canonicalUrl} />

      {/* Open Graph */}
      <meta property="og:title" content={page.title} />
      <meta property="og:description" content={page.description} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:image:width" content="1200" />
      <meta property="og:image:height" content="630" />
      <meta property="og:url" content={canonicalUrl} />
      <meta property="og:type" content={page.type || 'website'} />
      <meta property="og:site_name" content={business.name} />
      <meta property="og:locale" content="en_AU" />

      {/* Article-specific (if blog post) */}
      {page.type === 'article' && page.datePublished && (
        <>
          <meta property="article:published_time" content={page.datePublished} />
          {page.dateModified && (
            <meta property="article:modified_time" content={page.dateModified} />
          )}
        </>
      )}

      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={page.title} />
      <meta name="twitter:description" content={page.description} />
      <meta name="twitter:image" content={ogImage} />

      {/* JSON-LD - Business Schema */}
      <script type="application/ld+json">
        {JSON.stringify(businessSchema)}
      </script>

      {/* JSON-LD - Breadcrumbs */}
      {breadcrumbSchema && (
        <script type="application/ld+json">
          {JSON.stringify(breadcrumbSchema)}
        </script>
      )}

      {/* JSON-LD - Custom Schema */}
      {jsonLd && (
        <script type="application/ld+json">
          {JSON.stringify(jsonLd)}
        </script>
      )}
    </Helmet>
  );
}

/**
 * Usage Example:
 *
 * const pageData: PageSEO = {
 *   title: 'Emergency Plumber Sydney',
 *   description: 'Fast emergency plumbing in Sydney. Licensed plumbers, 24/7 service, upfront quotes. Call 1300 XXX XXX.',
 *   path: '/emergency-plumbing',
 *   type: 'website',
 *   image: 'https://acmeplumbing.com.au/images/emergency-og.jpg'
 * };
 *
 * const businessData: BusinessInfo = {
 *   name: 'Acme Plumbing',
 *   url: 'https://acmeplumbing.com.au',
 *   phone: '+61-XXX-XXX-XXX',
 *   email: 'info@acmeplumbing.com.au',
 *   logo: 'https://acmeplumbing.com.au/logo.png',
 *   address: {
 *     street: '123 Main Street',
 *     city: 'Sydney',
 *     state: 'NSW',
 *     postalCode: '2000',
 *     country: 'AU'
 *   },
 *   geo: {
 *     latitude: -33.8688,
 *     longitude: 151.2093
 *   },
 *   businessType: 'Plumber',
 *   priceRange: '$$',
 *   openingHours: [
 *     {
 *       days: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
 *       opens: '07:00',
 *       closes: '17:00'
 *     }
 *   ],
 *   socialMedia: [
 *     'https://facebook.com/acmeplumbing',
 *     'https://instagram.com/acmeplumbing'
 *   ],
 *   rating: {
 *     value: 4.9,
 *     count: 127
 *   }
 * };
 *
 * // In your component
 * <SEOHead page={pageData} business={businessData} />
 *
 * // With custom JSON-LD (FAQ)
 * const faqSchema = {
 *   "@context": "https://schema.org",
 *   "@type": "FAQPage",
 *   "mainEntity": [
 *     {
 *       "@type": "Question",
 *       "name": "How much does a plumber cost?",
 *       "acceptedAnswer": {
 *         "@type": "Answer",
 *         "text": "Rates typically range from $100-$150 per hour."
 *       }
 *     }
 *   ]
 * };
 *
 * <SEOHead page={pageData} business={businessData} jsonLd={faqSchema} />
 */

/**
 * App Setup (Required):
 *
 * // In your root App component
 * import { HelmetProvider } from 'react-helmet-async';
 *
 * function App() {
 *   return (
 *     <HelmetProvider>
 *       <Router>
 *         {/* Your routes *\/}
 *       </Router>
 *     </HelmetProvider>
 *   );
 * }
 */
