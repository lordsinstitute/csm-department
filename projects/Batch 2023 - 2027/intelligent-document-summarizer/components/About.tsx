import React from 'react';
import { GitHubIcon } from './icons/GitHubIcon';

/**
 * A reusable component for creating a titled section with content.
 */
const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div className="mb-8">
    <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-teal-400 mb-4 pb-2 border-b-2 border-gray-700">
      {title}
    </h2>
    <div className="text-gray-300 space-y-4">{children}</div>
  </div>
);

/**
 * A reusable accordion-style component for FAQ items.
 */
const FaqItem: React.FC<{ question: string; children: React.ReactNode }> = ({ question, children }) => (
    <details className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 cursor-pointer group transition-all duration-300 hover:border-cyan-500/50">
        <summary className="font-semibold text-gray-200 list-none flex justify-between items-center">
            {question}
            <span className="transform transition-transform duration-300 group-open:rotate-180">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
            </span>
        </summary>
        <div className="mt-3 pt-3 border-t border-gray-700 text-gray-400 text-sm">
            {children}
        </div>
    </details>
);

/**
 * The About page component.
 * It provides information about the application, its features, technology, and FAQs.
 */
const About: React.FC = () => {
  return (
    <div className="p-6 md:p-8 text-gray-300">
      <h1 className="text-4xl font-extrabold text-center mb-8 text-white">
        About Intelligent Document Summarizer
      </h1>
      
      <Section title="Purpose">
        <p>
          This tool is designed to provide intelligent and accurate summaries of complex legal and financial documents. Leveraging the power of Google's Gemini API, it helps users quickly grasp core information, saving time and effort in document analysis.
        </p>
      </Section>

      <Section title="Features">
        <ul className="list-disc list-inside space-y-2">
            <li><strong>Dual-Mode Summarization:</strong> Generate both extractive (direct quotes) and abstractive (rephrased) summaries.</li>
            <li><strong>Key Point Extraction:</strong> Quickly identify the most crucial takeaways in a bolded, bulleted list.</li>
            <li><strong>Multi-Format Support:</strong> Upload <strong>.txt</strong>, <strong>.pdf</strong>, <strong>.jpg</strong>, and <strong>.png</strong> files for analysis.</li>
            <li><strong>Interactive Chatbot:</strong> Ask follow-up questions and get instant clarification on the document's content.</li>
            <li><strong>Secure & Private:</strong> Your data is processed securely and is never used to train AI models.</li>
            <li><strong>Export Options:</strong> Download your generated summaries as a .txt or .pdf file.</li>
        </ul>
      </Section>
      
      <Section title="Technology Stack">
         <ul className="list-disc list-inside space-y-2">
            <li><strong>Frontend:</strong> Built with React, TypeScript, and styled with Tailwind CSS for a modern, responsive user experience.</li>
            <li><strong>AI Engine:</strong> Powered by the <strong>Google Gemini API</strong> for state-of-the-art text extraction, summarization, and chat capabilities.</li>
        </ul>
      </Section>

      <Section title="Frequently Asked Questions (FAQ)">
        <div className="space-y-4">
            <FaqItem question="How is my data handled?">
                <p>We prioritize your privacy. Documents are sent directly to Google's Generative AI for processing and are not stored on our servers. All communications are encrypted, and your data is not used to train AI models, as per Google's privacy policy.</p>
            </FaqItem>
            <FaqItem question="What file types can I upload?">
                <p>The summarizer supports plain text (.txt), PDF documents (.pdf), and images (.jpg, .jpeg, .png). For images, Optical Character Recognition (OCR) is used to extract the text before summarization.</p>
            </FaqItem>
            <FaqItem question="Is this a substitute for professional legal or financial advice?">
                <p><strong>No.</strong> This tool is provided for educational and informational purposes only. The summaries are AI-generated and may not capture every nuance. It should not be considered a substitute for advice from a qualified professional.</p>
            </FaqItem>
        </div>
      </Section>

      <Section title="Contact & Contribution">
        <p>
          Have questions, feedback, or want to contribute? This project is open-source! Feel free to raise an issue, submit a pull request, or just check out the code on GitHub.
        </p>
         <div className="mt-4">
          <a
            href="https://github.com/syednawazali01"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-gray-300 bg-gray-800 hover:bg-gray-700 hover:text-cyan-400 transition-colors px-4 py-2 rounded-lg"
            aria-label="View source code on GitHub"
          >
            <GitHubIcon className="w-5 h-5" />
            <span>syednawazali01</span>
          </a>
        </div>
      </Section>
    </div>
  );
};

export default About;