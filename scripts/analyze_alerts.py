import csv
from collections import defaultdict

input_file = "data/raw/synthetic_90d_alert_history.csv"
output_ranking_file = "data/processed/top_10_noisy_alerts.csv"

stats = defaultdict(lambda: {
    "total_firings": 0,
    "no_action_count": 0,
    "auto_resolve_count": 0,
    "durations": [],
    "severity": "",
    "service": ""
})

with open(input_file, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row["alertname"]
        stats[name]["total_firings"] += 1
        stats[name]["severity"] = row["severity"]
        stats[name]["service"] = row["service"]
        stats[name]["durations"].append(int(row["duration_sec"]))
        if row["action_required"].strip().lower() == "no":
            stats[name]["no_action_count"] += 1
        if row["status"].strip().lower() == "resolved":
            stats[name]["auto_resolve_count"] += 1

results = []
for name, data in stats.items():
    total = data["total_firings"]
    no_action_rate = (data["no_action_count"] / total) * 100
    avg_duration = sum(data["durations"]) / total
    
    # Noise Score Formula: High volume + High % no action + Short average duration
    # Alerts that self-resolve rapidly and require zero actions get maximum noise score
    noise_score = (data["no_action_count"] * (100 / max(avg_duration, 1)))
    
    results.append({
        "alertname": name,
        "service": data["service"],
        "severity": data["severity"],
        "total_firings": total,
        "no_action_firings": data["no_action_count"],
        "no_action_pct": round(no_action_rate, 1),
        "avg_duration_sec": round(avg_duration, 1),
        "noise_score": round(noise_score, 2)
    })

# Rank strictly by Noise Score
results.sort(key=lambda x: x["noise_score"], reverse=True)
top_10 = results[:10]

# Write to processed CSV
with open(output_ranking_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=top_10[0].keys())
    writer.writeheader()
    writer.writerows(top_10)

# Display pretty table in terminal
header = f"{'Rank':<5}{'Alert Name':<30}{'Firings':<10}{'No Action %':<14}{'Avg Dur (s)':<14}{'Noise Score':<12}"
print("=" * 85)
print("TOP 10 NOISY ALERTS AUDIT REPORT (PAST 90 DAYS)")
print("=" * 85)
print(header)
print("-" * 85)
for i, item in enumerate(top_10, 1):
    print(f"{i:<5}{item['alertname']:<30}{item['total_firings']:<10}{str(item['no_action_pct'])+'%':<14}{item['avg_duration_sec']:<14}{item['noise_score']:<12}")
print("=" * 85)
print(f"Top 10 noise ranking saved to: {output_ranking_file}")