'use client';

import { useAuth0 } from '@auth0/auth0-react';
import { Button } from '@/components/ui/button';
import { LogIn, LogOut, Loader2 } from 'lucide-react';

export function LoginButton() {
  const { loginWithRedirect, isLoading } = useAuth0();

  return (
    <Button
      onClick={() => loginWithRedirect()}
      disabled={isLoading}
      variant="default"
      className="gap-2"
    >
      {isLoading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        <LogIn className="h-4 w-4" />
      )}
      Sign In
    </Button>
  );
}

export function LogoutButton() {
  const { logout, isLoading } = useAuth0();

  return (
    <Button
      onClick={() => logout({ logoutParams: { returnTo: window.location.origin } })}
      disabled={isLoading}
      variant="outline"
      className="gap-2"
    >
      {isLoading ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        <LogOut className="h-4 w-4" />
      )}
      Sign Out
    </Button>
  );
}

export function AuthButton() {
  const { isAuthenticated, isLoading } = useAuth0();

  if (isLoading) {
    return (
      <Button disabled variant="ghost" className="gap-2">
        <Loader2 className="h-4 w-4 animate-spin" />
      </Button>
    );
  }

  return isAuthenticated ? <LogoutButton /> : <LoginButton />;
}

export function UserProfile() {
  const { user, isAuthenticated, isLoading } = useAuth0();

  if (isLoading || !isAuthenticated || !user) {
    return null;
  }

  return (
    <div className="flex items-center gap-3">
      {user.picture && (
        <img
          src={user.picture}
          alt={user.name || 'User'}
          className="h-8 w-8 rounded-full border border-border"
        />
      )}
      <div className="hidden md:block">
        <p className="text-sm font-medium">{user.name}</p>
        <p className="text-xs text-muted-foreground">{user.email}</p>
      </div>
    </div>
  );
}
