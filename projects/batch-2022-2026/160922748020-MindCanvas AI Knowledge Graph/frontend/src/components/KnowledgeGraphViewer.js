// KnowledgeGraphViewer — neuron-sphere nodes, premium glow, fcose layout
import React, { useRef, useEffect, useState, useCallback } from 'react';
import styled, { keyframes } from 'styled-components';
import cytoscape from 'cytoscape';
import fcose from 'cytoscape-fcose';

cytoscape.use(fcose);

// ─── Styled Components ────────────────────────────────────────────────────────

const Wrapper = styled.div`
  position: relative;
  width: 100%;
  height: 100%;
  background: transparent;
  overflow: hidden;
`;

const CyContainer = styled.div`
  width: 100%;
  height: 100%;
`;

const spin = keyframes`
  to { transform: rotate(360deg); }
`;

const LoadingPill = styled.div`
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(11, 11, 24, 0.88);
  border: 1px solid rgba(99, 102, 241, 0.28);
  border-radius: 20px;
  padding: 7px 16px;
  backdrop-filter: blur(14px);
  pointer-events: none;
  z-index: 10;
`;

const Spinner = styled.div`
  width: 12px;
  height: 12px;
  border: 2px solid rgba(99, 102, 241, 0.25);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: ${spin} 0.75s linear infinite;
`;

const LoadingText = styled.span`
  font-size: 11px;
  color: rgba(226, 232, 240, 0.6);
  letter-spacing: 0.4px;
  font-family: 'Inter', sans-serif;
`;

const CountBadge = styled.div`
  position: absolute;
  bottom: 14px;
  left: 14px;
  background: rgba(11, 11, 24, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 8px;
  padding: 5px 11px;
  font-size: 11px;
  color: rgba(226, 232, 240, 0.45);
  backdrop-filter: blur(10px);
  pointer-events: none;
  z-index: 5;
  font-family: 'Inter', sans-serif;
  letter-spacing: 0.2px;
`;

// ─── Colour Palette ───────────────────────────────────────────────────────────

const CLUSTER_COLORS = [
  '#6366f1', '#8b5cf6', '#06b6d4', '#10b981',
  '#f59e0b', '#ef4444', '#ec4899', '#14b8a6',
  '#f97316', '#a855f7', '#22c55e', '#3b82f6',
];

// ─── Node SVG generator ───────────────────────────────────────────────────────
// Holographic orb: dark core → colored rim light.
// Avoids white-highlight "plastic ball" look — instead uses the cluster colour
// as the light source, creating a sci-fi bioluminescent cell appearance.

