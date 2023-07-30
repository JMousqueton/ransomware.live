import json
import xml.etree.ElementTree as ET
import os
import datetime
from sharedutils import stdlog
from sharedutils import openjson

def capitalize_first_letter(s):
    return s[:1].upper() + s[1:]

def generate_sitemapXML(base_url, pages, note_directories, output_file="./docs/sitemap.xml"):
    # Create the root element
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    # Add the static URLs
    static_urls = [
        "recentvictims",
        "recentcyberattacks",
        "ransomnotes",
        "negotiations",
        "stats",
        "stats?id=victims-by-month",
        "stats?id=victims-by-month-cumulative",
        "stats?id=_2023",
        "stats?id=_2022",
        "about",
        "CHANGELOG"
    ]

    for page in static_urls:
        # Create a URL entry for each static page
        url = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = f"{base_url}/#{page}"
        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = datetime.date.today().isoformat()

    for page in pages:
        # Create a URL entry for each page
        url = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = f"{base_url}/#/group/{page['name']}"
        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = datetime.date.today().isoformat()
    
    # Add URLs based on note directories
    note_directories = sorted(note_directories)
    for directory in note_directories:
        directory = directory[:-3]
        url = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url, "loc")
        loc.text = f"{base_url}/#/notes/{directory}"
        lastmod = ET.SubElement(url, "lastmod")
        lastmod.text = datetime.date.today().isoformat()


    # Create an ElementTree object and write it to a file
    tree = ET.ElementTree(urlset)
    tree.write(output_file, encoding="UTF-8", xml_declaration=True)


def generate_sitemapHTML(base_url, pages, note_directories, output_file="./docs/sitemap.xml"):
    with open(output_file, "w") as file:
        file.write("<!DOCTYPE html>\n")
        file.write("<html>\n")
        file.write("<head>\n")
        file.write("<title>Ransomware.live Sitemap</title>\n")
        file.write("</head>\n")
        file.write("<body>\n")
        file.write("<h1>Sitemap</h1>\n")

        # Generate links to static pages
        static_urls = [
            ("Recent Victims", "recentvictims"),
            ("Recent Cyberattacks", "recentcyberattacks"),
            ("Ransom Notes", "ransomnotes"),
            ("Negotiations", "negotiations"),
            ("Stats", "stats"),
            ("Stats Victims by month", "stats?id=victims-by-month"),
            ("Stats Victims by month cumulative", "stats?id=victims-by-month-cumulative"),
            ("Stats for 2023", "stats?id=_2023"),
            ("Stats for 2022", "stats?id=_2022"),
            ("About Ransomware.live", "about"),
            ("Changelog", "CHANGELOG")
        ]

        file.write("<ul>\n")
        for title, url in static_urls:
            file.write(f'<li><a href="{base_url}/#{url}">{title}</a></li>\n')
        file.write("</ul>\n")

        # Generate links to pages from groups.json
        file.write("<ul>\n")
        for page in pages:
            file.write(f'<li><a href="{base_url}/#/group/{page["name"]}">Profile for {capitalize_first_letter(page["name"])}</a></li>\n')
        file.write("</ul>\n")

        # Generate links to note directories
        file.write("<ul>\n")
        note_directories = sorted(note_directories)
        for directory in note_directories:
            directory = directory[:-3]
            file.write(f'<li><a href="{base_url}/#/notes/{directory}">Ransom Note for {capitalize_first_letter(directory)}</a></li>\n')
        file.write("</ul>\n")

        file.write("</body>\n")
        file.write("</html>\n")

if __name__ == "__main__":
    print(
    '''
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
    stdlog('Generating Sitemap')
    # Replace this value with your website's base URL
    base_url = "https://www.ransomware.live"

    # Load the pages from the groups.json file
    pages = openjson('groups.json')

    note_directories = [directory for directory in os.listdir("./docs/notes/") if directory.lower() != ".git.md"]

    generate_sitemapXML(base_url, pages, note_directories, output_file="./docs/sitemap.xml")
    stdlog('sitemap.xml generated')
    generate_sitemapHTML(base_url, pages, note_directories, output_file="./docs/sitemap.html")
    stdlog('sitemap.html generated')
