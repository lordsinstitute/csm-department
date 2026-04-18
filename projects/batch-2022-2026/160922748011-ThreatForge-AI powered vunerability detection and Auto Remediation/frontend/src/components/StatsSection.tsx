'use client';

import { motion } from 'framer-motion';
import { AlertTriangle, TrendingUp, Shield, Target } from 'lucide-react';

export default function StatsSection() {
  const stats = [
    { label: "Vulnerabilities Detected", value: "10,000+", icon: AlertTriangle },
    { label: "Security Analyses", value: "5,000+", icon: TrendingUp },
    { label: "Active Users", value: "1,200+", icon: Shield },
    { label: "Attack Patterns", value: "500+", icon: Target }
  ];

  return (
    <section className="py-16 bg-[#CBAD9C] border-y border-purple-500/20">
      <div className="container mx-auto grid grid-cols-2 lg:grid-cols-4 gap-8">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: i * 0.1 }}
            className="text-center"
          >
            <s.icon className="h-8 w-8 mx-auto mb-2 text-primary" />
            <div className="text-3xl font-bold">{s.value}</div>
            <div className="text-sm text-muted-foreground">{s.label}</div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
