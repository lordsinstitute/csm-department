'use client';

import { motion } from 'framer-motion';
import { Shield, Database, Target, GitBranch } from 'lucide-react';

export default function FeaturesSection() {
  const features = [
    {
      icon: Target,
      title: "AI-Driven Attack Simulation",
      description: "Advanced machine learning models simulate real-world attack patterns."
    },
    {
      icon: GitBranch,
      title: "CI/CD Pipeline Security",
      description: "Analyze deployment pipelines before they reach production."
    },
    {
      icon: Shield,
      title: "Proactive Threat Detection",
      description: "Predictive analysis and early warning systems."
    },
    {
      icon: Database,
      title: "Detailed Reporting",
      description: "Actionable insights with attack paths and remediation steps."
    }
  ];

  return (
    <section
  id="features"
  className="py-24 bg-gradient-to-b from-[#1A120D] via-[#24160F] to-[#1A120D]"
>

      <div className="container mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl md:text-5xl font-bold text-white">
            Why Choose <span className="gradient-text">CognitoForge</span>?
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((f) => (
            <div
              key={f.title}
              className="
                p-6 rounded-xl
                bg-[#2C1D15]/80
                border border-[#C89B5A]/50
                hover:bg-[#3A261B]/90
                transition-all duration-300
                hover:shadow-lg hover:shadow-[#C89B5A]/20
              "
            >
              <f.icon className="h-12 w-12 text-[#C89B5A] mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">
                {f.title}
              </h3>
              <p className="text-[#E8D6C0]">
                {f.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

