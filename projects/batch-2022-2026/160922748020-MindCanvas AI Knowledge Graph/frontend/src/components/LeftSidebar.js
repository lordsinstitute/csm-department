// src/components/LeftSidebar.js — Unified premium left sidebar
import React from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';

// ─── Layout ───────────────────────────────────────────────────────────────────

const Sidebar = styled.div`
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 14px;
  overflow: hidden;
  backdrop-filter: blur(20px);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
`;

// ─── Brand ────────────────────────────────────────────────────────────────────

const Brand = styled.div`
  padding: 20px 18px 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.04) 100%);
  flex-shrink: 0;
`;

const BrandLogo = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
`;

const BrandIcon = styled.div`
  width: 30px;
  height: 30px;
  border-radius: 9px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  box-shadow: 0 2px 10px rgba(99, 102, 241, 0.35);
  flex-shrink: 0;
`;

const BrandName = styled.div`
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: -0.6px;
  background: linear-gradient(135deg, #a5b4fc 0%, #818cf8 50%, #c4b5fd 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
`;

const BrandSub = styled.div`
  font-size: 0.62rem;
  font-weight: 500;
  color: rgba(226, 232, 240, 0.35);
  text-transform: uppercase;
  letter-spacing: 1.4px;
  margin-left: 40px;
`;

// ─── Scroll area ──────────────────────────────────────────────────────────────

const ScrollArea = styled.div`
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 22px;

  &::-webkit-scrollbar { width: 3px; }
  &::-webkit-scrollbar-track { background: transparent; }
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
  }
`;

// ─── Section ──────────────────────────────────────────────────────────────────

const Section = styled.div``;

const SectionLabel = styled.div`
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.4px;
  color: rgba(226, 232, 240, 0.3);
  margin-bottom: 10px;
`;

// ─── Stats grid ───────────────────────────────────────────────────────────────

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
`;

const StatCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 13px 12px 11px;
  position: relative;
  overflow: hidden;

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: ${props => props.$accent};
    opacity: 0.75;
    border-radius: 10px 10px 0 0;
  }
`;

const StatValue = styled.div`
  font-size: 1.55rem;
  font-weight: 700;
  color: ${props => props.$color};
  letter-spacing: -0.5px;
  line-height: 1;
  margin-bottom: 5px;
`;

const StatLabel = styled.div`
  font-size: 0.65rem;
  color: rgba(226, 232, 240, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-weight: 600;
`;

// ─── Content type bars ────────────────────────────────────────────────────────

const TypeRow = styled.div`
  margin-bottom: 9px;

  &:last-child { margin-bottom: 0; }
`;

const TypeHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 5px;
`;

const TypeName = styled.div`
  font-size: 0.77rem;
  color: rgba(226, 232, 240, 0.72);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 65%;
`;

const TypeCount = styled.div`
  font-size: 0.68rem;
  color: rgba(226, 232, 240, 0.35);
  font-weight: 600;
`;

const BarTrack = styled.div`
  height: 3px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 2px;
  overflow: hidden;
`;

const BarFill = styled(motion.div)`
  height: 100%;
  background: ${props => props.$color};
  border-radius: 2px;
  opacity: 0.8;
`;

// ─── Trending list ────────────────────────────────────────────────────────────

const TrendingRow = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 7px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  cursor: default;

  &:last-child { border-bottom: none; }
`;

const TrendDot = styled.div`
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: ${props => props.$color};
  flex-shrink: 0;
  opacity: 0.85;
`;

const TrendName = styled.div`
  flex: 1;
  font-size: 0.79rem;
  color: rgba(226, 232, 240, 0.75);
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
`;

const TrendBadge = styled.div`
  font-size: 0.67rem;
  font-weight: 600;
  color: rgba(226, 232, 240, 0.38);
  background: rgba(255, 255, 255, 0.06);
  padding: 2px 8px;
  border-radius: 20px;
  flex-shrink: 0;
`;

// ─── Recommendations ──────────────────────────────────────────────────────────

const RecCard = styled(motion.div)`
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 9px;
  padding: 10px 11px;
  cursor: pointer;
  margin-bottom: 6px;
  transition: background 0.15s, border-color 0.15s;

  &:last-child { margin-bottom: 0; }

  &:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(99, 102, 241, 0.25);
  }
`;

const RecTitle = styled.div`
  font-size: 0.78rem;
  font-weight: 600;
  color: rgba(226, 232, 240, 0.82);
  line-height: 1.3;
  margin-bottom: 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const RecMeta = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
`;

const RecBadge = styled.div`
  font-size: 0.63rem;
  font-weight: 600;
  background: rgba(99, 102, 241, 0.15);
  color: rgba(165, 180, 252, 0.8);
  padding: 2px 7px;
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 55%;
`;

const RecQuality = styled.div`
  font-size: 0.65rem;
  color: rgba(16, 185, 129, 0.75);
  font-weight: 600;
