"use client";

import { Auth0Provider, useAuth0 } from "@auth0/auth0-react";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { setTokenGetter } from "@/lib/api";

function TokenSetup({ children }: { children: React.ReactNode }) {
  const { getAccessTokenSilently, isAuthenticated } = useAuth0();

  useEffect(() => {
    // Set up the token getter function for the API service
    if (isAuthenticated) {
      setTokenGetter(async () => {
        try {
          const token = await getAccessTokenSilently({
            authorizationParams: {
              audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
              scope: "openid profile email",
            },
          });
          return token;
        } catch (error) {
          console.error("Error getting access token:", error);
          return "";
        }
      });
    }
  }, [getAccessTokenSilently, isAuthenticated]);

  return <>{children}</>;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  // Auth0 configuration - using environment variables for security
  const domain =
    process.env.NEXT_PUBLIC_AUTH0_DOMAIN || "dev-wcii3qy64cqx6v0w.us.auth0.com"; // ❌ REMOVED https://
  const clientId =
    process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID ||
    "48hZTEbnBvboITcdUE5tcJ8OnH3mVgya";
  const audience =
    process.env.NEXT_PUBLIC_AUTH0_AUDIENCE || "https://major-api";
  const redirectUri =
    typeof window !== "undefined" ? window.location.origin : "";

  if (!domain || !clientId) {
    console.error(
      "Auth0 credentials missing. Please check your environment variables.",
    );
    return <>{children}</>;
  }

  const onRedirectCallback = (appState?: any) => {
    // Navigate to the return path or default to /demo after login
    router.push(appState?.returnTo || "/demo");
  };

  return (
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: redirectUri,
        audience: audience,
        scope: "openid profile email offline_access", // ✅ ADDED offline_access
      }}
      onRedirectCallback={onRedirectCallback}
      cacheLocation="localstorage"
      useRefreshTokens={true}
    >
      <TokenSetup>{children}</TokenSetup>
    </Auth0Provider>
  );
}
