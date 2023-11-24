#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
screenshot up hosts using playwright 
inspired by Ransomwatch & Ransomlook 
'''

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_sync 
from sharedutils import stdlog, errlog
from sharedutils import openjson  
import sys      
from PIL import Image
from PIL import ImageDraw
from PIL.PngImagePlugin import PngInfo
from datetime import datetime
from parse import add_watermark

def screenshot(webpage,fqdn,group=None):
    stdlog('webshot: {}'.format(webpage))
    with sync_playwright() as play:
        try:
            if group in ['blackbasta']:
                    stdlog('(!) Exception for blackbasta')
                    browser = play.firefox.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                          args=[''])
            else:
                    browser = play.chromium.launch(proxy={"server": "socks5://127.0.0.1:9050"},
                          args=[''])
            context = browser.new_context(ignore_https_errors= True )
            Image.MAX_IMAGE_PIXELS = None
            page = context.new_page()
            stealth_sync(page)
            page.goto(webpage, wait_until='load', timeout = 120000)
            page.bring_to_front()
            delay=15000

            page.wait_for_timeout(delay)
            page.mouse.move(x=500, y=400)
            page.wait_for_load_state('networkidle')
            page.mouse.wheel(delta_y=2000, delta_x=0)
            page.wait_for_load_state('networkidle')
            page.wait_for_timeout(5000)

            #page.wait_for_timeout(delay)
            #page.mouse.move(x=500, y=400)
            #page.wait_for_load_state('networkidle')
            #page.mouse.wheel(delta_y=2000, delta_x=0)
            #page.wait_for_load_state('networkidle')
            #page.mouse.wheel(delta_y=2000, delta_x=0)
            #page.wait_for_timeout(5000)
            name = 'docs/screenshots/' + fqdn.replace('.', '-') + '.png'
            page.screenshot(path=name, full_page=True)
            image = Image.open(name)
            metadata = PngInfo()
            metadata.add_text("Source", "Ransomware.live")
            metadata.add_text("Copyright", "Ransomware.live")
            Description = group + " : " + webpage
            metadata.add_text("Description",Description)
            metadata.add_text("Author","Julien Mousqueton")
            current_date = str(datetime.now().strftime('%Y:%m:%d %H:%M:%S'))
            metadata.add_text("Creation Time",current_date)
            # image.save(name, pnginfo=metadata)
            stdlog(' Image : ' + fqdn + ' has been written')
            draw = ImageDraw.Draw(image)
            draw.text((10, 10), "https://www.ransomware.live", fill=(0, 0, 0))
            # image.save(name)
            image.save(name, pnginfo=metadata)
            stdlog(' Image : ' + fqdn + ' has been tag')
            add_watermark(name)
        except PlaywrightTimeoutError:
            stdlog('Timeout!')
        except Exception as exception:
            stdlog(exception)
        browser.close()


def main():
    groupname = sys.argv[1]
    groups = openjson('groups.json')
    if groupname is None:
        for group in groups:
            stdlog('group: {}'.format(group['name']))
            for webpage in group['locations']:
                if webpage['available'] is True:
                    screenshot('http://'+webpage['fqdn'],webpage['fqdn'])
                else:
                    stdlog('webshot: {}'.format(webpage['slug']) + ' not available')
    else:
        stdlog('group: '+ groupname)
        for group in groups:
            if group["name"] == groupname:
                for webpage in group['locations']:
                    screenshot('http://'+webpage['fqdn'],webpage['fqdn'],groupname) 



if __name__ == '__main__':
    main()

