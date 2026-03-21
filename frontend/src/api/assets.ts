import apiClient from './client'
import type { AssetGroup, AssetRecord, RawAssetGroup, RawAssetRecord } from '@/types/assets'

function toAssetRecord(asset: RawAssetRecord): AssetRecord {
  return {
    name: asset.name,
    category: asset.category,
    relativePath: asset.relative_path,
    url: asset.url,
  }
}

export function toAssetGroup(payload: RawAssetGroup): AssetGroup {
  return {
    documents: payload.documents.map(toAssetRecord),
    figures: payload.figures.map(toAssetRecord),
  }
}

export const assetsApi = {
  getIndex: async (): Promise<AssetGroup> => {
    const response = await apiClient.get<RawAssetGroup>('/assets/index')
    return toAssetGroup(response.data)
  },
}
