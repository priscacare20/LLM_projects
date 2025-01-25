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

def user_prompt_for(website):
    """
    Generate a user prompt for summarizing news from a website.

    Args:
        website (WebsiteCrawler): The WebsiteCrawler object containing the website's content.

    Returns:
        str: The user prompt string.
    """
    return (
        f"You are looking at a website titled {website.title}\n"
        "The contents of this website are as follows; please highlight the top 3 breaking news related to cryptocurrencies.\n"
        "Provide a link to access this breaking news.\n"
        f"{website.text}"
    )

def messages_for(website):
    """
    Generate messages for the OpenAI model based on the website content.

    Args:
        website (WebsiteCrawler): The WebsiteCrawler object.

    Returns:
        list: A list of message dictionaries for the OpenAI API.
    """
    system_prompt = (
        "You are a crypto investor that searches websites to extract and summarize daily latest crypto news that will impact the price of crypto. "
        "Ignore text that is not crypto-related or not current news. Do nothing if you are unable to access the website or there is no content available. Respond in markdown."
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(website)},
    ]

def new_summary(url, chrome_path, openai_api):
    """
    Get a summary of cryptocurrency news from a website.

    Args:
        url (str): The URL of the website.
        chrome_path (str): Path to the Chrome binary.
        openai_api (OpenAI): OpenAI API client.

    Returns:
        str: The summary of the website content.
    """
    web = WebsiteCrawler(url, 30, chrome_path)
    response = openai_api.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_for(web),
    )
    return response.choices[0].message.content

def user_prompt(all_news):
    """
    Generate a user prompt to summarize news from multiple websites.

    Args:
        all_news (dict): A dictionary where keys are website URLs and values are news summaries.

    Returns:
        str: The user prompt string.
    """
    prompt = (
        "You are looking at the content of a Python dictionary where the key is the source website and the values are the top 3 latest news from that website.\n"
        "The contents of this dictionary are as follows; Please combine and summarize all the news avoiding duplicating the information. Highlight the top 12 latest news that have a high impact on cryptocurrency prices.\n"
        "When news appears in multiple sources, identify all the website sources it appeared in.\n"
    )
    for source, news in all_news.items():
        prompt += f"source={source}, news={news}\n"
    return prompt

def messages(all_news):
    """
    Generate messages for summarizing news from multiple websites.

    Args:
        all_news (dict): A dictionary of news summaries from websites.

    Returns:
        list: A list of message dictionaries for the OpenAI API.
    """
    system_prompt = (
        "You are a crypto news analyst named Amy that reports crypto news. Prepare the news in a format that can be emailed to crypto enthusiasts. Add the source to each news."
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt(all_news)},
    ]