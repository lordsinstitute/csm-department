// src/components/SettingsPanel.js
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { useKnowledgeStore } from '../store/knowledgeStore';
import { ThemeUtils } from '../utils/themeUtils';

/* ── Backdrop ──────────────────────────────────────────────────── */
const Backdrop = styled(motion.div)`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(14px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
`;

/* ── Modal shell ───────────────────────────────────────────────── */
const Modal = styled(motion.div)`
  width: 100%;
  max-width: 980px;
  max-height: 90vh;
  background: linear-gradient(160deg, rgba(10,10,22,0.99) 0%, rgba(13,13,26,0.99) 100%);
  border: 1px solid rgba(99, 102, 241, 0.18);
  border-radius: 18px;
  box-shadow: 0 32px 80px rgba(0,0,0,0.65), 0 0 0 1px rgba(255,255,255,0.04);
  overflow: hidden;
  display: grid;
  grid-template-columns: 240px 1fr;
`;

/* ── Sidebar ───────────────────────────────────────────────────── */
const Sidebar = styled.div`
  background: rgba(255, 255, 255, 0.025);
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const SideTop = styled.div`
  padding: 0 0 2px;
`;

const SideAccent = styled.div`
  height: 2px;
  background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4);
`;

const SideBrand = styled.div`
  padding: 18px 18px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  gap: 10px;
`;

const BrandIcon = styled.div`
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  box-shadow: 0 2px 10px rgba(99,102,241,0.35);
  flex-shrink: 0;
