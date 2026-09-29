// src/components/SearchOverlay.js
import React, { useState, useEffect, useRef, useCallback } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { useKnowledgeStore } from '../store/knowledgeStore';
import Fuse from 'fuse.js';

/* ── Backdrop ──────────────────────────────────────────────────── */
const Backdrop = styled(motion.div)`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.72);
  backdrop-filter: blur(14px);
  z-index: 9999;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 9vh;
`;

/* ── Search card ───────────────────────────────────────────────── */
const Card = styled(motion.div)`
  width: 90%;
  max-width: 780px;
  max-height: 82vh;
  background: linear-gradient(160deg, rgba(10,10,22,0.99) 0%, rgba(13,13,26,0.99) 100%);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 18px;
  box-shadow: 0 32px 80px rgba(0,0,0,0.65), 0 0 0 1px rgba(255,255,255,0.04);
  overflow: hidden;
  display: flex;
  flex-direction: column;
`;

const AccentBar = styled.div`
  height: 2px;
  background: linear-gradient(90deg, #6366f1, #8b5cf6, #06b6d4);
  flex-shrink: 0;
`;

/* ── Search header ─────────────────────────────────────────────── */
const SearchHead = styled.div`
  padding: 20px 22px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
`;

const InputWrap = styled.div`
  position: relative;
  margin-bottom: 14px;
`;

const SearchIconEl = styled.div`
  position: absolute;
  left: 18px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.2rem;
  color: rgba(165, 180, 252, 0.5);
  pointer-events: none;
`;

const Input = styled.input`
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border: 1.5px solid rgba(255, 255, 255, 0.1);
  border-radius: 13px;
  padding: 14px 50px 14px 52px;
  color: #e2e8f0;
  font-size: 1.05rem;
  font-family: inherit;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;

  &::placeholder { color: rgba(226, 232, 240, 0.3); }

  &:focus {
    outline: none;
    border-color: rgba(99, 102, 241, 0.55);
    background: rgba(99, 102, 241, 0.05);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
  }
`;

const ClearBtn = styled(motion.button)`
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255,255,255,0.07);
  border: none;
  color: rgba(226,232,240,0.5);
  width: 28px;
  height: 28px;
  border-radius: 7px;
  cursor: pointer;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover { background: rgba(255,255,255,0.12); color: #e2e8f0; }
`;

/* ── Filter pills ──────────────────────────────────────────────── */
const FilterRow = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
`;

const FilterLabel = styled.span`
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: rgba(165, 180, 252, 0.4);
  margin-right: 2px;
`;

const FilterPill = styled(motion.button)`
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
  border: 1px solid ${p => p.$active ? 'rgba(99,102,241,0.5)' : 'rgba(255,255,255,0.1)'};
  background: ${p => p.$active ? 'rgba(99,102,241,0.2)' : 'transparent'};
  color: ${p => p.$active ? '#a5b4fc' : 'rgba(226,232,240,0.5)'};

  &:hover {
    background: rgba(99,102,241,0.15);
    border-color: rgba(99,102,241,0.35);
    color: #a5b4fc;
  }
`;

const SearchMeta = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 12px;
`;

const ResultCount = styled.div`
  font-size: 0.75rem;
  color: rgba(226,232,240,0.35);
  font-weight: 500;
`;

const QuickList = styled.div`
  display: flex;
  gap: 6px;
`;

const QuickChip = styled(motion.button)`
  padding: 4px 10px;
  border-radius: 14px;
  font-size: 0.72rem;
  font-weight: 600;
  border: 1px solid rgba(99,102,241,0.2);
  background: rgba(99,102,241,0.08);
  color: rgba(165,180,252,0.6);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;

  &:hover {
    background: rgba(99,102,241,0.18);
    color: #a5b4fc;
  }
`;

/* ── Results area ──────────────────────────────────────────────── */
const ResultsWrap = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 14px 18px 18px;
  scrollbar-width: thin;
  scrollbar-color: rgba(99,102,241,0.3) transparent;
  &::-webkit-scrollbar { width: 4px; }
  &::-webkit-scrollbar-thumb { background: rgba(99,102,241,0.3); border-radius: 2px; }
`;

const ResultCard = styled(motion.div)`
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-left: 2px solid transparent;
  border-radius: 11px;
  padding: 13px 15px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;

  &:hover {
    background: rgba(99,102,241,0.07);
    border-left-color: #6366f1;
  }

  &:last-child { margin-bottom: 0; }
`;

const RHead = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 5px;
  gap: 10px;
`;

