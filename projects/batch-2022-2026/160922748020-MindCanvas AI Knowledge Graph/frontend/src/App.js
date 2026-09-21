// src/App.js - Fixed layout with proper chatbot integration
import React, { useState, useEffect, useCallback, Component } from 'react';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { useKnowledgeStore } from './store/knowledgeStore';
import { useKeyboardShortcuts } from './hooks/useKeyboardShortcuts';
import { useGraphAnalytics } from './hooks/useGraphAnalytics';

// Import all the components
import KnowledgeGraphViewer from './components/KnowledgeGraphViewer';
import ChatbotPanel from './components/ChatbotPanel';
import ControlPanel from './components/ControlPanel';
import NodeDetailsModal from './components/NodeDetailsModal';
import SearchOverlay from './components/SearchOverlay';
import SettingsPanel from './components/SettingsPanel';
import LeftSidebar from './components/LeftSidebar';
import PerformanceMonitor from './components/PerformanceMonitor';

class ModalErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { hasError: false }; }
  static getDerivedStateFromError() { return { hasError: true }; }
  componentDidCatch(err) { console.error('Modal render error:', err); }
  render() {
    if (this.state.hasError) return null;
    return this.props.children;
  }
}

// Professional dark theme
const theme = {
  colors: {
    primary: '#6366f1',
    secondary: '#8b5cf6',
    accent: '#06b6d4',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    bg: 'linear-gradient(160deg, #0b0b18 0%, #0e0e1e 55%, #101024 100%)',
    surface: 'rgba(255, 255, 255, 0.04)',
    surfaceHover: 'rgba(255, 255, 255, 0.08)',
    text: '#e2e8f0',
    textSecondary: 'rgba(226, 232, 240, 0.5)',
    border: 'rgba(255, 255, 255, 0.07)',
  },
  spacing: {
    xs: '4px',
    sm: '8px',
    md: '16px',
    lg: '24px',
    xl: '32px',
    xxl: '48px'
  },
  borderRadius: {
    sm: '6px',
    md: '10px',
    lg: '14px',
    xl: '20px'
  },
  shadows: {
    sm: '0 2px 12px rgba(0, 0, 0, 0.25)',
    md: '0 8px 30px rgba(0, 0, 0, 0.35)',
    lg: '0 20px 60px rgba(0, 0, 0, 0.45)',
  },
  animations: {
    fast: '0.15s ease',
    normal: '0.3s ease',
    slow: '0.5s ease'
  },
  fonts: {
    primary: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif"
  }
};

const GlobalStyle = createGlobalStyle`
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  html, body {
    height: 100%;
    width: 100%;
    font-family: ${props => props.theme.fonts.primary};
    background: ${props => props.theme.colors.bg};
    color: ${props => props.theme.colors.text};
    overflow: hidden;
  }

  #root {
    height: 100%;
    width: 100%;
    display: flex;
    flex-direction: column;
  }

  ::-webkit-scrollbar {
    width: 5px;
  }

  ::-webkit-scrollbar-track {
    background: transparent;
  }

  ::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 10px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.25);
  }
`;

const AppContainer = styled.div`
  height: 100vh;
  width: 100vw;
  display: grid;
  grid-template-areas: "left-panel main-graph right-panel";
  grid-template-columns: 272px 1fr 308px;
  grid-template-rows: 1fr;
  gap: 10px;
  padding: 10px;
  overflow: hidden;

  @media (max-width: 1400px) {
    grid-template-columns: 252px 1fr 288px;
  }

  @media (max-width: 1100px) {
    grid-template-areas:
      "main-graph"
      "left-panel"
      "right-panel";
    grid-template-columns: 1fr;
    grid-template-rows: 55vh auto auto;
    height: auto;
    overflow-y: auto;
  }
`;

const MainGraphArea = styled(motion.div)`
  grid-area: main-graph;
  background: rgba(255, 255, 255, 0.03);
  border-radius: ${props => props.theme.borderRadius.lg};
  backdrop-filter: blur(20px);
  border: 1px solid ${props => props.theme.colors.border};
  overflow: hidden;
  box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.05), ${props => props.theme.shadows.lg};
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 0;

  @media (max-width: 1100px) {
    min-height: 50vh;
  }
`;

