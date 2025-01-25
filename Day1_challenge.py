"""
author: Prisca Ekhaeyemhe

# # Purpose:
# This code uses gpt_4o_mini to summarize the latest crypto news from 9 best crypto websites and
# emails the result to my mailbox.
"""

# import libraries
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
from email.message import EmailMessage
import ssl
import smtplib
from IPython.display import Markdown, display


class WebsiteCrawler:
    """
    A class to scrape JavaScript-rendered content from a website using Selenium.

    Attributes:
        url (str): The URL of the website to scrape.
        wait_time (int): Maximum time to wait for content to load (default: 20 seconds).
        chrome_binary_path (str): Path to the Chrome binary, if not in default location.
        title (str): Title of the website.
        text (str): Text content extracted from the website.
    """

    def __init__(self, url, wait_time=20, chrome_binary_path=None):
        self.url = url
        self.wait_time = wait_time
        self.title = ""
        self.text = ""

        options = uc.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("start-maximized")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        )
        if chrome_binary_path:
            options.binary_location = chrome_binary_path

        self.driver = uc.Chrome(options=options)

        try:
            self.driver.get(url)
            time.sleep(10)  # Wait for potential checks (e.g., Cloudflare)
            WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )

            main_content = self.driver.find_element(By.CSS_SELECTOR, "main").get_attribute("outerHTML")
            soup = BeautifulSoup(main_content, "html.parser")
            self.title = self.driver.title or "No title found"
            self.text = soup.get_text(separator="\n", strip=True)

        except Exception as e:
            print(f"Error occurred while scraping: {e}")
            self.title = "Error occurred"
            self.text = ""

        finally:
            self.driver.quit()