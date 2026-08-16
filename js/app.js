// ============================================
// CyberRange AI — Application Controller
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initTopbar();
    renderStaticContent();
    initCharts();
    animateCounters();
    startLiveUpdates();
    drawTopology();
});

// =================== NAVIGATION ===================
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const pageId = item.dataset.page;
            navItems.forEach(n => n.classList.remove('active'));
            item.classList.add('active');
            document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
            const target = document.getElementById('page-' + pageId);
            if (target) {
                target.classList.add('active');
                target.style.animation = 'none';
                target.offsetHeight; // reflow
                target.style.animation = '';
            }
            document.getElementById('pageBreadcrumb').textContent =
                item.querySelector('span').textContent;
            // Re-animate counters on page switch
            animateCounters(target);
            // Init charts for newly visible page
            initChartsForPage(pageId);
            // Close sidebar on mobile
            document.getElementById('sidebar').classList.remove('open');
        });
    });
}

function initTopbar() {
    document.getElementById('menuToggle').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('open');
    });
    document.getElementById('notifBtn').addEventListener('click', () => {
        document.getElementById('notifPanel').classList.toggle('open');
    });
    document.getElementById('clearNotifs')?.addEventListener('click', () => {
        document.getElementById('notifList').innerHTML = '<p style="text-align:center;color:var(--text-muted);padding:40px;">No notifications</p>';
    });
    renderNotifications();
}

// =================== STATIC CONTENT RENDERS ===================
function renderStaticContent() {
    renderActiveScenarios();
    renderAlerts();
    renderHealthGrid();
    renderTrafficTable();
    renderAgentTable();
    renderMitreMatrix();
    renderKillChain();
    renderIOCFeed();
    renderScenarioCards();
    renderYAML();
    renderLogViewer();
    renderHeatmap();
    renderGauges();
    renderContainers();
    renderVMs();
    renderPipeline();
}

function renderActiveScenarios() {
    const el = document.getElementById('activeScenariosList');
    if (!el) return;
    el.innerHTML = DATA.activeScenarios.map(s => `
        <div class="infra-item" style="cursor:pointer">
            <div class="infra-icon docker"><i class="fas fa-diagram-project"></i></div>
            <div class="infra-info">
                <div class="infra-name">${s.name}</div>
                <div class="infra-meta"><i class="fas fa-users"></i> ${s.users} users • ${s.status}</div>
            </div>
            <div style="text-align:right;min-width:80px">
                <div style="font-weight:700;font-size:.9rem;color:var(--cyan)">${s.progress}%</div>
                <div class="infra-bar" style="width:80px"><div class="infra-bar-fill fill-green" style="width:${s.progress}%"></div></div>
            </div>
        </div>
    `).join('');
}

function renderAlerts() {
    const el = document.getElementById('recentAlertsList');
    if (!el) return;
    const colorMap = { critical: 'var(--red)', error: '#ff6e40', warning: 'var(--orange)', info: 'var(--cyan)' };
    el.innerHTML = DATA.alerts.map(a => `
        <div class="infra-item" style="border-left:3px solid ${colorMap[a.severity]}">
            <div style="flex:1">
                <div class="infra-name" style="font-size:.82rem">${a.msg}</div>
                <div class="infra-meta">${a.src} • ${a.time}</div>
            </div>
            <span class="status-badge ${a.severity === 'critical' ? 'error' : a.severity === 'error' ? 'idle' : 'active'}" style="text-transform:uppercase;font-size:.65rem">${a.severity}</span>
        </div>
    `).join('');
}

function renderHealthGrid() {
    const el = document.getElementById('healthGrid');
    if (!el) return;
    el.innerHTML = DATA.health.map(h => `
        <div class="health-item ${h.status}">
            <div class="health-icon"><i class="fas ${h.icon}"></i></div>
            <div class="health-name">${h.name}</div>
            <div class="health-status">${h.label}</div>
        </div>
    `).join('');
}

function renderTrafficTable() {
    const tbody = document.querySelector('#trafficTable tbody');
    if (!tbody) return;
    let rows = '';
    for (let i = 0; i < 12; i++) {
        const r = generateTrafficRow();
        rows += `<tr>
            <td style="font-family:var(--mono);font-size:.8rem">${r.srcIP}</td>
            <td style="font-family:var(--mono);font-size:.8rem">${r.dstIP}</td>
            <td>${r.proto}</td>
            <td>${r.port}</td>
            <td>${r.bytes.toLocaleString()}</td>
            <td><span class="status-badge ${r.status}">${r.status}</span></td>
        </tr>`;
    }
    tbody.innerHTML = rows;
}