const RTitle = styled.h4`
  margin: 0;
  font-size: 0.92rem;
  font-weight: 600;
  color: #e2e8f0;
  flex: 1;
  line-height: 1.35;
`;

const BadgeRow = styled.div`
  display: flex;
  gap: 5px;
  flex-shrink: 0;
`;

const RBadge = styled.span`
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.67rem;
  font-weight: 700;
  letter-spacing: 0.2px;
  background: ${p => p.$bg || 'rgba(99,102,241,0.14)'};
  color: ${p => p.$color || '#a5b4fc'};
`;

const RDesc = styled.p`
  margin: 0 0 7px;
  color: rgba(226,232,240,0.5);
  font-size: 0.82rem;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
`;

const RFoot = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const TopicList = styled.div`
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
`;

const TopicPill = styled.span`
  background: rgba(99,102,241,0.1);
  color: rgba(165,180,252,0.65);
  border-radius: 8px;
  padding: 2px 7px;
  font-size: 0.68rem;
  font-weight: 500;
`;

const RLink = styled.span`
  font-size: 0.72rem;
  color: rgba(99,102,241,0.6);
  font-weight: 600;
`;

/* ── Empty / loading states ────────────────────────────────────── */
const EmptyState = styled.div`
  text-align: center;
  padding: 48px 20px;

  .icon {
    font-size: 2.8rem;
    margin-bottom: 14px;
    opacity: 0.35;
    display: block;
  }

  .title {
    font-size: 1rem;
    font-weight: 600;
    color: rgba(226,232,240,0.6);
    margin-bottom: 6px;
  }

  .desc {
    font-size: 0.82rem;
    color: rgba(226,232,240,0.32);
    line-height: 1.55;
  }
`;

