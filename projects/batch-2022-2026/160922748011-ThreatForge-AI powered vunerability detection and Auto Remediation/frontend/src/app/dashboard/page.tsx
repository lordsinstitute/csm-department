'use client';

import { ProtectedRoute } from '@/components/auth';
import { Dashboard } from '@/components/Dashboard';
import { UserProfile } from '@/components/auth';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <header className="border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
          <div className="container mx-auto px-4">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-4">
                <Link href="/" className="text-xl font-bold gradient-text">
                  CognitoForge
                </Link>
                <div className="h-6 w-px bg-border/40" />
                <span className="text-muted-foreground">Performance Test</span>
              </div>
              
              <div className="flex items-center gap-4">
                <Link href="/demo" className="text-sm text-muted-foreground hover:text-foreground transition-colors flex items-center gap-2">
                  <ArrowLeft className="h-4 w-4" />
                  Back to Demo
                </Link>
                <UserProfile />
              </div>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main>
          <Dashboard />
        </main>
      </div>
    </ProtectedRoute>
  );
}
