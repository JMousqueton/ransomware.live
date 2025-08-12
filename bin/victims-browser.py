#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import curses
import json
import time
import os
import sys
import subprocess
from datetime import datetime 

VICTIMS_FILE = '../db/victims.json'
LOCK_FILE = '../tmp/parse.lock'

MODE_LIST = 0
MODE_DETAIL = 1

EDITABLE_FIELDS = ['country', 'activity', 'website']
ACTIVITY_OPTIONS = [
    "Manufacturing", "Construction", "Transportation/Logistics", "Technology",
    "Healthcare", "Financial Services", "Public Sector", "Education",
    "Business Services", "Consumer Services", "Energy", "Telecommunication",
    "Agriculture and Food Production", "Hospitality and Tourism", "Not Found"
]

def load_victims():
    with open(VICTIMS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return list(reversed(data))

def save_victims(victims):
    with open(VICTIMS_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(reversed(victims)), f, indent=4, ensure_ascii=False)

def create_lock():
    if os.path.exists(LOCK_FILE):
        print("Lock file exists. Another instance may be running.")
        sys.exit(1)
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

def remove_lock():
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE, 'r') as f:
            pid = f.read().strip()
        if pid == str(os.getpid()):
            os.remove(LOCK_FILE)

def apply_filters(victims, filters):
    filtered = victims
    if filters['empty_website']:
        filtered = [v for v in filtered if not v.get('website')]
    if filters['empty_country']:
        filtered = [v for v in filtered if not v.get('country')]
    if filters['empty_activity']:
        filtered = [v for v in filtered if not v.get('activity') or v.get('activity') == "Not Found"]
    return filtered

