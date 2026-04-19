#!/usr/bin/env python3
"""
health_check.py — CI/CD pipeline health check CLI tool
Demonstrates: Python tooling for developer workflows (JD requirement)

Usage:
  python scripts/health_check.py --env staging
  python scripts/health_check.py --env prod --timeout 60
  python scripts/health_check.py --url http://localhost:3000
"""

import argparse
import sys
import time
import json
import urllib.request
import urllib.error
from datetime import datetime


ENVIRONMENTS = {
    "dev":     "http://localhost:3000",
    "staging": "https://staging.cicd-showcase.example.com",
    "prod":    "https://cicd-showcase.example.com",
}

COLORS = {
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "red":    "\033[91m",
    "blue":   "\033[94m",
    "reset":  "\033[0m",
    "bold":   "\033[1m",
}


def log(message: str, level: str = "info") -> None:
    ts = datetime.utcnow().strftime("%H:%M:%S")
    color_map = {"info": "blue", "success": "green", "warning": "yellow", "error": "red"}
    color = COLORS.get(color_map.get(level, "reset"), "")
    prefix = {"info": "●", "success": "✓", "warning": "!", "error": "✗"}.get(level, "·")
    print(f"{color}[{ts}] {prefix} {message}{COLORS['reset']}")


def check_endpoint(url: str, timeout: int = 10) -> dict:
    """Perform a single health check against a URL."""
    start = time.time()
    try:
        req = urllib.request.urlopen(url + "/health", timeout=timeout)
        elapsed = round((time.time() - start) * 1000)
        body = req.read().decode()
        return {
            "status": "healthy",
            "http_code": req.status,
            "response_time_ms": elapsed,
            "body": body,
        }
    except urllib.error.HTTPError as e:
        return {"status": "degraded", "http_code": e.code, "error": str(e)}
    except Exception as e:
        return {"status": "unreachable", "http_code": 0, "error": str(e)}


def wait_for_healthy(url: str, retries: int, delay: int, timeout: int) -> bool:
    """Poll until healthy or max retries reached."""
    log(f"Health checking: {url}", "info")
    log(f"Config: {retries} retries, {delay}s delay, {timeout}s timeout", "info")
    print()

    for attempt in range(1, retries + 1):
        result = check_endpoint(url, timeout)
        status = result["status"]

        if status == "healthy":
            log(f"[{attempt}/{retries}] HEALTHY — HTTP {result['http_code']} in {result['response_time_ms']}ms", "success")
            return True
        elif status == "degraded":
            log(f"[{attempt}/{retries}] DEGRADED — HTTP {result['http_code']}", "warning")
        else:
            log(f"[{attempt}/{retries}] UNREACHABLE — {result.get('error', 'unknown')}", "error")

        if attempt < retries:
            log(f"Retrying in {delay}s...", "info")
            time.sleep(delay)

    return False


def main():
    parser = argparse.ArgumentParser(
        description="CI/CD Showcase health check CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--env",     choices=list(ENVIRONMENTS.keys()), default="dev")
    parser.add_argument("--url",     help="Override URL (skips --env lookup)")
    parser.add_argument("--retries", type=int, default=5)
    parser.add_argument("--delay",   type=int, default=10, help="Seconds between retries")
    parser.add_argument("--timeout", type=int, default=10, help="HTTP timeout per attempt")
    parser.add_argument("--json",    action="store_true", help="Output JSON result")
    args = parser.parse_args()

    target_url = args.url or ENVIRONMENTS[args.env]

    print(f"\n{COLORS['bold']}=== CI/CD Showcase Health Check ==={COLORS['reset']}")
    print(f"Environment : {args.env}")
    print(f"URL         : {target_url}")
    print(f"Timestamp   : {datetime.utcnow().isoformat()}Z\n")

    success = wait_for_healthy(target_url, args.retries, args.delay, args.timeout)

    result = {
        "success": success,
        "environment": args.env,
        "url": target_url,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if args.json:
        print(json.dumps(result, indent=2))

    print()
    if success:
        log("All health checks passed.", "success")
        sys.exit(0)
    else:
        log("Health check FAILED after all retries.", "error")
        sys.exit(1)


if __name__ == "__main__":
    main()
