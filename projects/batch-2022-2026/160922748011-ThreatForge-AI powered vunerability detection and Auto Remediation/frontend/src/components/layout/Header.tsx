'use client'

import Link from 'next/link'
import { AuthButton, UserProfile } from '@/components/auth'
import { useAuth0 } from '@auth0/auth0-react'

interface HeaderProps {
  variant?: 'default' | 'demo'
}

export function Header({ variant = 'default' }: HeaderProps) {
  const { isAuthenticated } = useAuth0()

  return (
    <header className="fixed top-0 w-full z-50 glass border-b border-border/40">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-4">
            <Link href="/" className="text-xl font-bold gradient-text">
              CognitoForge
            </Link>
            {variant === 'demo' && (
              <>
                <div className="h-6 w-px bg-border/40" />
                <span className="text-muted-foreground">Security Analysis</span>
              </>
            )}
          </div>
          
          <nav className="hidden md:flex items-center space-x-8">
            <Link 
              href="#features" 
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Features
            </Link>
            <Link 
              href="/demo" 
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Demo
            </Link>
            
            {isAuthenticated && <UserProfile />}
            
            <AuthButton />
          </nav>
        </div>
      </div>
    </header>
  )
}