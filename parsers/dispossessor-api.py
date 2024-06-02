import requests
from datetime import datetime
from sharedutils import stdlog, dbglog, errlog   # , honk
from parse import appender

def fetch_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"HTTP request failed: {e}")
        return None

def extract_and_convert_data(json_data):
    items = json_data["data"]["items"]
    for item in items: 
        try:
            company_name = item["company_name"]
            id =  item["id"]
            uploaded_date =  convert_date_format(item["uploaded_date"])
            description =  item["brief_description"]
            url="https://dispossessor.com/blogs/"+str(id)
            """
            +------------------------------+------------------+----------
            | Description | Published Date | Victim's Website | Post URL |
            +------------------------------+------------------+----------+
            |      X      |      X         |                 |     x    |
            +------------------------------+------------------+----------+
            Rappel : def appender(post_title, group_name, description="", website="", published="", post_url=""):
            """
            appender(company_name,'dispossessor',description,'',uploaded_date,url)
        except:
            pass

def convert_date_format(date_string):
    dt = datetime.strptime(date_string, "%d %b, %Y %H:%M:%S UTC")
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")

def main():
    base_url = "https://dispossessor.com/back/getallblogs?search=&page={}"
    page = 1
    all_data = []

    # Fetch the first page to get the total number of pages
    json_response = fetch_json(base_url.format(page))
    if json_response and json_response["success"]:
        total_pages = json_response["data"]["totalPages"]
        stdlog("    Parsing [1/"+ str(total_pages)+"]")
        extract_and_convert_data(json_response)

        # Fetch the rest of the pages
        for page in range(2, total_pages + 1):
            stdlog("    Parsing [" +  str(page) + "/"+ str(total_pages)+"]")
            json_response = fetch_json(base_url.format(page))
            if json_response and json_response["success"]:
                extract_and_convert_data(json_response)
            else:
                stdlog("Failed to fetch page " + page)


if __name__ == "__main__":
    main()
