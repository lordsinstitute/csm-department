'use client'

import Link from 'next/link'

export function Footer() {
  return (
    <footer className="border-t border-border/40 py-12 bg-background/50">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="text-muted-foreground text-sm">
            © 2025 CognitoForge. All rights reserved.
          </div>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <Link 
              href="/privacy" 
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Privacy
            </Link>
            <Link 
              href="/terms" 
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Terms
            </Link>
            <Link 
              href="/docs" 
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Documentation
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}