const SidePanel = styled(motion.div)`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.sm};
  overflow-y: auto;
  overflow-x: hidden;
  min-height: 0;

  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 4px;
  }

  &::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.25);
  }

  @media (max-width: 1100px) {
    overflow-y: visible;
  }
`;

const ChatbotArea = styled(motion.div)`
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  width: 100%;
  height: 100%;
`;


const ControlsPanel = styled(motion.div)`
  position: absolute;
  top: ${props => props.theme.spacing.lg};
  left: ${props => props.theme.spacing.lg};
  z-index: 1000;
`;

const LoadingOverlay = styled(motion.div)`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  color: white;
  
  .loader {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-top: 3px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: ${props => props.theme.spacing.lg};
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const EmptyGraphState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: ${props => props.theme.colors.textSecondary};
  padding: ${props => props.theme.spacing.xl};
  
  .icon {
    font-size: 4rem;
    margin-bottom: ${props => props.theme.spacing.lg};
    opacity: 0.6;
  }
  
  .title {
    font-size: 1.5rem;
    margin-bottom: ${props => props.theme.spacing.md};
    color: ${props => props.theme.colors.text};
  }
  
  .description {
    max-width: 400px;
    line-height: 1.6;
    margin-bottom: ${props => props.theme.spacing.lg};
  }
`;

