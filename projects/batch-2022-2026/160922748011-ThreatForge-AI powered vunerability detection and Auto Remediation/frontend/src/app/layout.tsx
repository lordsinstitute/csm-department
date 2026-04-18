import { Inter } from 'next/font/google';
import '../styles/globals.css';
import { HealthCheck } from '@/components/HealthCheck';
import { AuthProvider } from '@/components/auth';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'ThreatForge - AI Red Team Testing',
  description: 'AI-powered red team testing platform that simulates intelligent attacks on your code, CI/CD pipelines, and infrastructure before real hackers do.',
  keywords: 'cybersecurity, red team testing, AI security, vulnerability testing, DevSecOps',
  authors: [{ name: 'CognitoForge' }],
  viewport: 'width=device-width, initial-scale=1',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        <AuthProvider>
          <div className="min-h-screen bg-background antialiased">
            {children}
            <HealthCheck />
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}