function renderAgentTable() {
    const tbody = document.querySelector('#agentTable tbody');
    if (!tbody) return;
    tbody.innerHTML = DATA.agents.map(a => `
        <tr>
            <td><strong>${a.name}</strong></td>
            <td>${a.role}</td>
            <td><span class="status-badge ${a.status}">${a.status}</span></td>
            <td>${a.actions}</td>
            <td>${a.session}</td>
            <td>${a.workflow}</td>
            <td><button class="btn btn-sm btn-outline"><i class="fas fa-eye"></i></button></td>
        </tr>
    `).join('');
}

function renderMitreMatrix() {
    const el = document.getElementById('mitreMatrix');
    if (!el) return;
    el.innerHTML = DATA.mitre.tactics.map(tac => `
        <div class="mitre-col">
            <div class="mitre-header">${tac.name}</div>
            ${tac.techniques.map(t => `<div class="mitre-tech ${DATA.mitre.usedTechniques.includes(t) ? 'used' : ''}">${t}</div>`).join('')}
        </div>
    `).join('');
}

function renderKillChain() {
    const el = document.getElementById('killChain');
    if (!el) return;
    el.innerHTML = DATA.killChain.map(p => `
        <div class="kc-phase ${p.status}">
            <span class="kc-icon"><i class="fas ${p.icon}"></i></span>
            <span class="kc-name">${p.name}</span>
        </div>
    `).join('');
}

function renderIOCFeed() {
    const el = document.getElementById('iocFeed');
    if (!el) return;
    el.innerHTML = DATA.iocs.map(i => `
        <div class="ioc-item">
            <span class="ioc-type ${i.type}">${i.type}</span>
            <span class="ioc-value">${i.value}</span>
            <span style="flex:1;font-size:.78rem;color:var(--text-secondary)">${i.desc}</span>
            <span class="ioc-time">${i.time}</span>
        </div>
    `).join('');
}

function renderScenarioCards() {
    const el = document.getElementById('scenarioCards');
    if (!el) return;
    el.innerHTML = DATA.scenarios.map(s => `
        <div class="scenario-card">
            <div class="sc-header">
                <div class="sc-title">${s.title}</div>
                <span class="sc-diff ${s.diff}">${s.diff}</span>
            </div>
            <div class="sc-desc">${s.desc}</div>
            <div class="sc-meta">
                <span><i class="fas fa-users"></i> ${s.users} users</span>
                <span><i class="fas fa-clock"></i> ${s.duration}</span>
                <span><i class="fas fa-crosshairs"></i> ${s.attacks} attacks</span>
            </div>
            <div class="sc-actions">
                <button class="btn btn-sm btn-primary"><i class="fas fa-play"></i> Launch</button>
                <button class="btn btn-sm btn-outline"><i class="fas fa-pen"></i> Edit</button>
            </div>
        </div>
    `).join('');
}

function renderYAML() {
    const el = document.getElementById('yamlPreview');
    if (!el) return;
    el.textContent = DATA.yaml;
}

function renderLogViewer() {
    const el = document.getElementById('logViewer');
    if (!el) return;
    let logs = '';
    for (let i = 0; i < 40; i++) {
        const log = generateLogEntry();
        logs += `<div class="log-entry"><span class="log-time">${log.time}</span><span class="log-level ${log.level}">${log.level}</span><span class="log-src">[${log.src}]</span><span class="log-msg">${log.msg}</span></div>`;
    }
    el.innerHTML = logs;
    el.scrollTop = el.scrollHeight;
    // Filter
    document.getElementById('logLevel')?.addEventListener('change', function () {
        filterLogs();
    });
    document.getElementById('logFilter')?.addEventListener('input', function () {
        filterLogs();
    });
}

function filterLogs() {
    const level = document.getElementById('logLevel').value;
    const text = document.getElementById('logFilter').value.toLowerCase();
    const entries = document.querySelectorAll('#logViewer .log-entry');
    entries.forEach(e => {
        const entryLevel = e.querySelector('.log-level').textContent.trim().toLowerCase();
        const entryText = e.textContent.toLowerCase();
        const matchLevel = level === 'all' || entryLevel === level;
        const matchText = !text || entryText.includes(text);
        e.style.display = matchLevel && matchText ? '' : 'none';
    });
}

function renderHeatmap() {
    const el = document.getElementById('detectionHeatmap');
    if (!el) return;
    let cells = '';
    for (let day = 0; day < 7; day++) {
        for (let hour = 0; hour < 24; hour++) {
            const val = Math.floor(Math.random() * 6);
            cells += `<div class="heat-cell heat-${val}" title="Day ${day + 1}, Hour ${hour}:00 — ${val} detections"></div>`;
        }
    }
    el.innerHTML = cells;
}

