// src/components/StatisticsPanel.js - Compact & Professional
import React, { useState, useMemo } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend
} from 'recharts';

const PanelContainer = styled(motion.div)`
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px);
  border-radius: ${props => props.theme.borderRadius.lg};
  border: 1px solid ${props => props.theme.colors.border};
  overflow: hidden;
  box-shadow: ${props => props.theme.shadows.sm};
`;

const PanelHeader = styled.div`
  padding: ${props => props.theme.spacing.sm};
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid ${props => props.theme.colors.border};
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const PanelTitle = styled.h3`
  margin: 0;
  font-size: 0.78rem;
  font-weight: 600;
  color: ${props => props.theme.colors.text};
  text-transform: uppercase;
  letter-spacing: 0.5px;
`;

const ToggleButton = styled(motion.button)`
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: ${props => props.theme.colors.text};
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
  
  &:hover {
    background: rgba(255, 255, 255, 0.12);
  }
`;

const PanelContent = styled.div`
  padding: ${props => props.theme.spacing.sm};
`;

const StatCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-left: 3px solid ${props => props.color};
  border-radius: ${props => props.theme.borderRadius.md};
  padding: 10px ${props => props.theme.spacing.sm};
  color: white;
  margin-bottom: ${props => props.theme.spacing.sm};
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(8px);

  .stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 2px;
    color: ${props => props.color};
    letter-spacing: -0.5px;
  }

  .stat-label {
    font-size: 0.7rem;
    color: ${props => props.theme.colors.textSecondary};
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 500;
  }
`;

const ChartContainer = styled.div`
  height: 160px;
  margin: ${props => props.theme.spacing.sm} 0;
  
  .recharts-text {
    fill: ${props => props.theme.colors.text};
    font-size: 11px;
  }
`;

const TrendingList = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${props => props.theme.spacing.xs};
  max-height: 200px;
  overflow-y: auto;
`;

const TrendingItem = styled(motion.div)`
  background: rgba(255, 255, 255, 0.05);
  border-radius: ${props => props.theme.borderRadius.sm};
  padding: 4px 8px;
  border-left: 3px solid ${props => props.color};
  
  &:hover {
    background: rgba(255, 255, 255, 0.08);
  }
  
  .trending-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 2px;
  }
  
  .trending-title {
    font-weight: 600;
    font-size: 0.8rem;
    color: ${props => props.theme.colors.text};
  }
  
  .trending-value {
    background: ${props => props.color};
    color: white;
    padding: 2px 6px;
    border-radius: 10px;
    font-size: 0.65rem;
    font-weight: 600;
  }
  
  .trending-meta {
    font-size: 0.7rem;
    color: ${props => props.theme.colors.textSecondary};
  }
`;

const RecommendationCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.05);
  border-radius: ${props => props.theme.borderRadius.md};
  padding: 6px;
  margin-bottom: ${props => props.theme.spacing.sm};
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  
  &:hover {
    background: rgba(255, 255, 255, 0.08);
    transform: translateY(-1px);
  }
  
  .recommendation-title {
    font-weight: 600;
    font-size: 0.8rem;
    color: ${props => props.theme.colors.text};
    margin-bottom: ${props => props.theme.spacing.xs};
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .recommendation-summary {
    font-size: 0.7rem;
    color: ${props => props.theme.colors.textSecondary};
    line-height: 1.3;
    margin-bottom: ${props => props.theme.spacing.xs};
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .recommendation-meta {
    display: flex;
    gap: ${props => props.theme.spacing.xs};
    align-items: center;
    justify-content: space-between;
    font-size: 0.65rem;
    
    .type-badge {
      background: ${props => props.theme.colors.primary};
      color: white;
      padding: 2px 6px;
      border-radius: 4px;
    }
    
    .quality-score {
      color: ${props => props.theme.colors.success};
      font-weight: 600;
    }
  }
`;

const EmptyState = styled.div`
  text-align: center;
  padding: ${props => props.theme.spacing.lg};
  color: ${props => props.theme.colors.textSecondary};
  font-size: 0.85rem;
  
  .empty-icon {
    font-size: 2rem;
    margin-bottom: ${props => props.theme.spacing.sm};
    opacity: 0.5;
  }
`;

const CHART_COLORS = ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#8b5cf6', '#f43f5e'];