const Button = styled(motion.button)`
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  border: none;
  color: white;
  padding: ${props => props.theme.spacing.md} ${props => props.theme.spacing.lg};
  border-radius: ${props => props.theme.borderRadius.md};
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${props => props.theme.shadows.md};
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const StatusBanner = styled(motion.div)`
  position: absolute;
  top: 18px;
  right: 18px;
  background: ${props => props.$connected ?
    'rgba(16, 185, 129, 0.12)' :
    'rgba(239, 68, 68, 0.12)'};
  color: ${props => props.$connected ? '#10b981' : '#ef4444'};
  border: 1px solid ${props => props.$connected ?
    'rgba(16, 185, 129, 0.25)' :
    'rgba(239, 68, 68, 0.25)'};
  padding: 5px 12px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 600;
  z-index: 1001;
  display: flex;
  align-items: center;
  gap: 6px;
  backdrop-filter: blur(12px);
  letter-spacing: 0.1px;

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
    animation: ${props => props.$connected ? 'pulse 2s infinite' : 'none'};
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }
`;

const ErrorToast = styled(motion.div)`
  position: fixed;
  bottom: 20px;
  left: 20px;
  background: rgba(239, 68, 68, 0.95);
  color: white;
  padding: 16px 20px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  z-index: 10000;
  max-width: 400px;
  
  .error-title {
    font-weight: 600;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .error-message {
    font-size: 0.9rem;
    opacity: 0.9;
    line-height: 1.4;
  }
  
  .error-dismiss {
    position: absolute;
    top: 8px;
    right: 8px;
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    font-size: 18px;
    opacity: 0.7;
    
    &:hover {
      opacity: 1;
    }
  }
`;


const App = () => {
  // UI State
  const [backendConnected, setBackendConnected] = useState(false);
  const [showPerformanceMonitor, setShowPerformanceMonitor] = useState(false);
  const [showSearchOverlay, setShowSearchOverlay] = useState(false);
  const [showSettingsPanel, setShowSettingsPanel] = useState(false);
  const [currentLayout, setCurrentLayout] = useState('fcose');
  const [selectedNodeDetails, setSelectedNodeDetails] = useState(null);

  // Store State
  const {
    graphData,
    isLoading,
    error,
    selectedNode,
    stats,
    trending,
    recommendations,
    refreshAllData,
    setLoading,
    setSelectedNode,
    checkBackendHealth,
    clearError,
    performSemanticSearch,
    loadStats,
    loadContent,
    loadTrending,
    loadRecommendations
  } = useKnowledgeStore();

  const analytics = useGraphAnalytics();

  // Keyboard shortcuts
  useKeyboardShortcuts([
    {
      keys: 'ctrl+k',
      action: () => setShowSearchOverlay(true)
    },
    {
      keys: 'ctrl+r',
      action: (e) => {
        e.preventDefault();
        handleRefresh();
      }
    },
    {
      keys: 'ctrl+shift+p',
      action: () => setShowPerformanceMonitor(!showPerformanceMonitor)
    },
    {
      keys: 'ctrl+comma',
      action: () => setShowSettingsPanel(true)
    },
    {
      keys: 'escape',
      action: () => {
        setShowSearchOverlay(false);
        setShowSettingsPanel(false);
        setSelectedNodeDetails(null);
        setSelectedNode(null);
      }
    }
  ]);

  // Initialize app - check backend and load data
  useEffect(() => {
    const initializeApp = async () => {
      console.log('🚀 Initializing MindCanvas App...');

      try {
        // Check backend health first
        const isHealthy = await checkBackendHealth();
        setBackendConnected(isHealthy);

        if (isHealthy) {
          console.log('✅ Backend is healthy, loading all data...');

          // refreshAllData already calls all sub-loaders internally
          await refreshAllData();

          console.log('✅ App initialization complete');
        } else {
          console.log('❌ Backend is not available');
        }
      } catch (error) {
        console.error('❌ App initialization failed:', error);
        setBackendConnected(false);
      }
    };

    initializeApp();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // run once on mount — store functions are stable Zustand references

  // Periodic health check
  useEffect(() => {
    const healthCheckInterval = setInterval(async () => {
      try {
        const isHealthy = await checkBackendHealth();
        setBackendConnected(isHealthy);
      } catch (error) {
        setBackendConnected(false);
      }
    }, 30000); // Check every 30 seconds

    return () => clearInterval(healthCheckInterval);
  }, [checkBackendHealth]);

  // Auto-dismiss error messages
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        clearError();
      }, 10000); // Auto-dismiss after 10 seconds

      return () => clearTimeout(timer);
    }
  }, [error, clearError]);

  // Handle refresh
  const handleRefresh = useCallback(async () => {
    try {
      setLoading(true);
      await Promise.allSettled([
        refreshAllData(),
        loadStats(),
        loadContent(),
        loadTrending(),
        loadRecommendations()
      ]);
      console.log('🔄 Data refreshed successfully');
    } catch (error) {
      console.error('🔄 Refresh failed:', error);
    }
  }, [refreshAllData, loadStats, loadContent, loadTrending, loadRecommendations, setLoading]);

  // Handle node selection
  const handleNodeSelect = useCallback((node) => {
    console.log('📌 Node selected:', node);
    setSelectedNode(node);
    setSelectedNodeDetails(node);
  }, [setSelectedNode]);

  // Handle background click
  const handleBackgroundClick = useCallback(() => {
    setSelectedNode(null);
    setSelectedNodeDetails(null);
  }, [setSelectedNode]);

  // Handle layout change
  const handleLayoutChange = useCallback((layout) => {
    console.log('🎯 Layout changed to:', layout);
    setCurrentLayout(layout);
  }, []);

  // Handle search
  const handleSearch = useCallback(async (query) => {
    try {
      console.log('🔍 Performing search:', query);
      await performSemanticSearch(query, 20);
      setShowSearchOverlay(false);
    } catch (error) {
      console.error('🔍 Search failed:', error);
    }
  }, [performSemanticSearch]);

  // Handle export history (Chrome extension feature)
  const handleExportHistory = () => {
    // Check if running in extension context
    if (typeof window !== 'undefined' && window.chrome && window.chrome.runtime) {
      // Extension context
      window.chrome.runtime.sendMessage({ action: 'exportHistory' });
    } else {
      // Web context - show instruction
      alert('📱 To export your browsing history:\n\n1. Install the MindCanvas Chrome extension\n2. Click the extension icon\n3. Click "Export History"\n\nThe extension will send your data to this application.');
    }
  };

  // Check if we have graph data
  const hasGraphData = graphData && graphData.nodes && graphData.nodes.length > 0;

  // Prepare stats for panels
  const overviewStats = {
    totalContent: stats.total_content || 0,
    vectorEnabled: stats.vector_enabled || 0,
    avgQuality: stats.avg_quality || 0,
    clusters: stats.content_clusters || 0
  };

  const contentTypeData = stats.by_content_type || {};
  const trendingData = trending || [];
  const recommendationsData = recommendations || [];

  return (
    <ThemeProvider theme={theme}>
      <GlobalStyle />
      <AppContainer>
        {/* Left Panel - Unified Sidebar */}
        <SidePanel
          initial={{ x: -300, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          style={{ gridArea: 'left-panel' }}
        >
          <LeftSidebar
            stats={stats}
            trending={trendingData}
            recommendations={recommendationsData}
          />
        </SidePanel>

        {/* Main Graph Area */}
        <MainGraphArea
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          {/* Status indicator — top-right of graph, away from chat panel */}
          <StatusBanner
            $connected={backendConnected}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.4, delay: 0.3 }}
          >
            <div className="status-dot" />
            {backendConnected ? 'Connected' : 'Offline'}
          </StatusBanner>

          {/* Controls */}
          <ControlsPanel>
            <ControlPanel
              onSearch={() => setShowSearchOverlay(true)}
              onRefresh={handleRefresh}
              onLayoutChange={handleLayoutChange}
              currentLayout={currentLayout}
              isRefreshing={isLoading}
            />
          </ControlsPanel>

          {/* Graph Visualization */}
          {hasGraphData ? (
            <KnowledgeGraphViewer
              data={graphData}
              selectedNode={selectedNode}
              onNodeSelect={handleNodeSelect}
              onBackgroundClick={handleBackgroundClick}
              layout={currentLayout}
            />
          ) : (
            <EmptyGraphState>
              <div className="icon">🕸️</div>
              <div className="title">
                {backendConnected ? 'Knowledge Graph Ready' : 'Backend Offline'}
              </div>
              <div className="description">
                {backendConnected ? (
                  graphData.nodes?.length === 0 ? (
                    "Your knowledge graph is ready! Use the Chrome extension to export your browsing history and start building your personal knowledge network."
                  ) : (
                    `Displaying ${graphData.nodes?.length} knowledge nodes with ${graphData.links?.length} connections.`
                  )
                ) : (
                  "Please start the backend server to begin using MindCanvas. Check the README for setup instructions."
                )}
              </div>

              {backendConnected && (!graphData.nodes || graphData.nodes.length === 0) && (
                <Button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleExportHistory}
                >
                  📱 Use Chrome Extension
                </Button>
              )}
            </EmptyGraphState>
          )}

          {/* Performance Monitor */}
          <PerformanceMonitor
            isVisible={showPerformanceMonitor}
            nodeCount={analytics.nodeCount}
            edgeCount={analytics.edgeCount}
            placement="graph"
          />

          {/* Loading Overlay */}
          <AnimatePresence>
            {isLoading && (
              <LoadingOverlay
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <div className="loader" />
                <div>Loading your knowledge graph...</div>
              </LoadingOverlay>
            )}
          </AnimatePresence>
        </MainGraphArea>

        {/* Right Panel - Chat */}
        <SidePanel
          initial={{ x: 300, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          style={{ gridArea: 'right-panel' }}
        >
          <ChatbotArea
            initial={{ y: 50, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.45 }}
          >
            <ChatbotPanel graphData={graphData} />
          </ChatbotArea>
        </SidePanel>

        {/* Modals and Overlays */}
        <AnimatePresence>
          {showSearchOverlay && (
            <SearchOverlay
              onClose={() => setShowSearchOverlay(false)}
              onSearch={handleSearch}
              graphData={graphData}
            />
          )}
        </AnimatePresence>

        <AnimatePresence>
          {showSettingsPanel && (
            <SettingsPanel
              isOpen={showSettingsPanel}
              onClose={() => setShowSettingsPanel(false)}
            />
          )}
        </AnimatePresence>

        <ModalErrorBoundary>
          <AnimatePresence>
            {selectedNodeDetails && (
              <NodeDetailsModal
                node={selectedNodeDetails}
                onClose={() => {
                  setSelectedNodeDetails(null);
                  setSelectedNode(null);
                }}
                graphData={graphData}
              />
            )}
          </AnimatePresence>
        </ModalErrorBoundary>

        {/* Error Display */}
        <AnimatePresence>
          {error && (
            <ErrorToast
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 50 }}
            >
              <button
                className="error-dismiss"
                onClick={clearError}
                aria-label="Dismiss error"
              >
                ×
              </button>
              <div className="error-title">
                ⚠️ Error
              </div>
              <div className="error-message">{error}</div>
            </ErrorToast>
          )}
        </AnimatePresence>
      </AppContainer>
    </ThemeProvider>
  );
};

export default App;
