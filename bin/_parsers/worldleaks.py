import json,os
from datetime import datetime
from shared_utils import appender, errlog
from pathlib import Path
from dotenv import load_dotenv


env_path = Path("../.env")
load_dotenv(dotenv_path=env_path)
home = os.getenv("RANSOMWARELIVE_HOME")
tmp_dir = Path(home + os.getenv("TMP_DIR"))


def convert_date(unix_timestamp):
    try:
        dt = datetime.fromtimestamp(int(unix_timestamp))
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        return ""

def main():
    ## Get the ransomware group name from the script name 
    script_path = os.path.abspath(__file__)
    # If it's a symbolic link find the link source 
    if os.path.islink(script_path):
        original_path = os.readlink(script_path)
        if not os.path.isabs(original_path):
            original_path = os.path.join(os.path.dirname(script_path), original_path)
        original_path = os.path.abspath(original_path)
        original_name = os.path.basename(original_path)
        group_name = original_name.replace('.py','')
    # else get the script name 
    else:
        script_name = os.path.basename(script_path)
        group_name = script_name.replace('.py','')

    for filename in os.listdir(tmp_dir):
        try:
            if filename.startswith(group_name+'-'):
                html_doc = tmp_dir / filename
                with open(html_doc, "r", encoding="utf-8") as f:
                    lines = f.readlines()


                for line in lines:
                    try:
                        item = json.loads(line.strip())
                        title = item.get('title', '').strip()
                        post_id = item.get('id', '')
                        website = item.get('website', '').strip().replace("https:// http", "http")  # cleaning one entry
                        published = convert_date(item.get('updated_at', 0))
                        country_code = item.get('country', '').upper()
                        post_url = f"https://worldleaksartrjm3c6vasllvgacbi5u3mgzkluehrzhk2jz4taufuid.onion/companies/{post_id}"

                        appender(
                            victim=title,
                            group_name='worldleaks',
                            description='',
                            website=website,
                            published=published,
                            post_url=post_url,
                            country=country_code
                        )
                    except Exception as e: 
                        pass
        except Exception as e:
            errlog(f"[Worldleaks] Error processing line: {e}")


