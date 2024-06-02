import os, hashlib
from sys import platform
from sharedutils import openjson
from sharedutils import runshellcmd
# from sharedutils import todiscord, totwitter, toteams
from sharedutils import stdlog, dbglog, errlog   # , honk
# For screenshot 
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
# For watermark on screenshot 
from PIL import Image
from PIL import ImageDraw
from PIL import ImageEnhance
from PIL.PngImagePlugin import PngInfo
from datetime import datetime
# For Notification 
import sys

def add_watermark(image_path, watermark_image_path='./docs/ransomwarelive.png'):
    """
    Adds a watermark image (with 50% transparency) to the center of the input image and overwrites it.
    
    :param image_path: Path to the image to be watermarked.
    :param watermark_image_path: Path to the watermark image.
    :return: None
    """
    # Open the image to be watermarked
    stdlog('open image ' + image_path)
    original = Image.open(image_path)
    if original.mode != 'RGBA':
        original = original.convert('RGBA')
    
    # Open the watermark image
    stdlog('open watermark image ' + watermark_image_path)
    watermark = Image.open(watermark_image_path)
    if watermark.mode != 'RGBA':
        watermark = watermark.convert('RGBA')

    # Adjust opacity of watermark
    transparent = Image.new('RGBA', watermark.size, (255, 255, 255, 0))
    for x in range(watermark.width):
        for y in range(watermark.height):
            r, g, b, a = watermark.getpixel((x, y))
            transparent.putpixel((x, y), (r, g, b, int(a * 0.2)))

    watermark = transparent

    # Position watermark in the center
    x = (original.width - watermark.width) // 2
    y = (original.height - watermark.height) // 2

    # Overlay the watermark onto the screenshot
    original.paste(watermark, (x, y), watermark)
    
    # Overwrite the original screenshot
    stdlog('save image ' + image_path)
    original.save(image_path, 'PNG')



def screenshot(webpage,delay=30000,output=None):
    stdlog('webshot: {}'.format(webpage))
    name = 'docs/screenshots/posts/' + output + '.png'
    with sync_playwright() as play:
                try:
                    tor_prefixes = ["http://stniiomy", "http://noescape", "http://medusa", "http://cactus", "http://hl666", "http://incblog","http://rhysida"]
                    if any(webpage.startswith(prefix) for prefix in tor_prefixes):
                        browser = play.firefox.launch(proxy={"server": "socks5://127.0.0.1:9050"}, args=[''])
                        print('(!) exception')
                    elif webpage.startswith("https://handala"):
                        browser = play.firefox.launch()
                        print('(!) not via tor')
                    elif webpage.startswith("https://t.me"):
                        browser = play.firefox.launch()
                        print('(!) not via tor')
                    elif webpage.startswith("http://incapt.su"):
                        browser = play.firefox.launch()
                        print('(!) not via tor')
                    elif webpage.startswith('https://werewolves'):
                        browser = play.firefox.launch()
                        print('(!) not via tor')
                    elif  webpage.startswith('https://dispossessor'):
                        browser = play.firefox.launch()
                        print('(!) not via tor')
                    else:
                        browser = play.chromium.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                            args=[''])
                    context = browser.new_context(ignore_https_errors= True )
                    Image.MAX_IMAGE_PIXELS = None
                    page = context.new_page()
                    page.goto(webpage, wait_until='load', timeout = 240000)
                    page.bring_to_front()
                    page.wait_for_timeout(delay)
                    page.mouse.move(x=500, y=400)
                    page.wait_for_load_state('networkidle')
                    page.mouse.wheel(delta_y=2000, delta_x=0)
                    page.wait_for_load_state('networkidle')
                    page.wait_for_timeout(12000)
                    page.screenshot(path=name, full_page=True)
                    image = Image.open(name)
                    metadata = PngInfo()
                    metadata.add_text("Source", "Ransomware.live")
                    metadata.add_text("Copyright", "Ransomware.live")
                    metadata.add_text("Description",webpage)
                    metadata.add_text("Author","Julien Mousqueton")
                    current_date = datetime.now().strftime('%Y:%m:%d %H:%M:%S') 
                    metadata.add_text("Creation Time",current_date)
                    draw = ImageDraw.Draw(image)
                    current_datetime = datetime.now()
                    iso_formatted = current_datetime.isoformat()
                    draw.text((10, 10), iso_formatted, fill=(0, 0, 0))
                    #draw.text((10, 10), "https://www.ransomware.live", fill=(0, 0, 0))
                    image.save(name, pnginfo=metadata)  
                    add_watermark(name)
                except PlaywrightTimeoutError:
                    stdlog('Timeout!')
                except Exception as exception:
                    stdlog(exception)
                #browser.close()

def main():
    post_url = sys.argv[1]
    
    hash_object = hashlib.md5()
    hash_object.update(post_url.encode('utf-8'))
    hex_digest = hash_object.hexdigest()
    screenshot(post_url,15000,hex_digest)
    stdlog(' --> ' + hex_digest)

if __name__ == '__main__':
    main()