const StatisticsPanel = ({ title, type, data, stats, trending }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: 'rgba(0, 0, 0, 0.9)',
          padding: '6px 10px',
          border: '1px solid rgba(255, 255, 255, 0.2)',
          borderRadius: '4px',
          fontSize: '0.75rem',
          color: 'white'
        }}>
          <p style={{ margin: 0 }}>{`${payload[0].name}: ${payload[0].value}`}</p>
        </div>
      );
    }
    return null;
  };

  const processedData = useMemo(() => {
    if (!data) return null;

    switch (type) {
      case 'overview':
        return {
          totalContent: stats?.total_content || 0,
          vectorEnabled: stats?.vector_enabled || 0,
          avgQuality: stats?.average_quality || 0,
        };

      case 'contentTypes':
        if (!data || typeof data !== 'object') return [];
        const entries = Object.entries(data);
        if (entries.length === 0) return [];
        
        return entries.map(([type, count], index) => ({
          name: type,
          value: count,
          color: CHART_COLORS[index % CHART_COLORS.length]
        }));

      case 'recommendations':
        return Array.isArray(data) ? data.slice(0, 5) : [];

      default:
        return data;
    }
  }, [data, stats, type]);

  const renderContent = () => {
    switch (type) {
      case 'overview':
        return (
          <>
            <StatCard
              color="#6366f1"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="stat-value">{processedData?.totalContent || 0}</div>
              <div className="stat-label">Knowledge Items</div>
            </StatCard>

            <StatCard
              color="#10b981"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <div className="stat-value">
                {processedData?.avgQuality ? Number(processedData.avgQuality).toFixed(1) : '—'}<span style={{ fontSize: '0.75rem', opacity: 0.6 }}>/10</span>
              </div>
              <div className="stat-label">Avg Quality</div>
            </StatCard>
          </>
        );

      case 'contentTypes':
        if (!processedData || processedData.length === 0) {
          return (
            <EmptyState>
              <div className="empty-icon">📊</div>
              <div>Loading content types...</div>
            </EmptyState>
          );
        }
        
        return (
          <ChartContainer>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={processedData}
                  cx="50%"
                  cy="50%"
                  outerRadius={70}
                  dataKey="value"
                  nameKey="name"
                  label={({ percent }) => `${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {processedData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                <Legend 
                  wrapperStyle={{ fontSize: '0.75rem' }}
                  iconSize={8}
                />
              </PieChart>
            </ResponsiveContainer>
          </ChartContainer>
        );

      case 'recommendations':
        if (!processedData || processedData.length === 0) {
          return (
            <EmptyState>
              <div className="empty-icon">💡</div>
              <div>No recommendations yet</div>
            </EmptyState>
          );
        }
        
        return (
          <div>
            {processedData.map((item, index) => (
              <RecommendationCard
                key={item.id || index}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => item.url && window.open(item.url, '_blank')}
              >
                <div className="recommendation-title">{item.title}</div>
                <div className="recommendation-summary">{item.summary}</div>
                <div className="recommendation-meta">
                  <span className="type-badge">{item.content_type}</span>
                  <span className="quality-score">{item.quality_score}/10</span>
                </div>
              </RecommendationCard>
            ))}
          </div>
        );

      case 'trending':
      default:
        if (trending && trending.length > 0) {
          return (
            <TrendingList>
              {trending.map((item, index) => (
                <TrendingItem
                  key={item.topic || index}
                  color={CHART_COLORS[index % CHART_COLORS.length]}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <div className="trending-header">
                    <span className="trending-title">{item.topic}</span>
                    <span className="trending-value">{item.count}</span>
                  </div>
                  <div className="trending-meta">
                    Quality: {item.average_quality}/10
                  </div>
                </TrendingItem>
              ))}
            </TrendingList>
          );
        }
        
        return (
          <EmptyState>
            <div className="empty-icon">🔥</div>
            <div>Loading trending topics...</div>
          </EmptyState>
        );
    }
  };

  return (
    <PanelContainer
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
    >
      <PanelHeader>
        <PanelTitle>{title}</PanelTitle>
        <ToggleButton
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? '−' : '+'}
        </ToggleButton>
      </PanelHeader>

      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <PanelContent>
              {renderContent()}
            </PanelContent>
          </motion.div>
        )}
      </AnimatePresence>
    </PanelContainer>
  );
};

export default StatisticsPanel;