const LoadingRow = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 28px;
  color: rgba(226,232,240,0.35);
  font-size: 0.85rem;

  .ring {
    width: 22px;
    height: 22px;
    border: 2px solid rgba(99,102,241,0.15);
    border-top-color: #6366f1;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
`;

/* ── Color helpers ─────────────────────────────────────────────── */
const TYPE_COLORS = {
  Tutorial:      { bg: 'rgba(6,182,212,0.15)',   color: '#67e8f9' },
  Documentation: { bg: 'rgba(139,92,246,0.15)',  color: '#c4b5fd' },
  Article:       { bg: 'rgba(245,158,11,0.15)',  color: '#fcd34d' },
  Blog:          { bg: 'rgba(249,115,22,0.15)',  color: '#fdba74' },
  Research:      { bg: 'rgba(239,68,68,0.15)',   color: '#fca5a5' },
  News:          { bg: 'rgba(220,38,38,0.15)',   color: '#fca5a5' },
};
const typeStyle = t => TYPE_COLORS[t] || { bg: 'rgba(99,102,241,0.15)', color: '#a5b4fc' };

/* ════════════════════════════════════════════════════════════════ */
const SearchOverlay = ({ onClose, onSearch, graphData }) => {
  const [query, setQuery]         = useState('');
  const [results, setResults]     = useState([]);
  const [loading, setLoading]     = useState(false);
  const [searchType, setSearchType] = useState('semantic');

  const inputRef = useRef(null);
  const { performSemanticSearch, performTextSearch } = useKnowledgeStore();

  const fuse = React.useMemo(() => {
    if (!graphData?.nodes) return null;
    return new Fuse(graphData.nodes, {
      keys: ['name', 'title', 'summary', 'topics'],
      threshold: 0.3,
      includeScore: true,
    });
  }, [graphData]);

  useEffect(() => { inputRef.current?.focus(); }, []);

  useEffect(() => {
    const id = window.addEventListener('keydown', e => { if (e.key === 'Escape') onClose(); });
    return () => window.removeEventListener('keydown', id);
  }, [onClose]);

  useEffect(() => {
    const id = setTimeout(() => {
      if (query.trim()) runSearch(query);
      else setResults([]);
    }, 280);
    return () => clearTimeout(id);
  }, [query, searchType]);

  const runSearch = async (q) => {
    setLoading(true);
    try {
      let res = [];
      if      (searchType === 'local'    && fuse) res = fuse.search(q).map(r => ({ ...r.item, similarity: 1 - r.score }));
      else if (searchType === 'semantic')         res = await performSemanticSearch(q, 20);
      else                                        res = await performTextSearch(q, 20);
      setResults(res);
    } catch (e) {
      console.error('Search failed:', e);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleClick = (r) => {
    onSearch(query);
    onClose();
    if (r.id && graphData?.nodes) {
      const node = graphData.nodes.find(n => n.id === r.id);
      if (node) useKnowledgeStore.getState().setSelectedNode(node);
    }
    if (r.url) window.open(r.url, '_blank');
  };

  const FILTERS = [
    { id: 'semantic', label: '⬡ Semantic' },
    { id: 'text',     label: '≡ Text'     },
    { id: 'local',    label: '⚡ Local'   },
  ];

  const QUICK = ['machine learning', 'tutorial', 'documentation'];

  return (
    <Backdrop
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      <Card
        initial={{ opacity: 0, y: -40, scale: 0.96 }}
        animate={{ opacity: 1, y: 0,   scale: 1    }}
        exit={{    opacity: 0, y: -40, scale: 0.96 }}
        transition={{ type: 'spring', damping: 26, stiffness: 320 }}
      >
        <AccentBar />

        {/* ── Header ─────────────────────────────── */}
        <SearchHead>
          <InputWrap>
            <SearchIconEl>⌕</SearchIconEl>
            <Input
              ref={inputRef}
              type="text"
              placeholder="Search your knowledge graph…"
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && results.length > 0) handleClick(results[0]);
              }}
            />
            <AnimatePresence>
              {query && (
                <ClearBtn
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1   }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => setQuery('')}
                >
                  ✕
                </ClearBtn>
              )}
            </AnimatePresence>
          </InputWrap>

          <FilterRow>
            <FilterLabel>Mode</FilterLabel>
            {FILTERS.map(f => (
              <FilterPill
                key={f.id}
                $active={searchType === f.id}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSearchType(f.id)}
              >
                {f.label}
              </FilterPill>
            ))}
          </FilterRow>

          <SearchMeta>
            <ResultCount>
              {loading
                ? 'Searching…'
                : query.trim()
                  ? `${results.length} result${results.length !== 1 ? 's' : ''} found`
                  : 'Type to search'}
            </ResultCount>
            <QuickList>
              {QUICK.map(q => (
                <QuickChip key={q} whileTap={{ scale: 0.95 }} onClick={() => setQuery(q)}>
                  {q}
                </QuickChip>
              ))}
            </QuickList>
          </SearchMeta>
        </SearchHead>

        {/* ── Results ────────────────────────────── */}
        <ResultsWrap>
          {loading && (
            <LoadingRow>
              <div className="ring" />
              Searching…
            </LoadingRow>
          )}

          {!loading && results.length === 0 && query.trim() && (
            <EmptyState>
              <span className="icon">⌕</span>
              <div className="title">No results found</div>
              <div className="desc">
                Try different keywords or switch to semantic search<br />
                for concept-based discovery.
              </div>
            </EmptyState>
          )}

          {!loading && !query.trim() && (
            <EmptyState>
              <span className="icon">✦</span>
              <div className="title">Intelligent Search</div>
              <div className="desc">
                Search your entire knowledge graph using AI-powered semantic understanding.<br />
                Try concepts, topics, or specific content titles.
              </div>
            </EmptyState>
          )}

          <AnimatePresence>
            {!loading && results.map((r, i) => {
              const ct = r.content_type || r.type;
              const ts = typeStyle(ct);
              return (
                <ResultCard
                  key={r.id || i}
                  initial={{ opacity: 0, y: 14 }}
                  animate={{ opacity: 1, y: 0  }}
                  exit={{    opacity: 0, y: -10 }}
                  transition={{ delay: i * 0.04 }}
                  onClick={() => handleClick(r)}
                >
                  <RHead>
                    <RTitle>{r.title || r.name}</RTitle>
                    <BadgeRow>
                      {r.similarity != null && (
                        <RBadge $bg="rgba(6,182,212,0.15)" $color="#67e8f9">
                          {(r.similarity * 100).toFixed(0)}%
                        </RBadge>
                      )}
                      {ct && <RBadge $bg={ts.bg} $color={ts.color}>{ct}</RBadge>}
                      {(r.quality_score || r.quality) && (
                        <RBadge $bg="rgba(245,158,11,0.15)" $color="#fcd34d">
                          {r.quality_score || r.quality}/10
                        </RBadge>
                      )}
                    </BadgeRow>
                  </RHead>

                  <RDesc>{r.summary || r.description || 'No description available'}</RDesc>

                  <RFoot>
                    <TopicList>
                      {(r.key_topics || r.topics || []).slice(0, 3).map((t, j) => (
                        <TopicPill key={j}>{t}</TopicPill>
                      ))}
                    </TopicList>
                    {r.url && <RLink>↗ Link</RLink>}
                  </RFoot>
                </ResultCard>
              );
            })}
          </AnimatePresence>
        </ResultsWrap>
      </Card>
    </Backdrop>
  );
};

export default SearchOverlay;
