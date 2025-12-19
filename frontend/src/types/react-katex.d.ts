declare module 'react-katex' {
  import { ComponentType } from 'react'

  export interface BlockMathProps {
    math: string
    errorColor?: string
    renderError?: (error: Error) => React.ReactNode
  }

  export const BlockMath: ComponentType<BlockMathProps>
  export const InlineMath: ComponentType<BlockMathProps>
}

