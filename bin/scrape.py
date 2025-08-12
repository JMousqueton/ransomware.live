#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import asyncio
from aiohttp_socks import ProxyConnector
import aiohttp
import aiofiles
import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv
import os
import argparse
import sys
from shared_utils import get_current_timestamp, is_file_older_than, stdlog, errlog
from playwright.async_api import async_playwright
import socket
import fcntl  # Works on Unix-based systems
import time
import base64
import psutil
import ssl
import re
import requests
from urllib.parse import urljoin, urlparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import inspect

from libcapture import capture_group

# -------------------- CONFIG OVERRIDES --------------------
# Any group name in this set will be scraped via simple Tor HTTP (requests)
SPECIAL_HTML_FETCH_GROUPS = {"interlock", "worldleaks"}  # extend as needed, e.g., {"interlock", "examplegroup"}

# -------------------- ENV LOADING --------------------
env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)

home = os.getenv("RANSOMWARELIVE_HOME")
db_dir = Path(home + os.getenv("DB_DIR"))
img_dir = Path(home + os.getenv("IMAGES_DIR"))
tmp_dir = Path(home + os.getenv("TMP_DIR"))
watermark = Path(home + os.getenv("WATERMARK_IMAGE_PATH"))
TOR_PWD = os.getenv("TOR_PASSWORD")

proxy_address = os.getenv("TOR_PROXY_SERVER", "socks5://127.0.0.1:9050")  # Default to Tor proxy

# add this helper (e.g., above scrape_group)
async def _run_capture_group(url: str):
    """
    Safely invoke libcapture.capture_group from within an async context.
    - If it's a coroutine function: await it.
    - If it's sync but uses asyncio.run internally: run it in a worker thread.
    """
    if inspect.iscoroutinefunction(capture_group):
        return await capture_group(url)
    # capture_group is sync; run it in a separate thread so asyncio.run inside won't conflict
    return await asyncio.to_thread(capture_group, url)



# -------------------- FAVICON (Playwright path) --------------------
async def download_favicon(page, save_path):
    try:
        favicon_url = await page.evaluate(
            "() => { return document.querySelector('link[rel~=\"icon\"]')?.href; }"
        )
        if not favicon_url:
            return False

        if favicon_url.startswith("data:"):
            try:
                header, base64_data = favicon_url.split(",", 1)
                favicon_bytes = base64.b64decode(base64_data)
                async with aiofiles.open(save_path, "wb") as f:
                    await f.write(favicon_bytes)
                stdlog(f"Base64-encoded favicon saved at {save_path}")
                return True
            except Exception as e:
                errlog(f"Error decoding Base64 favicon: {str(e).splitlines()[0]}")
                return False
        else:
            connector = ProxyConnector.from_url("socks5://127.0.0.1:9050")
            retries = 1
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            for attempt in range(retries):
                try:
                    async with aiohttp.ClientSession(connector=connector) as session:
                        async with session.get(favicon_url, ssl=ssl_context) as response:
                            if response.status == 200:
                                async with aiofiles.open(save_path, "wb") as f:
                                    await f.write(await response.read())
                                stdlog(f"Favicon saved at {save_path}")
                                return True
                            else:
                                errlog(f"Failed to fetch favicon: HTTP {response.status}")
                except Exception as e:
                    errlog(f"Retry {attempt + 1}/{retries}: Error downloading favicon: {str(e)}")
                    await asyncio.sleep(2)

            errlog(f"Failed to download favicon after {retries} attempts: {favicon_url}")
            return False

    except Exception as e:
        errlog(f"Error downloading favicon: {str(e).splitlines()[0]}")
        return False

