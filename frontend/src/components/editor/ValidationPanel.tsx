import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { AlertCircle, CheckCircle, AlertTriangle, XCircle } from 'lucide-react'
import type { ValidationResult } from '@/types/latex'

interface ValidationPanelProps {
  validation: ValidationResult | null
  isLoading?: boolean
}

export default function ValidationPanel({ validation, isLoading }: ValidationPanelProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Validation</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Validating...</p>
        </CardContent>
      </Card>
    )
  }

  if (!validation) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Validation</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">No validation results yet</p>
        </CardContent>
      </Card>
    )
  }

  const severityColors = {
    low: 'bg-blue-100 text-blue-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-orange-100 text-orange-800',
    critical: 'bg-red-100 text-red-800',
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <XCircle className="h-4 w-4" />
      case 'high':
        return <AlertCircle className="h-4 w-4" />
      case 'medium':
        return <AlertTriangle className="h-4 w-4" />
      default:
        return <CheckCircle className="h-4 w-4" />
    }
  }

  const riskScore = validation.risk_score
  const riskLevel = riskScore < 0.3 ? 'low' : riskScore < 0.7 ? 'medium' : 'high'

  return (
    <Card>
      <CardHeader>
        <CardTitle>Validation Results</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium">Status</span>
          <Badge variant={validation.is_valid ? 'default' : 'destructive'}>
            {validation.is_valid ? 'Valid' : 'Invalid'}
          </Badge>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Risk Score</span>
            <span className="text-sm font-bold">{riskScore.toFixed(2)}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                riskLevel === 'low' ? 'bg-green-500' : riskLevel === 'medium' ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${riskScore * 100}%` }}
            />
          </div>
        </div>

        {validation.violations.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold mb-2">Violations ({validation.violations.length})</h4>
            <div className="space-y-2 max-h-60 overflow-y-auto">
              {validation.violations.map((violation, index) => (
                <div
                  key={index}
                  className="p-2 rounded border text-sm"
                >
                  <div className="flex items-start gap-2">
                    {getSeverityIcon(violation.severity)}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={severityColors[violation.severity as keyof typeof severityColors]}>
                          {violation.severity}
                        </Badge>
                        <span className="font-medium">{violation.type}</span>
                      </div>
                      <p className="text-muted-foreground">{violation.message}</p>
                      {violation.line !== undefined && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Line {violation.line}
                          {violation.column !== undefined && `, Column ${violation.column}`}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {validation.warnings.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold mb-2">Warnings ({validation.warnings.length})</h4>
            <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
              {validation.warnings.map((warning, index) => (
                <li key={index}>{warning}</li>
              ))}
            </ul>
          </div>
        )}

        {validation.is_valid && validation.violations.length === 0 && (
          <div className="flex items-center gap-2 text-green-600">
            <CheckCircle className="h-5 w-5" />
            <span className="text-sm font-medium">Rule passes all validation checks</span>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

