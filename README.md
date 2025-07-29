# Instagram Follower Scraper

This Python script automates the process of logging into Instagram using your **username and password**, scraping your followers, and then visiting each of their profiles to collect their followers. The data is stored in a Google Sheet via the Google Sheets API.

---

## 📌 Features

- Log in to Instagram using credentials (username/password)
- Scrape your followers
- Visit each follower’s profile and scrape their followers
- Save everything to a Google Sheet

---

## 🛠 Requirements

- Chrome browser
- ChromeDriver (matching your browser version)
- Python 3.7 or higher
- Google Service Account credentials (`.json` file)
- Instagram username and password

---

## 🔐 Login Method: Username & Password

This script uses your Instagram login credentials (entered directly into the script) to authenticate via Selenium.

> ⚠️ Instagram may detect automation and temporarily block actions. Use responsibly.

---

## 📗 Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/ahmedrana603/Instagram-followers-of-followers-id.git
   cd instagram-follower-scraper