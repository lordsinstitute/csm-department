'use client';

import { useAuth0 } from '@auth0/auth0-react';
import { motion } from 'framer-motion';
import { Shield, GitBranch, Clock, TrendingUp, AlertTriangle, CheckCircle, Play, FileText } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function WelcomeDashboard({ onStartAnalysis }: { onStartAnalysis: () => void }) {
  const { user } = useAuth0();

  const fadeIn = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.5 }
  };

  const staggerChildren = {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  // Mock data - replace with real data from your backend
  const stats = {
    totalScans: 12,
    vulnerabilities: 3,
    lastScan: '2 days ago',
    riskScore: 7.5
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Welcome Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground mb-2">
              Welcome back, {user?.name?.split(' ')[0] || 'there'}! 👋
            </h1>
            <p className="text-lg text-muted-foreground">
              Your security dashboard is ready. Let's analyze some code.
            </p>
          </div>
          <div className="hidden md:flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Member since</p>
              <p className="text-sm font-medium">Oct 2025</p>
            </div>
            {user?.picture && (
              <img
                src={user.picture}
                alt={user.name || 'User'}
                className="h-16 w-16 rounded-full border-2 border-primary shadow-lg"
              />
            )}
          </div>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        variants={staggerChildren}
        initial="initial"
        animate="animate"
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
      >
        <motion.div variants={fadeIn} className="glass p-6 rounded-lg border border-border/40">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <GitBranch className="h-6 w-6 text-blue-500" />
            </div>
            <span className="text-2xl font-bold text-foreground">{stats.totalScans}</span>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">Total Scans</h3>
        </motion.div>

        <motion.div variants={fadeIn} className="glass p-6 rounded-lg border border-border/40">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-red-500/10 rounded-lg">
              <AlertTriangle className="h-6 w-6 text-red-500" />
            </div>
            <span className="text-2xl font-bold text-foreground">{stats.vulnerabilities}</span>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">Open Vulnerabilities</h3>
        </motion.div>

        <motion.div variants={fadeIn} className="glass p-6 rounded-lg border border-border/40">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-orange-500/10 rounded-lg">
              <TrendingUp className="h-6 w-6 text-orange-500" />
            </div>
            <span className="text-2xl font-bold text-foreground">{stats.riskScore}/10</span>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">Risk Score</h3>
        </motion.div>

        <motion.div variants={fadeIn} className="glass p-6 rounded-lg border border-border/40">
          <div className="flex items-center justify-between mb-4">
            <div className="p-2 bg-green-500/10 rounded-lg">
              <Clock className="h-6 w-6 text-green-500" />
            </div>
            <span className="text-lg font-bold text-foreground">{stats.lastScan}</span>
          </div>
          <h3 className="text-sm font-medium text-muted-foreground">Last Scan</h3>
        </motion.div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.3 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8"
      >
        <div className="glass p-6 rounded-lg border border-border/40 hover:border-primary/50 transition-colors cursor-pointer group" onClick={onStartAnalysis}>
          <div className="flex items-start gap-4">
            <div className="p-3 bg-primary/10 rounded-lg group-hover:bg-primary/20 transition-colors">
              <Play className="h-6 w-6 text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-foreground mb-2">New Security Scan</h3>
              <p className="text-sm text-muted-foreground mb-3">
                Start a comprehensive security analysis of your repository
              </p>
              <Button size="sm" className="w-full">
                Start Analysis
              </Button>
            </div>
          </div>
        </div>

        <div className="glass p-6 rounded-lg border border-border/40 hover:border-primary/50 transition-colors cursor-pointer group">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-green-500/10 rounded-lg group-hover:bg-green-500/20 transition-colors">
              <FileText className="h-6 w-6 text-green-500" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-foreground mb-2">View Reports</h3>
              <p className="text-sm text-muted-foreground mb-3">
                Access your previous security analysis reports
              </p>
              <Button size="sm" variant="outline" className="w-full">
                View All Reports
              </Button>
            </div>
          </div>
        </div>

        <div className="glass p-6 rounded-lg border border-border/40 hover:border-primary/50 transition-colors cursor-pointer group">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-blue-500/10 rounded-lg group-hover:bg-blue-500/20 transition-colors">
              <Shield className="h-6 w-6 text-blue-500" />
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-foreground mb-2">Security Dashboard</h3>
              <p className="text-sm text-muted-foreground mb-3">
                View trends and insights across all your projects
              </p>
              <Button size="sm" variant="outline" className="w-full">
                Open Dashboard
              </Button>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="glass p-6 rounded-lg border border-border/40"
      >
        <h3 className="text-lg font-semibold text-foreground mb-4">Recent Activity</h3>
        <div className="space-y-4">
          <div className="flex items-start gap-4 pb-4 border-b border-border/40 last:border-0 last:pb-0">
            <div className="p-2 bg-green-500/10 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-500" />
            </div>
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-foreground">Security scan completed</p>
                  <p className="text-sm text-muted-foreground">node-express-demo repository</p>
                </div>
                <span className="text-xs text-muted-foreground">2 days ago</span>
              </div>
            </div>
          </div>

          <div className="flex items-start gap-4 pb-4 border-b border-border/40 last:border-0 last:pb-0">
            <div className="p-2 bg-red-500/10 rounded-lg">
              <AlertTriangle className="h-5 w-5 text-red-500" />
            </div>
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-foreground">3 vulnerabilities detected</p>
                  <p className="text-sm text-muted-foreground">react-dashboard project</p>
                </div>
                <span className="text-xs text-muted-foreground">5 days ago</span>
              </div>
            </div>
          </div>

          <div className="flex items-start gap-4 pb-4 border-b border-border/40 last:border-0 last:pb-0">
            <div className="p-2 bg-blue-500/10 rounded-lg">
              <GitBranch className="h-5 w-5 text-blue-500" />
            </div>
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-foreground">Repository connected</p>
                  <p className="text-sm text-muted-foreground">api-backend-service</p>
                </div>
                <span className="text-xs text-muted-foreground">1 week ago</span>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