function renderGauges() {
    const el = document.getElementById('gaugeGrid');
    if (!el) return;
    el.innerHTML = DATA.gauges.map(g => `
        <div class="gauge">
            <div class="gauge-circle" style="--pct:${g.value}%;background:conic-gradient(${g.color} ${g.value}%, rgba(255,255,255,.06) ${g.value}%)">
                <span class="gauge-val">${g.value}%</span>
            </div>
            <div class="gauge-label">${g.label}</div>
        </div>
    `).join('');
}

function renderContainers() {
    const el = document.getElementById('containerList');
    if (!el) return;
    el.innerHTML = DATA.containers.map(c => {
        const fillClass = c.cpu > 75 ? 'fill-red' : c.cpu > 50 ? 'fill-yellow' : 'fill-green';
        return `
        <div class="infra-item">
            <div class="infra-icon docker"><i class="fab fa-docker"></i></div>
            <div class="infra-info">
                <div class="infra-name">${c.name}</div>
                <div class="infra-meta">${c.image}</div>
            </div>
            <div style="text-align:right">
                <div style="font-size:.72rem;color:var(--text-muted)">CPU ${c.cpu}% • Mem ${c.mem}%</div>
                <div class="infra-bar"><div class="infra-bar-fill ${fillClass}" style="width:${c.cpu}%"></div></div>
            </div>
            <span class="status-badge ${c.status}">${c.status}</span>
        </div>`;
    }).join('');
}

function renderVMs() {
    const el = document.getElementById('vmList');
    if (!el) return;
    el.innerHTML = DATA.vms.map(v => {
        const fillClass = v.cpu > 75 ? 'fill-red' : v.cpu > 50 ? 'fill-yellow' : 'fill-green';
        return `
        <div class="infra-item">
            <div class="infra-icon vm"><i class="fas fa-hard-drive"></i></div>
            <div class="infra-info">
                <div class="infra-name">${v.name}</div>
                <div class="infra-meta">${v.os}</div>
            </div>
            <div style="text-align:right">
                <div style="font-size:.72rem;color:var(--text-muted)">CPU ${v.cpu}% • Mem ${v.mem}%</div>
                <div class="infra-bar"><div class="infra-bar-fill ${fillClass}" style="width:${v.cpu}%"></div></div>
            </div>
            <span class="status-badge ${v.status}">${v.status}</span>
        </div>`;
    }).join('');
}

function renderPipeline() {
    const el = document.getElementById('deployPipeline');
    if (!el) return;
    el.innerHTML = DATA.pipeline.map((p, i) => {
        const arrow = i < DATA.pipeline.length - 1 ? '<span class="pipe-arrow"><i class="fas fa-chevron-right"></i></span>' : '';
        return `<div class="pipe-stage ${p.status}"><span class="pipe-icon"><i class="fas ${p.icon}"></i></span>${p.name}</div>${arrow}`;
    }).join('');
}

function renderNotifications() {
    const el = document.getElementById('notifList');
    if (!el) return;
    el.innerHTML = DATA.notifications.map(n => `
        <div class="notif-item ${n.type}">
            <div class="notif-title">${n.title}</div>
            <div class="notif-body">${n.body}</div>
            <div class="notif-time">${n.time}</div>
        </div>
    `).join('');
}

// =================== CHARTS ===================
const chartsInitialized = {};

function initCharts() {
    initChartsForPage('dashboard');
}

function initChartsForPage(page) {
    if (chartsInitialized[page]) return;
    chartsInitialized[page] = true;
    switch (page) {
        case 'dashboard':
            CyberCharts.initDashTraffic('dashTrafficChart');
            CyberCharts.initDashThreat('dashThreatChart');
            break;
        case 'traffic':
            CyberCharts.initBandwidth('bandwidthChart');
            CyberCharts.initProtocol('protocolChart');
            CyberCharts.initGanLoss('ganLossChart');
            CyberCharts.initLatency('latencyChart');
            break;
        case 'users':
            CyberCharts.initBehaviorRadar('behaviorRadar');
            CyberCharts.initAgentTimeline('agentTimelineChart');
            break;
        case 'attacks':
            CyberCharts.initCampaign('campaignChart');
            break;
        case 'analytics':
            CyberCharts.initIncident('incidentChart');
            break;
        case 'infrastructure':
            CyberCharts.initResource('resourceChart');
            break;
    }
}

