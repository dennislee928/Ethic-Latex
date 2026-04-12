export type AssetCategory = 'document' | 'figures' | 'simulation'

export interface RawAssetRecord {
  name: string
  category: AssetCategory
  relative_path: string
  url: string
}

export interface RawAssetGroup {
  documents: RawAssetRecord[]
  figures: RawAssetRecord[]
}

export interface AssetRecord {
  name: string
  category: AssetCategory
  relativePath: string
  url: string
}

export interface AssetGroup {
  documents: AssetRecord[]
  figures: AssetRecord[]
}