def show_help(stdscr):
    stdscr.clear()
    stdscr.border()
    height, width = stdscr.getmaxyx()
    title = "Help - Filters Explanation"
    stdscr.addstr(0, (width - len(title)) // 2, title)
    lines = [
        "w: toggle victims with empty website",
        "c: toggle victims with empty country",
        "a: toggle victims with empty activity",
        "r: reset filters",
        "Arrow Up/Down: move",
        "PageUp/PageDown: move by page",
        "Enter: edit",
        "q: quit program",
        "ESC or any key to return"
    ]
    for idx, line in enumerate(lines):
        stdscr.addstr(2 + idx, 2, line)
    stdscr.refresh()
    stdscr.getch()

from datetime import datetime

def edit_field(stdscr, all_victims, victims, current_idx, field):
    def add_modification(entry, field):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        modification = {
            "date": now,
            "description": f"Update {field}"
        }
        if "modifications" not in entry:
            entry["modifications"] = []
        entry["modifications"].append(modification)

    if field == 'activity':
        idx = 0
        while True:
            stdscr.clear()
            stdscr.border()
            height, width = stdscr.getmaxyx()
            title = "Select Activity (Enter to choose, ESC to cancel)"
            stdscr.addstr(0, (width - len(title)) // 2, title)
            for i, option in enumerate(ACTIVITY_OPTIONS):
                marker = "> " if i == idx else "  "
                stdscr.addstr(i + 2, 2, f"{marker}{option}")
            stdscr.refresh()

            key = stdscr.getch()
            if key == curses.KEY_UP and idx > 0:
                idx -= 1
            elif key == curses.KEY_DOWN and idx < len(ACTIVITY_OPTIONS) - 1:
                idx += 1
            elif key in (10, curses.KEY_ENTER):
                victims[current_idx][field] = ACTIVITY_OPTIONS[idx]
                add_modification(victims[current_idx], field)
                save_victims(all_victims)
                break
            elif key == 27:  # ESC
                return
    else:
        curses.echo()
        stdscr.addstr(curses.LINES-1, 2, f"New {field}: ")
        stdscr.clrtoeol()
        new_value = stdscr.getstr().decode('utf-8')
        curses.noecho()
        victims[current_idx][field] = new_value
        add_modification(victims[current_idx], field)
        save_victims(all_victims)

    # Blink "Saved!"
    for _ in range(2):
        stdscr.addstr(curses.LINES-2, 2, "Saved!")
        stdscr.clrtoeol()
        stdscr.refresh()
        time.sleep(0.3)
        stdscr.addstr(curses.LINES-2, 2, "")
        stdscr.clrtoeol()
        stdscr.refresh()
        time.sleep(0.3)




def draw_menu(stdscr, victims, current_idx, scroll_offset, mode, detail_idx=0, query=None, filters=None):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    visible_lines = height - 6

    stdscr.border()
    title = "ransomware.live victim's editor by Julien Mousqueton"
    stdscr.addstr(0, (width - len(title)) // 2, title)

    left_width = width // 2

    for idx, victim in enumerate(victims[scroll_offset:scroll_offset + visible_lines]):
        x = 1
        y = idx + 1
        line = f"{victim['group_name']} - {victim['post_title']}"
        absolute_idx = scroll_offset + idx
        if absolute_idx == current_idx and mode == MODE_LIST:
            stdscr.attron(curses.color_pair(1))
            stdscr.addstr(y, x, line[:left_width-2])
            stdscr.attroff(curses.color_pair(1))
        else:
            stdscr.addstr(y, x, line[:left_width-2])

    if victims:
        selected = victims[current_idx]
        details_x = left_width + 1
        details = [
            f"Group: {selected['group_name']}",
            f"Victim: {selected['post_title']}",
            f"Published: {selected['published']}",
            f"Discovered: {selected['discovered']}",
            f"Country (editable): {selected['country']}",
            f"Activity (editable): {selected['activity']}",
            f"Website (editable): {selected['website']}",
            f"Post URL: {selected['post_url']}",
            f"Description: {selected['description']}",
        ]
        for idx, line in enumerate(details):
            if idx + 1 >= height - 4:
                break
            display_line = f"{line}"
            if mode == MODE_DETAIL and idx == detail_idx:
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(idx + 1, details_x, display_line[:(width - details_x - 2)])
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(idx + 1, details_x, display_line[:(width - details_x - 2)])

    menu_text = "/ to search | I for Infostealer update | Enter to edit | w/c/a filters | r reset filter | ? help"

    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(height-3, (width - len(menu_text)) // 2, menu_text)
    stdscr.attroff(curses.color_pair(2))

    filter_text = "Filters: "
    if filters:
        if filters['empty_website']:
            filter_text += "[Website Empty] "
        if filters['empty_country']:
            filter_text += "[Country Empty] "
        if filters['empty_activity']:
            filter_text += "[Activity Empty] "
    filter_text += f"   ({len(victims)} victims)"
    stdscr.addstr(height-2, 2, filter_text)

    if query is not None:
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(height-1, 2, f"Search: {query}")
        stdscr.attroff(curses.color_pair(2))

    stdscr.refresh()


def launch_manage(stdscr, website):
    if not website:
        return
    curses.endwin()  # Quitte proprement curses
    
    manage_path = './manage.py'
    
    if not os.path.isfile(manage_path):
        print(f"Error: {manage_path} not found!")
        input("Press ENTER to return...")
    else:
        try:
            subprocess.call(['python3', manage_path, '-I', website])
        except Exception as e:
            print(f"Error launching manage.py: {e}")
        input("Press ENTER to return...")
    
    # Réinitialiser curses
    stdscr.clear()
    curses.initscr()
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)




def main(stdscr):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    all_victims = load_victims()
    filters = {'empty_website': False, 'empty_country': False, 'empty_activity': False}
    victims = all_victims
    current_idx = 0
    scroll_offset = 0
    detail_idx = 4
    query = None
    mode = MODE_LIST

    while True:
        victims = all_victims
        if query:
            victims = [v for v in victims if query.lower() in v['post_title'].lower()]
        victims = apply_filters(victims, filters)
        height, _ = stdscr.getmaxyx()
        visible_lines = height - 6

        if current_idx < scroll_offset:
            scroll_offset = current_idx
        elif current_idx >= scroll_offset + visible_lines:
            scroll_offset = current_idx - visible_lines + 1

        draw_menu(stdscr, victims, current_idx, scroll_offset, mode, detail_idx, query, filters)
        key = stdscr.getch()

        if mode == MODE_LIST:
            if key == curses.KEY_UP and current_idx > 0:
                current_idx -= 1
            elif key == curses.KEY_DOWN and current_idx < len(victims) - 1:
                current_idx += 1
            elif key == curses.KEY_NPAGE:  # Page Down
                current_idx = min(current_idx + visible_lines, len(victims) - 1)
            elif key == curses.KEY_PPAGE:  # Page Up
                current_idx = max(current_idx - visible_lines, 0)
            elif key == ord('q'):
                break
            elif key == ord('/'):
                curses.echo()
                stdscr.addstr(curses.LINES-1, 2, "Search: ")
                stdscr.clrtoeol()
                query = stdscr.getstr().decode('utf-8')
                curses.noecho()
                current_idx = 0
            elif key == ord('r'):
                victims = all_victims
                query = None
                filters = {'empty_website': False, 'empty_country': False, 'empty_activity': False}
                current_idx = 0
            elif key == ord('c'):
                filters['empty_country'] = not filters['empty_country']
                current_idx = 0
            elif key == ord('w'):
                filters['empty_website'] = not filters['empty_website']
                current_idx = 0
            elif key == ord('a'):
                filters['empty_activity'] = not filters['empty_activity']
                current_idx = 0
            elif key == ord('?'):
                show_help(stdscr)
            elif key == ord('r'):
                query = None
                filters = {'empty_website': False, 'empty_country': False, 'empty_activity': False}
                current_idx = 0
            elif key == ord('I'):
                website = victims[current_idx].get('website', '')
                launch_manage(stdscr, website)
            elif key == curses.KEY_ENTER or key == 10:
                mode = MODE_DETAIL
                detail_idx = 4
        elif mode == MODE_DETAIL:
            if key == curses.KEY_UP and detail_idx > 4:
                detail_idx -= 1
            elif key == curses.KEY_DOWN and detail_idx < 6:
                detail_idx += 1
            elif key == 27:
                mode = MODE_LIST
            elif key == ord('q'):
                break
            elif key == curses.KEY_ENTER or key == 10:
                field = EDITABLE_FIELDS[detail_idx - 4]
                edit_field(stdscr, all_victims, victims, current_idx, field)

if __name__ == '__main__':
    try:
        create_lock()
        curses.wrapper(main)
    finally:
        remove_lock()