# -------------------- FAVICON (special path helper) --------------------
async def download_favicon_from_url(page_url: str, save_path: str) -> bool:
    """
    Minimal favicon fetcher for SPECIAL_HTML_FETCH_GROUPS.
    Tries /favicon.ico at the origin of the provided page URL via Tor.
    """
    try:
        parsed = urlparse(page_url)
        origin = f"{parsed.scheme}://{parsed.netloc}/"
        favicon_url = urljoin(origin, "favicon.ico")

        connector = ProxyConnector.from_url("socks5://127.0.0.1:9050")
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(favicon_url, ssl=ssl_context, timeout=30) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    if data:
                        async with aiofiles.open(save_path, "wb") as f:
                            await f.write(data)
                        stdlog(f"Favicon (fallback) saved at {save_path}")
                        return True
        return False
    except Exception as e:
        errlog(f"Favicon fallback failed for {page_url}: {str(e).splitlines()[0]}")
        return False

# -------------------- TOR CONTROL --------------------
def restart_tor_control_port(control_port=9051, password=None):
    try:
        with socket.create_connection(("127.0.0.1", control_port)) as s:
            if password:
                s.sendall(f"AUTHENTICATE \"{password}\"\r\n".encode())
            else:
                s.sendall(b"AUTHENTICATE\r\n")

            response = s.recv(1024).decode()
            if "250 OK" not in response:
                raise Exception(f"Authentication failed: {response}")

            s.sendall(b"SIGNAL RELOAD\r\n")
            response = s.recv(1024).decode()
            if "250 OK" in response:
                stdlog("Tor successfully restarted via control port.")
            else:
                raise Exception(f"Failed to restart Tor: {response}")
    except Exception as e:
        errlog(f"Error: {e}")
        exit()

# -------------------- LOCKING --------------------
lock_file_path = tmp_dir / "scrape.lock"

def is_process_alive(pid):
    try:
        return psutil.pid_exists(pid)
    except Exception:
        return False

