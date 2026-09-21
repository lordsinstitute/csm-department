import React, { useState } from 'react';
import Summarizer from './components/Summarizer';
import Chatbot from './components/Chatbot';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import About from './components/About';

/**
 * Defines the possible tabs for navigation within the app.
 */
export type Tab = 'summarizer' | 'chatbot' | 'about';

/**
 * The root component of the application.
 * It manages the active tab state and renders the corresponding component.
 */
const App: React.FC = () => {
  // State to track the currently active tab. Defaults to 'summarizer'.
  const [activeTab, setActiveTab] = useState<Tab>('summarizer');
  
  /**
   * Renders the component corresponding to the active tab.
   * @returns The React component for the active tab.
   */
  const renderActiveTab = () => {
    switch (activeTab) {
      case 'summarizer':
        return <Summarizer />;
      case 'chatbot':
        return <Chatbot />;
      case 'about':
        return <About />;
      default:
        return <Summarizer />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation bar, receives active tab state and a function to update it */}
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
      />
      
      {/* Main content area */}
      <div className="flex-grow pt-20 pb-6 sm:pb-8"> {/* Adjusted padding for fixed navbar */}
        <div className="w-full max-w-4xl mx-auto px-2 sm:px-4">
          <main className="bg-gray-900/60 backdrop-blur-md border border-gray-800/50 rounded-lg shadow-2xl overflow-hidden">
            {/* Render the active tab's component */}
            {renderActiveTab()}
          </main>
        </div>
      </div>

      {/* Application footer */}
      <Footer />
    </div>
  );
};

export default App;