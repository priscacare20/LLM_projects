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