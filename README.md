![Ransomware.live Logo](.github/ransomware.live.png)

# Ransomware.live

Ransomware.live is originally a fork of **ransomwatch**.  
It is a ransomware leak site monitoring tool that scrapes entries from various ransomware leak sites and publishes them.

🔗 GitHub repository: [https://github.com/JMousqueton/ransomware.live](https://github.com/JMousqueton/ransomware.live)

Ransomware.live handles **data collection, parsing, enrichment, and automation** to maintain the database.

---

## 📌 Features

- **Automated scraping** of ransomware leak sites (including `.onion` domains via Tor)
- **Integration** with Hudson Rock for infostealer data via a Telegram bot
- **Data management** tools for victims and groups
- **Image capture** of leak site posts with watermarking, metadata, and optional face blurring
- **Notifications** via ntfy and Bluesky servers
- **Environment-based configuration** via `.env`

---

## 📂 Repository Structure

```
ransomwarelive/
│
├── bin/                  # Core Python scripts and libraries
|   ├── _parser/          # All parsers 
│   ├── libcapture.py     # Capture victim/group screenshots
│   ├── hudsonrockapi.py  # Hudson Rock API integration via Telegram bot
│   ├── parse.py          # Parse collected data into structured formats
│   ├── scrape.py         # Main scraping engine
│   ├── manage.py         # Management CLI
│   ├── shared_utils.py   # Shared helper functions
│   ├── victims-browser.py# Victim data viewer
│   ├── status.py         # System health and process status
│   ├── rsslib.py         # (Optional) RSS feed generation
│   └── requirements.txt  # Python dependencies
│
├── images/               # Static assets & watermarks
├── db/                   # Local databases (JSON)
├── tmp/                  # Temporary working files
└── .env.sample           # Example environment configuration


---

## ⚙️ Installation

### 1. Clone the Repository
```bash
git clone https://github.com/JMousqueton/ransomware.live.git
cd ransomwarelive
```

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r bin/requirements.txt
```

### 4. Configure Environment
Copy the example `.env` file and edit it with your configuration:
```bash
cp .env.sample .env
nano .env
```

---

## 🚀 Usage

### Start Scraping
```bash
cd bin
python scrape.py
```

### Parse Collected Data
```bash
cd bin
python parse.py
```

### Manage Data
```bash
cd bin
python manage.py --help 
```

---

## 🛡️ Requirements

- Python **3.9+**
- [Tor service](https://www.torproject.org/) running locally for `.onion` access
- Telegram bot credentials (used to query Hudson Rock for infostealer data)
- ntfy server credentials (for notifications)
- Bluesky server credentials (for notifications)
- Unix-based environment (Linux/macOS) recommended

---

## 📜 License

This project is licensed under the **unlicense** License**.  
See the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

This project is for **research and educational purposes only**.  
Do **not** use it for unauthorized access to systems or data.  
The maintainers take no responsibility for misuse of the code.

This project is only the parsing and scraping, not the website. 

---

## 🤝 Contributing

Contributions are welcome!  
Please open an issue or submit a pull request to suggest improvements or add new features.

---

**Maintainer:** [Julien Mousqueton](https://www.linkedin.com/in/julienmousqueton)  
**Website:** [https://ransomware.live](https://ransomware.live)
