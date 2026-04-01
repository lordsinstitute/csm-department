'use client';

import dynamic from 'next/dynamic';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Header } from '@/components/layout/Header';
import Hero from '@/components/Hero';
// import { ShaderAnimation } from '@/components/ShaderAnimation';

// ✅ Lazy-loaded sections
const FeaturesSection = dynamic(() => import('@/components/FeaturesSection'), {
  ssr: false,
  loading: () => null,
});

const CTASection = dynamic(() => import('@/components/CTASection'), {
  ssr: false,
  loading: () => null,
});

// ✅ Hero wrapper
function HeroSection() {
  return (
    <section className="relative min-h-screen overflow-hidden">
      <Hero
        headline={{
          line1: 'AI-Powered',
          line2: 'Red Team Testing',
        }}
        subtitle="CognitoForge simulates intelligent adversarial attacks on your code and CI/CD pipelines."
        buttons={{
          primary: {
            text: 'Get Started Free',
            onClick: () => (window.location.href = '/demo'),
          },
          secondary: {
            text: 'Learn More',
            onClick: () => {
              const el = document.getElementById('features');
              el?.scrollIntoView({ behavior: 'smooth' });
            },
          },
        }}
      />
    </section>
  );
}

// ✅ Default export
export default function HomePage() {
  const isDev = process.env.NODE_ENV === 'development';

  return (
    <div className="min-h-screen">
      {/* Disable heavy background in development */}
      {/* {!isDev && <ShaderAnimation />} */}

      {/* Header */}
      <Header />

      {/* Main content */}
      <main>
        <HeroSection />
        <FeaturesSection />
        <CTASection />
      </main>

      {/* Footer */}
      <footer className="py-12 text-sm opacity-70">
        <div className="max-w-6xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-10 text-center md:text-left">
          {/* Column 1 */}
          <div>
            <h3 className="text-base font-semibold mb-4 opacity-100">
              Quick Links
            </h3>
            <ul className="space-y-2">
              <li className="hover:opacity-100 transition cursor-pointer">
                Home
              </li>
              <li className="hover:opacity-100 transition cursor-pointer">
                About Us
              </li>
            </ul>
          </div>

          {/* Column 2 */}
          <div>
            <h3 className="text-base font-semibold mb-4 opacity-100">
              Support
            </h3>
            <ul className="space-y-2">
              <li className="hover:opacity-100 transition cursor-pointer">
                Contact Us
              </li>
              <li className="hover:opacity-100 transition cursor-pointer">
                Privacy Policy
              </li>
              <li className="hover:opacity-100 transition cursor-pointer">
                Terms and Conditions
              </li>
            </ul>
          </div>

          {/* Column 3 */}
          <div>
            <h3 className="text-base font-semibold mb-4 opacity-100">
              Contact Us
            </h3>
            <ul className="space-y-2">
              <li>PH.NO : 91-9652274756</li>
              <li>Email : threatforge@gmail.com</li>
              <li>Location : Hyderabad, Telangana</li>
            </ul>
          </div>
        </div>

        {/* Bottom Copyright */}
        <div className="mt-10 text-center text-sm opacity-70">
          © 2025 CognitoForge. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