`;

const BrandText = styled.div`
  .name {
    font-size: 0.88rem;
    font-weight: 700;
    background: linear-gradient(135deg, #a5b4fc, #818cf8, #c4b5fd);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .sub {
    font-size: 0.62rem;
    color: rgba(165,180,252,0.4);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.8px;
  }
`;

const TabNav = styled.nav`
  padding: 10px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
`;

const Tab = styled(motion.button)`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid ${p => p.$active ? 'rgba(99,102,241,0.3)' : 'transparent'};
  background: ${p => p.$active ? 'rgba(99,102,241,0.15)' : 'transparent'};
  color: ${p => p.$active ? '#a5b4fc' : 'rgba(226,232,240,0.5)'};
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: ${p => p.$active ? '600' : '500'};
  text-align: left;
  width: 100%;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
  position: relative;

  &:hover {
    background: ${p => p.$active ? 'rgba(99,102,241,0.15)' : 'rgba(255,255,255,0.05)'};
    color: ${p => p.$active ? '#a5b4fc' : 'rgba(226,232,240,0.75)'};
  }

  .tab-icon { font-size: 1rem; width: 20px; text-align: center; flex-shrink: 0; }
`;

const ActiveIndicator = styled(motion.div)`
  position: absolute;
  left: 0;
  top: 4px;
  bottom: 4px;
  width: 2px;
  background: linear-gradient(180deg, #6366f1, #8b5cf6);
  border-radius: 0 2px 2px 0;
`;

/* ── Content area ──────────────────────────────────────────────── */
const Content = styled.div`
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const ContentHead = styled.div`
  padding: 0;
`;

const ContentAccent = styled.div`
  height: 2px;
  background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4);
`;

const ContentHeadRow = styled.div`
  padding: 18px 24px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(99,102,241,0.03);
`;

const ContentTitle = styled.h2`
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #e2e8f0;
  letter-spacing: -0.2px;
`;

const CloseBtn = styled(motion.button)`
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  color: rgba(226,232,240,0.55);
  width: 34px;
  height: 34px;
  border-radius: 9px;
  cursor: pointer;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.18s, color 0.18s;

  &:hover { background: rgba(255,255,255,0.1); color: #e2e8f0; }
`;

const ContentScroll = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 22px 24px;
  scrollbar-width: thin;
  scrollbar-color: rgba(99,102,241,0.3) transparent;
  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 2px; }
`;

/* ── Section ───────────────────────────────────────────────────── */
const Section = styled.div`
  margin-bottom: 24px;
`;

const SecLabel = styled.div`
  font-size: 0.67rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: rgba(165, 180, 252, 0.45);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;

  &::before {
    content: '';
    display: block;
    width: 16px;
    height: 2px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    border-radius: 1px;
  }
`;

/* ── Setting item ──────────────────────────────────────────────── */
const SettingRow = styled.div`
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 12px;
  padding: 14px 16px;
  margin-bottom: 8px;

  &:last-child { margin-bottom: 0; }
`;

const RowTop = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${p => p.$mb || '0'};
`;

const RowLabel = styled.label`
  font-size: 0.88rem;
  font-weight: 600;
  color: #e2e8f0;
  cursor: ${p => p.$clickable ? 'pointer' : 'default'};
`;

const RowDesc = styled.p`
  margin: 5px 0 0;
  font-size: 0.78rem;
  color: rgba(226,232,240,0.38);
  line-height: 1.4;
`;

/* ── Toggle switch ─────────────────────────────────────────────── */
const Toggle = styled(motion.div)`
  width: 44px;
  height: 24px;
  border-radius: 12px;
  background: ${p => p.$on
    ? 'linear-gradient(135deg, #6366f1, #8b5cf6)'
    : 'rgba(255,255,255,0.12)'};
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 2px;
  flex-shrink: 0;
  transition: background 0.22s;

  .thumb {
    width: 20px;
    height: 20px;
    background: white;
    border-radius: 50%;
    transform: translateX(${p => p.$on ? '20px' : '0px'});
    transition: transform 0.22s cubic-bezier(0.34,1.56,0.64,1);
    box-shadow: 0 1px 4px rgba(0,0,0,0.3);
  }
`;

/* ── Slider ────────────────────────────────────────────────────── */
const Slider = styled.input`
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: rgba(255,255,255,0.12);
  outline: none;
  margin-top: 10px;
  accent-color: #6366f1;

  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(99,102,241,0.4);
  }

  &::-moz-range-thumb {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    cursor: pointer;
    border: none;
    box-shadow: 0 2px 8px rgba(99,102,241,0.4);
  }
`;

/* ── Select ────────────────────────────────────────────────────── */
const Select = styled.select`
  width: 100%;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 9px;
  padding: 9px 12px;
  color: #e2e8f0;
  font-size: 0.85rem;
  font-family: inherit;
  margin-top: 10px;
  cursor: pointer;
  transition: border-color 0.18s;

  &:focus {
    outline: none;
    border-color: rgba(99,102,241,0.5);
  }

  option { background: #0d0d1a; color: #e2e8f0; }
`;

/* ── Color picker ──────────────────────────────────────────────── */
const ColorGrid = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
`;

const ColorDot = styled(motion.div)`
  width: 34px;
  height: 34px;
  border-radius: 9px;
  background: ${p => p.$color};
  cursor: pointer;
  border: 2.5px solid ${p => p.$active ? 'white' : 'transparent'};
  box-shadow: ${p => p.$active ? `0 0 0 1px ${p.$color}` : 'none'};
  transition: transform 0.15s, border-color 0.15s;

  &:hover { transform: scale(1.12); }
`;

/* ── Footer button group ───────────────────────────────────────── */
const Footer = styled.div`
  padding: 16px 24px;
  border-top: 1px solid rgba(255,255,255,0.06);
  background: rgba(0,0,0,0.15);
  display: flex;
  gap: 8px;
  flex-shrink: 0;
`;

const FootBtn = styled(motion.button)`
  padding: 9px 18px;
  border-radius: 10px;
  font-size: 0.84rem;
  font-weight: 600;
  cursor: pointer;
  transition: box-shadow 0.18s, opacity 0.18s;

  &.primary {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border: none;
    color: #fff;
    box-shadow: 0 2px 12px rgba(99,102,241,0.3);
    &:hover { box-shadow: 0 4px 20px rgba(99,102,241,0.45); }
  }

  &.ghost {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    color: rgba(226,232,240,0.65);
    &:hover { background: rgba(255,255,255,0.08); color: #e2e8f0; }
  }
`;

/* ════════════════════════════════════════════════════════════════ */
const DEFAULT_SETTINGS = {
  appearance: { theme: 'dark', primaryColor: '#6366f1', animations: true, fontSize: 14, compactMode: false },
  graph:      { layout: 'fcose', showLabels: true, nodeSize: 'quality', edgeStyle: 'curved', clustering: true, physics: true, performance: 'balanced' },
  search:     { defaultType: 'semantic', autoComplete: true, searchHistory: true, maxResults: 20 },
  privacy:    { analytics: false, errorReporting: true, dataRetention: '30days', shareUsage: false },
  advanced:   { debugMode: false, experimentalFeatures: false, cacheSize: 100, refreshInterval: 30 },
};

const TABS = [
  { id: 'appearance', label: 'Appearance',    icon: '⬡' },
  { id: 'graph',      label: 'Graph',          icon: '⊞' },
  { id: 'search',     label: 'Search & AI',   icon: '⌕' },
  { id: 'privacy',    label: 'Privacy',        icon: '⬡' },
  { id: 'advanced',   label: 'Advanced',       icon: '⚙' },
];

const COLOR_OPTIONS = [
  '#6366f1', '#8b5cf6', '#06b6d4', '#10b981',
  '#f59e0b', '#f97316', '#ef4444', '#ec4899',
  '#3b82f6', '#64748b',
];

/* ════════════════════════════════════════════════════════════════ */
const SettingsPanel = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState('appearance');
  const [settings, setSettings]   = useState(DEFAULT_SETTINGS);

  const { updateGraphSettings } = useKnowledgeStore();

  useEffect(() => {
    const saved = localStorage.getItem('mindcanvas-settings');
    if (saved) {
      try { setSettings(JSON.parse(saved)); }
      catch { /* ignore */ }
    }
  }, []);

  const set = (cat, key, val) =>
    setSettings(prev => ({ ...prev, [cat]: { ...prev[cat], [key]: val } }));

  const save = () => {
    localStorage.setItem('mindcanvas-settings', JSON.stringify(settings));
    updateGraphSettings({
      layout:    settings.graph.layout,
      showLabels: settings.graph.showLabels,
      clustering: settings.graph.clustering,
      physics:    settings.graph.physics,
    });
    document.documentElement.style.setProperty('--primary-color', settings.appearance.primaryColor);
    document.documentElement.style.setProperty('--font-size', `${settings.appearance.fontSize}px`);
    onClose();
  };

  const reset = () => {
    if (window.confirm('Reset all settings to defaults?')) {
      localStorage.removeItem('mindcanvas-settings');
      setSettings(DEFAULT_SETTINGS);
    }
  };

  /* ── Per-tab content ───────────────────────────── */
  const tabContent = {
    appearance: (
      <>
        <Section>
          <SecLabel>Theme & Colours</SecLabel>

          <SettingRow>
            <RowTop $mb="4px"><RowLabel>Primary Colour</RowLabel></RowTop>
            <RowDesc>Main accent colour used throughout the interface</RowDesc>
            <ColorGrid>
              {COLOR_OPTIONS.map(c => (
                <ColorDot
                  key={c}
                  $color={c}
                  $active={settings.appearance.primaryColor === c}
                  whileHover={{ scale: 1.12 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => set('appearance', 'primaryColor', c)}
                />
              ))}
            </ColorGrid>
          </SettingRow>

          <SettingRow>
            <RowTop $mb="4px">
              <RowLabel htmlFor="fontSize">
                Font Size — {settings.appearance.fontSize}px
              </RowLabel>
            </RowTop>
            <RowDesc>Adjust base font size for readability</RowDesc>
            <Slider
              id="fontSize" type="range" min="12" max="18"
              value={settings.appearance.fontSize}
              onChange={e => set('appearance', 'fontSize', +e.target.value)}
            />
          </SettingRow>

          <SettingRow>
            <RowTop>
              <RowLabel $clickable onClick={() => set('appearance', 'animations', !settings.appearance.animations)}>
                Animations
              </RowLabel>
              <Toggle
                $on={settings.appearance.animations}
                onClick={() => set('appearance', 'animations', !settings.appearance.animations)}
              >
                <div className="thumb" />
              </Toggle>
            </RowTop>
            <RowDesc>Enable smooth transitions and motion effects</RowDesc>
          </SettingRow>

          <SettingRow>
            <RowTop>
              <RowLabel $clickable onClick={() => set('appearance', 'compactMode', !settings.appearance.compactMode)}>
                Compact Mode
              </RowLabel>
              <Toggle
                $on={settings.appearance.compactMode}
                onClick={() => set('appearance', 'compactMode', !settings.appearance.compactMode)}
              >
                <div className="thumb" />
              </Toggle>
            </RowTop>
            <RowDesc>Reduce spacing for higher information density</RowDesc>
          </SettingRow>
        </Section>
      </>
    ),

    graph: (
      <>
        <Section>
          <SecLabel>Graph Visualisation</SecLabel>

          <SettingRow>
            <RowTop $mb="4px"><RowLabel>Default Layout</RowLabel></RowTop>
            <RowDesc>Algorithm used for arranging nodes in the graph</RowDesc>
            <Select
              value={settings.graph.layout}
              onChange={e => set('graph', 'layout', e.target.value)}
            >
              <option value="fcose">Force-Directed (fCoSE) — clusters emerge naturally</option>
              <option value="dagre">Hierarchical (Dagre) — top-down knowledge flow</option>
            </Select>
          </SettingRow>

          <SettingRow>
            <RowTop>
              <RowLabel $clickable onClick={() => set('graph', 'showLabels', !settings.graph.showLabels)}>
                Show Node Labels
              </RowLabel>
              <Toggle $on={settings.graph.showLabels} onClick={() => set('graph', 'showLabels', !settings.graph.showLabels)}>
                <div className="thumb" />
              </Toggle>
            </RowTop>
            <RowDesc>Display text labels on graph nodes</RowDesc>
          </SettingRow>

          <SettingRow>
            <RowTop>
              <RowLabel $clickable onClick={() => set('graph', 'clustering', !settings.graph.clustering)}>
                Enable Clustering
              </RowLabel>
              <Toggle $on={settings.graph.clustering} onClick={() => set('graph', 'clustering', !settings.graph.clustering)}>
                <div className="thumb" />
              </Toggle>
            </RowTop>
            <RowDesc>Automatically group related nodes into clusters</RowDesc>
          </SettingRow>

          <SettingRow>
            <RowTop>
              <RowLabel $clickable onClick={() => set('graph', 'physics', !settings.graph.physics)}>
                Physics Simulation
              </RowLabel>
              <Toggle $on={settings.graph.physics} onClick={() => set('graph', 'physics', !settings.graph.physics)}>
                <div className="thumb" />
              </Toggle>
            </RowTop>
            <RowDesc>Enable interactive node movement with physics</RowDesc>
          </SettingRow>

          <SettingRow>
            <RowTop $mb="4px"><RowLabel>Performance Mode</RowLabel></RowTop>
            <RowDesc>Balance visual quality against rendering speed</RowDesc>
            <Select
              value={settings.graph.performance}
              onChange={e => set('graph', 'performance', e.target.value)}
            >
              <option value="quality">High Quality</option>
              <option value="balanced">Balanced</option>
              <option value="performance">High Performance</option>
            </Select>
          </SettingRow>
        </Section>
      </>
    ),

    search: (
      <>
        <Section>
          <SecLabel>Search & AI</SecLabel>

          <SettingRow>
            <RowTop $mb="4px"><RowLabel>Default Search Mode</RowLabel></RowTop>
            <RowDesc>Method used when you open the search overlay</RowDesc>
            <Select
              value={settings.search.defaultType}
              onChange={e => set('search', 'defaultType', e.target.value)}
            >
              <option value="semantic">Semantic — AI-powered concept search</option>
              <option value="text">Text — keyword-based search</option>
              <option value="local">Local — instant offline search</option>
            </Select>
          </SettingRow>

          <SettingRow>
            <RowTop>
              <RowLabel $clickable onClick={() => set('search', 'autoComplete', !settings.search.autoComplete)}>
                Auto-Complete
              </RowLabel>
              <Toggle $on={settings.search.autoComplete} onClick={() => set('search', 'autoComplete', !settings.search.autoComplete)}>
                <div className="thumb" />
              </Toggle>
            </RowTop>
            <RowDesc>Show search suggestions as you type</RowDesc>
          </SettingRow>

          <SettingRow>
            <RowTop>
              <RowLabel $clickable onClick={() => set('search', 'searchHistory', !settings.search.searchHistory)}>
                Search History
              </RowLabel>
              <Toggle $on={settings.search.searchHistory} onClick={() => set('search', 'searchHistory', !settings.search.searchHistory)}>
                <div className="thumb" />
              </Toggle>
            </RowTop>
            <RowDesc>Remember recent searches for quick access</RowDesc>
          </SettingRow>

          <SettingRow>
            <RowTop $mb="4px">
              <RowLabel htmlFor="maxResults">Max Results — {settings.search.maxResults}</RowLabel>
            </RowTop>
            <RowDesc>Maximum number of results displayed per search</RowDesc>
            <Slider
              id="maxResults" type="range" min="10" max="50"
              value={settings.search.maxResults}
              onChange={e => set('search', 'maxResults', +e.target.value)}
            />
          </SettingRow>
        </Section>
      </>
    ),

    privacy: (
      <>
        <Section>
          <SecLabel>Privacy & Data</SecLabel>

          <SettingRow>
            <RowTop>
              <RowLabel $clickable onClick={() => set('privacy', 'analytics', !settings.privacy.analytics)}>
                Usage Analytics
              </RowLabel>
              <Toggle $on={settings.privacy.analytics} onClick={() => set('privacy', 'analytics', !settings.privacy.analytics)}>
                <div className="thumb" />
              </Toggle>
            </RowTop>
            <RowDesc>Share anonymous usage data to help improve MindCanvas</RowDesc>
          </SettingRow>

          <SettingRow>
            <RowTop>
              <RowLabel $clickable onClick={() => set('privacy', 'errorReporting', !settings.privacy.errorReporting)}>
                Error Reporting
              </RowLabel>
              <Toggle $on={settings.privacy.errorReporting} onClick={() => set('privacy', 'errorReporting', !settings.privacy.errorReporting)}>
                <div className="thumb" />
              </Toggle>
            </RowTop>
            <RowDesc>Automatically report errors to help fix bugs faster</RowDesc>
          </SettingRow>

          <SettingRow>
            <RowTop $mb="4px"><RowLabel>Data Retention</RowLabel></RowTop>
            <RowDesc>How long browsing data is kept locally on your device</RowDesc>
            <Select
              value={settings.privacy.dataRetention}
              onChange={e => set('privacy', 'dataRetention', e.target.value)}
            >
              <option value="7days">7 Days</option>
              <option value="30days">30 Days</option>
              <option value="90days">90 Days</option>
              <option value="1year">1 Year</option>
              <option value="forever">Keep Forever</option>
            </Select>
          </SettingRow>
        </Section>
      </>
    ),

    advanced: (
      <>
        <Section>
          <SecLabel>Advanced Settings</SecLabel>

          <SettingRow>
            <RowTop>
              <RowLabel $clickable onClick={() => set('advanced', 'debugMode', !settings.advanced.debugMode)}>
                Debug Mode
              </RowLabel>
              <Toggle $on={settings.advanced.debugMode} onClick={() => set('advanced', 'debugMode', !settings.advanced.debugMode)}>
                <div className="thumb" />
              </Toggle>
            </RowTop>
            <RowDesc>Show developer information and verbose logging</RowDesc>
          </SettingRow>

          <SettingRow>
            <RowTop>
              <RowLabel $clickable onClick={() => set('advanced', 'experimentalFeatures', !settings.advanced.experimentalFeatures)}>
                Experimental Features
              </RowLabel>
              <Toggle $on={settings.advanced.experimentalFeatures} onClick={() => set('advanced', 'experimentalFeatures', !settings.advanced.experimentalFeatures)}>
                <div className="thumb" />
              </Toggle>
            </RowTop>
            <RowDesc>Enable beta features — may be unstable</RowDesc>
          </SettingRow>

          <SettingRow>
            <RowTop $mb="4px">
              <RowLabel htmlFor="cacheSize">Cache Size — {settings.advanced.cacheSize} MB</RowLabel>
            </RowTop>
            <RowDesc>Memory allocated for caching graph and search data</RowDesc>
            <Slider
              id="cacheSize" type="range" min="50" max="500" step="50"
              value={settings.advanced.cacheSize}
              onChange={e => set('advanced', 'cacheSize', +e.target.value)}
            />
          </SettingRow>

          <SettingRow>
            <RowTop $mb="4px">
              <RowLabel htmlFor="refreshInterval">Auto-Refresh — {settings.advanced.refreshInterval}s</RowLabel>
            </RowTop>
            <RowDesc>Interval for automatically refreshing data from the backend</RowDesc>
            <Slider
              id="refreshInterval" type="range" min="10" max="300" step="10"
              value={settings.advanced.refreshInterval}
              onChange={e => set('advanced', 'refreshInterval', +e.target.value)}
            />
          </SettingRow>
        </Section>
      </>
    ),
  };

  if (!isOpen) return null;

  const activeTabLabel = TABS.find(t => t.id === activeTab)?.label || 'Settings';

  return (
    <Backdrop
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      <Modal
        initial={{ opacity: 0, scale: 0.92, y: 40 }}
        animate={{ opacity: 1, scale: 1,    y: 0  }}
        exit={{    opacity: 0, scale: 0.92, y: 40 }}
        transition={{ type: 'spring', damping: 26, stiffness: 320 }}
      >
        {/* ── Sidebar ─────────────────────────────── */}
        <Sidebar>
          <SideTop>
            <SideAccent />
            <SideBrand>
              <BrandIcon>✦</BrandIcon>
              <BrandText>
                <div className="name">MindCanvas</div>
                <div className="sub">Settings</div>
              </BrandText>
            </SideBrand>
          </SideTop>

          <TabNav>
            {TABS.map(t => (
              <Tab
                key={t.id}
                $active={activeTab === t.id}
                onClick={() => setActiveTab(t.id)}
                whileTap={{ scale: 0.97 }}
              >
                {activeTab === t.id && (
                  <ActiveIndicator
                    layoutId="activeIndicator"
                    transition={{ type: 'spring', damping: 28, stiffness: 380 }}
                  />
                )}
                <span className="tab-icon">{t.icon}</span>
                {t.label}
              </Tab>
            ))}
          </TabNav>
        </Sidebar>

        {/* ── Content ─────────────────────────────── */}
        <Content>
          <ContentHead>
            <ContentAccent />
            <ContentHeadRow>
              <ContentTitle>{activeTabLabel}</ContentTitle>
              <CloseBtn
                whileHover={{ scale: 1.08 }}
                whileTap={{ scale: 0.92 }}
                onClick={onClose}
              >
                ✕
              </CloseBtn>
            </ContentHeadRow>
          </ContentHead>

          <ContentScroll>
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTab}
                initial={{ opacity: 0, x: 12 }}
                animate={{ opacity: 1, x: 0  }}
                exit={{    opacity: 0, x: -8 }}
                transition={{ duration: 0.18 }}
              >
                {tabContent[activeTab]}
              </motion.div>
            </AnimatePresence>
          </ContentScroll>

          <Footer>
            <FootBtn className="primary" whileTap={{ scale: 0.96 }} onClick={save}>
              Save Changes
            </FootBtn>
            <FootBtn className="ghost" whileTap={{ scale: 0.96 }} onClick={reset}>
              Reset Defaults
            </FootBtn>
            <FootBtn className="ghost" whileTap={{ scale: 0.96 }} onClick={onClose}>
              Cancel
            </FootBtn>
          </Footer>
        </Content>
      </Modal>
    </Backdrop>
  );
};

export default SettingsPanel;
