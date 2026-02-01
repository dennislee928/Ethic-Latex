import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { settingsApi } from '@/api/settings'
import { Save, Loader2 } from 'lucide-react'
import type { UserPreferences } from '@/types/settings'

export default function Settings() {
  const queryClient = useQueryClient()
  const { data: settings, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: () => settingsApi.get(),
  })

  const [preferences, setPreferences] = useState<UserPreferences>({
    theme: 'light',
    default_judge_type: 'COMBINED',
    auto_save: true,
  })

  // Update local state when settings are loaded
  useEffect(() => {
    if (settings?.preferences) {
      setPreferences(settings.preferences as UserPreferences)
    }
  }, [settings])

  const updateMutation = useMutation({
    mutationFn: (prefs: UserPreferences) => settingsApi.update(prefs),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] })
    },
  })

  const handleSave = () => {
    updateMutation.mutate(preferences)
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground mt-2">Manage SDK configuration, API keys, and preferences</p>
        </div>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground mt-2">
          Manage SDK configuration, API keys, and preferences
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* User Preferences */}
        <Card>
          <CardHeader>
            <CardTitle>User Preferences</CardTitle>
            <CardDescription>Configure your application preferences</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Theme</label>
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={preferences.theme}
                onChange={(e) =>
                  setPreferences({
                    ...preferences,
                    theme: e.target.value as 'light' | 'dark' | 'system',
                  })
                }
              >
                <option value="light">Light</option>
                <option value="dark">Dark</option>
                <option value="system">System</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">Default Judge Type</label>
              <select
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={preferences.default_judge_type}
                onChange={(e) =>
                  setPreferences({
                    ...preferences,
                    default_judge_type: e.target.value as 'PIPELINE' | 'HUMAN' | 'COMBINED',
                  })
                }
              >
                <option value="PIPELINE">Pipeline</option>
                <option value="HUMAN">Human</option>
                <option value="COMBINED">Combined</option>
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="auto_save"
                checked={preferences.auto_save}
                onChange={(e) =>
                  setPreferences({
                    ...preferences,
                    auto_save: e.target.checked,
                  })
                }
                className="h-4 w-4 rounded border-gray-300"
              />
              <label htmlFor="auto_save" className="text-sm font-medium">
                Enable auto-save
              </label>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">API Base URL (optional)</label>
              <Input
                type="url"
                value={preferences.api_base_url || ''}
                onChange={(e) =>
                  setPreferences({
                    ...preferences,
                    api_base_url: e.target.value || undefined,
                  })
                }
                placeholder="http://localhost:8000"
              />
            </div>

            <Button onClick={handleSave} disabled={updateMutation.isPending} className="w-full">
              {updateMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Preferences
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* SDK Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>SDK Configuration</CardTitle>
            <CardDescription>Configure JavaScript SDK settings</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">SDK Version</label>
              <Input value="0.1.0" disabled />
              <p className="text-xs text-muted-foreground mt-1">
                Current SDK version (read-only)
              </p>
            </div>

            <div>
              <label className="text-sm font-medium mb-2 block">API Endpoint</label>
              <Input value="http://localhost:8000" disabled />
              <p className="text-xs text-muted-foreground mt-1">
                Backend API endpoint (configured in environment)
              </p>
            </div>
          </CardContent>
        </Card>

        {/* API Keys */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>API Keys</CardTitle>
            <CardDescription>
              Manage API keys for external services. Keys are stored securely on the backend.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                API key management will be implemented in a future update. For now, API keys should be
                configured directly in the backend environment variables.
              </p>
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm font-medium mb-2">Security Note</p>
                <p className="text-xs text-muted-foreground">
                  API keys are never exposed to the frontend. All sensitive operations are handled
                  server-side to ensure security.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
