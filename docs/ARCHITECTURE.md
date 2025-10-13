# Architecture and Data Mapping

This document describes the recommended architecture and which data sources map to stages of the APT lifecycle.

Components

- Elasticsearch — storage, indexing and detection engine.
- Logstash — optional parsing and enrichment pipeline between Beats and Elasticsearch.
- Kibana — dashboarding and detection rule import (Elastic Security/Detections).
- Beats (Winlogbeat/Filebeat/Packetbeat) — lightweight agents on endpoints/servers to forward events.

Data sources and common mappings

- Windows Event Logs (Sysmon, Security, PowerShell) — process creations, command line, network connections, credential dumping events (Event IDs), service creation.
- Endpoint Malware/EDR logs — alerts and process trees.
- Network logs (firewalls, proxy) — unusual egress, beaconing.
- Authentication logs (Domain controllers) — suspicious logon patterns, lateral movement.

MITRE ATT&CK mapping (examples)

- Initial Access: T1190, T1078 — monitor suspicious external connections and credential use.
- Execution: T1059 (Cmd/PowerShell) — detect encoded commands, one-liners, downloads via powershell.
- Persistence: T1547 (Service) — detect new/changed services and registry run keys.
- Privilege Escalation: T1055 (Process Injection) — monitor process creation trees and known injector patterns.
- Lateral Movement: T1021 (Remote services) — detect remote process execution, SMB/WinRM usage.
- Exfiltration: T1041, T1030 — detect large uploads, unusual destinations.

Runbook Overview

1. Install and configure Beats on source hosts.
2. Configure Logstash to parse and enrich logs.
3. Create detection rules in Kibana or ElastAlert and map rules to MITRE techniques.
4. Ingest sample data from `samples/` and validate rules.
