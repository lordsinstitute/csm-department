// ============================================
// CyberRange AI — Fake Data & Generators
// ============================================

const DATA = {
    // ----- MITRE ATT&CK -----
    mitre: {
        tactics: [
            { id: 'TA0043', name: 'Reconnaissance', techniques: ['Active Scanning','Gather Victim Info','Search Open Websites','Phishing for Info','Search Victim Networks'] },
            { id: 'TA0042', name: 'Resource Dev', techniques: ['Acquire Infrastructure','Compromise Accounts','Develop Capabilities','Establish Accounts','Obtain Capabilities'] },
            { id: 'TA0001', name: 'Initial Access', techniques: ['Drive-by Compromise','Exploit Public App','External Remote Svc','Phishing','Supply Chain','Valid Accounts'] },
            { id: 'TA0002', name: 'Execution', techniques: ['Command & Script','Container Admin','Native API','Scheduled Task','User Execution','WMI'] },
            { id: 'TA0003', name: 'Persistence', techniques: ['Account Manipulation','Boot Autostart','Create Account','Hijack Flow','Scheduled Task','Server Software'] },
            { id: 'TA0004', name: 'Priv Escalation', techniques: ['Abuse Elevation','Access Token','Boot Autostart','Domain Policy','Hijack Flow','Process Injection'] },
            { id: 'TA0005', name: 'Defense Evasion', techniques: ['Deobfuscate','File Deletion','Masquerading','Obfuscated Files','Process Injection','Rootkit'] },
            { id: 'TA0006', name: 'Credential Access', techniques: ['Brute Force','Credentials from Store','Kerberoasting','LLMNR Poisoning','OS Credential Dump','Steal Tokens'] },
            { id: 'TA0007', name: 'Discovery', techniques: ['Account Discovery','File & Dir Discovery','Network Scanning','Permission Groups','Remote System Disc','System Info'] },
            { id: 'TA0008', name: 'Lateral Movement', techniques: ['Exploitation of Remote','Internal Spearphish','Lateral Tool Transfer','Remote Desktop','SMB/Windows Share','SSH'] },
            { id: 'TA0009', name: 'Collection', techniques: ['Archive Collected','Audio Capture','Clipboard Data','Data from Local','Email Collection','Screen Capture'] },
            { id: 'TA0011', name: 'C2', techniques: ['Application Layer','Data Encoding','Dynamic Resolution','Encrypted Channel','Ingress Tool','Proxy'] },
            { id: 'TA0010', name: 'Exfiltration', techniques: ['Automated Exfil','Exfil Over C2','Exfil Over Alt Proto','Exfil Over Web','Scheduled Transfer','Transfer to Cloud'] },
            { id: 'TA0040', name: 'Impact', techniques: ['Account Access Removal','Data Destruction','Data Encryption','Defacement','Disk Wipe','Service Stop'] }
        ],
        usedTechniques: ['Phishing','Valid Accounts','Process Injection','Kerberoasting','OS Credential Dump','Lateral Tool Transfer','Encrypted Channel','Exfil Over C2','Masquerading','Brute Force','Command & Script','Remote Desktop','Data Encryption','Active Scanning','Network Scanning','SMB/Windows Share','Application Layer']
    },

    // ----- KILL CHAIN PHASES -----
    killChain: [
        { name: 'Recon', icon: 'fa-binoculars', status: 'completed' },
        { name: 'Weaponize', icon: 'fa-hammer', status: 'completed' },
        { name: 'Deliver', icon: 'fa-envelope', status: 'completed' },
        { name: 'Exploit', icon: 'fa-bug', status: 'completed' },
        { name: 'Install', icon: 'fa-download', status: 'active-phase' },
        { name: 'C2', icon: 'fa-tower-broadcast', status: 'pending' },
        { name: 'Actions', icon: 'fa-flag', status: 'pending' }
    ],

    // ----- SCENARIOS -----
    scenarios: [
        { title: 'APT29 Enterprise Intrusion', diff: 'hard', desc: 'Simulate Cozy Bear TTPs against a multi-domain Windows AD environment with lateral movement and data exfiltration.', users: 12, duration: '4h', attacks: 23 },
        { title: 'Ransomware Response', diff: 'hard', desc: 'Respond to a simulated LockBit 3.0 ransomware outbreak affecting critical file servers and domain controllers.', users: 8, duration: '3h', attacks: 15 },
        { title: 'Insider Threat Detection', diff: 'medium', desc: 'Identify and contain a rogue employee exfiltrating sensitive data through encrypted channels and USB devices.', users: 6, duration: '2h', attacks: 9 },
        { title: 'Cloud Breach Scenario', diff: 'medium', desc: 'Defend against unauthorized access to AWS infrastructure via compromised IAM credentials and S3 bucket misconfigs.', users: 10, duration: '3h', attacks: 18 },
        { title: 'Phishing Campaign', diff: 'easy', desc: 'Train SOC analysts on identifying and triaging a multi-stage phishing campaign targeting executive accounts.', users: 15, duration: '1.5h', attacks: 7 },
        { title: 'Supply Chain Attack', diff: 'hard', desc: 'Investigate a compromised software update mechanism leading to backdoor deployment across the enterprise.', users: 5, duration: '5h', attacks: 31 }
    ],

    // ----- YAML CONFIG -----
    yaml: `scenario:
  name: "APT29 Enterprise Intrusion"
  version: "2.1.0"
  difficulty: hard
  duration: 4h

network:
  topology: enterprise-standard
  subnets:
    - name: corporate-lan
      cidr: 10.10.0.0/16
      vlan_id: 100
    - name: dmz
      cidr: 172.16.0.0/24
      vlan_id: 200
    - name: server-farm
      cidr: 10.20.0.0/24
      vlan_id: 300

traffic_generation:
  model: gan-v3
  bandwidth_target: 2800Mbps
  protocols:
    - { name: HTTP, weight: 0.35 }
    - { name: HTTPS, weight: 0.30 }
    - { name: DNS, weight: 0.15 }
    - { name: SMB, weight: 0.10 }
    - { name: SSH, weight: 0.05 }
    - { name: RDP, weight: 0.05 }

user_emulation:
  agent_count: 48
  roles:
    - { type: analyst, count: 12 }
    - { type: developer, count: 15 }
    - { type: manager, count: 8 }
    - { type: sysadmin, count: 5 }
    - { type: executive, count: 4 }
    - { type: intern, count: 4 }

attack:
  framework: mitre-attack-v14
  campaigns:
    - name: primary-intrusion
      tactics: [initial-access, execution, persistence]
      evasion: true
    - name: lateral-spread
      tactics: [lateral-movement, credential-access]
      evasion: true

monitoring:
  elk_endpoint: https://elk.local:9200
  metrics_interval: 5s
  alerting:
    slack: true
    email: true`,

    // ----- AGENTS -----
    agents: [
        { name: 'Sarah Chen', role: 'Security Analyst', status: 'active', actions: 342, session: '2h 14m', workflow: 'Incident Triage' },
        { name: 'Marcus Wright', role: 'Developer', status: 'active', actions: 218, session: '1h 47m', workflow: 'Code Review' },
        { name: 'Elena Volkov', role: 'Sys Admin', status: 'active', actions: 156, session: '3h 02m', workflow: 'Server Maintenance' },
        { name: 'James Nakamura', role: 'Manager', status: 'idle', actions: 87, session: '0h 34m', workflow: 'Report Review' },
        { name: 'Aisha Patel', role: 'Developer', status: 'active', actions: 291, session: '2h 38m', workflow: 'API Development' },
        { name: 'Tom Anderson', role: 'SOC Analyst', status: 'active', actions: 423, session: '4h 12m', workflow: 'Threat Hunting' },
        { name: 'Li Wei', role: 'Intern', status: 'active', actions: 64, session: '1h 05m', workflow: 'Log Analysis' },
        { name: 'Rachel Kim', role: 'Executive', status: 'idle', actions: 12, session: '0h 15m', workflow: 'Dashboard Review' },
        { name: 'Dmitri Sokolov', role: 'Pentester', status: 'active', actions: 567, session: '3h 45m', workflow: 'Vulnerability Scan' },
        { name: 'Maria Garcia', role: 'Developer', status: 'active', actions: 198, session: '1h 22m', workflow: 'Database Queries' },
    ],

    // ----- IOCs -----
    iocs: [
        { type: 'ip', value: '185.243.115.47', desc: 'C2 Server Communication', time: '2m ago' },
        { type: 'domain', value: 'evil-update.darknet.xyz', desc: 'Malware Distribution Point', time: '5m ago' },
        { type: 'hash', value: 'a3f2b8e91c4d...7f2e', desc: 'Cobalt Strike Beacon', time: '8m ago' },
        { type: 'ip', value: '91.234.99.102', desc: 'Data Exfiltration Endpoint', time: '12m ago' },
        { type: 'url', value: 'https://cdn.legit-update.com/payload.exe', desc: 'Staged Payload Delivery', time: '15m ago' },
        { type: 'hash', value: 'e7d1f4a82b3c...9a1d', desc: 'Mimikatz Variant', time: '18m ago' },
        { type: 'domain', value: 'auth-microsoft365.phish.io', desc: 'Credential Harvesting', time: '22m ago' },
        { type: 'ip', value: '45.77.128.91', desc: 'Tor Exit Node', time: '28m ago' },
        { type: 'url', value: 'http://10.10.5.14:8443/beacon', desc: 'Internal C2 Callback', time: '31m ago' },
        { type: 'hash', value: 'c9b3e2d7f5a1...4c8b', desc: 'Custom RAT Binary', time: '35m ago' },
    ],

    // ----- CONTAINERS -----
    containers: [
        { name: 'nginx-proxy', image: 'nginx:1.25', cpu: 12, mem: 28, status: 'running' },
        { name: 'elk-elasticsearch', image: 'elastic/es:8.11', cpu: 67, mem: 82, status: 'running' },
        { name: 'elk-logstash', image: 'elastic/logstash:8.11', cpu: 45, mem: 61, status: 'running' },
        { name: 'elk-kibana', image: 'elastic/kibana:8.11', cpu: 23, mem: 44, status: 'running' },
        { name: 'gan-traffic-gen', image: 'cyberrange/gan:3.2', cpu: 89, mem: 76, status: 'running' },
        { name: 'user-emulator', image: 'cyberrange/emu:2.1', cpu: 34, mem: 52, status: 'running' },
        { name: 'attack-engine', image: 'cyberrange/attack:1.8', cpu: 78, mem: 65, status: 'running' },
        { name: 'dns-server', image: 'coredns:1.11', cpu: 5, mem: 15, status: 'running' },
        { name: 'mail-server', image: 'mailhog:latest', cpu: 8, mem: 22, status: 'running' },
        { name: 'ad-controller', image: 'samba-ad:4.19', cpu: 42, mem: 58, status: 'running' },
        { name: 'vuln-webapp', image: 'dvwa:latest', cpu: 15, mem: 31, status: 'stopped' },
        { name: 'honeypot-ssh', image: 'cowrie:latest', cpu: 3, mem: 12, status: 'running' },
    ],

    // ----- VMs -----
    vms: [
        { name: 'DC-PRIMARY', os: 'Windows Server 2022', cpu: 45, mem: 72, status: 'running' },
        { name: 'DC-BACKUP', os: 'Windows Server 2022', cpu: 22, mem: 48, status: 'running' },
        { name: 'FILE-SERVER-01', os: 'Windows Server 2019', cpu: 38, mem: 65, status: 'running' },
        { name: 'LINUX-WEB-01', os: 'Ubuntu 22.04 LTS', cpu: 56, mem: 43, status: 'running' },
        { name: 'KALI-ATTACKER', os: 'Kali Linux 2024.1', cpu: 71, mem: 58, status: 'running' },
        { name: 'WIN10-USER-01', os: 'Windows 10 Pro', cpu: 33, mem: 52, status: 'running' },
        { name: 'WIN10-USER-02', os: 'Windows 10 Pro', cpu: 28, mem: 47, status: 'running' },
        { name: 'SIEM-SERVER', os: 'CentOS Stream 9', cpu: 62, mem: 78, status: 'running' },
    ],

    // ----- PIPELINE -----
    pipeline: [
        { name: 'Pull Images', icon: 'fa-download', status: 'done' },
        { name: 'Build Network', icon: 'fa-network-wired', status: 'done' },
        { name: 'Deploy VMs', icon: 'fa-server', status: 'done' },
        { name: 'Configure AD', icon: 'fa-sitemap', status: 'done' },
        { name: 'Start Traffic', icon: 'fa-wave-square', status: 'running' },
        { name: 'Deploy Agents', icon: 'fa-robot', status: 'queued' },
        { name: 'Arm Attacks', icon: 'fa-crosshairs', status: 'queued' },
        { name: 'Health Check', icon: 'fa-heart-pulse', status: 'queued' },
    ],

    // ----- HEALTH ITEMS -----
    health: [
        { name: 'GAN Engine', icon: 'fa-brain', status: 'ok', label: 'Operational' },
        { name: 'ELK Stack', icon: 'fa-layer-group', status: 'ok', label: 'Operational' },
        { name: 'Docker Host', icon: 'fab fa-docker', status: 'ok', label: 'Operational' },
        { name: 'Network Core', icon: 'fa-network-wired', status: 'warn', label: 'High Load' },
        { name: 'Disk I/O', icon: 'fa-hard-drive', status: 'ok', label: 'Operational' },
        { name: 'API Gateway', icon: 'fa-plug', status: 'ok', label: 'Operational' },
    ],

    // ----- GAUGES -----
    gauges: [
        { label: 'CPU Load', value: 73, color: 'var(--cyan)' },
        { label: 'Memory', value: 61, color: 'var(--purple)' },
        { label: 'Disk I/O', value: 42, color: 'var(--green)' },
        { label: 'Network', value: 87, color: 'var(--orange)' },
    ],

    // ----- NOTIFICATIONS -----
    notifications: [
        { type: 'critical', title: 'Lateral Movement Detected', body: 'SMB/Windows Admin Share access from KALI-ATTACKER to FILE-SERVER-01', time: '2 min ago' },
        { type: 'critical', title: 'Credential Dump Detected', body: 'LSASS memory dump attempt on DC-PRIMARY via procdump.exe', time: '5 min ago' },
        { type: 'warning', title: 'High CPU on GAN Engine', body: 'Container gan-traffic-gen CPU at 89% — consider scaling', time: '12 min ago' },
        { type: 'info', title: 'New Agent Deployed', body: 'User emulation agent "Dmitri Sokolov" joined the scenario', time: '18 min ago' },
        { type: 'warning', title: 'Unusual DNS Queries', body: '847 DNS queries to non-standard TLDs in last 5 minutes', time: '25 min ago' },
    ],

    // ----- ACTIVE SCENARIOS -----
    activeScenarios: [
        { name: 'APT29 Enterprise Intrusion', progress: 68, status: 'In Progress', users: 12, severity: 'high' },
        { name: 'Ransomware Response', progress: 34, status: 'In Progress', users: 8, severity: 'critical' },
        { name: 'Insider Threat Detection', progress: 92, status: 'Completing', users: 6, severity: 'medium' },
    ],

    // ----- RECENT ALERTS -----
    alerts: [
        { severity: 'critical', msg: 'Kerberoasting attempt detected on DC-PRIMARY', time: '1m ago', src: 'ATT&CK T1558.003' },
        { severity: 'critical', msg: 'Cobalt Strike beacon callback to 185.243.115.47:443', time: '3m ago', src: 'NDR Engine' },
        { severity: 'error', msg: 'Failed login brute force: 47 attempts in 60s on SSH', time: '7m ago', src: 'Auth Monitor' },
        { severity: 'warning', msg: 'Unusual PowerShell encoded command execution', time: '11m ago', src: 'EDR Agent' },
        { severity: 'warning', msg: 'DNS tunneling pattern detected on port 53', time: '15m ago', src: 'Traffic Analyzer' },
        { severity: 'info', msg: 'New TLS certificate installed on nginx-proxy', time: '22m ago', src: 'Config Manager' },
        { severity: 'info', msg: 'ELK index rotation completed successfully', time: '30m ago', src: 'ELK Stack' },
    ]
};

