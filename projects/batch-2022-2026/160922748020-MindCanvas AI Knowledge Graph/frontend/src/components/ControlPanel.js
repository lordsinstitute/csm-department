// src/components/ControlPanel.js
import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { useKnowledgeStore } from '../store/knowledgeStore';

/* ── Toolbar wrapper ────────────────────────────────────────────── */
const ControlContainer = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 2px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 4px;
  backdrop-filter: blur(16px);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
`;

const Divider = styled.div`
  width: 1px;
  height: 22px;
  background: rgba(255, 255, 255, 0.1);
  margin: 0 2px;
`;

/* ── Standard button ────────────────────────────────────────────── */
const Btn = styled(motion.button)`
  background: transparent;
  border: none;
  color: rgba(226, 232, 240, 0.7);
  width: 36px;
  height: 36px;
  border-radius: 10px;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  transition: background 0.18s, color 0.18s;

  &:hover {
    background: rgba(99, 102, 241, 0.18);
    color: #a5b4fc;
  }
  &:active  { background: rgba(99, 102, 241, 0.28); }
  &:disabled { opacity: 0.35; cursor: not-allowed; }
  &.active  { background: rgba(99, 102, 241, 0.22); color: #a5b4fc; }
`;

/* ── Destructive (clear) button — red tint ──────────────────────── */
const DangerBtn = styled(Btn)`
  &:hover {
    background: rgba(239, 68, 68, 0.18);
    color: #fca5a5;
  }
  &:active { background: rgba(239, 68, 68, 0.28); }
  &.confirming {
    background: rgba(239, 68, 68, 0.2);
    border: 1px solid rgba(239, 68, 68, 0.35);
    color: #fca5a5;
    width: auto;
    padding: 0 10px;
    gap: 6px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    white-space: nowrap;
  }
`;

const ConfirmYes = styled(motion.button)`
  background: rgba(239, 68, 68, 0.35);
  border: 1px solid rgba(239, 68, 68, 0.5);
  color: #fca5a5;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 700;
  cursor: pointer;
  &:hover { background: rgba(239, 68, 68, 0.55); }
`;

const ConfirmNo = styled(motion.button)`
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: rgba(226, 232, 240, 0.55);
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 700;
  cursor: pointer;
  &:hover { background: rgba(255, 255, 255, 0.1); color: #e2e8f0; }
`;

/* ── Layout dropdown ────────────────────────────────────────────── */
const DropdownWrap = styled.div`
  position: relative;
`;

const DropdownMenu = styled(motion.div)`
  position: absolute;
  top: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: rgba(10, 10, 22, 0.97);
  backdrop-filter: blur(24px);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 12px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.55), 0 0 0 1px rgba(255,255,255,0.04);
  overflow: hidden;
  z-index: 1200;
  min-width: 230px;
`;

const MenuHeader = styled.div`
  padding: 10px 16px 8px;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: rgba(165, 180, 252, 0.5);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
`;

const MenuItem = styled.div`
  padding: 11px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: background 0.15s;
  border-left: 2px solid transparent;

  &:hover  { background: rgba(99,102,241,0.12); border-left-color: rgba(99,102,241,0.4); }
  &.active { background: rgba(99,102,241,0.16); border-left-color: #6366f1; }

  .item-icon  { font-size: 1.05rem; width: 22px; text-align: center; flex-shrink: 0; }
  .item-label { font-size: 0.88rem; font-weight: 600; color: #e2e8f0; }
  .item-desc  { font-size: 0.75rem; color: rgba(226,232,240,0.42); margin-top: 2px; line-height: 1.3; }
  .check      { margin-left: auto; font-size: 0.8rem; color: #6366f1; }
`;

/* ── Tooltip ────────────────────────────────────────────────────── */
const Tip = styled(motion.div)`
  position: absolute;
  bottom: calc(100% + 8px);
  left: 50%;
  transform: translateX(-50%);
  background: rgba(8, 8, 18, 0.96);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #e2e8f0;
  padding: 5px 10px;
  border-radius: 7px;
  font-size: 0.73rem;
  font-weight: 500;
  white-space: nowrap;
  pointer-events: none;
  z-index: 1300;
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);

  &::after {
    content: '';
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    border: 4px solid transparent;
    border-top-color: rgba(8, 8, 18, 0.96);
  }
`;

const KbdTag = styled.span`
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 1px 5px;
  font-size: 0.68rem;
  margin-left: 6px;
  color: rgba(226, 232, 240, 0.55);
`;

const SpinIcon = styled.span`
  display: inline-block;
  animation: spin 0.8s linear infinite;
  @keyframes spin { to { transform: rotate(360deg); } }
`;

/* ════════════════════════════════════════════════════════════════ */
const ControlPanel = ({ onSearch, onRefresh, onLayoutChange, currentLayout, isRefreshing }) => {
  const [showLayout,    setShowLayout]    = useState(false);
  const [hovered,       setHovered]       = useState(null);
  const [confirmClear,  setConfirmClear]  = useState(false);
  const [isClearing,    setIsClearing]    = useState(false);
  const [isLoadingSample, setIsLoadingSample] = useState(false);

  const { updateGraphSettings, refreshAllData, exportKnowledgeGraph, clearAllData, loadSampleData } =
    useKnowledgeStore();

  const layouts = [
    { id: 'fcose', icon: '⬡', label: 'Force-Directed', desc: 'Physics-based — clusters emerge naturally'  },
    { id: 'dagre', icon: '⧉', label: 'Hierarchical',    desc: 'Top-down hierarchy — shows knowledge flow' },
  ];

  const handleLayout = (id) => {
    onLayoutChange(id);
    updateGraphSettings({ layout: id });
    setShowLayout(false);
  };

  const handleRefresh = async () => {
    try { await refreshAllData(); onRefresh(); }
    catch (e) { console.error('Refresh failed:', e); }
  };

  const handleExport = async () => {
    try { await exportKnowledgeGraph(); }
    catch (e) { console.error('Export failed:', e); }
  };

  const handleLoadSample = async () => {
    setIsLoadingSample(true);
    try {
      await loadSampleData();
      await refreshAllData();
      onRefresh();
    } catch (e) {
      console.error('Load sample failed:', e);
    } finally {
      setIsLoadingSample(false);
    }
  };

  const handleClearConfirmed = async () => {
    setIsClearing(true);
    setConfirmClear(false);
    try {
      await clearAllData();
      onRefresh();
    } catch (e) {
      console.error('Clear failed:', e);
    } finally {
      setIsClearing(false);
    }
  };

  const tip = (id, label, kbd) => hovered === id && !confirmClear && (
    <Tip
      key="tip"
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 4 }}
      transition={{ duration: 0.12 }}
    >
      {label}{kbd && <KbdTag>{kbd}</KbdTag>}
    </Tip>
  );

  return (
    <ControlContainer>
      {/* Search */}
      <Btn
        whileTap={{ scale: 0.9 }}
        onClick={onSearch}
        onMouseEnter={() => setHovered('search')}
        onMouseLeave={() => setHovered(null)}
      >
        ⌕
        <AnimatePresence>{tip('search', 'Search Knowledge', '⌘K')}</AnimatePresence>
      </Btn>

      <Divider />

      {/* Layout picker */}
      <DropdownWrap>
        <Btn
          className={showLayout ? 'active' : ''}
          whileTap={{ scale: 0.9 }}
          onClick={() => setShowLayout(v => !v)}
          onMouseEnter={() => setHovered('layout')}
          onMouseLeave={() => setHovered(null)}
        >
          ⊞
          <AnimatePresence>{!showLayout && tip('layout', 'Change Layout')}</AnimatePresence>
        </Btn>

        <AnimatePresence>
          {showLayout && (
            <DropdownMenu
              initial={{ opacity: 0, y: -8, scale: 0.96 }}
              animate={{ opacity: 1, y: 0,  scale: 1    }}
              exit={{    opacity: 0, y: -8, scale: 0.96 }}
              transition={{ duration: 0.14 }}
            >
              <MenuHeader>Graph Layout</MenuHeader>
              {layouts.map(l => (
                <MenuItem
                  key={l.id}
                  className={currentLayout === l.id ? 'active' : ''}
                  onClick={() => handleLayout(l.id)}
                >
                  <span className="item-icon">{l.icon}</span>
                  <div>
                    <div className="item-label">{l.label}</div>
                    <div className="item-desc">{l.desc}</div>
                  </div>
                  {currentLayout === l.id && <span className="check">✓</span>}
                </MenuItem>
              ))}
            </DropdownMenu>
          )}
        </AnimatePresence>
      </DropdownWrap>

      {/* Refresh */}
      <Btn
        whileTap={{ scale: 0.9 }}
        onClick={handleRefresh}
        disabled={isRefreshing}
        onMouseEnter={() => setHovered('refresh')}
        onMouseLeave={() => setHovered(null)}
      >
        {isRefreshing ? <SpinIcon>↻</SpinIcon> : '↻'}
        <AnimatePresence>{!isRefreshing && tip('refresh', 'Refresh Data', '⌘R')}</AnimatePresence>
      </Btn>

      <Divider />

      {/* Export */}
      <Btn
        whileTap={{ scale: 0.9 }}
        onClick={handleExport}
        onMouseEnter={() => setHovered('export')}
        onMouseLeave={() => setHovered(null)}
      >
        ↓
        <AnimatePresence>{tip('export', 'Export Graph')}</AnimatePresence>
      </Btn>

      {/* Load sample data */}
      <Btn
        whileTap={{ scale: 0.9 }}
        disabled={isLoadingSample}
        onClick={handleLoadSample}
        onMouseEnter={() => setHovered('sample')}
        onMouseLeave={() => setHovered(null)}
        style={{ color: isLoadingSample ? '#a5b4fc' : undefined }}
      >
        {isLoadingSample ? <SpinIcon>↻</SpinIcon> : '⊕'}
        <AnimatePresence>
          {!isLoadingSample && tip('sample', 'Load Sample Data')}
        </AnimatePresence>
      </Btn>

      {/* Fullscreen */}
      <Btn
        whileTap={{ scale: 0.9 }}
        onClick={() => {
          if (document.fullscreenElement) document.exitFullscreen();
          else document.documentElement.requestFullscreen();
        }}
        onMouseEnter={() => setHovered('fs')}
        onMouseLeave={() => setHovered(null)}
      >
        ⤢
        <AnimatePresence>{tip('fs', 'Fullscreen', 'F11')}</AnimatePresence>
      </Btn>

      <Divider />

      {/* Clear all — with inline confirmation */}
      <AnimatePresence mode="wait">
        {confirmClear ? (
          <DangerBtn
            key="confirm"
            className="confirming"
            as={motion.div}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1   }}
            exit={{    opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.12 }}
          >
            Clear all?
            <ConfirmYes
              whileTap={{ scale: 0.92 }}
              onClick={handleClearConfirmed}
            >
              Yes
            </ConfirmYes>
            <ConfirmNo
              whileTap={{ scale: 0.92 }}
              onClick={() => setConfirmClear(false)}
            >
              No
            </ConfirmNo>
          </DangerBtn>
        ) : (
          <DangerBtn
            key="trash"
            whileTap={{ scale: 0.9 }}
            disabled={isClearing}
            onClick={() => setConfirmClear(true)}
            onMouseEnter={() => setHovered('clear')}
            onMouseLeave={() => setHovered(null)}
          >
            {isClearing ? <SpinIcon>↻</SpinIcon> : '⊗'}
            <AnimatePresence>{tip('clear', 'Clear All Nodes')}</AnimatePresence>
          </DangerBtn>
        )}
      </AnimatePresence>
    </ControlContainer>
  );
};

export default ControlPanel;
