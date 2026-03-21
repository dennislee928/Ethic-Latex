import { useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import HeroPanel from '@/components/home/HeroPanel'
import DocumentShelf from '@/components/home/DocumentShelf'
import FigureGallery from '@/components/home/FigureGallery'
import AnalysisOverview from '@/components/home/AnalysisOverview'
import QuickSimulation from '@/components/home/QuickSimulation'
import QuickVerifier from '@/components/home/QuickVerifier'
import EmptyState from '@/components/layout/EmptyState'
import { dashboardApi } from '@/api/dashboard'
import { assetsApi } from '@/api/assets'
import apiClient from '@/api/client'
import { useDemoStore } from '@/store/demoStore'

export default function Dashboard() {
  const queryClient = useQueryClient()
  const judgeType = useDemoStore((state) => state.judgeType)
  const selectedDocument = useDemoStore((state) => state.selectedDocument)
  const selectedFigure = useDemoStore((state) => state.selectedFigure)
  const setSelectedDocument = useDemoStore((state) => state.setSelectedDocument)
  const setSelectedFigure = useDemoStore((state) => state.setSelectedFigure)

  const { data: assets } = useQuery({
    queryKey: ['assets'],
    queryFn: () => assetsApi.getIndex(),
  })

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['analysis-summary', judgeType],
    queryFn: () => dashboardApi.getSummary(judgeType),
  })

  const { data: curves, isLoading: curvesLoading } = useQuery({
    queryKey: ['analysis-curves', judgeType],
    queryFn: () => dashboardApi.getCurves(judgeType),
  })

  const { data: health } = useQuery({
    queryKey: ['analysis-health', judgeType],
    queryFn: () => dashboardApi.getHealth(judgeType),
  })

  const { data: stats } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardApi.getStats(),
  })

  const ingestionMutation = useMutation({
    mutationFn: () => apiClient.post('/ingestion/run', null, { params: { mode: 'mock' } }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ['analysis-summary'] }),
        queryClient.invalidateQueries({ queryKey: ['analysis-curves'] }),
        queryClient.invalidateQueries({ queryKey: ['analysis-health'] }),
        queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] }),
      ])
    },
  })

  useEffect(() => {
    if (!selectedDocument && assets?.documents.length) {
      setSelectedDocument(assets.documents[0].url)
    }
  }, [assets?.documents, selectedDocument, setSelectedDocument])

  useEffect(() => {
    if (!selectedFigure && assets?.figures.length) {
      setSelectedFigure(assets.figures[0].url)
    }
  }, [assets?.figures, selectedFigure, setSelectedFigure])

  return (
    <div className="space-y-8">
      <HeroPanel
        summary={summary}
        stats={stats}
        documentCount={assets?.documents.length ?? 0}
        figureCount={assets?.figures.length ?? 0}
        onRunMockIngestion={() => ingestionMutation.mutate()}
        isRunningMockIngestion={ingestionMutation.isPending}
      />

      {ingestionMutation.isError ? (
        <EmptyState
          title="Mock ingestion failed"
          description="The backend rejected the mock ingestion request. Check that the FastAPI service is running and reachable from the frontend."
        />
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <DocumentShelf
          documents={assets?.documents ?? []}
          selectedUrl={selectedDocument}
          onSelect={setSelectedDocument}
        />
        <AnalysisOverview
          summary={summary}
          curves={curves}
          health={health}
          stats={stats}
          isLoading={summaryLoading || curvesLoading}
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <FigureGallery
          figures={assets?.figures ?? []}
          selectedUrl={selectedFigure}
          onSelect={setSelectedFigure}
        />
        <div className="grid gap-6">
          <QuickSimulation />
          <QuickVerifier />
        </div>
      </div>
    </div>
  )
}
