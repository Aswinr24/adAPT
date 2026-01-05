# Setup Guide

## Prerequisites

- **Proxmox VE** hypervisor (or equivalent virtualization platform)
- VMs with the following specifications:
  - **ELK Server**: Ubuntu Server 24.04, 6GB+ RAM, 100GB+ storage
  - **Windows 10 Pro**: 4GB+ RAM
  - **Windows Server 22H2**: 4GB+ RAM
  - **Ubuntu Server 24.04**: 2GB+ RAM (log source + Zeek)
  - **Mail Server**: 2GB+ RAM
  - **pfSense**: 2GB+ RAM (firewall/gateway)

---

## 1. Network Configuration

### Proxmox Internal Network

Create an internal network bridge in Proxmox for VM communication:

1. In Proxmox, go to **Datacenter → Node → Network**
2. Create a new Linux Bridge (e.g., `vmbr1`) for the internal network
3. Attach all VMs to this bridge adapter
4. Assign static IPs to VMs via Proxmox terminal:
   ```bash
   # Example: Assign IP to a VM's interface
   ip addr add 10.10.10.x/24 dev eth1
   ```

### pfSense Setup

Configure pfSense as the perimeter gateway for the internal network:

1. Assign WAN (external) and LAN (internal vmbr1) interfaces
2. Configure NAT for outbound traffic
3. Enable syslog forwarding to the ELK server:
   ```
   Status → System Logs → Settings
   - Enable Remote Logging
   - Remote Log Server
   - Remote Syslog Contents: Select all relevant logs
   ```

---

## 2. ELK Stack Installation

### Elasticsearch

