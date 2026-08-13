import React from 'react';
import type { Tab } from '../App';
import { DocumentTextIcon } from './icons/DocumentTextIcon';

/**
 * Props for the Navbar component.
 */
interface NavbarProps {
  /** The currently active tab. */
  activeTab: Tab;
  /** Function to set the active tab. */
  setActiveTab: (tab: Tab) => void;
}

/**
 * Renders the top navigation bar for the application.
 * It displays the app title and navigation buttons to switch between tabs.
 */
const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  /**
   * Generates Tailwind CSS classes for a navigation link based on whether it's active.
   * @param tabName The name of the tab to generate classes for.
   * @returns A string of CSS classes.
   */
  const navLinkClasses = (tabName: Tab) =>
    `px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-950 focus:ring-cyan-500 ${
      activeTab === tabName
        ? 'bg-cyan-400/10 text-cyan-400' // Active tab style
        : 'text-gray-400 hover:bg-gray-800/60 hover:text-gray-100' // Inactive tab style
    }`;
  
  return (
    <nav className="bg-gray-950/70 backdrop-blur-lg fixed top-0 left-0 right-0 z-10 border-b border-gray-800">
      <div className="w-full max-w-4xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* App Logo and Title */}
          <div className="flex items-center gap-3">
             <DocumentTextIcon className="w-8 h-8 text-cyan-400"/>
             <span className="hidden sm:inline text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-teal-400">
                Doc Summarizer
             </span>
          </div>
          {/* Navigation Links */}
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setActiveTab('summarizer')}
              className={navLinkClasses('summarizer')}
            >
              Summarizer
            </button>
            <button
              onClick={() => setActiveTab('chatbot')}
              className={navLinkClasses('chatbot')}
            >
              Chatbot
            </button>
             <button
              onClick={() => setActiveTab('about')}
              className={navLinkClasses('about')}
            >
              About
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;