`;

// ─── Empty state ──────────────────────────────────────────────────────────────

const Empty = styled.div`
  font-size: 0.75rem;
  color: rgba(226, 232, 240, 0.25);
  text-align: center;
  padding: 8px 0;
`;

// ─── Palette ──────────────────────────────────────────────────────────────────

const COLORS = [
  '#6366f1', '#06b6d4', '#10b981', '#f59e0b',
  '#8b5cf6', '#f43f5e', '#22c55e', '#3b82f6',
];

// ─── Component ────────────────────────────────────────────────────────────────

const LeftSidebar = ({ stats, trending, recommendations }) => {
  const totalContent  = stats?.total_content  || 0;
  const avgQuality    = stats?.average_quality || stats?.avg_quality || 0;
  const vectorEnabled = stats?.vector_enabled  || 0;
  const clusters      = stats?.content_clusters || 0;
  const byType        = stats?.by_content_type  || {};

  const typeEntries = Object.entries(byType);
  const maxCount    = Math.max(...typeEntries.map(([, v]) => v), 1);

  const recList = Array.isArray(recommendations) ? recommendations.slice(0, 5) : [];

  return (
    <Sidebar>
      {/* Brand */}
      <Brand>
        <BrandLogo>
          <BrandIcon>✦</BrandIcon>
          <BrandName>MindCanvas</BrandName>
        </BrandLogo>
        <BrandSub>AI Knowledge Graph</BrandSub>
      </Brand>

      <ScrollArea>
        {/* Overview stats */}
        <Section>
          <SectionLabel>Overview</SectionLabel>
          <StatsGrid>
            <StatCard
              $accent="#6366f1"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0 }}
            >
              <StatValue $color="#818cf8">{totalContent}</StatValue>
              <StatLabel>Items</StatLabel>
            </StatCard>

            <StatCard
              $accent="#10b981"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
            >
              <StatValue $color="#34d399">
                {avgQuality ? Number(avgQuality).toFixed(1) : '—'}
              </StatValue>
              <StatLabel>Quality</StatLabel>
            </StatCard>

            <StatCard
              $accent="#06b6d4"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <StatValue $color="#22d3ee">{clusters}</StatValue>
              <StatLabel>Clusters</StatLabel>
            </StatCard>

            <StatCard
              $accent="#8b5cf6"
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <StatValue $color="#a78bfa">{vectorEnabled}</StatValue>
              <StatLabel>Indexed</StatLabel>
            </StatCard>
          </StatsGrid>
        </Section>

        {/* Content types */}
        {typeEntries.length > 0 && (
          <Section>
            <SectionLabel>Content Types</SectionLabel>
            {typeEntries.slice(0, 7).map(([typeName, count], i) => (
              <TypeRow key={typeName}>
                <TypeHeader>
                  <TypeName>{typeName}</TypeName>
                  <TypeCount>{count}</TypeCount>
                </TypeHeader>
                <BarTrack>
                  <BarFill
                    $color={COLORS[i % COLORS.length]}
                    initial={{ width: 0 }}
                    animate={{ width: `${(count / maxCount) * 100}%` }}
                    transition={{ delay: i * 0.04, duration: 0.55, ease: 'easeOut' }}
                  />
                </BarTrack>
              </TypeRow>
            ))}
          </Section>
        )}

        {/* Trending categories */}
        {trending && trending.length > 0 && (
          <Section>
            <SectionLabel>Categories</SectionLabel>
            {trending.slice(0, 8).map((item, i) => (
              <TrendingRow
                key={item.topic || i}
                initial={{ opacity: 0, x: -6 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.035 }}
              >
                <TrendDot $color={COLORS[i % COLORS.length]} />
                <TrendName>{item.topic}</TrendName>
                <TrendBadge>{item.count}</TrendBadge>
              </TrendingRow>
            ))}
          </Section>
        )}

        {/* Recommendations */}
        {recList.length > 0 && (
          <Section>
            <SectionLabel>Recommended</SectionLabel>
            {recList.map((item, i) => (
              <RecCard
                key={item.id || i}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                onClick={() => item.url && window.open(item.url, '_blank')}
              >
                <RecTitle>{item.title}</RecTitle>
                <RecMeta>
                  <RecBadge>{item.content_type || 'Article'}</RecBadge>
                  <RecQuality>{item.quality_score}/10</RecQuality>
                </RecMeta>
              </RecCard>
            ))}
          </Section>
        )}

        {/* Empty state when no data yet */}
        {totalContent === 0 && (
          <Empty>
            No data yet — use the Chrome extension or load sample data to begin.
          </Empty>
        )}
      </ScrollArea>
    </Sidebar>
  );
};

export default LeftSidebar;