// =================== ANIMATED COUNTERS ===================
function animateCounters(container) {
    const scope = container || document;
    const counters = scope.querySelectorAll('.kpi-value[data-count]');
    counters.forEach(el => {
        const target = parseInt(el.dataset.count);
        const duration = 1200;
        const start = performance.now();
        el.textContent = '0';
        function step(ts) {
            const progress = Math.min((ts - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease out cubic
            el.textContent = Math.floor(eased * target).toLocaleString();
            if (progress < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    });
}

// =================== LIVE UPDATES ===================
function startLiveUpdates() {
    // Update traffic chart every 3s
    setInterval(() => {
        CyberCharts.pushData('dashTraffic', [randBetween(800, 2200), randBetween(400, 1400)]);
        CyberCharts.pushData('bandwidth', [randBetween(1500, 3200), randBetween(1200, 2800), randBetween(50, 400)]);
        CyberCharts.pushData('resource', [randBetween(40, 90), randBetween(50, 80), randBetween(20, 60), randBetween(60, 95)]);
    }, 3000);

    // Append new log entry every 2s
    setInterval(() => {
        const viewer = document.getElementById('logViewer');
        if (!viewer) return;
        const log = generateLogEntry();
        const div = document.createElement('div');
        div.className = 'log-entry';
        div.innerHTML = `<span class="log-time">${log.time}</span><span class="log-level ${log.level}">${log.level}</span><span class="log-src">[${log.src}]</span><span class="log-msg">${log.msg}</span>`;
        viewer.appendChild(div);
        if (viewer.children.length > 100) viewer.removeChild(viewer.firstChild);
        viewer.scrollTop = viewer.scrollHeight;
    }, 2000);

    // Refresh traffic table every 5s
    setInterval(() => {
        renderTrafficTable();
    }, 5000);
}

// =================== TOPOLOGY CANVAS ===================
function drawTopology() {
    const canvas = document.getElementById('topologyCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const W = canvas.width = canvas.parentElement.offsetWidth - 40;
    const H = canvas.height = 400;

    const nodes = [
        { x: W / 2, y: 40, label: 'Internet', color: '#ff1744', icon: '🌐' },
        { x: W / 2, y: 120, label: 'Firewall', color: '#ffab00', icon: '🛡️' },
        { x: W / 4, y: 200, label: 'DMZ', color: '#00e5ff', icon: '🖥️' },
        { x: W / 2, y: 200, label: 'Core Switch', color: '#7c4dff', icon: '🔄' },
        { x: 3 * W / 4, y: 200, label: 'IDS/IPS', color: '#00e676', icon: '👁️' },
        { x: W / 6, y: 300, label: 'Web Server', color: '#00e5ff', icon: '🌐' },
        { x: W / 3, y: 300, label: 'Mail Server', color: '#00e5ff', icon: '📧' },
        { x: W / 2, y: 300, label: 'AD Controller', color: '#7c4dff', icon: '🏛️' },
        { x: 2 * W / 3, y: 300, label: 'File Server', color: '#7c4dff', icon: '📁' },
        { x: 5 * W / 6, y: 300, label: 'SIEM', color: '#00e676', icon: '📊' },
        { x: W / 4, y: 380, label: 'User Subnet', color: '#ffab00', icon: '👥' },
        { x: 3 * W / 4, y: 380, label: 'Server Farm', color: '#ffab00', icon: '🗄️' },
    ];

    const edges = [[0, 1], [1, 2], [1, 3], [1, 4], [2, 5], [2, 6], [3, 7], [3, 8], [4, 9], [3, 10], [3, 11]];

    function draw() {
        ctx.clearRect(0, 0, W, H);
        // Draw edges
        edges.forEach(([a, b]) => {
            ctx.beginPath();
            ctx.moveTo(nodes[a].x, nodes[a].y);
            ctx.lineTo(nodes[b].x, nodes[b].y);
            ctx.strokeStyle = 'rgba(0,229,255,0.2)';
            ctx.lineWidth = 1.5;
            ctx.stroke();
            // Animate packet dots
            const t = (Date.now() % 3000) / 3000;
            const px = nodes[a].x + (nodes[b].x - nodes[a].x) * t;
            const py = nodes[a].y + (nodes[b].y - nodes[a].y) * t;
            ctx.beginPath();
            ctx.arc(px, py, 2.5, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(0,229,255,0.7)';
            ctx.fill();
        });
        // Draw nodes
        nodes.forEach(n => {
            ctx.beginPath();
            ctx.arc(n.x, n.y, 22, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(12,18,40,0.9)';
            ctx.fill();
            ctx.strokeStyle = n.color;
            ctx.lineWidth = 2;
            ctx.stroke();
            ctx.font = '16px serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(n.icon, n.x, n.y);
            ctx.font = '10px Inter, sans-serif';
            ctx.fillStyle = '#8892a8';
            ctx.fillText(n.label, n.x, n.y + 34);
        });
        requestAnimationFrame(draw);
    }
    draw();
}
