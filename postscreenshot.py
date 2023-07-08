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
                    page.wait_for_timeout(6000)
                    page.screenshot(path=name, full_page=True)
                    image = Image.open(name)
                    draw = ImageDraw.Draw(image)
                    draw.text((10, 10), "https://www.ransomware.live", fill=(0, 0, 0))
                    image.save(name)
                except PlaywrightTimeoutError:
                    stdlog('Timeout!')
                except Exception as exception:
                    errlog(exception)
                    errlog("error")
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

