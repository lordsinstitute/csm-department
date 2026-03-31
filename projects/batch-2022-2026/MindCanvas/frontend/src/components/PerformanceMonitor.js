// src/components/PerformanceMonitor.js
import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

const getPlacementStyles = (placement) => {
  if (placement === 'graph') {
    return `
      position: absolute;
      bottom: 12px;
      right: 12px;
      z-index: 1100;
    `;
  }

  return `
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 10000;
  `;
};

const MonitorContainer = styled(motion.div)`
  ${props => getPlacementStyles(props.placement)}
  background: rgba(12, 12, 24, 0.72);
  color: ${props => props.theme?.colors?.text ?? 'white'};
  padding: 12px;
  border-radius: 12px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12px;
  min-width: 220px;
  max-width: 260px;
  border: 1px solid ${props => props.theme?.colors?.border ?? 'rgba(255, 255, 255, 0.12)'};
  box-shadow: ${props => props.theme?.shadows?.md ?? '0 10px 30px rgba(0,0,0,0.35)'};
  backdrop-filter: blur(14px);
`;

const MinimizedButton = styled(motion.button)`
  ${props => getPlacementStyles(props.placement)}
  appearance: none;
  border: 1px solid ${props => props.theme?.colors?.border ?? 'rgba(255, 255, 255, 0.12)'};
  background: rgba(12, 12, 24, 0.72);
  color: ${props => props.theme?.colors?.text ?? 'white'};
  border-radius: 999px;
  padding: 6px 10px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  box-shadow: ${props => props.theme?.shadows?.sm ?? '0 6px 18px rgba(0,0,0,0.28)'};
  backdrop-filter: blur(14px);

  &:hover {
    background: rgba(12, 12, 24, 0.86);
  }

  &:focus-visible {
    outline: 2px solid ${props => props.theme?.colors?.primary ?? '#6366f1'};
    outline-offset: 2px;
  }

  .pill-title {
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.2px;
  }

  .pill-sub {
    font-size: 11px;
    color: ${props => props.theme?.colors?.textSecondary ?? 'rgba(255, 255, 255, 0.75)'};
  }
`;

const MonitorHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;

  .title {
    font-weight: 700;
    letter-spacing: 0.2px;
    color: ${props => props.theme?.colors?.primary ?? '#6366f1'};
  }
`;

const ControlButton = styled.button`
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: ${props => props.theme?.colors?.text ?? 'white'};
  padding: 4px 8px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  line-height: 1;

  &:hover {
    background: rgba(255, 255, 255, 0.16);
  }

  &:focus-visible {
    outline: 2px solid ${props => props.theme?.colors?.primary ?? '#6366f1'};
    outline-offset: 2px;
  }
`;

const MetricRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;

  .label {
    color: ${props => props.theme?.colors?.textSecondary ?? 'rgba(255, 255, 255, 0.75)'};
  }

  .value {
    font-weight: 600;
    color: ${props => props.theme?.colors?.success ?? '#10b981'};
  }
`;

const PerformanceMonitor = ({
  isVisible = false,
  nodeCount = 0,
  edgeCount = 0,
  placement = 'graph'
}) => {
  const [isMinimized, setIsMinimized] = useState(false);

  // Simple mock metrics
  const metrics = {
    fps: 60,
    memory: 45,
    renderTime: 8.2
  };

  if (!isVisible) return null;

  if (isMinimized) {
    return (
      <MinimizedButton
        type="button"
        placement={placement}
        onClick={() => setIsMinimized(false)}
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        whileHover={{ scale: 1.03 }}
        aria-label="Open performance monitor"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M4 19V5M4 19H20M7 16V11M11 16V7M15 16V13M19 16V9"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
        <span className="pill-title">Perf</span>
        <span className="pill-sub">{metrics.fps} FPS</span>
      </MinimizedButton>
    );
  }

  return (
    <MonitorContainer
      placement={placement}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <MonitorHeader>
        <span className="title">Performance</span>
        <ControlButton
          type="button"
          onClick={() => setIsMinimized(true)}
          aria-label="Minimize performance monitor"
        >
          -
        </ControlButton>
      </MonitorHeader>

      <MetricRow>
        <span className="label">FPS:</span>
        <span className="value">{metrics.fps}</span>
      </MetricRow>

      <MetricRow>
        <span className="label">Memory:</span>
        <span className="value">{metrics.memory}MB</span>
      </MetricRow>

      <MetricRow>
        <span className="label">Render:</span>
        <span className="value">{metrics.renderTime}ms</span>
      </MetricRow>

      <MetricRow>
        <span className="label">Nodes:</span>
        <span className="value">{nodeCount}</span>
      </MetricRow>

      <MetricRow>
        <span className="label">Edges:</span>
        <span className="value">{edgeCount}</span>
      </MetricRow>
    </MonitorContainer>
  );
};

export default PerformanceMonitor;
