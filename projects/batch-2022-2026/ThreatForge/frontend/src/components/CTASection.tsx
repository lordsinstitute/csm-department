'use client';

import Link from 'next/link';
import { Shield } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function CTASection() {
  return (
    <section className="py-24 bg-black text-center">
      <h2 className="text-4xl font-bold mb-6">
        Ready to Secure Your Code?
      </h2>
      <p className="text-xl mb-8 text-[#614334]">

        Join thousands of developers who trust CognitoForge
      </p>

      <Link href="/demo">
        <Button size="lg" variant="purple">
          <Shield className="mr-2 h-5 w-5" />
          Get Started Free
        </Button>
      </Link>
    </section>
  );
}
