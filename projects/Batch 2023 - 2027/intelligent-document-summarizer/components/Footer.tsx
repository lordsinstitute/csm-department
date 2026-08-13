import React from 'react';
import { GitHubIcon } from './icons/GitHubIcon';

/**
 * Renders the application footer.
 * It includes copyright information and a link to the GitHub repository.
 */
const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="w-full border-t border-gray-800 bg-gray-950/70 backdrop-blur-lg text-gray-400 text-sm">
      <div className="max-w-4xl mx-auto px-4 py-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="text-center sm:text-left">
          <p>&copy; {currentYear} Intelligent Document Summarizer.</p>
          <p>For educational use only.</p>
        </div>
        <div className="flex-shrink-0">
          <a
            href="https://github.com/syednawazali01"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-gray-400 hover:text-cyan-400 transition-colors"
            aria-label="View source code on GitHub"
          >
            <GitHubIcon className="w-5 h-5" />
            <span>View on GitHub</span>
          </a>
        </div>
      </div>
    </footer>
  );
};

export default Footer;