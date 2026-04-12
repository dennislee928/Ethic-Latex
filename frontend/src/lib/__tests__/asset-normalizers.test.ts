import { describe, expect, it } from 'vitest'
import { toAssetGroup } from '@/api/assets'
import type { RawAssetGroup } from '@/types/assets'

describe('toAssetGroup', () => {
  it('normalizes document and figure urls', () => {
    const payload: RawAssetGroup = {
      documents: [{ name: 'paper.pdf', category: 'document', relative_path: 'paper.pdf', url: '/assets/files/paper.pdf' }],
      figures: [],
    }

    expect(toAssetGroup(payload).documents[0].url).toBe('/assets/files/paper.pdf')
  })
})
