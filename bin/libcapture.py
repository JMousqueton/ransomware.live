import asyncio
import hashlib
import json
import os
import sys
import re
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image, ImageFilter
from playwright.async_api import async_playwright
import shared_utils
import cv2  # OpenCV

# ----- FIXED CONFIG -----
TOR_PROXY = "socks5://127.0.0.1:9050"
VICTIM_OUTPUT_DIR = "/opt/ransomwarelive/images/victims"
GROUP_OUTPUT_DIR = "/opt/ransomwarelive/images/groups"
WATERMARK_PATH = Path("/opt/ransomwarelive/images/ransomwarelive.png")
VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 1000
OVERLAP = 100  # px

blur_gang = ['pear', 'qilin', 'rhysida']
networkidle_gang = ['incransom']
GROUPS_JSON_PATH = os.path.join(os.path.dirname(__file__), "../db/groups.json")
HAAR_CASCADE_PATH = "/opt/ransomwarelive/etc/haarcascade_frontalface_default.xml"
# -------------------------

# Default OUTPUT_DIR for victims (keeps capture_victim behavior unchanged)
OUTPUT_DIR = VICTIM_OUTPUT_DIR
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- helpers ---
def url_to_md5(url: str) -> str:
    return hashlib.md5(url.encode("utf-8")).hexdigest()

def _load_groups():
    if not os.path.exists(GROUPS_JSON_PATH):
        return []
    with open(GROUPS_JSON_PATH, encoding="utf-8") as f:
        return json.load(f)

def _fqdn_from_url(target_url: str):
    try:
        return urlparse(target_url).hostname
    except Exception:
        return None

def url_in_group_list(target_url: str, group_names: list[str]) -> bool:
    target_fqdn = _fqdn_from_url(target_url)
    if not target_fqdn:
        return False
    groups = _load_groups()
    group_set = {g.lower() for g in group_names}
    for group in groups:
        if group.get("name", "").lower() in group_set:
            for loc in group.get("locations", []):
                if loc.get("fqdn") == target_fqdn:
                    return True
    return False

def _safe_slug(name: str) -> str:
    s = re.sub(r"\s+", "-", name.strip().lower())
    s = re.sub(r"[^a-z0-9\-._]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "unknown"

def resolve_group_name_from_url(target_url: str) -> str | None:
    """
    Return the group name owning target_url (match by fqdn in groups.json), else None.
    """
    target_fqdn = _fqdn_from_url(target_url)
    if not target_fqdn:
        return None
    for group in _load_groups():
        for loc in group.get("locations", []):
            if loc.get("fqdn") == target_fqdn:
                return group.get("name")
    return None

def blur_image(img_path: str, radius: int = 5):
    img = Image.open(img_path)
    blurred = img.filter(ImageFilter.GaussianBlur(radius=radius))
    blurred.save(img_path)

def detect_faces_and_blur(img_path: str) -> bool:
    if not os.path.exists(HAAR_CASCADE_PATH):
        print(f"[WARN] Haar cascade not found: {HAAR_CASCADE_PATH}")
        return False
    face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
    img = cv2.imread(img_path)
    if img is None:
        return False
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
    if len(faces) > 0:
        print(f"[✓] Detected {len(faces)} face(s) → blurring...")
        blur_image(img_path)
        return True
    return False

def decide_simplewait(url: str) -> bool:
    if url_in_group_list(url, networkidle_gang):
        print("[policy] URL forces networkidle mode")
        return False
    return True  # default is simplewait ON

# --- core capture functions ---
async def screenshot_onion(url: str) -> str:
    simplewait = decide_simplewait(url)
    md5_base = url_to_md5(url)
    final_path = os.path.join(OUTPUT_DIR, f"{md5_base}.png")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            proxy={"server": TOR_PROXY},
            viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
            ignore_https_errors=True
        )
        page = await context.new_page()
        print(f"[+] Navigating to {url} via Tor...")

        if simplewait:
            await page.goto(url, timeout=60000)
            print("[~] Waiting 8s for JS...")
            await page.wait_for_timeout(8000)
        else:
            await page.goto(url, wait_until="networkidle", timeout=120000)
            await asyncio.sleep(2)

        scroll_height = await page.evaluate("() => document.body.scrollHeight")
        inner_height = await page.evaluate("() => window.innerHeight")

        if scroll_height <= inner_height + 20:
            await page.screenshot(path=final_path, full_page=True)
        else:
            segment_dir = os.path.join(OUTPUT_DIR, f"{md5_base}_segments")
            os.makedirs(segment_dir, exist_ok=True)
            y, n, stitched_images, last_position = 0, 0, [], -1
            while True:
                await page.evaluate(f"window.scrollTo(0, {y});")
                await asyncio.sleep(1.1)
                seg_path = os.path.join(segment_dir, f"{n:03d}.png")
                await page.screenshot(path=seg_path, full_page=False)
                stitched_images.append(seg_path)
                n += 1
                position = await page.evaluate("() => window.scrollY")
                inner_height = await page.evaluate("() => window.innerHeight")
                scroll_height = await page.evaluate("() => document.body.scrollHeight")
                if position + inner_height >= scroll_height or position == last_position:
                    break
                last_position = position
                y += (VIEWPORT_HEIGHT - OVERLAP)

            images = [Image.open(p) for p in stitched_images]
            total_width, total_height = images[0].width, images[0].height
            crops = [images[0]]
            for img in images[1:]:
                crop_box = (0, OVERLAP, img.width, img.height)
                crops.append(img.crop(crop_box))
                total_height += (img.height - OVERLAP)
            stitched = Image.new("RGB", (total_width, total_height))
            offset = 0
            for img in crops:
                stitched.paste(img, (0, offset))
                offset += img.height
                if img is not crops[0]:
                    offset -= OVERLAP
            stitched.save(final_path)
            for pth in stitched_images:
                os.remove(pth)
            os.rmdir(segment_dir)

        await browser.close()

    if url_in_group_list(url, blur_gang):
        blur_image(final_path)
    else:
        detect_faces_and_blur(final_path)

    if WATERMARK_PATH.exists() and os.path.exists(final_path):
        shared_utils.add_watermark(final_path, WATERMARK_PATH)

    return final_path

