import csv
import random
from datetime import datetime, timedelta

# 90-day simulation window ending today (October 2026)
END_TIME = datetime(2026, 10, 2, 12, 0, 0)
START_TIME = END_TIME - timedelta(days=90)

# Alert profiles: (alertname, severity, service, is_noisy, target_firings)
ALERT_DEFINITIONS = [
    ("HighCPUUsage", "warning", "node-exporter", True, 450),
    ("DiskFillingFast", "warning", "node-exporter", True, 380),
    ("HighMemoryUsage", "warning", "node-exporter", True, 290),
    ("NetworkReceiveDropRate", "warning", "network", True, 260),
    ("HTTPClientSlowLatency", "warning", "api-gateway", True, 240),
    ("TemporaryLockContention", "warning", "database", True, 210),
    ("HighContextSwitches", "info", "system", True, 180),
    ("ContainerOOMKilledTransient", "warning", "app-worker", True, 160),
    ("DNSResolutionSlowSpike", "warning", "coredns", True, 140),
    ("NginxWorkerThreadStall", "warning", "ingress", True, 120),
    ("DiskAlmostFull", "critical", "storage", False, 18),
    ("InstanceDown", "critical", "infrastructure", False, 9),
    ("DatabaseReplicationLag", "critical", "database", False, 12),
]

records = []

for alertname, severity, service, is_noisy, count in ALERT_DEFINITIONS:
    for _ in range(count):
        # Random timestamp inside the 90-day window
        random_seconds = random.randint(0, int((END_TIME - START_TIME).total_seconds()))
        firing_time = START_TIME + timedelta(seconds=random_seconds)
        
        if is_noisy:
            duration_sec = random.randint(20, 180)  # Short-lived spike
            status = "resolved"
            action_required = "no"  # Noise = self-resolves with 0 operational action
        else:
            duration_sec = random.randint(1200, 7200)  # Sustained outage
            status = "resolved" if random.random() > 0.1 else "firing"
            action_required = "yes"  # Real incident = required engineering intervention
            
        instance = f"prod-node-{random.randint(1, 3)}:9100"
        
        records.append({
            "timestamp": firing_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "alertname": alertname,
            "severity": severity,
            "service": service,
            "instance": instance,
            "status": status,
            "duration_sec": duration_sec,
            "action_required": action_required
        })

# Sort chronologically
records.sort(key=lambda x: x["timestamp"])

output_file = "data/raw/synthetic_90d_alert_history.csv"
with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=records[0].keys())
    writer.writeheader()
    writer.writerows(records)

print(f"Generated {len(records)} alert events across 90 days in {output_file}")