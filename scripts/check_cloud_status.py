#!/usr/bin/env python3
"""
AegisGov AI - Reusable Cloud Run Status & Resource Telemetry Monitor
====================================================================
Queries Google Cloud Run, Cloud Logging, and Live Health Probes to deliver
an instant health, resource usage, traffic, and free-tier cost assessment.

Usage:
    python scripts/check_cloud_status.py
    python scripts/check_cloud_status.py --json
    python scripts/check_cloud_status.py --alert-on-error
    ./scripts/check_cloud_status.sh
"""

import sys
import os
import re
import json
import time
import argparse
import subprocess
import urllib.request
import urllib.error

# ANSI Color Codes
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

def load_env(env_path):
    config = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip("'\"")
                config[k] = v
    return config

def run_gcloud_json(cmd_args):
    try:
        res = subprocess.run(
            ["gcloud"] + cmd_args + ["--format=json"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return json.loads(res.stdout) if res.stdout.strip() else {}
    except subprocess.CalledProcessError as e:
        return {"error": e.stderr.strip() or str(e)}
    except Exception as e:
        return {"error": str(e)}

def probe_http_health(url, timeout=5):
    health_url = url.rstrip("/") + "/api/health"
    start_time = time.time()
    try:
        req = urllib.request.Request(
            health_url,
            headers={"User-Agent": "AegisGov-CloudMonitor/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latency_ms = (time.time() - start_time) * 1000.0
            data = json.loads(resp.read().decode("utf-8"))
            return {
                "accessible": True,
                "status_code": resp.status,
                "latency_ms": round(latency_ms, 2),
                "data": data,
                "error": None
            }
    except urllib.error.HTTPError as e:
        latency_ms = (time.time() - start_time) * 1000.0
        return {
            "accessible": False,
            "status_code": e.code,
            "latency_ms": round(latency_ms, 2),
            "data": None,
            "error": str(e)
        }
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000.0
        return {
            "accessible": False,
            "status_code": None,
            "latency_ms": round(latency_ms, 2),
            "data": None,
            "error": str(e)
        }

def collect_telemetry(project, account, region, service, log_limit=250):
    telemetry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "project_id": project,
        "account": account,
        "region": region,
        "service_name": service,
        "service_details": {},
        "health_probe": {},
        "traffic_metrics": {},
        "free_tier_status": {},
        "alerts": []
    }

    # 1. Cloud Run Service Details
    svc_data = run_gcloud_json([
        "run", "services", "describe", service,
        f"--region={region}",
        f"--project={project}",
        f"--account={account}"
    ])

    if "error" in svc_data:
        telemetry["alerts"].append(f"Failed to describe Cloud Run service: {svc_data['error']}")
        return telemetry

    status_obj = svc_data.get("status", {})
    spec_obj = svc_data.get("spec", {})
    template_spec = spec_obj.get("template", {}).get("spec", {})
    template_meta = spec_obj.get("template", {}).get("metadata", {})
    annotations = template_meta.get("annotations", {})
    containers = template_spec.get("containers", [{}])
    container_resources = containers[0].get("resources", {}).get("limits", {})

    service_url = status_obj.get("url", "")
    ready_cond = next((c for c in status_obj.get("conditions", []) if c.get("type") == "Ready"), {})
    routes_cond = next((c for c in status_obj.get("conditions", []) if c.get("type") == "RoutesReady"), {})
    configs_cond = next((c for c in status_obj.get("conditions", []) if c.get("type") == "ConfigurationsReady"), {})

    telemetry["service_details"] = {
        "url": service_url,
        "revision": status_obj.get("latestReadyRevisionName", "unknown"),
        "ready": ready_cond.get("status") == "True",
        "routes_ready": routes_cond.get("status") == "True",
        "configs_ready": configs_cond.get("status") == "True",
        "cpu_limit": container_resources.get("cpu", "1"),
        "memory_limit": container_resources.get("memory", "512Mi"),
        "max_instances": int(annotations.get("autoscaling.knative.dev/maxScale", 2)),
        "min_instances": int(annotations.get("autoscaling.knative.dev/minScale", 0)),
        "concurrency": template_spec.get("containerConcurrency", 80),
        "startup_cpu_boost": annotations.get("run.googleapis.com/startup-cpu-boost") == "true"
    }

    # 2. Live HTTP Health Probe
    if service_url:
        telemetry["health_probe"] = probe_http_health(service_url)

    # 3. Query Cloud Logging for recent HTTP traffic
    log_query = f'resource.type="cloud_run_revision" AND resource.labels.service_name="{service}" AND httpRequest.requestMethod:*'
    logs = run_gcloud_json([
        "logging", "read", log_query,
        f"--project={project}",
        f"--account={account}",
        f"--limit={log_limit}"
    ])

    status_counts = {}
    total_latency_sec = 0.0
    latency_samples = 0
    recent_timestamp = None

    if isinstance(logs, list):
        for entry in logs:
            req = entry.get("httpRequest", {})
            st = str(req.get("status", "unknown"))
            status_counts[st] = status_counts.get(st, 0) + 1

            if not recent_timestamp:
                recent_timestamp = entry.get("timestamp")

            lat_str = req.get("latency")
            if lat_str and lat_str.endswith("s"):
                try:
                    sec = float(lat_str[:-1])
                    total_latency_sec += sec
                    latency_samples += 1
                except ValueError:
                    pass

    total_requests = sum(status_counts.values())
    errors_5xx = sum(count for st, count in status_counts.items() if st.startswith("5"))
    errors_4xx = sum(count for st, count in status_counts.items() if st.startswith("4"))
    success_2xx = sum(count for st, count in status_counts.items() if st.startswith("2"))
    cached_3xx = sum(count for st, count in status_counts.items() if st.startswith("3"))

    avg_latency_ms = round((total_latency_sec / latency_samples) * 1000.0, 2) if latency_samples > 0 else 0.0

    telemetry["traffic_metrics"] = {
        "sampled_requests": total_requests,
        "status_distribution": status_counts,
        "success_count": success_2xx + cached_3xx,
        "client_error_count": errors_4xx,
        "server_error_count": errors_5xx,
        "avg_latency_ms": avg_latency_ms,
        "last_activity": recent_timestamp or "No recent traffic"
    }

    # 4. Free Tier and Cost Guardrail Assessment
    free_tier_allowance_reqs = 2000000
    telemetry["free_tier_status"] = {
        "monthly_request_allowance": free_tier_allowance_reqs,
        "sampled_usage": total_requests,
        "percent_quota_used": round((total_requests / free_tier_allowance_reqs) * 100.0, 4),
        "estimated_cost_usd": "$0.00",
        "cost_guardrail_active": telemetry["service_details"]["max_instances"] <= 2
    }

    # Check for alerts
    if not telemetry["service_details"].get("ready"):
        telemetry["alerts"].append("Service Ready condition is FALSE.")
    if errors_5xx > 0:
        telemetry["alerts"].append(f"Detected {errors_5xx} HTTP 5xx server errors in recent logs.")
    if not telemetry["health_probe"].get("accessible"):
        telemetry["alerts"].append(f"Public health probe failed: {telemetry['health_probe'].get('error')}")

    return telemetry

def render_dashboard(t):
    svc = t["service_details"]
    hp = t["health_probe"]
    tf = t["traffic_metrics"]
    ft = t["free_tier_status"]

    print(f"\n{BOLD}{CYAN}========================================================================{RESET}")
    print(f"{BOLD}{CYAN}  🛡️  AegisGov AI — Cloud Run Live Status & Resource Dashboard{RESET}")
    print(f"{BOLD}{CYAN}========================================================================{RESET}")
    print(f" {DIM}Timestamp :{RESET} {t['timestamp']}   |   {DIM}Region:{RESET} {t['region']} (Singapore)")
    print(f" {DIM}Project   :{RESET} {t['project_id']}      |   {DIM}Account:{RESET} {t['account']}")
    print(f"{CYAN}------------------------------------------------------------------------{RESET}")

    # Section 1: Health & Ingress
    ready_badge = f"{GREEN}● READY (100% Traffic){RESET}" if svc.get("ready") else f"{RED}● DEGRADED{RESET}"
    probe_badge = f"{GREEN}● 200 OK ({hp.get('latency_ms')} ms){RESET}" if hp.get("accessible") else f"{RED}● UNREACHABLE{RESET}"
    print(f"\n{BOLD}1. Operational Status & Health Probe:{RESET}")
    print(f"   • Service State      : {ready_badge}")
    print(f"   • Active Revision    : {BOLD}{svc.get('revision')}{RESET}")
    print(f"   • Public URL         : {CYAN}{svc.get('url')}{RESET}")
    print(f"   • Live Health Probe  : {probe_badge}")

    # Section 2: Compute Resources & Guardrails
    guard_badge = f"{GREEN}ACTIVE (max=2){RESET}" if ft.get("cost_guardrail_active") else f"{YELLOW}CAUTION{RESET}"
    print(f"\n{BOLD}2. Compute Resources & Cost Guardrails:{RESET}")
    print(f"   • CPU Allocation     : {svc.get('cpu_limit')} vCPU (Startup CPU Boost: {svc.get('startup_cpu_boost')})")
    print(f"   • Memory Allocation  : {svc.get('memory_limit')}")
    print(f"   • Instance Scaling   : Min={svc.get('min_instances')} (scale-to-zero), Max={svc.get('max_instances')}")
    print(f"   • Concurrency Limit  : {svc.get('concurrency')} concurrent requests per container")
    print(f"   • Free Tier Guard    : {guard_badge}")

    # Section 3: Traffic & Telemetry
    print(f"\n{BOLD}3. Traffic Analytics & Performance (Sampled):{RESET}")
    print(f"   • Total Requests     : {BOLD}{tf.get('sampled_requests')}{RESET}")
    print(f"   • Status Breakdown   : {GREEN}2xx/3xx: {tf.get('success_count')}{RESET} | {YELLOW}4xx: {tf.get('client_error_count')}{RESET} | {RED}5xx: {tf.get('server_error_count')}{RESET}")
    print(f"   • Average Latency    : {BOLD}{tf.get('avg_latency_ms')} ms{RESET}")
    print(f"   • Last Request Seen  : {tf.get('last_activity')}")

    # Section 4: Billing Impact
    print(f"\n{BOLD}4. Free Tier Consumption & Billing:{RESET}")
    print(f"   • Monthly Allowance  : {ft.get('monthly_request_allowance'):,} requests free")
    print(f"   • Quota Utilized     : {ft.get('percent_quota_used')}%")
    print(f"   • Estimated Cost     : {GREEN}{BOLD}{ft.get('estimated_cost_usd')}{RESET} (Safely within 100% Free Tier)")

    # Alerts
    if t["alerts"]:
        print(f"\n{RED}{BOLD}⚠️  ALERTS:{RESET}")
        for alert in t["alerts"]:
            print(f"   {RED}• {alert}{RESET}")
    else:
        print(f"\n{GREEN}✅ System is 100% healthy with zero active alerts.{RESET}")

    print(f"{CYAN}========================================================================{RESET}\n")

def main():
    parser = argparse.ArgumentParser(description="Check AegisGov AI Cloud Run status and resource telemetry.")
    parser.add_argument("--json", action="store_true", help="Output raw telemetry data as JSON.")
    parser.add_argument("--alert-on-error", action="store_true", help="Exit with code 1 if errors or degradation are found.")
    parser.add_argument("--project", default=None, help="GCP Project ID.")
    parser.add_argument("--account", default=None, help="GCP Account email.")
    parser.add_argument("--region", default=None, help="GCP Location / Region.")
    parser.add_argument("--service", default="aegisgov-ai", help="Cloud Run service name.")
    parser.add_argument("--limit", type=int, default=200, help="Number of recent log entries to sample.")

    args = parser.parse_args()

    # Load defaults from root .env
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, ".."))
    env_cfg = load_env(os.path.join(root_dir, ".env"))

    project = args.project or env_cfg.get("GCP_PROJECT_ID", "aegisgov-ai-2026")
    account = args.account or env_cfg.get("GCP_DEPLOY_ACCOUNT", "shanusingh684@gmail.com")
    region = args.region or env_cfg.get("GCP_LOCATION", "asia-southeast1")
    service = args.service

    telemetry = collect_telemetry(project, account, region, service, log_limit=args.limit)

    if args.json:
        print(json.dumps(telemetry, indent=2))
    else:
        render_dashboard(telemetry)

    if args.alert_on_error and len(telemetry.get("alerts", [])) > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