async def screenshot_onion_with_path(url: str, final_path: str) -> str:
    """
    Same logic as screenshot_onion, but writes to the provided final_path.
    Used by capture_group to customize filename.
    """
    simplewait = decide_simplewait(url)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            proxy={"server": TOR_PROXY},
            viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT},
            ignore_https_errors=True
        )
        page = await context.new_page()
        print(f"[+] Navigating to {url} via Tor...")

        if simplewait:
            await page.goto(url, timeout=60000)
            print("[~] Waiting 8s for JS...")
            await page.wait_for_timeout(8000)
        else:
            await page.goto(url, wait_until="networkidle", timeout=120000)
            await asyncio.sleep(2)

        scroll_height = await page.evaluate("() => document.body.scrollHeight")
        inner_height = await page.evaluate("() => window.innerHeight")

        if scroll_height <= inner_height + 20:
            await page.screenshot(path=final_path, full_page=True)
        else:
            segment_dir = os.path.join(os.path.dirname(final_path), f"{Path(final_path).stem}_segments")
            os.makedirs(segment_dir, exist_ok=True)
            y, n, stitched_images, last_position = 0, 0, [], -1
            while True:
                await page.evaluate(f"window.scrollTo(0, {y});")
                await asyncio.sleep(1.1)
                seg_path = os.path.join(segment_dir, f"{n:03d}.png")
                await page.screenshot(path=seg_path, full_page=False)
                stitched_images.append(seg_path)
                n += 1
                position = await page.evaluate("() => window.scrollY")
                inner_height = await page.evaluate("() => window.innerHeight")
                scroll_height = await page.evaluate("() => document.body.scrollHeight")
                if position + inner_height >= scroll_height or position == last_position:
                    break
                last_position = position
                y += (VIEWPORT_HEIGHT - OVERLAP)

            images = [Image.open(p) for p in stitched_images]
            total_width, total_height = images[0].width, images[0].height
            crops = [images[0]]
            for img in images[1:]:
                crop_box = (0, OVERLAP, img.width, img.height)
                crops.append(img.crop(crop_box))
                total_height += (img.height - OVERLAP)
            stitched = Image.new("RGB", (total_width, total_height))
            offset = 0
            for img in crops:
                stitched.paste(img, (0, offset))
                offset += img.height
                if img is not crops[0]:
                    offset -= OVERLAP
            stitched.save(final_path)
            for pth in stitched_images:
                os.remove(pth)
            os.rmdir(segment_dir)

        await browser.close()

    if url_in_group_list(url, blur_gang):
        blur_image(final_path)
    else:
        detect_faces_and_blur(final_path)

    if WATERMARK_PATH.exists() and os.path.exists(final_path):
        shared_utils.add_watermark(final_path, WATERMARK_PATH)

    return final_path

# --- public API ---
def capture_victim(url: str) -> str:
    # Unchanged behavior: saves to VICTIM_OUTPUT_DIR/<md5(url)>.png
    return asyncio.run(screenshot_onion(url))

def capture_group(url: str) -> str:
    """
    Save to: <GROUP_OUTPUT_DIR>/<group_name-from-URL>-<md5(url)>.png
    Group name is deduced by matching the URL's fqdn against groups.json.
    """
    group_name = resolve_group_name_from_url(url)
    if not group_name:
        raise ValueError(f"Could not resolve group for URL: {url}")

    safe_group = _safe_slug(group_name)
    md5_base = url_to_md5(url)
    final_path = os.path.join(GROUP_OUTPUT_DIR, f"{safe_group}-{md5_base}.png")
    os.makedirs(GROUP_OUTPUT_DIR, exist_ok=True)

    return asyncio.run(screenshot_onion_with_path(url, final_path))
