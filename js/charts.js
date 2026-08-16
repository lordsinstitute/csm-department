// ============================================
// CyberRange AI — Chart.js Configurations
// ============================================

const CHART_COLORS = {
    cyan: '#00e5ff', purple: '#7c4dff', green: '#00e676',
    orange: '#ffab00', red: '#ff1744', blue: '#2979ff',
    cyanAlpha: 'rgba(0,229,255,.15)', purpleAlpha: 'rgba(124,77,255,.15)',
    gridColor: 'rgba(255,255,255,.04)', tickColor: '#505a70'
};

const baseScales = {
    x: { grid: { color: CHART_COLORS.gridColor }, ticks: { color: CHART_COLORS.tickColor, font: { family: 'Inter', size: 11 } } },
    y: { grid: { color: CHART_COLORS.gridColor }, ticks: { color: CHART_COLORS.tickColor, font: { family: 'Inter', size: 11 } } }
};
const baseLegend = { labels: { color: '#8892a8', font: { family: 'Inter', size: 12 }, boxWidth: 12, padding: 16 } };

function timeLabels(n) { const l = []; const now = new Date(); for (let i = n; i >= 0; i--) { const d = new Date(now - i * 60000); l.push(d.toTimeString().slice(0, 5)); } return l; }
function randArr(n, min, max) { return Array.from({ length: n }, () => Math.floor(Math.random() * (max - min + 1)) + min); }

