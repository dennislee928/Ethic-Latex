import { describe, expect, it, vi } from 'vitest'
import { renderWithProviders, screen } from '@/test/render'
import Dashboard from '@/pages/Dashboard'

vi.mock('@/api/assets', () => ({
  assetsApi: {
    getIndex: vi.fn().mockResolvedValue({
      documents: [{ name: 'ethical_riemann_hypothesis.pdf', category: 'document', relativePath: 'ethical_riemann_hypothesis.pdf', url: '/assets/files/ethical_riemann_hypothesis.pdf' }],
      figures: [{ name: 'paper_fig1.pdf', category: 'figures', relativePath: 'figures/paper_fig1.pdf', url: '/assets/files/figures/paper_fig1.pdf' }],
    }),
  },
}))

vi.mock('@/api/dashboard', () => ({
  dashboardApi: {
    getSummary: vi.fn().mockResolvedValue({
      judge_type: 'COMBINED',
      num_samples: 144,
      num_primes: 12,
      estimated_alpha: 0.48,
      r_squared: 0.92,
    }),
    getCurves: vi.fn().mockResolvedValue({
      pi_curve: [{ x: 1, y: 1 }],
      error_curve: [{ x: 1, y: 0.1 }],
    }),
    getHealth: vi.fn().mockResolvedValue({
      error_curve: [{ x: 1, y: 0.1 }],
      riemann_bound: [{ x: 1, y: 0.2 }],
      violation: false,
      violation_points: [],
    }),
    getStats: vi.fn().mockResolvedValue({
      total_rules: 3,
      active_rules: 2,
      pass_rate: 0.9,
      total_violations: 12,
      critical_violations: 12,
    }),
  },
}))

describe('Dashboard home', () => {
  it('renders research assets and live lab panels together', async () => {
    renderWithProviders(<Dashboard />)

    expect(await screen.findByText(/research papers/i)).toBeInTheDocument()
    expect(await screen.findByText(/live analysis/i)).toBeInTheDocument()
  })
})