function makeNodeSvg(color) {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="120" height="120" viewBox="0 0 120 120">
    <defs>
      <radialGradient id="body" cx="50%" cy="50%" r="50%">
        <stop offset="0%"   stop-color="#05050e"/>
        <stop offset="38%"  stop-color="${color}" stop-opacity="0.08"/>
        <stop offset="62%"  stop-color="${color}" stop-opacity="0.42"/>
        <stop offset="82%"  stop-color="${color}" stop-opacity="0.82"/>
        <stop offset="100%" stop-color="${color}" stop-opacity="1"/>
      </radialGradient>
      <radialGradient id="spec" cx="36%" cy="30%" r="32%">
        <stop offset="0%"   stop-color="rgba(255,255,255,0.16)"/>
        <stop offset="55%"  stop-color="rgba(255,255,255,0.04)"/>
        <stop offset="100%" stop-color="rgba(255,255,255,0)"/>
      </radialGradient>
    </defs>
    <circle cx="60" cy="60" r="58" fill="url(#body)"/>
    <circle cx="60" cy="60" r="58" fill="url(#spec)"/>
    <circle cx="60" cy="60" r="56" fill="none" stroke="${color}" stroke-width="1.2" stroke-opacity="0.55"/>
  </svg>`;
  return 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
}

// ─── Cluster key from node ────────────────────────────────────────────────────

function clusterKey(node) {
  if (node.cluster) return node.cluster;
  if (node.type && node.type !== 'Unknown') return node.type;
  if (node.content_type && node.content_type !== 'Unknown') return node.content_type;
  const topics = node.topics || node.key_topics || [];
  if (topics.length > 0) return topics[0];
  return 'General';
}

// ─── Organic cluster shape placer ────────────────────────────────────────────
// Returns [{x,y}] for every node in the cluster using different geometric
// patterns per size so clusters look like distinct neural structures, not
// identical circles.

function computeClusterShape(size, cx, cy, radius, clusterIdx) {
  const positions = [];
  // Unique starting rotation per cluster — no two clusters face the same way
  const rot = (clusterIdx * 53 + 17) * (Math.PI / 180);
  const jit = (s) => (Math.random() - 0.5) * 2 * s;

  if (size === 1) {
    positions.push({ x: cx + jit(4), y: cy + jit(4) });

  } else if (size === 2) {
    // Dumbbell along the rotation axis
    const d = radius * 0.6;
    positions.push({ x: cx - d * Math.cos(rot) + jit(5), y: cy - d * Math.sin(rot) + jit(5) });
    positions.push({ x: cx + d * Math.cos(rot) + jit(5), y: cy + d * Math.sin(rot) + jit(5) });

  } else if (size === 3) {
    // Equilateral triangle
    for (let i = 0; i < 3; i++) {
      const ang = rot + (i / 3) * 2 * Math.PI - Math.PI / 2;
      positions.push({ x: cx + radius * Math.cos(ang) + jit(7), y: cy + radius * Math.sin(ang) + jit(7) });
    }

  } else if (size === 4) {
    // Diamond (rotated square)
    for (let i = 0; i < 4; i++) {
      const ang = rot + (i / 4) * 2 * Math.PI + Math.PI / 4;
      positions.push({ x: cx + radius * Math.cos(ang) + jit(7), y: cy + radius * Math.sin(ang) + jit(7) });
    }

  } else if (size === 5) {
    // Pentagon
    for (let i = 0; i < 5; i++) {
      const ang = rot + (i / 5) * 2 * Math.PI - Math.PI / 2;
      positions.push({ x: cx + radius * Math.cos(ang) + jit(8), y: cy + radius * Math.sin(ang) + jit(8) });
    }

  } else if (size === 6) {
    // Hexagon
    for (let i = 0; i < 6; i++) {
      const ang = rot + (i / 6) * 2 * Math.PI;
      positions.push({ x: cx + radius * Math.cos(ang) + jit(8), y: cy + radius * Math.sin(ang) + jit(8) });
    }

  } else if (size <= 9) {
    // Neuron: 1 central hub (soma) + irregular outer dendrite ring
    positions.push({ x: cx + jit(5), y: cy + jit(5) }); // soma
    const outer = size - 1;
    for (let i = 0; i < outer; i++) {
      const ang = rot + (i / outer) * 2 * Math.PI;
      const r = radius * (0.85 + Math.random() * 0.25); // organic variation
      positions.push({ x: cx + r * Math.cos(ang) + jit(9), y: cy + r * Math.sin(ang) + jit(9) });
    }

  } else if (size <= 16) {
    // Double-ring: inner polygon + offset outer ring (two shells of a neural cluster)
    const innerCount = Math.round(size * 0.36);
    const outerCount = size - innerCount;
    const innerR = radius * 0.45;
    for (let i = 0; i < innerCount; i++) {
      const ang = rot + (i / innerCount) * 2 * Math.PI;
      positions.push({ x: cx + innerR * Math.cos(ang) + jit(7), y: cy + innerR * Math.sin(ang) + jit(7) });
    }
    for (let i = 0; i < outerCount; i++) {
      const ang = rot + (Math.PI / outerCount) + (i / outerCount) * 2 * Math.PI;
      const r = radius * (0.88 + Math.random() * 0.2);
      positions.push({ x: cx + r * Math.cos(ang) + jit(10), y: cy + r * Math.sin(ang) + jit(10) });
    }

  } else {
    // Golden-angle phyllotaxis spiral — organic sunflower / dendritic mass
    const phi = 137.508 * (Math.PI / 180);
    const scale = (radius * 1.2) / Math.sqrt(size);
    for (let i = 0; i < size; i++) {
      const r = scale * Math.sqrt(i + 1);
      const ang = i * phi + rot;
      positions.push({ x: cx + r * Math.cos(ang) + jit(6), y: cy + r * Math.sin(ang) + jit(6) });
    }
  }

  return positions;
}

// ─── Phyllotaxis cluster-centre placement ─────────────────────────────────────

function computeClusterCenters(clusterKeys, W, H) {
  const n = clusterKeys.length;
  if (n === 0) return {};
  if (n === 1) return { [clusterKeys[0]]: { x: W / 2, y: H / 2 } };

  const cx = W / 2;
  const cy = H / 2;
  const goldenAngle = 137.508 * (Math.PI / 180);
  // Spread must be large enough so cluster rings don't overlap.
  // Phyllotaxis min-neighbour distance ≈ maxR * sqrt(2/n).
  // We need: 2 * maxInnerR < maxR * sqrt(2/n)  →  maxR grows with n.
  const maxR = Math.min(W, H) * Math.max(0.44, Math.min(0.58, 0.34 + clusterKeys.length * 0.016));
  const centers = {};

  clusterKeys.forEach((key, i) => {
    const r = maxR * Math.sqrt((i + 0.5) / n);
    const theta = i * goldenAngle;
    centers[key] = {
      x: cx + r * Math.cos(theta),
      y: cy + r * Math.sin(theta),
    };
  });

  return centers;
}

// ─── Cytoscape stylesheet ─────────────────────────────────────────────────────

function buildStylesheet() {
  return [
    {
      selector: 'node',
      style: {
        shape: 'ellipse',
        width: 'data(size)',
        height: 'data(size)',

        // SVG neuron-sphere background — replaces flat solid color
        'background-color': 'data(color)',      // fallback if image fails
        'background-opacity': 0,               // hide solid bg; SVG takes over
        'background-image': 'data(bgImage)',
        'background-fit': 'cover',
        'background-image-opacity': 1,

        // Label
        label: 'data(label)',
        'font-size': '9px',
        'font-family': "'Inter', 'Segoe UI', sans-serif",
        'font-weight': '600',
        color: '#e2e8f0',
        'text-valign': 'bottom',
        'text-halign': 'center',
        'text-margin-y': 4,
        'text-outline-width': 2,
        'text-outline-color': 'rgba(6,6,16,0.9)',
        'text-max-width': '76px',
        'text-wrap': 'ellipsis',

        // Outer aura / glow — coloured atmospheric halo
        'shadow-blur': 36,
        'shadow-color': 'data(color)',
        'shadow-opacity': 0.65,
        'shadow-offset-x': 0,
        'shadow-offset-y': 0,

        // Thin coloured rim (no white — SVG handles the rim look)
        'border-width': 0,
        'border-opacity': 0,

        'transition-property': 'shadow-blur, shadow-opacity, width, height, border-width',
        'transition-duration': '0.18s',
      },
    },
    {
      selector: 'node:selected',
      style: {
        'border-width': 2,
        'border-color': 'data(color)',
        'border-opacity': 1,
        'shadow-blur': 55,
        'shadow-opacity': 1,
        'z-index': 20,
      },
    },
    {
      selector: 'node.highlighted',
      style: {
        'shadow-blur': 48,
        'shadow-opacity': 0.85,
        'z-index': 15,
      },
    },
    {
      selector: 'node.dimmed',
      style: {
        opacity: 0.14,
        'shadow-opacity': 0.03,
      },
    },
    {
      selector: 'edge',
      style: {
        width: 'data(weight)',
        'line-color': 'data(color)',
        'line-opacity': 0.42,
        'curve-style': 'bezier',
        'target-arrow-shape': 'none',
        'transition-property': 'line-opacity, width',
        'transition-duration': '0.18s',
      },
    },
    {
      selector: 'edge.highlighted',
      style: {
        'line-opacity': 0.88,
        width: 2.8,
        'z-index': 10,
      },
    },
    {
      selector: 'edge.dimmed',
      style: {
        'line-opacity': 0.02,
      },
    },
  ];
}

// ─── Main Component ───────────────────────────────────────────────────────────

const KnowledgeGraphViewer = ({ data, selectedNode, onNodeSelect, onBackgroundClick }) => {
  const cyRef           = useRef(null);
  const containerRef    = useRef(null);
  const timeoutsRef     = useRef([]);
  const [isLayoutRunning, setIsLayoutRunning] = useState(false);
  const [nodeCount,  setNodeCount]  = useState(0);
  const [edgeCount,  setEdgeCount]  = useState(0);

  const clearAllTimeouts = useCallback(() => {
    timeoutsRef.current.forEach(id => clearTimeout(id));
    timeoutsRef.current = [];
  }, []);

  const track = useCallback((id) => {
    timeoutsRef.current.push(id);
    return id;
  }, []);

  useEffect(() => {
    if (!containerRef.current) return;

    const rawNodes = data?.nodes || [];
    const rawEdges = data?.edges || data?.links || [];

    if (rawNodes.length === 0) {
      if (cyRef.current) { cyRef.current.destroy(); cyRef.current = null; }
      setNodeCount(0);
      setEdgeCount(0);
      setIsLayoutRunning(false);
      return;
    }

    // ── 1. Cluster colours ───────────────────────────────────────────────────
    const clusterSet = new Set(rawNodes.map(n => clusterKey(n)));
    const clusterKeys = Array.from(clusterSet);
    const clusterColorMap = {};
    // Cache SVG per color so we don't regenerate for the same cluster
    const svgCache = {};
    clusterKeys.forEach((k, i) => {
      const color = CLUSTER_COLORS[i % CLUSTER_COLORS.length];
      clusterColorMap[k] = color;
      svgCache[k] = makeNodeSvg(color);
    });

    // ── 2. Phyllotaxis centres ────────────────────────────────────────────────
    const W = containerRef.current.offsetWidth  || 800;
    const H = containerRef.current.offsetHeight || 600;
    const centers = computeClusterCenters(clusterKeys, W, H);

    // ── 3. Degree pre-pass (count connections per node for size bonus) ────────
    const degreeMap = {};
    rawNodes.forEach(n => { degreeMap[String(n.id)] = 0; });
    rawEdges.forEach(e => {
      const s = String(e.source || e.from);
      const t = String(e.target || e.to);
      if (degreeMap[s] !== undefined) degreeMap[s]++;
      if (degreeMap[t] !== undefined) degreeMap[t]++;
    });
    const maxDeg = Math.max(...Object.values(degreeMap), 1);

    // ── 4. Pre-group nodes by cluster & pre-compute shaped positions ──────────
    const clusterNodeMap = {};   // cluster -> [nodeId, ...]
    clusterKeys.forEach(k => { clusterNodeMap[k] = []; });
    rawNodes.forEach(node => clusterNodeMap[clusterKey(node)].push(String(node.id)));

    const nodeClusterIndex = {}; // nodeId -> index within its cluster
    const clusterPositions = {}; // cluster -> [{x, y}, ...]
    clusterKeys.forEach((k, clusterIdx) => {
      clusterNodeMap[k].forEach((id, i) => { nodeClusterIndex[id] = i; });
      const size   = clusterNodeMap[k].length;
      const center = centers[k] || { x: W / 2, y: H / 2 };
      // Radius scales with node count but stays safe so cluster rings don't collide
      const baseR  = Math.min(62, Math.max(24, 14 + size * 6.5));
      clusterPositions[k] = computeClusterShape(size, center.x, center.y, baseR, clusterIdx);
    });

    // ── 5. Build node elements ───────────────────────────────────────────────
    const elements = [];

    rawNodes.forEach(node => {
      const id      = String(node.id);
      const cluster = clusterKey(node);
      const idx     = nodeClusterIndex[id] ?? 0;
      const pos     = clusterPositions[cluster]?.[idx] ?? centers[cluster] ?? { x: W / 2, y: H / 2 };

      // Node size: quality-scaled 16–46px so nodes stay readable but compact
      const quality  = node.quality_score || node.quality || 5;
      const degBonus = (degreeMap[id] / maxDeg) * 8;   // 0-8 bonus
      const nodeSize = Math.min(46, Math.max(16, 16 + quality * 1.9 + degBonus * 0.5));

      elements.push({
        group: 'nodes',
        data: {
          id,
          label:   node.title || node.name || id,
          color:   clusterColorMap[cluster],
          bgImage: svgCache[cluster],
          cluster,
          size: nodeSize,
          rawData: node,
        },
        position: pos,
      });
    });

    // ── 6. Build edge elements ───────────────────────────────────────────────
    const nodeClusterMap = {};
    elements.forEach(el => {
      if (el.group === 'nodes') nodeClusterMap[el.data.id] = el.data.cluster;
    });

    rawEdges.forEach((edge, i) => {
      const src = String(edge.source || edge.from);
      const tgt = String(edge.target || edge.to);
      if (!src || !tgt || src === tgt) return;
      const sameCluster = nodeClusterMap[src] === nodeClusterMap[tgt];
      const srcCluster  = nodeClusterMap[src] || 'default';

      elements.push({
        group: 'edges',
        data: {
          id: `e${i}-${src}-${tgt}`,
          source: src,
          target: tgt,
          weight:    sameCluster ? 1.4 : 0.6,
          color:     sameCluster
            ? clusterColorMap[srcCluster]
            : 'rgba(148,163,184,0.3)',
          sameCluster,
        },
      });
    });

    setNodeCount(rawNodes.length);
    setEdgeCount(rawEdges.length);

    // ── 8. Destroy old instance ───────────────────────────────────────────────
    clearAllTimeouts();
    if (cyRef.current) { cyRef.current.destroy(); cyRef.current = null; }

    setIsLayoutRunning(true);

    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: buildStylesheet(),
      layout: { name: 'preset' },
      userZoomingEnabled: true,
      userPanningEnabled: true,
      minZoom: 0.08,
      maxZoom: 4,
      wheelSensitivity: 0.28,
    });

    cyRef.current = cy;

    // ── 9. layoutstop ────────────────────────────────────────────────────────
    cy.one('layoutstop', () => {
      clearAllTimeouts();
      setIsLayoutRunning(false);
      try { cy.fit(undefined, 70); } catch (_) {}
    });

    // Safety fallback
    track(setTimeout(() => {
      setIsLayoutRunning(false);
      try { cy.fit(undefined, 70); } catch (_) {}
    }, 10000));

    // ── 10. Preset layout — nodes stay at their ring positions, no physics ──────
    if (rawNodes.length > 1) {
      cy.layout({ name: 'preset', fit: true, padding: 70 }).run();
    } else {
      cy.fit(undefined, 70);
      setIsLayoutRunning(false);
      clearAllTimeouts();
    }

    // ── 11. Interactions ─────────────────────────────────────────────────────
    cy.on('mouseover', 'node', e => {
      const node         = e.target;
      const connEdges    = node.connectedEdges();
      const neighbors    = connEdges.connectedNodes();
      cy.elements()
        .not(node).not(connEdges).not(neighbors)
        .addClass('dimmed');
      connEdges.addClass('highlighted');
      node.addClass('highlighted');
    });

    cy.on('mouseout', 'node', () => {
      cy.elements().removeClass('dimmed highlighted');
    });

    cy.on('tap', 'node', e => {
      if (onNodeSelect) onNodeSelect(e.target.data('rawData'));
    });

    cy.on('tap', e => {
      if (e.target === cy) {
        cy.elements().removeClass('dimmed highlighted');
        if (onBackgroundClick) onBackgroundClick();
      }
    });

    return () => {
      clearAllTimeouts();
      if (cyRef.current) { cyRef.current.destroy(); cyRef.current = null; }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data]);

  // Highlight externally selected node
  useEffect(() => {
    if (!cyRef.current) return;
    cyRef.current.elements().removeClass('dimmed highlighted');
    if (selectedNode?.id) {
      const node = cyRef.current.getElementById(String(selectedNode.id));
      if (node.length) {
        const edges = node.connectedEdges();
        edges.addClass('highlighted');
        cyRef.current.elements()
          .not(node).not(edges).not(edges.connectedNodes())
          .addClass('dimmed');
        cyRef.current.animate({ center: { eles: node }, zoom: 1.6 }, { duration: 320 });
      }
    }
  }, [selectedNode]);

  return (
    <Wrapper>
      <CyContainer ref={containerRef} />
      {nodeCount > 0 && (
        <CountBadge>{nodeCount} nodes · {edgeCount} edges</CountBadge>
      )}
      {isLayoutRunning && (
        <LoadingPill>
          <Spinner />
          <LoadingText>Arranging neural clusters…</LoadingText>
        </LoadingPill>
      )}
    </Wrapper>
  );
};

export default KnowledgeGraphViewer;
