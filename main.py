from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from urllib.parse import urlparse

def setup_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        r"C:\Users\ahmed\Downloads\REPLACE YOUR JSIN FILE NAME", scope)
    client = gspread.authorize(creds)
    sheet = client.open("followers").sheet1
    sheet.clear()
    sheet.update(range_name="A1:C1", values=[["Follower ID", "No of followers", "Followers of followers"]])
    return sheet

def get_followers_count(driver, wait):
    try:
        count_elem = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//a[contains(@href, "/followers")]/span')
        ))
        return count_elem.text
    except:
        return "0"

def extract_usernames_from_modal(driver, limit=None):
    elements = driver.find_elements(
        By.XPATH, '//div[@role="dialog"]//a[contains(@href, "/") and not(contains(@href, "stories"))]'
    )
    usernames = []
    for el in elements:
        href = el.get_attribute("href")
        if href and "instagram.com/" in href:
            username = href.split("instagram.com/")[-1].split('/')[0]
            if username and username not in usernames:
                usernames.append(username)
                if limit and len(usernames) >= limit:
                    break
    return usernames

def append_to_sheet(sheet, follower_id, followers_count, followers_str):
    sheet.append_row([follower_id, followers_count, followers_str])

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 30)

driver.get("https://www.instagram.com/")
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="username"]'))).send_keys("ENTER YOUR USERNAME")
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="password"]'))).send_keys("ENTER YOUR PASSWORD")
login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[@type="submit"]')))
login_btn.click()
time.sleep(25)

profile_btn = wait.until(EC.element_to_be_clickable(
    (By.XPATH, '//span[text()="Profile"]/ancestor::a[@role="link"]')
))
driver.execute_script("arguments[0].click();", profile_btn)
time.sleep(5)

followers_link = wait.until(EC.element_to_be_clickable(
    (By.XPATH, '//a[contains(@href, "/followers")]')
))
followers_link.click()
time.sleep(5)

my_followers_count_str = get_followers_count(driver, wait)
try:
    my_followers_count = int(''.join(filter(str.isdigit, my_followers_count_str)))
except:
    my_followers_count = 0

print(f"\nYou have {my_followers_count} followers")

all_follower_urls = []
followers_modal = wait.until(EC.presence_of_element_located((
    By.XPATH, '//div[@role="dialog"]//div[contains(@class, "x6nl9eh")]'
)))

scroll_retries = 0
max_scroll_retries = 5

while len(all_follower_urls) < my_followers_count and scroll_retries < max_scroll_retries:
    initial_count = len(all_follower_urls)
    follower_links = driver.find_elements(
        By.XPATH, '//div[@role="dialog"]//a[contains(@href, "/") and not(contains(@href, "explore"))]'
    )
    for el in follower_links:
        href = el.get_attribute("href")
        if href and href not in all_follower_urls:
            all_follower_urls.append(href)
            if len(all_follower_urls) >= my_followers_count:
                break
    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_modal)
    time.sleep(2)
    if len(all_follower_urls) == initial_count:
        scroll_retries += 1
    else:
        scroll_retries = 0

try:
    close_btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, '//button//*[name()="svg"][@aria-label="Close" or .//title[text()="Close"]]/ancestor::button'
    )))
    close_btn.click()
    time.sleep(2)
except:
    pass

sheet = setup_google_sheet()

for i, url in enumerate(all_follower_urls):
    try:
        print(f"\nVisiting follower {i+1}/{len(all_follower_urls)}: {url}")
        driver.get(url)
        time.sleep(5)

        path_parts = urlparse(driver.current_url).path.strip('/').split('/')
        follower_id = path_parts[0]

        followers_count_str = get_followers_count(driver, wait)
        try:
            followers_count = int(''.join(filter(str.isdigit, followers_count_str)))
        except:
            followers_count = 0

        print(f"{follower_id} has {followers_count} followers")

        follower_followers_link = wait.until(EC.element_to_be_clickable((
            By.XPATH, '//a[contains(@href, "/followers")]'
        )))
        follower_followers_link.click()
        time.sleep(3)

        modal = wait.until(EC.presence_of_element_located((
            By.XPATH, '//div[@role="dialog"]//div[contains(@class, "x6nl9eh")]'
        )))

        temp_usernames = []
        previous_count = -1
        max_scrolls = 50
        scroll_attempts = 0

        while len(temp_usernames) < followers_count and scroll_attempts < max_scrolls:
            temp_usernames = extract_usernames_from_modal(driver, limit=followers_count)
            print(f"Scroll {scroll_attempts + 1}: Collected {len(temp_usernames)} / {followers_count}")

            if len(temp_usernames) == previous_count:
                print("No more new followers loading. Breaking scroll.")
                break
            previous_count = len(temp_usernames)

            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal)
            time.sleep(4)
            scroll_attempts += 1

        print(f"Collected {len(temp_usernames)} followers of {follower_id}")
        followers_str = ", ".join(temp_usernames)

        append_to_sheet(sheet, follower_id, followers_count, followers_str)

        try:
            close_btn = wait.until(EC.element_to_be_clickable((
                By.XPATH, '//button//*[name()="svg"][@aria-label="Close" or .//title[text()="Close"]]/ancestor::button'
            )))
            close_btn.click()
            time.sleep(2)
        except:
            pass

    except Exception as e:
        print(f"Error processing follower {url}: {e}")
        continue

print("\nDone scraping all followers and saving to Google Sheet.")
driver.quit()
