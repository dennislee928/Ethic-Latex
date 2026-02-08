import { Editor } from '@tiptap/core'
import Image from '@tiptap/extension-image'

/**
 * Image Upload Handler for Cloudflare R2
 *
 * Pattern: Base64 preview → background upload → replace with URL
 *
 * Benefits:
 * - Immediate user feedback (base64 preview)
 * - No database bloat (URL replaces base64)
 * - Works with Cloudflare R2
 * - Graceful error handling
 *
 * Prerequisites:
 * - R2 bucket configured in wrangler.jsonc
 * - Upload API endpoint (see below)
 * - Image extension installed: npm install @tiptap/extension-image
 */

/**
 * Example Upload API Endpoint (Cloudflare Worker)
 *
 * Place this in your Worker's routes:
 * ```typescript
 * import { Env } from './types'
 *
 * export async function handleImageUpload(request: Request, env: Env) {
 *   const formData = await request.formData()
 *   const file = formData.get('file') as File
 *
 *   if (!file) {
 *     return Response.json({ error: 'No file provided' }, { status: 400 })
 *   }
 *
 *   // Generate unique filename
 *   const filename = `${crypto.randomUUID()}-${file.name}`
 *
 *   // Upload to R2
 *   await env.IMAGES_BUCKET.put(filename, file.stream(), {
 *     httpMetadata: {
 *       contentType: file.type,
 *     },
 *   })
 *
 *   // Return public URL (configure custom domain in R2 settings)
 *   const url = `https://images.yourdomain.com/${filename}`
 *
 *   return Response.json({ url })
 * }
 * ```
 */

interface UploadImageOptions {
  editor: Editor
  file: File
  uploadEndpoint?: string
  onProgress?: (progress: number) => void
  onError?: (error: Error) => void
}

/**
 * Upload image to R2 with base64 preview
 */
export async function uploadImageToR2({
  editor,
  file,
  uploadEndpoint = '/api/upload',
  onProgress,
  onError,
}: UploadImageOptions): Promise<string | null> {
  try {
    // 1. Create base64 preview for immediate display
    const base64 = await fileToBase64(file)

    // 2. Insert preview into editor (user sees image immediately)
    editor.chain().focus().setImage({ src: base64 }).run()

    onProgress?.(10) // Loading started

    // 3. Upload to R2 in background
    const formData = new FormData()
    formData.append('file', file)

    onProgress?.(50) // Upload in progress

    const response = await fetch(uploadEndpoint, {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`)
    }

    const { url } = await response.json()

    onProgress?.(90) // Processing complete

    // 4. Replace base64 preview with permanent URL
    // Find the image node and update its src attribute
    const { state } = editor
    const { selection } = state
    const pos = selection.$from.pos

    // Update the image that was just inserted
    editor.chain()
      .focus()
      .updateAttributes('image', { src: url })
      .run()

    onProgress?.(100) // Done

    return url
  } catch (error) {
    console.error('Image upload failed:', error)
    onError?.(error as Error)

    // Remove failed image from editor
    editor.chain().focus().deleteSelection().run()

    return null
  }
}

/**
 * Convert File to base64 string
 */
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

/**
 * Configure Image extension with upload handler
 *
 * Usage in useEditor():
 * ```typescript
 * import { getImageExtensionWithUpload } from '@/lib/tiptap-image-upload'
 *
 * const editor = useEditor({
 *   extensions: [
 *     StarterKit,
 *     getImageExtensionWithUpload(),
 *   ],
 * })
 * ```
 */
export function getImageExtensionWithUpload() {
  return Image.extend({
    addProseMirrorPlugins() {
      return [
        // Add paste handler for images
        new Plugin({
          key: new PluginKey('imageUpload'),
          props: {
            handlePaste(view, event) {
              const items = Array.from(event.clipboardData?.items || [])
              const editor = view.state as any // Get editor instance

              for (const item of items) {
                if (item.type.startsWith('image/')) {
                  event.preventDefault()

                  const file = item.getAsFile()
                  if (file) {
                    uploadImageToR2({ editor, file })
                  }

                  return true
                }
              }

              return false
            },
            handleDrop(view, event) {
              const files = Array.from(event.dataTransfer?.files || [])
              const editor = view.state as any

              for (const file of files) {
                if (file.type.startsWith('image/')) {
                  event.preventDefault()
                  uploadImageToR2({ editor, file })
                  return true
                }
              }

              return false
            },
          },
        }),
      ]
    },
  }).configure({
    inline: true,
    allowBase64: false, // ⚠️ Prevent base64 bloat in database
    HTMLAttributes: {
      class: 'rounded-lg max-w-full h-auto',
    },
  })
}

/**
 * Example: Editor component with image upload
 */
export function EditorWithImageUpload() {
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)

  const editor = useEditor({
    extensions: [
      StarterKit,
      getImageExtensionWithUpload(),
    ],
    immediatelyRender: false,
  })

  const handleImageUpload = async (file: File) => {
    if (!editor) return

    setUploading(true)
    setProgress(0)

    await uploadImageToR2({
      editor,
      file,
      onProgress: setProgress,
      onError: (error) => {
        alert(`Upload failed: ${error.message}`)
      },
    })

    setUploading(false)
  }

  return (
    <div>
      {uploading && (
        <div className="mb-2">
          <div className="h-2 bg-muted rounded">
            <div
              className="h-full bg-primary rounded transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-muted-foreground mt-1">
            Uploading... {progress}%
          </p>
        </div>
      )}

      <EditorContent editor={editor} />

      <div className="mt-2">
        <input
          type="file"
          accept="image/*"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) handleImageUpload(file)
          }}
          className="text-sm"
        />
      </div>
    </div>
  )
}

// Required imports for Plugin example
import { Plugin, PluginKey } from '@tiptap/pm/state'
import { EditorContent, useEditor } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import { useState } from 'react'
