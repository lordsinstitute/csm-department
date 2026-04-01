'use client'

import * as React from "react"
import { cn } from "@/lib/utils"

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 
    | 'default'
    | 'destructive'
    | 'outline'
    | 'secondary'
    | 'ghost'
    | 'link'
    | 'purple'
    | 'purple-outline'
    | 'purple-ghost'
    | 'brand'
  size?: 'default' | 'sm' | 'lg' | 'icon'
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'default', size = 'default', asChild = false, ...props }, ref) => {

    const baseStyles =
      "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-300 ease-out " +
      "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#614334] focus-visible:ring-offset-2 " +
      "disabled:pointer-events-none disabled:opacity-50 will-change-transform"

    const variants = {
      default:
        "bg-gradient-to-r from-purple-600 to-violet-600 text-white " +
        "hover:from-purple-500 hover:to-violet-500 hover:shadow-lg hover:shadow-purple-500/40 " +
        "transform hover:scale-105",

      destructive:
        "bg-red-500 text-white hover:bg-red-600 hover:shadow-lg hover:shadow-red-500/25",

      outline:
        "border-2 border-purple-400/40 bg-transparent text-purple-300 " +
        "hover:bg-purple-500/15 hover:border-purple-400/70 hover:text-purple-100",

      secondary:
        "bg-slate-800/80 text-purple-200 hover:bg-slate-700/90 border border-purple-700/40",

      ghost:
        "text-purple-300 hover:bg-purple-500/15 hover:text-purple-100",

      link:
        "text-purple-400 underline-offset-4 hover:underline hover:text-purple-300",

      // ✅ REPLACED PURPLE VARIANT (NOW #614334)
      purple:
        "bg-[#614334] text-white hover:bg-[#52392c] " +
        "hover:shadow-xl hover:shadow-[#614334]/50 glow-on-hover " +
        "transform hover:scale-105",

      "purple-outline":
        "border-2 border-purple-400/60 text-purple-300 " +
        "hover:bg-purple-500/25 hover:border-purple-400 hover:text-purple-100 " +
        "hover:shadow-lg hover:shadow-purple-500/30",

      "purple-ghost":
        "text-purple-400 hover:bg-purple-500/20 hover:text-purple-200 backdrop-blur-sm",

      brand:
        "bg-brand-primary text-white shadow-lg shadow-brand-dark/40 " +
        "hover:bg-brand-secondary hover:shadow-brand-dark/60",
    }

    const sizes = {
      default: "h-10 px-6 py-2",
      sm: "h-9 rounded-lg px-4 text-xs",
      lg: "h-12 rounded-xl px-8 text-base font-semibold",
      icon: "h-10 w-10 rounded-lg",
    }

    if (asChild) {
      return React.cloneElement(props.children as React.ReactElement, {
        className: cn(baseStyles, variants[variant], sizes[size], className),
        ref,
        ...props,
      })
    }

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        {...props}
      />
    )
  }
)

Button.displayName = "Button"

export { Button }