// ----- LOG GENERATOR -----
const LOG_SOURCES = ['kernel','sshd','nginx','elasticsearch','docker','attack-engine','gan-model','user-agent','kibana','logstash','firewall','dns-server'];
const LOG_MESSAGES = {
    critical: [
        'CRITICAL: Memory allocation failure in traffic generator — OOM killer invoked',
        'CRITICAL: Unauthorized root login detected from 10.10.5.99',
        'CRITICAL: Ransomware encryption pattern detected on FILE-SERVER-01',
        'CRITICAL: Domain admin credentials compromised via pass-the-hash',
    ],
    error: [
        'ERROR: Connection refused to Elasticsearch cluster node-3:9200',
        'ERROR: TLS handshake failed — certificate expired for api.internal',
        'ERROR: Container gan-traffic-gen exited with code 137 (OOMKilled)',
        'ERROR: Failed to authenticate user via Kerberos — clock skew too great',
    ],
    warning: [
        'WARN: CPU utilization exceeded 85% threshold on attack-engine',
        'WARN: Disk usage at 78% on /var/log — consider rotation',
        'WARN: 23 failed SSH login attempts from 10.10.3.45 in last 5min',
        'WARN: GAN discriminator loss diverging — epoch 847',
    ],
    info: [
        'INFO: New user agent deployed — ID:agent-048 role:developer',
        'INFO: Traffic generation model checkpoint saved — epoch 1200',
        'INFO: Scenario "APT29" phase 4 initiated — persistence established',
        'INFO: ELK index rotated successfully — logs-2026.03.12',
        'INFO: Container health check passed — all 34 containers operational',
        'INFO: DNS query resolved: internal.cyberrange.lab → 10.10.1.5',
    ],
    debug: [
        'DEBUG: GAN generator output tensor shape: [1, 3, 64, 64]',
        'DEBUG: Agent decision tree traversal — node: browse_web, prob: 0.73',
        'DEBUG: Packet captured — src:10.10.2.14 dst:10.10.1.5 proto:TCP len:1460',
        'DEBUG: Behavioral model weight update — lr: 0.0001, batch: 64',
    ]
};

