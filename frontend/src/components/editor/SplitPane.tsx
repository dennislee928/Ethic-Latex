import { useState, ReactNode, useEffect } from 'react'

interface SplitPaneProps {
  left: ReactNode
  right: ReactNode
  defaultSplit?: number // Percentage for left pane (0-100)
}

export default function SplitPane({ left, right, defaultSplit = 50 }: SplitPaneProps) {
  const [split, setSplit] = useState(defaultSplit)
  const [isDragging, setIsDragging] = useState(false)

  const handleMouseDown = () => {
    setIsDragging(true)
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging) return

    const container = (e.target as HTMLElement).closest('.split-pane-container') as HTMLElement
    if (!container) return

    const rect = container.getBoundingClientRect()
    const newSplit = ((e.clientX - rect.left) / rect.width) * 100
    setSplit(Math.max(20, Math.min(80, newSplit))) // Clamp between 20% and 80%
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  // Add global event listeners when dragging
  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove as any)
      window.addEventListener('mouseup', handleMouseUp)
      return () => {
        window.removeEventListener('mousemove', handleMouseMove as any)
        window.removeEventListener('mouseup', handleMouseUp)
      }
    }
  }, [isDragging])

  return (
    <div className="split-pane-container flex h-full">
      <div className="flex-shrink-0" style={{ width: `${split}%` }}>
        {left}
      </div>
      <div
        className="w-1 bg-border cursor-col-resize hover:bg-primary/50 transition-colors"
        onMouseDown={handleMouseDown}
      />
      <div className="flex-1" style={{ width: `${100 - split}%` }}>
        {right}
      </div>
    </div>
  )
}

