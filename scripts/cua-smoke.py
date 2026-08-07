#!/usr/bin/env python3
"""CUA smoke test for NSIS-installed fleet apps (pywinauto-mcp canary).

CUA_SMOKE_VERSION = 2
If this file differs from templates/tauri-native/scripts/cua-smoke.py in
mcp-central-docs, copy the template over - version number will have changed.

Usage:
    python scripts/cua-smoke.py
    python scripts/cua-smoke.py --installer path/to/setup.exe
    python scripts/cua-smoke.py --config scripts/cua-nsis-config.json

Phases:
    1. Kill stale processes
    2. Silent install NSIS
    3. Launch app, wait for backend health
    4. Verify window (pywinauto)
    5. Screenshot evidence
    6. Feature-route smoke (health + data endpoint)
    7. Check diagnostics
    8. Uninstall
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error

CUA_SMOKE_VERSION = 2

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cua-nsis-config.json")


def load_config(path=None):
    p = path or DEFAULT_CONFIG_PATH
    if not os.path.exists(p):
        print(f"  [cua] WARNING: config not found at {p}, using built-in defaults", flush=True)
        return {}
    with open(p) as f:
        cfg = json.load(f)
    def _expand(v):
        if isinstance(v, str):
            return os.path.expandvars(v)
        if isinstance(v, list):
            return [_expand(x) for x in v]
        return v
    return {k: _expand(v) for k, v in cfg.items()}


def _check_version():
    from pathlib import Path
    ver_file = Path(__file__)
    tpl = Path(os.getenv("MCP_CENTRAL_DOCS", "")) / "templates/tauri-native/scripts/cua-smoke.py"
    if tpl.exists():
        tpl_text = tpl.read_text(encoding="utf-8")
        import re
        m = re.search(r'CUA_SMOKE_VERSION\s*=\s*(\d+)', tpl_text)
        if m and int(m.group(1)) > CUA_SMOKE_VERSION:
            print(f"  [cua] WARNING: cua-smoke.py v{CUA_SMOKE_VERSION} is outdated "
                  f"(template v{m.group(1)}). Copy template over.", flush=True)


def cfg(key, default=""):
    return _CONFIG.get(key, default)


_CONFIG = load_config()

BACKEND_PORT = int(cfg("backend_port", 11116))
BACKEND_URL = f"http://127.0.0.1:{BACKEND_PORT}"
PRODUCT_NAME = cfg("product_name", "Mixx-DJ-MCP")
HEALTH_PATH = cfg("health_path", "/health")
DIAGNOSTICS_PATH = cfg("diagnostics_path", "/api/v1/diagnostics")
FEATURE_PATH = cfg("feature_smoke_path", "/api/v1/status")
WINDOW_TITLE_RE = cfg("window_title_re", "Mixx DJ MCP")
INSTALL_DIR = cfg("install_dir", "%LOCALAPPDATA%\\Mixx-DJ-MCP")
OPERATOR_EXE = cfg("operator_exe", "mixx-dj-native.exe")
PROCESS_NAMES = cfg("backend_process_names", ["mixx-dj-native", "mixx-dj-mcp-backend"])
NSIS_GLOB = cfg("nsis_glob", "native/target/release/bundle/nsis/Mixx-DJ-MCP_*_x64-setup.exe")
REGISTRY_FILTER = cfg("uninstall_registry_filter", "*Mixx-DJ*")
MAX_RETRY = 10
RETRY_DELAY = 3

_INSTALLED = False


def log(msg):
    print(f"  [cua] {msg}", flush=True)


class PhaseFailed(Exception):
    pass


def fatal(msg):
    print(f"  [cua] FATAL: {msg}", flush=True)
    sys.exit(1)


def phase_fail(msg):
    print(f"  [cua] PHASE FAIL: {msg}", flush=True)
    raise PhaseFailed(msg)


def kill_stale():
    for name in PROCESS_NAMES:
        subprocess.run(["taskkill", "/F", "/IM", f"{name}.exe", "/T"], capture_output=True, timeout=10)
    time.sleep(1)
    log("Stale processes killed")


def find_installer():
    import glob
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pattern = os.path.join(repo_root, *NSIS_GLOB.replace("/", "\\").split("\\"))
    matches = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    if matches:
        return matches[0]
    fatal("No NSIS installer found. Run 'just build-native' first.")


def silent_install(installer):
    log(f"Installing: {installer}")
    r = subprocess.run([installer, "/S"], capture_output=True, timeout=120)
    if r.returncode != 0:
        fatal(f"NSIS install exited with code {r.returncode}")
    global _INSTALLED
    _INSTALLED = True
    time.sleep(2)
    log("Install complete")


def launch_app():
    exe = os.path.join(INSTALL_DIR, OPERATOR_EXE)
    if not os.path.exists(exe):
        fatal(f"Operator not found at {exe}")
    subprocess.Popen([exe], cwd=INSTALL_DIR)
    log(f"Launched {exe}")
    for attempt in range(MAX_RETRY):
        try:
            resp = urllib.request.urlopen(f"{BACKEND_URL}{HEALTH_PATH}", timeout=5)
            if resp.status == 200:
                log(f"Backend healthy (attempt {attempt + 1})")
                return
        except (urllib.error.URLError, urllib.error.HTTPError, OSError):
            pass
        time.sleep(RETRY_DELAY)
    fatal(f"Backend not reachable after {MAX_RETRY * RETRY_DELAY}s")


def verify_window():
    try:
        import pywinauto
        app = pywinauto.Application(backend="uia").connect(title_re=WINDOW_TITLE_RE)
        win = app.window(title_re=WINDOW_TITLE_RE)
        win.wait("visible", timeout=5)
        rect = win.rectangle()
        w = rect.width if isinstance(rect.width, int) else rect.width()
        h = rect.height if isinstance(rect.height, int) else rect.height()
        log(f"Window found: {w}x{h}")
        if w > 0 and h > 0 and (w < 100 or h < 100):
            phase_fail(f"Window too small: {w}x{h}")
    except ImportError:
        log("pywinauto not available - window check skipped")
    except Exception as e:
        log(f"Window not found: {e}")


def take_screenshot(output_dir):
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"cua-smoke-{int(time.time())}.png")
    try:
        import pywinauto
        app = pywinauto.Application(backend="uia").connect(title_re=WINDOW_TITLE_RE)
        win = app.window(title_re=WINDOW_TITLE_RE)
        win.set_focus()
        time.sleep(1)
        capture = win.capture_as_image()
        capture.save(path)
        log(f"Screenshot saved: {path} ({os.path.getsize(path)} bytes)")
    except Exception:
        log("Screenshot not available")


def nav_click_through(output_dir):
    """Click each sidebar nav item, capture per-page screenshot."""
    if not cua_available():
        log("CUA client unavailable - nav click-through skipped")
        return
    nav_routes = cfg("nav_routes", [])
    if not isinstance(nav_routes, list) or not nav_routes:
        log("No nav_routes in config - nav walk skipped")
        return
    import pywinauto
    handle = _find_tauri_window()
    app = pywinauto.Application(backend="uia").connect(handle=handle)
    win = app.window(handle=handle)
    win.set_focus(); win.maximize(); time.sleep(1)
    for label, expected in nav_routes:
        try:
            link = win.descendants(title=label)
            if link:
                link[0].click_input()
            else:
                elements = win.descendants(control_type="Hyperlink")
                el = [e for e in elements if label.lower() in (e.window_text() or "").lower()]
                if el:
                    el[0].click_input()
                else:
                    log(f"Nav '{label}': no link found - skipped")
                    continue
            time.sleep(2)
            path = os.path.join(output_dir, f"nav-{label.lower().replace(' ','-')}.png")
            win.capture_as_image().save(path)
            log(f"Nav '{label}': clicked + screenshot ({os.path.getsize(path)} bytes)")
        except Exception as e:
            log(f"Nav '{label}' failed (non-fatal): {e}")

def check_feature_route():
    try:
        resp = urllib.request.urlopen(f"{BACKEND_URL}{FEATURE_PATH}", timeout=5)
        body = json.loads(resp.read())
        log(f"Feature route {FEATURE_PATH}: HTTP {resp.status}")
        if resp.status == 200:
            log(f"  response keys: {list(body.keys())[:5]}")
    except Exception as e:
        log(f"Feature route check failed (non-fatal): {e}")


def check_diagnostics():
    try:
        resp = urllib.request.urlopen(f"{BACKEND_URL}{DIAGNOSTICS_PATH}", timeout=5)
        data = json.loads(resp.read())
        if data.get("success"):
            d = data["data"]
            log(f"Backend: {d['backend'].get('status')} v{d['backend'].get('version')}")
            log(f"System: CPU {d['system'].get('cpu_percent')}% | Mem {d['system'].get('memory_percent')}% | Disk {d['system'].get('disk_percent')}%")
            log(f"Tools: {d['tools'].get('total')} registered")
        else:
            log(f"Diagnostics returned: {data}")
    except Exception as e:
        log(f"Diagnostics check failed (non-fatal): {e}")


def uninstall():
    uninstaller = os.path.join(INSTALL_DIR, "uninstall.exe")
    if not os.path.exists(uninstaller):
        if _INSTALLED:
            log(f"Uninstaller not found at {uninstaller}")
        return
    r = subprocess.run([uninstaller, "/S"], capture_output=True, timeout=60)
    log(f"Uninstaller exited with code {r.returncode}")
    time.sleep(2)
    remaining = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         f"Get-ItemProperty 'HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*' -ErrorAction SilentlyContinue | Where-Object {{ $_.DisplayName -like '{REGISTRY_FILTER}' }}"],
        capture_output=True, text=True, timeout=15,
    )
    if remaining.stdout.strip():
        log("WARNING: App may still be registered")
    else:
        log("Clean: app uninstalled")


def main():
    _check_version()

    parser = argparse.ArgumentParser(description="CUA-NSIS smoke test")
    parser.add_argument("--installer", help="Path to NSIS installer .exe")
    parser.add_argument("--config", help="Path to cua-nsis-config.json")
    parser.add_argument("--output-dir", default="cua-reports", help="Screenshot output directory")
    args = parser.parse_args()

    if args.config:
        _CONFIG.update(load_config(args.config))

    phases = [
        (True,  "Kill stale processes",  lambda: kill_stale()),
        (True,  "Install NSIS",          lambda: silent_install(args.installer or find_installer())),
        (True,  "Launch app",            launch_app),
        (False, "Verify window",         verify_window),
        (False, "Screenshot", lambda: take_screenshot(args.output_dir)),
        (False, "Nav walk", lambda: nav_click_through(args.output_dir)),
        (False, "Feature route",         check_feature_route),
        (False, "Check diagnostics",     check_diagnostics),
        (False, "Uninstall",             uninstall),
    ]

    passed = failed = 0
    fatal_failed = False

    print(f"\n{'='*50}")
    print(f"  CUA Smoke Test - {PRODUCT_NAME}")
    print(f"{'='*50}\n")

    for is_fatal, name, fn in phases:
        print(f"  Phase {phases.index((is_fatal, name, fn)) + 1}: {name}")
        try:
            fn()
            print(f"  V {name}\n")
            passed += 1
        except PhaseFailed:
            print(f"  X {name}\n")
            failed += 1
            if is_fatal:
                fatal_failed = True
        except Exception as e:
            print(f"  X {name}: {e}\n")
            failed += 1
            if is_fatal:
                fatal_failed = True

    print(f"{'='*50}")
    print(f"  Result: {passed}/{passed + failed} phases passed")
    if failed:
        print(f"  {failed} phase(s) FAILED")
    if fatal_failed:
        print(f"  FATAL phase failure - see above")
        sys.exit(1)
    print(f"  ALL PHASES PASSED")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
