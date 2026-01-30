/**
 * Contact Form Component
 *
 * Complete contact form with validation styling.
 * Includes name, email, subject, and message fields.
 *
 * Usage:
 *   <ContactForm onSubmit={handleSubmit} />
 */

'use client'

import { useState } from 'react'

interface ContactFormProps {
  onSubmit?: (data: ContactFormData) => Promise<void> | void
}

interface ContactFormData {
  name: string
  email: string
  subject: string
  message: string
}

export function ContactForm({ onSubmit }: ContactFormProps) {
  const [formData, setFormData] = useState<ContactFormData>({
    name: '',
    email: '',
    subject: '',
    message: '',
  })
  const [errors, setErrors] = useState<Partial<Record<keyof ContactFormData, string>>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    // Clear error when user starts typing
    if (errors[name as keyof ContactFormData]) {
      setErrors(prev => ({ ...prev, [name]: undefined }))
    }
  }

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof ContactFormData, string>> = {}

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required'
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email'
    }

    if (!formData.subject.trim()) {
      newErrors.subject = 'Subject is required'
    }

    if (!formData.message.trim()) {
      newErrors.message = 'Message is required'
    } else if (formData.message.length < 10) {
      newErrors.message = 'Message must be at least 10 characters'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validate()) return

    setIsSubmitting(true)
    try {
      await onSubmit?.(formData)
      setIsSuccess(true)
      setFormData({ name: '', email: '', subject: '', message: '' })
    } catch (error) {
      console.error('Form submission error:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSuccess) {
    return (
      <div className="max-w-md mx-auto bg-success/10 border border-success rounded-lg p-8 text-center">
        <svg className="h-12 w-12 text-success mx-auto mb-4">✓</svg>
        <h3 className="text-xl font-semibold mb-2">Message Sent!</h3>
        <p className="text-muted-foreground mb-4">
          Thank you for contacting us. We'll get back to you soon.
        </p>
        <button
          onClick={() => setIsSuccess(false)}
          className="text-primary hover:underline underline-offset-4"
        >
          Send another message
        </button>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto space-y-6">
      {/* Name */}
      <div className="space-y-2">
        <label htmlFor="name" className="text-sm font-medium">
          Name <span className="text-destructive">*</span>
        </label>
        <input
          id="name"
          name="name"
          type="text"
          value={formData.name}
          onChange={handleChange}
          className={`w-full px-3 py-2 bg-background border rounded-md focus:outline-none focus:ring-2 ${
            errors.name
              ? 'border-destructive focus:ring-destructive'
              : 'border-border focus:ring-primary'
          }`}
          placeholder="Your name"
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? 'name-error' : undefined}
        />
        {errors.name && (
          <p id="name-error" className="text-sm text-destructive">
            {errors.name}
          </p>
        )}
      </div>

      {/* Email */}
      <div className="space-y-2">
        <label htmlFor="email" className="text-sm font-medium">
          Email <span className="text-destructive">*</span>
        </label>
        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          className={`w-full px-3 py-2 bg-background border rounded-md focus:outline-none focus:ring-2 ${
            errors.email
              ? 'border-destructive focus:ring-destructive'
              : 'border-border focus:ring-primary'
          }`}
          placeholder="you@example.com"
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? 'email-error' : undefined}
        />
        {errors.email && (
          <p id="email-error" className="text-sm text-destructive">
            {errors.email}
          </p>
        )}
      </div>

      {/* Subject */}
      <div className="space-y-2">
        <label htmlFor="subject" className="text-sm font-medium">
          Subject <span className="text-destructive">*</span>
        </label>
        <select
          id="subject"
          name="subject"
          value={formData.subject}
          onChange={handleChange}
          className={`w-full px-3 py-2 bg-background border rounded-md focus:outline-none focus:ring-2 ${
            errors.subject
              ? 'border-destructive focus:ring-destructive'
              : 'border-border focus:ring-primary'
          }`}
          aria-invalid={!!errors.subject}
          aria-describedby={errors.subject ? 'subject-error' : undefined}
        >
          <option value="">Select a subject</option>
          <option value="general">General Inquiry</option>
          <option value="support">Technical Support</option>
          <option value="sales">Sales Question</option>
          <option value="other">Other</option>
        </select>
        {errors.subject && (
          <p id="subject-error" className="text-sm text-destructive">
            {errors.subject}
          </p>
        )}
      </div>

      {/* Message */}
      <div className="space-y-2">
        <label htmlFor="message" className="text-sm font-medium">
          Message <span className="text-destructive">*</span>
        </label>
        <textarea
          id="message"
          name="message"
          value={formData.message}
          onChange={handleChange}
          rows={5}
          className={`w-full px-3 py-2 bg-background border rounded-md focus:outline-none focus:ring-2 resize-y ${
            errors.message
              ? 'border-destructive focus:ring-destructive'
              : 'border-border focus:ring-primary'
          }`}
          placeholder="Your message..."
          aria-invalid={!!errors.message}
          aria-describedby={errors.message ? 'message-error' : undefined}
        />
        {errors.message && (
          <p id="message-error" className="text-sm text-destructive">
            {errors.message}
          </p>
        )}
        <p className="text-xs text-muted-foreground">
          {formData.message.length}/500 characters
        </p>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-primary text-primary-foreground px-4 py-3 rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {isSubmitting ? (
          <>
            <svg className="h-5 w-5 animate-spin">⟳</svg>
            <span>Sending...</span>
          </>
        ) : (
          'Send Message'
        )}
      </button>

      <p className="text-xs text-muted-foreground text-center">
        By submitting this form, you agree to our{' '}
        <a href="/privacy" className="text-primary hover:underline">
          privacy policy
        </a>
        .
      </p>
    </form>
  )
}

/**
 * Example Usage:
 *
 * <ContactForm
 *   onSubmit={async (data) => {
 *     await fetch('/api/contact', {
 *       method: 'POST',
 *       body: JSON.stringify(data),
 *     })
 *   }}
 * />
 */
