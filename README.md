# adAPT — Adaptive Detection for Advanced Persistent Threats (APTs)

A complete threat detection setup for the ELK stack (Elasticsearch, Logstash, Kibana) focused on Advanced Persistent Threat (APT) behaviors and phishing detection. Includes 100+ detection rules, Beats configurations, Logstash pipelines, and a machine learning-based phishing detection system for email log analysis.

---

## Project Structure

```
adapt/
├── sigma_rules/          # Detection rules for Elastic Security (KQL & EQL)
├── elasticsearch/        # Elasticsearch configuration
├── kibana/               # Kibana configuration
├── logstash/             # Logstash ingest pipeline configs
├── filebeat/             # Filebeat configuration
├── auditbeat/            # Auditbeat configuration
├── winlogbeat/           # Winlogbeat configuration
├── mail/                 # Mail log ingestion with ML phishing scoring
├── ML/                   # Phishing detection ML model & datasets
└── docs/                 # Architecture & setup documentation
```

---

## Directory Details

### `sigma_rules/`
Contains 100+ detection rules for Elastic Security (Kibana Detection Engine) written in **KQL** and **EQL** formats. Coverage includes:
- APT-36 attack chain detection
- PowerShell abuse and encoded command execution
- Credential dumping and lateral movement
- Privilege escalation techniques
- DNS tunneling and exfiltration
- SSH brute force and password spraying
- Phishing email detection (integrated with ML model)
- Threat intelligence indicator matching (hashes, IPs, JA3 fingerprints)
- MITRE ATT&CK technique coverage (T1003, T1059, T1021, T1078, etc.)

### `elasticsearch/`
Elasticsearch node configuration (`elasticsearch.yml`) for the cluster setup.

### `kibana/`
Kibana configuration (`kibana.yml`) for the Security/SIEM interface.

### `logstash/`
Logstash ingest pipeline configurations for log parsing, ECS normalization, GeoIP enrichment, and Elasticsearch output.

### `filebeat/`
Filebeat configuration (`filebeat.yml`) for shipping logs from Linux endpoints.

### `auditbeat/`
Auditbeat configuration (`auditbeat.yml`) for system audit and file integrity monitoring.

### `winlogbeat/`
Winlogbeat configuration for shipping Windows Event Logs (Sysmon, Security, PowerShell).

### `mail/`
Scripts and configs for ingesting mail logs into ELK, with ML-based phishing detection that appends phishing scores and labels to email events.

### `ML/`
Training datasets and DistilBERT-based phishing detection model for classifying emails as legitimate or phishing.

### `docs/`
Project documentation:
- `ARCHITECTURE.md` — System architecture, data sources, rule mapping and component overview
- `SETUP.md` — Detailed setup and deployment guide

---

## Key Features

- **100+ Detection Rules** — Comprehensive coverage of APT tactics and techniques in KQL/EQL
- **ECS Compliance** — All logs normalized to Elastic Common Schema
- **ML Phishing Detection** — DistilBERT-based model for real-time email classification
- **Threat Intelligence Integration** — Rules for matching against known IOCs
- **Multi-Platform Support** — Windows (Winlogbeat), Linux (Filebeat/Auditbeat), and network devices

---

## Notes

- Adapt paths, hostnames, and credentials in configuration files to your environment
- See `docs/SETUP.md` for detailed deployment instructions
- See `docs/ARCHITECTURE.md` for system design and data flow documentation
