import { create } from 'zustand'
import type { JudgeType } from '@/types/dashboard'

interface DemoState {
  judgeType: JudgeType
  selectedDocument: string | null
  selectedFigure: string | null
  selectedSimulationId: number | null
  setJudgeType: (judgeType: JudgeType) => void
  setSelectedDocument: (document: string | null) => void
  setSelectedFigure: (figure: string | null) => void
  setSelectedSimulationId: (simulationId: number | null) => void
}

export const useDemoStore = create<DemoState>((set) => ({
  judgeType: 'COMBINED',
  selectedDocument: null,
  selectedFigure: null,
  selectedSimulationId: null,
  setJudgeType: (judgeType) => set({ judgeType }),
  setSelectedDocument: (selectedDocument) => set({ selectedDocument }),
  setSelectedFigure: (selectedFigure) => set({ selectedFigure }),
  setSelectedSimulationId: (selectedSimulationId) => set({ selectedSimulationId }),
}))
