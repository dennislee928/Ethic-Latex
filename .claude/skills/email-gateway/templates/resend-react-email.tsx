/**
 * Resend React Email Template
 *
 * Use React components for email design (requires Node.js environment).
 * Install: npm install resend react-email @react-email/components
 *
 * For Cloudflare Workers: Pre-render with @react-email/render
 */

import { Resend } from 'resend';
import {
  Html,
  Head,
  Body,
  Container,
  Heading,
  Text,
  Button,
  Section,
  Hr,
} from '@react-email/components';

// ============================================================================
// Email Component
// ============================================================================

interface WelcomeEmailProps {
  name: string;
  confirmUrl: string;
}

export function WelcomeEmail({ name, confirmUrl }: WelcomeEmailProps) {
  return (
    <Html>
      <Head />
      <Body style={styles.body}>
        <Container style={styles.container}>
          <Heading style={styles.heading}>Welcome, {name}!</Heading>

          <Text style={styles.text}>
            Thanks for signing up. We're excited to have you on board.
          </Text>

          <Section style={styles.buttonSection}>
            <Button href={confirmUrl} style={styles.button}>
              Confirm Your Email
            </Button>
          </Section>

          <Hr style={styles.hr} />

          <Text style={styles.footer}>
            If you didn't create this account, you can safely ignore this email.
          </Text>
        </Container>
      </Body>
    </Html>
  );
}

const styles = {
  body: {
    backgroundColor: '#f6f9fc',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  container: {
    backgroundColor: '#ffffff',
    margin: '0 auto',
    padding: '20px 0 48px',
    marginBottom: '64px',
  },
  heading: {
    fontSize: '32px',
    lineHeight: '1.3',
    fontWeight: '700',
    color: '#484848',
    padding: '0 48px',
  },
  text: {
    fontSize: '16px',
    lineHeight: '1.6',
    color: '#484848',
    padding: '24px 48px 0',
  },
  buttonSection: {
    padding: '24px 48px',
  },
  button: {
    backgroundColor: '#000000',
    borderRadius: '8px',
    color: '#ffffff',
    fontSize: '16px',
    fontWeight: '600',
    textDecoration: 'none',
    textAlign: 'center' as const,
    display: 'block',
    width: '100%',
    padding: '12px 0',
  },
  hr: {
    borderColor: '#e6ebf1',
    margin: '20px 48px',
  },
  footer: {
    fontSize: '14px',
    lineHeight: '1.5',
    color: '#8898aa',
    padding: '0 48px',
  },
};

// ============================================================================
// Node.js Usage (with Resend SDK)
// ============================================================================

const resend = new Resend(process.env.RESEND_API_KEY);

export async function sendWelcomeEmail(name: string, email: string, confirmUrl: string) {
  try {
    const data = await resend.emails.send({
      from: 'noreply@yourdomain.com',
      to: email,
      subject: `Welcome, ${name}!`,
      react: WelcomeEmail({ name, confirmUrl }),
    });

    return { success: true, id: data.id };
  } catch (error) {
    return { success: false, error: (error as Error).message };
  }
}

// ============================================================================
// Cloudflare Workers Usage (pre-render)
// ============================================================================

import { render } from '@react-email/render';

interface Env {
  RESEND_API_KEY: string;
}

export async function sendWelcomeEmailWorker(
  name: string,
  email: string,
  confirmUrl: string,
  env: Env
) {
  // Render React component to HTML string
  const html = render(WelcomeEmail({ name, confirmUrl }));

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: 'noreply@yourdomain.com',
      to: email,
      subject: `Welcome, ${name}!`,
      html,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    return { success: false, error: error.message };
  }

  const data = await response.json();
  return { success: true, id: data.id };
}

// ============================================================================
// Preview Email (Development)
// ============================================================================

// Create emails/preview.tsx for local development:
// import { WelcomeEmail } from './welcome';
// export default function Preview() {
//   return <WelcomeEmail name="Alice" confirmUrl="https://example.com/confirm" />;
// }
//
// Run: npm run email dev
