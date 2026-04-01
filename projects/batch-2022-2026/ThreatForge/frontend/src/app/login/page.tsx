'use client';

import { useState } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Shield, Lock, Mail, ArrowLeft, Loader2, Github, Chrome } from 'lucide-react';

export default function LoginPage() {
  const { loginWithRedirect, isLoading } = useAuth0();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    // Auth0 handles the actual authentication
    await loginWithRedirect({
      authorizationParams: {
        screen_hint: 'login',
        login_hint: email,
      }
    });
  };

  const handleSocialLogin = async (connection: string) => {
    await loginWithRedirect({
      authorizationParams: {
        connection,
      }
    });
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse-glow" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-400/10 rounded-full blur-3xl animate-float" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md"
      >
        {/* Back to home */}
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 mb-8 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Home
        </Link>

        {/* Login card */}
        <div className="glass-purple-strong rounded-2xl p-8 border border-purple-500/20">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-purple-500/20 mb-4">
              <Shield className="h-8 w-8 text-purple-400" />
            </div>
            <h1 className="text-3xl font-bold gradient-text mb-2">
              Welcome Back
            </h1>
            <p className="text-muted-foreground">
              Sign in to access your security dashboard
            </p>
          </div>

          {/* Social login buttons */}
          <div className="space-y-3 mb-6">
            <Button
              onClick={() => handleSocialLogin('google-oauth2')}
              disabled={isLoading}
              variant="outline"
              className="w-full gap-2 hover:bg-purple-500/10"
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Chrome className="h-5 w-5" />
              )}
              Continue with Google
            </Button>

            <Button
              onClick={() => handleSocialLogin('github')}
              disabled={isLoading}
              variant="outline"
              className="w-full gap-2 hover:bg-purple-500/10"
            >
              {isLoading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <Github className="h-5 w-5" />
              )}
              Continue with GitHub
            </Button>
          </div>

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border/40"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-background/80 text-muted-foreground">
                Or continue with email
              </span>
            </div>
          </div>

          {/* Email login form */}
          <form onSubmit={handleEmailLogin} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-foreground mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className="w-full pl-10 pr-4 py-3 bg-background/50 border border-border/40 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-foreground mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                  className="w-full pl-10 pr-4 py-3 bg-background/50 border border-border/40 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  className="w-4 h-4 rounded border-border/40 text-purple-500 focus:ring-purple-500"
                />
                <span className="text-muted-foreground">Remember me</span>
              </label>
              <Link
                href="/forgot-password"
                className="text-purple-400 hover:text-purple-300 transition-colors"
              >
                Forgot password?
              </Link>
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              variant="purple"
              className="w-full gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Signing in...
                </>
              ) : (
                <>
                  <Lock className="h-5 w-5" />
                  Sign In
                </>
              )}
            </Button>
          </form>

          {/* Sign up link */}
          <div className="mt-6 text-center text-sm text-muted-foreground">
            Don't have an account?{' '}
            <Link
              href="/signup"
              className="text-purple-400 hover:text-purple-300 font-medium transition-colors"
            >
              Sign up for free
            </Link>
          </div>

          {/* Security note */}
          <div className="mt-6 p-3 bg-purple-500/5 border border-purple-500/20 rounded-lg">
            <div className="flex items-start gap-2">
              <Shield className="h-4 w-4 text-purple-400 mt-0.5 flex-shrink-0" />
              <p className="text-xs text-muted-foreground">
                Your credentials are securely handled by Auth0. We never store your password.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-muted-foreground mt-6">
          By signing in, you agree to our{' '}
          <Link href="/terms" className="text-purple-400 hover:text-purple-300">
            Terms of Service
          </Link>{' '}
          and{' '}
          <Link href="/privacy" className="text-purple-400 hover:text-purple-300">
            Privacy Policy
          </Link>
        </p>
      </motion.div>
    </div>
  );
}
