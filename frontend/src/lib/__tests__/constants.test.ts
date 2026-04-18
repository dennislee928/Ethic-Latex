import { describe, expect, it } from 'vitest'
import { ROUTES } from '@/lib/constants'

describe('ROUTES', () => {
  it('defines the hybrid home route at slash', () => {
    expect(ROUTES.HOME).toBe('/')
  })
})