function generateLogEntry() {
    const levels = ['info','info','info','debug','debug','warning','error','critical'];
    const level = levels[Math.floor(Math.random() * levels.length)];
    const msgs = LOG_MESSAGES[level];
    const msg = msgs[Math.floor(Math.random() * msgs.length)];
    const src = LOG_SOURCES[Math.floor(Math.random() * LOG_SOURCES.length)];
    const now = new Date();
    const time = now.toTimeString().slice(0,8);
    return { time, level, msg, src };
}

function generateTrafficRow() {
    const protocols = ['TCP','UDP','HTTP','HTTPS','DNS','SMB','SSH','RDP','ICMP'];
    const ips = ['10.10.1.','10.10.2.','10.10.3.','172.16.0.','192.168.1.'];
    const statuses = ['active','active','active','idle','error'];
    const proto = protocols[Math.floor(Math.random() * protocols.length)];
    const srcIP = ips[Math.floor(Math.random()*ips.length)] + Math.floor(Math.random()*254+1);
    const dstIP = ips[Math.floor(Math.random()*ips.length)] + Math.floor(Math.random()*254+1);
    const port = [80,443,53,445,22,3389,8080,8443,25,110][Math.floor(Math.random()*10)];
    const bytes = Math.floor(Math.random()*50000)+64;
    const status = statuses[Math.floor(Math.random()*statuses.length)];
    return { srcIP, dstIP, proto, port, bytes, status };
}

function randBetween(a, b) { return Math.floor(Math.random() * (b - a + 1)) + a; }