def acquire_lock():
    if lock_file_path.exists():
        try:
            with open(lock_file_path, "r") as f:
                content = f.read()
                if "PID" in content:
                    old_pid = int(content.strip().split(":")[1])
                    if is_process_alive(old_pid):
                        errlog(f"Script already running with PID {old_pid}. Exiting.")
                        sys.exit(1)
                    else:
                        stdlog(f"Stale lock file found (PID {old_pid} not running). Overwriting.")
        except Exception as e:
            errlog(f"Error reading existing lock file: {e}")

    lock_file = open(lock_file_path, "w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_file.write(f"PID: {os.getpid()}\n")
        lock_file.flush()
        return lock_file
    except BlockingIOError:
        errlog("Another instance of the script is already running (fcntl lock).")
        sys.exit(1)

def release_lock(lock_file):
    try:
        fcntl.flock(lock_file, fcntl.LOCK_UN)
        lock_file.close()
    except Exception as e:
        errlog(f"Error releasing lock: {e}")

def remove_lock_file():
    if lock_file_path.exists():
        lock_file_path.unlink()
        stdlog("Previous lock removed.")

# -------------------- UTILS --------------------
def offline_for_more_than(last_scrape, days):
    try:
        last_scrape_date = datetime.strptime(str(last_scrape), "%Y-%m-%d %H:%M:%S.%f")
        if last_scrape_date.tzinfo is None:
            last_scrape_date = last_scrape_date.replace(tzinfo=timezone.utc)
        current_time = datetime.now(timezone.utc)
        return current_time - last_scrape_date > timedelta(days=days)
    except ValueError:
        return False

def extract_title_from_html(html_text: str) -> str:
    try:
        m = re.search(r"<title[^>]*>(.*?)</title>", html_text, flags=re.IGNORECASE | re.DOTALL)
        if m:
            # Collapse whitespace/newlines
            return re.sub(r"\s+", " ", m.group(1)).strip()[:300]
    except Exception:
        pass
    return ""

def scrape_onion_text(url: str) -> str:
    """
    Blocking HTTP fetch via Tor SOCKS proxy using requests (as per your snippet).
    Returns the HTML text or raises an exception.
    """
    proxies = {
        "http": "socks5h://127.0.0.1:9050",
        "https": "socks5h://127.0.0.1:9050"
    }
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    resp = requests.get(url, proxies=proxies, headers=headers, verify=False, timeout=45)
    resp.raise_for_status()
    return resp.text

async def fetch_html_via_tor(url: str) -> str:
    # Run blocking requests in a thread
    return await asyncio.to_thread(scrape_onion_text, url)

# -------------------- SCRAPER --------------------
async def scrape_group(context, group, bypass_enabled_flag, verbose):
    group_name = group["name"]
    special_path = group_name.lower() in {g.lower() for g in SPECIAL_HTML_FETCH_GROUPS}

    for location in group["locations"]:
        slug = location["slug"]

        if bypass_enabled_flag or location["enabled"]:
            md5_slug = hashlib.md5(slug.encode()).hexdigest()
            filename = tmp_dir / f"{group_name}-{md5_slug}.html"

            if is_file_older_than(filename, 60):
                page = None
                try:
                    stdlog(f"[{group_name}] Scraping {slug} ...")

                    if special_path:
                        stdlog(f"[{group_name}] use simple HTML fetch for {slug}")
                        # ---- SPECIAL PATH: simple HTML fetch via Tor/requests ----
                        html_text = await fetch_html_via_tor(slug)
                        title = extract_title_from_html(html_text) or "(no title)"
                        async with aiofiles.open(filename, "w", encoding="utf-8", errors="ignore") as f:
                            await f.write(html_text)
                        if verbose:
                            stdlog(f"[{group_name}] (special) Saved HTML and extracted title: {title}")

                    else:
                        # ---- DEFAULT: Playwright path ----
                        page = await context.new_page()
                        await page.goto(slug, timeout=60000)
                        await page.mouse.move(x=500, y=400)
                        await page.mouse.wheel(delta_y=2000, delta_x=0)
                        await page.wait_for_timeout(60000)
                        content = await page.content()
                        title = await page.title()
                        if verbose:
                            stdlog(f"[{group_name}] Successfully got title for {slug}: {title}")
                        async with aiofiles.open(filename, "w", encoding="utf-8") as f:
                            await f.write(content)

                    # Common updates
                    now = get_current_timestamp()
                    location.update({
                        "available": True,
                        "updated": now,
                        "lastscrape": now,
                        "title": title,
                        "enabled": True,
                    })
                    if verbose:
                        stdlog(f"[{group_name}] Successfully scraped {slug}")

                    # Screenshot / capture
                    hash_slug = hashlib.md5(slug.encode()).hexdigest()
                    image_path = f"{img_dir}/groups/{group_name}-{hash_slug}.png"
                    if not Path(image_path).exists() or is_file_older_than(image_path, 10080):
                        # If you still want a screenshot from browser for non-special groups, keep page logic above.
                        # For both paths we’ll delegate to your capture lib which handles its own logic.
                        try:
                            #capture_group(slug)  # fixed undefined variable (was post_url)
                            await _run_capture_group(slug)
                        except Exception as e:
                            errlog(f"[{group_name}] capture_group failed: {str(e).splitlines()[0]}")

                    # Favicon
                    favicon_path = f"{img_dir}/groups/favicons/{group_name}-{hash_slug}.png"
                    if not Path(favicon_path).exists() or is_file_older_than(favicon_path, 10080):
                        if special_path:
                            await download_favicon_from_url(slug, favicon_path)
                        else:
                            if page:
                                await download_favicon(page, favicon_path)

                except Exception as e:
                    now = get_current_timestamp()
                    location.update({
                        "available": False,
                        "lastscrape": now,
                    })
                    errlog(f"[{group_name}] Error scraping {slug}: {str(e).splitlines()[0]}")
                    # Disable location if offline for more than the threshold days
                    days = 30
                    if offline_for_more_than(location.get("updated", now), days):
                        stdlog(f"[{group_name}] {slug} has been offline for more than {days} days. Disabling.")
                        location.update({"enabled": False})
                finally:
                    if page:
                        await page.close()


                try:
                    http_meta = await fetch_headers_via_tor(slug)
                    # Keep it compact in the JSON
                    location["http"] = {
                        "fetched_at": http_meta.get("fetched_at"),
                        "start_url": http_meta.get("start_url"),
                        "final_url": http_meta.get("final_url"),
                        "status": http_meta.get("status"),
                        "http_version": http_meta.get("http_version"),
                        "redirect_chain": http_meta.get("redirect_chain", []),
                        "fingerprint": http_meta.get("fingerprint", {}),
                        # If you want the full header bag, keep it; otherwise comment this out:
                        "headers": http_meta.get("headers", {}),
                        "error": http_meta.get("error"),
                    }
                    if verbose and not http_meta.get("error"):
                        stdlog(f"[{group_name}] Header fingerprint: {location['http']['fingerprint']}")
                except Exception as e:
                    errlog(f"[{group_name}] header fingerprint failed for {slug}: {str(e).splitlines()[0]}")
                
            else:
                if verbose:
                    stdlog(f"[{group_name}] Skipping {slug} as the file is fresh.")

async def scrape_pages(group_to_parse, bypass_enabled_flag, verbose=False):
    async with async_playwright() as p:
        browser = await p.firefox.launch(
            proxy={"server": proxy_address},
            headless=True
        )
        context = await browser.new_context(ignore_https_errors=True)

        await context.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
        })

        json_file_path = db_dir / "groups.json"
        if json_file_path.exists():
            with json_file_path.open('r', encoding="utf-8") as file:
                all_groups = json.load(file)
        else:
            all_groups = []

        if group_to_parse:
            groups_to_scrape = [group for group in all_groups if group["name"] == group_to_parse]
        else:
            groups_to_scrape = all_groups

        tasks = [scrape_group(context, group, bypass_enabled_flag, verbose) for group in groups_to_scrape]
        await asyncio.gather(*tasks)

        # Update original data
        for group in groups_to_scrape:
            for i, existing_group in enumerate(all_groups):
                if existing_group["name"] == group["name"]:
                    all_groups[i] = group
                    break
            else:
                all_groups.append(group)

        with json_file_path.open("w", encoding="utf-8") as file:
            json.dump(all_groups, file, indent=4)
            stdlog("Updated groups.json")

        await browser.close()


