import React, { useEffect, useState } from 'react';
import { Layout } from '../components/Layout';
import { ErrorSummaryCard } from '../components/ErrorSummaryCard';
import { ErhCurveChart } from '../components/ErhCurveChart';
import { ComplexityHeatmap } from '../components/ComplexityHeatmap';
import { HealthMonitorChart } from '../components/HealthMonitorChart';
import type {
  AnalysisCurves,
  AnalysisSummary,
  HeatmapResponse,
  HealthMonitorResponse,
  JudgeType
} from '../lib/api';
import { getCurves, getHeatmap, getSummary, getHealth } from '../lib/api';

const judgeTypes: JudgeType[] = ['PIPELINE', 'HUMAN', 'COMBINED'];

const IndexPage: React.FC = () => {
  const [judgeType, setJudgeType] = useState<JudgeType>('COMBINED');

  const [summary, setSummary] = useState<AnalysisSummary | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  const [curves, setCurves] = useState<AnalysisCurves | null>(null);
  const [curvesLoading, setCurvesLoading] = useState(false);
  const [curvesError, setCurvesError] = useState<string | null>(null);

  const [heatmap, setHeatmap] = useState<HeatmapResponse | null>(null);
  const [heatmapLoading, setHeatmapLoading] = useState(false);
  const [heatmapError, setHeatmapError] = useState<string | null>(null);

  const [health, setHealth] = useState<HealthMonitorResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState(false);
  const [healthError, setHealthError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      setSummaryLoading(true);
      setCurvesLoading(true);
      setHeatmapLoading(true);
      setHealthLoading(true);
      setSummaryError(null);
      setCurvesError(null);
      setHeatmapError(null);
      setHealthError(null);

      try {
        const [s, c, hm, hl] = await Promise.all([
          getSummary(judgeType),
          getCurves(judgeType),
          getHeatmap(judgeType),
          getHealth(judgeType)
        ]);
        if (!cancelled) {
          setSummary(s);
          setCurves(c);
          setHeatmap(hm);
          setHealth(hl);
        }
      } catch (err) {
        if (!cancelled) {
          const message =
            err instanceof Error ? err.message : 'Failed to load analysis data.';
          setSummaryError(message);
          setCurvesError(message);
          setHeatmapError(message);
          setHealthError(message);
        }
      } finally {
        if (!cancelled) {
          setSummaryLoading(false);
          setCurvesLoading(false);
          setHeatmapLoading(false);
          setHealthLoading(false);
        }
      }
    };

    void load();

    return () => {
      cancelled = true;
    };
  }, [judgeType]);

  return (
    <Layout>
      <div className="mb-4 flex items-center gap-3">
        <label className="text-sm text-slate-300">Judge type</label>
        <select
          className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-slate-100"
          value={judgeType}
          onChange={(e) => setJudgeType(e.target.value as JudgeType)}
        >
          {judgeTypes.map((jt) => (
            <option key={jt} value={jt}>
              {jt}
            </option>
          ))}
        </select>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="md:col-span-1">
          <ErrorSummaryCard
            summary={summary}
            judgeType={judgeType}
            loading={summaryLoading}
            error={summaryError}
          />
        </div>
        <div className="md:col-span-2">
          <ErhCurveChart curves={curves} loading={curvesLoading} error={curvesError} />
        </div>
      </div>

      <div className="mt-4">
        <HealthMonitorChart
          data={health}
          judgeType={judgeType}
          loading={healthLoading}
          error={healthError}
        />
      </div>

      <div className="mt-4">
        <ComplexityHeatmap
          data={heatmap}
          loading={heatmapLoading}
          error={heatmapError}
        />
      </div>
    </Layout>
  );
};

export default IndexPage;