Official installation guide: [Installing Elasticsearch](https://www.elastic.co/docs/deploy-manage/deploy/self-managed/installing-elasticsearch)

```bash
# Install Elasticsearch (after adding Elastic repo)
sudo apt install elasticsearch

# Copy configuration
sudo cp elasticsearch/elasticsearch.yml /etc/elasticsearch/

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch
```

**Important**: Save the generated elastic user password and enrollment token from the installation output.

### Kibana

Official installation guide: [Installing Kibana](https://www.elastic.co/guide/en/kibana/current/install.html)

```bash
# Install Kibana
sudo apt install kibana

# Copy configuration
sudo cp kibana/kibana.yml /etc/kibana/

# Enroll with Elasticsearch
sudo /usr/share/kibana/bin/kibana-setup

# Enable and start service
sudo systemctl enable kibana
sudo systemctl start kibana
```

Access Kibana at `http://<ELK_SERVER_IP>:5601`

### Logstash

Official installation guide: [Installing Logstash](https://www.elastic.co/guide/en/logstash/current/installing-logstash.html)

```bash
# Install Logstash
sudo apt install logstash

# Copy pipeline configurations
sudo cp logstash/*.conf /etc/logstash/conf.d/

# Update credentials in 99-output.conf with your elastic password
sudo nano /etc/logstash/conf.d/99-output.conf

# Enable and start service
sudo systemctl enable logstash
sudo systemctl start logstash
```

### SSL Certificates

Elasticsearch generates self-signed SSL certificates during installation. Copy the CA certificate for use with Logstash and Beats:

```bash
# CA certificate location
/etc/elasticsearch/certs/http_ca.crt

# Copy to Logstash (referenced in 99-output.conf)
sudo cp /etc/elasticsearch/certs/http_ca.crt /etc/logstash/
```

---

## 3. Beats Agent Deployment

### Windows Hosts (Winlogbeat)

Official installation guide: [Winlogbeat Installation](https://www.elastic.co/guide/en/beats/winlogbeat/current/winlogbeat-installation-configuration.html)

On each Windows host (Windows 10 Pro, Windows Server 22H2):

1. Download and extract Winlogbeat to `C:\Program Files\Winlogbeat`
2. Copy configuration and update Logstash output:
   ```powershell
   Copy-Item winlogbeat\winlogbeat.yml "C:\Program Files\Winlogbeat\winlogbeat.yml"
   # Edit winlogbeat.yml: output.logstash.hosts: ["<ELK_SERVER_IP>:5044"]
   ```
3. Install and start service:
   ```powershell
   cd "C:\Program Files\Winlogbeat"
   .\install-service-winlogbeat.ps1
   Start-Service winlogbeat
   ```

### Sysmon (Windows)

Official guide: [Sysmon - Sysinternals](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon)

```powershell
.\Sysmon64.exe -accepteula -i sysmonconfig-export.xml
```

### Ubuntu Host (Filebeat + Auditbeat)

Official guides: [Filebeat](https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-installation-configuration.html) | [Auditbeat](https://www.elastic.co/guide/en/beats/auditbeat/current/auditbeat-installation-configuration.html)

**Filebeat:**
```bash
sudo apt install filebeat
sudo cp filebeat/filebeat.yml /etc/filebeat/
sudo filebeat modules enable system auditd zeek
# Edit filebeat.yml: output.logstash.hosts: ["<ELK_SERVER_IP>:5043"]
sudo systemctl enable filebeat && sudo systemctl start filebeat
```

**Auditbeat:**
```bash
sudo apt install auditbeat
sudo cp auditbeat/auditbeat.yml /etc/auditbeat/
sudo systemctl enable auditbeat && sudo systemctl start auditbeat
```

### Zeek (Ubuntu)

Official installation guide: [Zeek Installation](https://docs.zeek.org/en/current/install.html)

```bash
# Install Zeek and configure interface in /opt/zeek/etc/node.cfg
sudo /opt/zeek/bin/zeekctl deploy

# Enable Filebeat Zeek module
sudo filebeat modules enable zeek
```

---

## 4. Mail Server Setup

Official guide: [Postfix Documentation](https://www.postfix.org/documentation.html)

### Postfix Configuration
```bash
sudo apt install postfix
sudo cp mail/postfig_mail.cf /etc/postfix/main.cf
sudo systemctl restart postfix
```

### Mail Watcher Service
```bash
pip install watchdog requests
sudo cp mail/mail_watcher.py /opt/mail_watcher/
sudo cp mail/mailwatcher.service /etc/systemd/system/

# Update MAIL_DIR in mail_watcher.py, then:
sudo systemctl daemon-reload
sudo systemctl enable mailwatcher && sudo systemctl start mailwatcher
```

The mail watcher requires the ML phishing API running on `http://127.0.0.1:5000/detect` (see `ML/` directory for model setup).

---

## 5. Detection Rules Import

### Import Rules to Kibana

1. Navigate to **Kibana → Security → Rules → Detection rules (SIEM)**

2. Click **Import rules**

3. Import rules from `sigma_rules/` directory:
   - Rules are in YAML format with KQL/EQL queries
   - Import individually or convert to NDJSON for bulk import

### Enable Rules

After import:
1. Select all imported rules
2. Click **Bulk actions → Enable**
3. Configure rule actions (email alerts, Slack notifications, etc.)

---

## 6. Verification

### Check Service Status

```bash
# ELK Stack
sudo systemctl status elasticsearch kibana logstash

# Beats (on respective hosts)
sudo systemctl status filebeat auditbeat
# Windows: Get-Service winlogbeat
```

### Verify Data Ingestion

In Kibana:
1. Go to **Stack Management → Index Management**
2. Verify indices are created:
   - `winlogbeat-*`
   - `filebeat-*`
   - `ubuntu-system-*`
   - `ubuntu-auditd-*`
   - `zeek-*`
   - `pfsense-*`

### Test Detection Rules

1. Go to **Security → Alerts**
2. Trigger a test event (e.g., run `whoami` on Windows)
3. Verify alert appears for matching rules

---

## Troubleshooting

### Common Commands
```bash
# Check service status
sudo systemctl status elasticsearch kibana logstash filebeat auditbeat

# View logs
sudo journalctl -u <service-name> -f

# Test Logstash config
sudo /usr/share/logstash/bin/logstash --config.test_and_exit -f /etc/logstash/conf.d/

# Test connectivity to Logstash
nc -zv <ELK_SERVER_IP> 5044
```

### Common Issues
- **Elasticsearch not starting**: Check JVM heap size in `/etc/elasticsearch/jvm.options`
- **Beats not sending data**: Verify Logstash host/port in Beat config
- **Permission errors**: Ensure correct ownership on data directories

---

## Security Considerations

- Change default Elasticsearch passwords immediately after installation
- Restrict network access to ELK ports (9200, 5601, 5044)
- Regularly update GeoIP databases and threat intel feeds
- Back up Elasticsearch indices and Kibana saved objects