# -------------------- HTTP FINGERPRINT --------------------
from typing import Dict, Any, List, Tuple

INTERESTING_SECURITY_HEADERS = [
    "content-security-policy",
    "strict-transport-security",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
    "cross-origin-opener-policy",
    "cross-origin-resource-policy",
    "x-xss-protection",
]

def _normalize_headers(hdrs: aiohttp.typedefs.LooseHeaders) -> Dict[str, str]:
    # aiohttp CIMultiDict -> plain dict with lowercase keys; join multiple values with ", "
    out = {}
    for k, v in hdrs.items():
        lk = k.lower()
        if lk in out:
            out[lk] = f"{out[lk]}, {v}"
        else:
            out[lk] = str(v)
    return out

async def _tiny_get(session: aiohttp.ClientSession, url: str):
    # Small GET when HEAD is blocked; ask just the first byte
    return await session.get(
        url,
        headers={"Range": "bytes=0-0"},
        allow_redirects=False,
        timeout=45,
        ssl=False  # we'll already run via Tor; also many .onion are http
    )

async def fetch_headers_via_tor(url: str, max_redirects: int = 5) -> Dict[str, Any]:
    """
    Collect HTTP(S) metadata over Tor for a URL:
    - redirect chain
    - final status / version
    - normalized headers
    - extracted fingerprint fields
    """
    connector = ProxyConnector.from_url("socks5://127.0.0.1:9050")
    result: Dict[str, Any] = {
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "start_url": url,
        "redirect_chain": [],   # list of {"status":..., "location":...}
        "final_url": None,
        "status": None,
        "http_version": None,
        "headers": {},
        "fingerprint": {},
        "error": None,
    }

    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            current = url
            redirects = 0

            while True:
                # Prefer HEAD
                try:
                    resp = await session.head(current, allow_redirects=False, timeout=45, ssl=False)
                except aiohttp.ClientResponseError as cre:
                    # Some servers actively reject HEAD with a 4xx; fall back to tiny GET
                    resp = await _tiny_get(session, current)
                except Exception:
                    # Network or method not allowed -> tiny GET
                    resp = await _tiny_get(session, current)

                version = getattr(resp, "version", None)
                http_ver = f"HTTP/{version.major}.{version.minor}" if version else None
                headers = _normalize_headers(resp.headers)
                status = resp.status

                # Handle redirect
                loc = headers.get("location")
                if status in (301, 302, 303, 307, 308) and loc and redirects < max_redirects:
                    result["redirect_chain"].append({"status": status, "location": loc})
                    # Resolve relative locations
                    try:
                        current = urljoin(current, loc)
                    except Exception:
                        current = loc
                    redirects += 1
                    continue

                # Final response reached
                result["final_url"] = str(resp.url)
                result["status"] = status
                result["http_version"] = http_ver
                result["headers"] = headers

                # Extract useful fields
                fp = {
                    "server": headers.get("server"),
                    "x_powered_by": headers.get("x-powered-by"),
                    "via": headers.get("via"),
                    "cdn": headers.get("cf-ray") or headers.get("x-amz-cf-id") or headers.get("x-akamai-transformed"),
                    "content_type": headers.get("content-type"),
                    "content_length": headers.get("content-length"),
                    "set_cookie_present": "set-cookie" in headers,
                    "security_headers": {h: headers[h] for h in INTERESTING_SECURITY_HEADERS if h in headers},
                }
                result["fingerprint"] = fp
                # Drain response body if tiny GET to avoid warnings
                try:
                    await resp.read()
                except Exception:
                    pass
                break

    except Exception as e:
        result["error"] = str(e).splitlines()[0]

    return result