const CyberCharts = {
    instances: {},

    // ----- DASHBOARD: Traffic Overview -----
    initDashTraffic(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        const labels = timeLabels(30);
        this.instances.dashTraffic = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    { label: 'Inbound (Mbps)', data: randArr(31, 800, 2200), borderColor: CHART_COLORS.cyan, backgroundColor: CHART_COLORS.cyanAlpha, fill: true, tension: .4, pointRadius: 0 },
                    { label: 'Outbound (Mbps)', data: randArr(31, 400, 1400), borderColor: CHART_COLORS.purple, backgroundColor: CHART_COLORS.purpleAlpha, fill: true, tension: .4, pointRadius: 0 }
                ]
            },
            options: { responsive: true, plugins: { legend: baseLegend }, scales: baseScales, animation: { duration: 800 } }
        });
    },

    // ----- DASHBOARD: Threat Distribution -----
    initDashThreat(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        this.instances.dashThreat = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Initial Access', 'Execution', 'Persistence', 'Priv Escalation', 'Defense Evasion', 'Credential Access', 'Lateral Movement', 'C2'],
                datasets: [{ data: [15, 12, 18, 9, 22, 14, 8, 11], backgroundColor: [CHART_COLORS.cyan, '#0091ea', CHART_COLORS.purple, '#aa00ff', CHART_COLORS.orange, CHART_COLORS.red, CHART_COLORS.green, CHART_COLORS.blue], borderWidth: 0 }]
            },
            options: { responsive: true, plugins: { legend: { ...baseLegend, position: 'right' } }, cutout: '65%' }
        });
    },

    // ----- TRAFFIC: Bandwidth Timeline -----
    initBandwidth(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        const labels = timeLabels(40);
        this.instances.bandwidth = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    { label: 'Real Traffic', data: randArr(41, 1500, 3200), borderColor: CHART_COLORS.cyan, backgroundColor: CHART_COLORS.cyanAlpha, fill: true, tension: .3, pointRadius: 0, borderWidth: 2 },
                    { label: 'GAN Generated', data: randArr(41, 1200, 2800), borderColor: CHART_COLORS.purple, backgroundColor: CHART_COLORS.purpleAlpha, fill: true, tension: .3, pointRadius: 0, borderWidth: 2 },
                    { label: 'Attack Traffic', data: randArr(41, 50, 400), borderColor: CHART_COLORS.red, backgroundColor: 'rgba(255,23,68,.1)', fill: true, tension: .3, pointRadius: 0, borderWidth: 2 }
                ]
            },
            options: { responsive: true, plugins: { legend: baseLegend }, scales: baseScales }
        });
    },

    // ----- TRAFFIC: Protocol Distribution -----
    initProtocol(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        this.instances.protocol = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['HTTP', 'HTTPS', 'DNS', 'SMB', 'SSH', 'RDP', 'Other'],
                datasets: [{ data: [35, 30, 15, 10, 5, 3, 2], backgroundColor: [CHART_COLORS.cyan, CHART_COLORS.purple, CHART_COLORS.green, CHART_COLORS.orange, CHART_COLORS.blue, CHART_COLORS.red, '#546e7a'], borderWidth: 0 }]
            },
            options: { responsive: true, plugins: { legend: { ...baseLegend, position: 'bottom' } }, cutout: '55%' }
        });
    },

    // ----- TRAFFIC: GAN Loss -----
    initGanLoss(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        const epochs = Array.from({ length: 50 }, (_, i) => `Epoch ${i * 25}`);
        const genLoss = Array.from({ length: 50 }, (_, i) => 3.5 * Math.exp(-i * 0.04) + Math.random() * 0.3);
        const discLoss = Array.from({ length: 50 }, (_, i) => 0.5 + 0.3 * Math.sin(i * 0.15) + Math.random() * 0.15);
        this.instances.ganLoss = new Chart(ctx, {
            type: 'line',
            data: {
                labels: epochs,
                datasets: [
                    { label: 'Generator Loss', data: genLoss, borderColor: CHART_COLORS.cyan, tension: .3, pointRadius: 0, borderWidth: 2 },
                    { label: 'Discriminator Loss', data: discLoss, borderColor: CHART_COLORS.red, tension: .3, pointRadius: 0, borderWidth: 2 }
                ]
            },
            options: { responsive: true, plugins: { legend: baseLegend }, scales: baseScales }
        });
    },

    // ----- TRAFFIC: Latency -----
    initLatency(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        const labels = timeLabels(30);
        this.instances.latency = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    { label: 'Latency (ms)', data: randArr(31, 1, 45), backgroundColor: randArr(31, 1, 45).map(v => v > 30 ? CHART_COLORS.red : v > 15 ? CHART_COLORS.orange : CHART_COLORS.cyan), borderWidth: 0, borderRadius: 3 }
                ]
            },
            options: { responsive: true, plugins: { legend: baseLegend }, scales: baseScales }
        });
    },

    // ----- USERS: Behavioral Radar -----
    initBehaviorRadar(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        this.instances.behaviorRadar = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Web Browsing', 'Email', 'File Access', 'CLI Usage', 'App Usage', 'Idle Time', 'Meeting', 'Code Editing'],
                datasets: [
                    { label: 'Analyst Profile', data: [65, 80, 70, 85, 50, 20, 45, 30], borderColor: CHART_COLORS.cyan, backgroundColor: CHART_COLORS.cyanAlpha, pointBackgroundColor: CHART_COLORS.cyan },
                    { label: 'Developer Profile', data: [40, 35, 55, 90, 75, 15, 30, 95], borderColor: CHART_COLORS.purple, backgroundColor: CHART_COLORS.purpleAlpha, pointBackgroundColor: CHART_COLORS.purple },
                    { label: 'Manager Profile', data: [50, 70, 40, 15, 60, 35, 85, 10], borderColor: CHART_COLORS.green, backgroundColor: 'rgba(0,230,118,.1)', pointBackgroundColor: CHART_COLORS.green }
                ]
            },
            options: {
                responsive: true, plugins: { legend: baseLegend },
                scales: { r: { grid: { color: CHART_COLORS.gridColor }, angleLines: { color: CHART_COLORS.gridColor }, pointLabels: { color: CHART_COLORS.tickColor, font: { family: 'Inter', size: 11 } }, ticks: { display: false }, suggestedMin: 0, suggestedMax: 100 } }
            }
        });
    },

    // ----- USERS: Activity Timeline -----
    initAgentTimeline(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        const labels = timeLabels(24);
        this.instances.agentTimeline = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    { label: 'Active Users', data: randArr(25, 20, 48), backgroundColor: CHART_COLORS.cyanAlpha, borderColor: CHART_COLORS.cyan, borderWidth: 1, borderRadius: 4 },
                    { label: 'Actions/min', data: randArr(25, 500, 2000), backgroundColor: CHART_COLORS.purpleAlpha, borderColor: CHART_COLORS.purple, borderWidth: 1, borderRadius: 4, yAxisID: 'y1' }
                ]
            },
            options: {
                responsive: true, plugins: { legend: baseLegend },
                scales: { ...baseScales, y1: { position: 'right', grid: { drawOnChartArea: false }, ticks: { color: CHART_COLORS.tickColor } } }
            }
        });
    },

    // ----- ATTACKS: Campaign Timeline -----
    initCampaign(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        const labels = timeLabels(20);
        this.instances.campaign = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    { label: 'Techniques Executed', data: randArr(21, 0, 8), borderColor: CHART_COLORS.red, backgroundColor: 'rgba(255,23,68,.1)', fill: true, tension: .3, stepped: 'before', pointRadius: 3, pointBackgroundColor: CHART_COLORS.red },
                    { label: 'Detections', data: randArr(21, 0, 5), borderColor: CHART_COLORS.green, backgroundColor: 'rgba(0,230,118,.1)', fill: true, tension: .3, pointRadius: 3, pointBackgroundColor: CHART_COLORS.green }
                ]
            },
            options: { responsive: true, plugins: { legend: baseLegend }, scales: baseScales }
        });
    },

    // ----- ANALYTICS: Incident Timeline -----
    initIncident(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        this.instances.incident = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: days,
                datasets: [
                    { label: 'Critical', data: randArr(7, 0, 8), backgroundColor: CHART_COLORS.red, borderRadius: 4 },
                    { label: 'Error', data: randArr(7, 2, 15), backgroundColor: CHART_COLORS.orange, borderRadius: 4 },
                    { label: 'Warning', data: randArr(7, 5, 25), backgroundColor: '#ffab0066', borderRadius: 4 },
                    { label: 'Info', data: randArr(7, 20, 80), backgroundColor: CHART_COLORS.cyanAlpha, borderRadius: 4 }
                ]
            },
            options: { responsive: true, plugins: { legend: baseLegend }, scales: { ...baseScales, x: { ...baseScales.x, stacked: true }, y: { ...baseScales.y, stacked: true } } }
        });
    },

    // ----- INFRASTRUCTURE: Resource Chart -----
    initResource(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;
        const labels = timeLabels(20);
        this.instances.resource = new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    { label: 'CPU %', data: randArr(21, 40, 90), borderColor: CHART_COLORS.cyan, tension: .4, pointRadius: 0, borderWidth: 2 },
                    { label: 'Memory %', data: randArr(21, 50, 80), borderColor: CHART_COLORS.purple, tension: .4, pointRadius: 0, borderWidth: 2 },
                    { label: 'Disk I/O %', data: randArr(21, 20, 60), borderColor: CHART_COLORS.green, tension: .4, pointRadius: 0, borderWidth: 2 },
                    { label: 'Network %', data: randArr(21, 60, 95), borderColor: CHART_COLORS.orange, tension: .4, pointRadius: 0, borderWidth: 2 }
                ]
            },
            options: { responsive: true, plugins: { legend: baseLegend }, scales: baseScales }
        });
    },

    // ----- Update chart with new data point -----
    pushData(chartKey, newDataPoints) {
        const chart = this.instances[chartKey];
        if (!chart) return;
        chart.data.labels.push(new Date().toTimeString().slice(0, 5));
        chart.data.labels.shift();
        chart.data.datasets.forEach((ds, i) => {
            ds.data.push(newDataPoints[i] != null ? newDataPoints[i] : ds.data[ds.data.length - 1]);
            ds.data.shift();
        });
        chart.update('none');
    }
};
