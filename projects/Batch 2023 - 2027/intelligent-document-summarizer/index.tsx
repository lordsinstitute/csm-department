/**
 * Main entry point for the React application.
 * This file handles the rendering of the root App component into the DOM.
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Find the root DOM element
const rootElement = document.getElementById('root');
if (!rootElement) {
  throw new Error("Could not find root element to mount to");
}

// Create a React root and render the App component
const root = ReactDOM.createRoot(rootElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);