# -------------------- MAIN --------------------
if __name__ == "__main__":
    print(
    r'''
       _______________                        |*\_/*|________
      |  ___________  |                      ||_/-\_|______  |
      | |           | |                      | |           | |
      | |   0   0   | |                      | |   0   0   | |
      | |     -     | |                      | |     -     | |
      | |   \___/   | |                      | |   \___/   | |
      | |___     ___| |                      | |___________| |
      |_____|\_/|_____|                      |_______________|
        _|__|/ \|_|_.............💔.............._|________|_
       / ********** \                          / ********** \ 
     /  ************  \   ransomware.live     /  ************  \ 
    --------------------                    --------------------
    '''
    )

    start_time = time.time()
    parser = argparse.ArgumentParser(description="Scrape data from groups.json")
    parser.add_argument("-G", "--group", help="Specify the group name to parse", default=None)
    parser.add_argument("-F", "--force", help="Force remove previous lock and run the script", action="store_true")
    parser.add_argument("-B", "--bypass", help="Scrape all locations even if 'enabled' is false", action="store_true")
    parser.add_argument("-V", "--verbose", help="Display more information", action="store_true")
    args = parser.parse_args()

    if args.force:
        remove_lock_file()

    lock_file = None
    if not args.group:
        lock_file = acquire_lock()

    try:
        restart_tor_control_port(password=TOR_PWD)
        asyncio.run(scrape_pages(args.group, args.bypass, args.verbose))
    finally:
        if lock_file:
            release_lock(lock_file)
        end_time = time.time()
        stdlog(f"Script finished. Total runtime: {(end_time - start_time)/60:.2f} minutes.")
