import { beforeEach, describe, expect, it } from 'vitest'
import { fireEvent, renderWithProviders, screen } from '@/test/render'
import JudgePicker from '@/components/layout/JudgePicker'
import { useDemoStore } from '@/store/demoStore'

describe('JudgePicker', () => {
  beforeEach(() => {
    useDemoStore.setState({ judgeType: 'COMBINED' })
  })

  it('updates the selected judge type', () => {
    renderWithProviders(<JudgePicker />)

    fireEvent.click(screen.getByRole('button', { name: /human/i }))

    expect(useDemoStore.getState().judgeType).toBe('HUMAN')
  })
})
