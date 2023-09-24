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
from PIL.PngImagePlugin import PngInfo
from datetime import datetime
# For Notification 
import sys

def screenshot(webpage,delay=15000,output=None):
    stdlog('webshot: {}'.format(webpage))
    name = 'docs/screenshots/posts/' + output + '.png'
    with sync_playwright() as play:
                try:
                    if webpage.startswith("http://stniiomy"):
                        browser = play.firefox.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                          args=[''])
                        print('(!) exception')
                    elif webpage.startswith("http://noescape"):
                        browser = play.firefox.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                          args=[''])
                        print('(!) exception')
                    elif webpage.startswith("http://medusa"):
                        browser = play.firefox.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                          args=[''])
                        print('(!) exception')
                    elif webpage.startswith("http://cactus"):
                        browser = play.firefox.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                          args=[''])
                        print('(!) exception')
                    elif webpage.startswith("http://hl666"):
                        browser = play.firefox.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                          args=[''])
                        print('(!) exception')
                    elif webpage.startswith("https://ransomed.vc/"):
                        browser = play.firefox.launch()
                        print('(!) not via tor')
                    else:
                        browser = play.chromium.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                            args=[''])
                    context = browser.new_context(ignore_https_errors= True )
                    Image.MAX_IMAGE_PIXELS = None
                    page = context.new_page()
                    page.goto(webpage, wait_until='load', timeout = 120000)
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
                    current_date = str(datetime.now().strftime('%Y:%m:%d %H:%M:%S')) 
                    metadata.add_text("Creation Time",current_date)
                    draw = ImageDraw.Draw(image)
                    draw.text((10, 10), "https://www.ransomware.live", fill=(0, 0, 0))
                    image.save(name, pnginfo=metadata)  
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

