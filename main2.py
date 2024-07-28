import feedparser
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# List of RSS feeds from top cybersecurity news sources
feeds = {
    'Krebs on Security': 'https://krebsonsecurity.com/feed/',
    'Threatpost': 'https://threatpost.com/feed/',
    'Dark Reading': 'https://www.darkreading.com/rss.xml',
    'Bleeping Computer': 'https://www.bleepingcomputer.com/feed/',
    'SecurityWeek': 'http://feeds.feedburner.com/securityweek'
}

# Function to parse date with multiple formats
def parse_date(date_str):
    date_formats = [
        '%a, %d %b %Y %H:%M:%S %Z',      # 'Fri, 19 Jul 2024 14:24:27 +0000'
        '%a, %d %b %Y %H:%M:%S %z',      # Another common RSS format
        '%Y-%m-%dT%H:%M:%SZ',            # ISO 8601 format
        '%Y-%m-%dT%H:%M:%S.%fZ'          # ISO 8601 format with microseconds
    ]
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Date format for '{date_str}' not recognized.")

# Function to fetch the full article content using Selenium
def fetch_full_article_with_selenium(url):
    try:
        # Initialize Selenium WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run in headless mode
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        
        # Load the page
        driver.get(url)

        # Example extraction logic for different sites
        if 'krebsonsecurity' in url:
            content = driver.find_element(By.TAG_NAME, 'article').text
        elif 'threatpost' in url:
            content = driver.find_element(By.TAG_NAME, 'article').text
        elif 'darkreading' in url:
            content_div = driver.find_element(By.CLASS_NAME, 'ArticleBase-BodyContent_Article')
            paragraphs = content_div.find_elements(By.TAG_NAME, 'p')
            content = "\n".join([p.text for p in paragraphs])
        elif 'bleepingcomputer' in url:
            # Specific logic for Bleeping Computer
            article_div = driver.find_element(By.CLASS_NAME, 'articleBody')
            paragraphs = article_div.find_elements(By.TAG_NAME, 'p')
            content = "\n".join([p.text for p in paragraphs])
        elif 'securityweek' in url:
            content = driver.find_element(By.CLASS_NAME, 'article-content').text
        else:
            # Generic fallback extraction logic
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            content = "\n".join([p.text for p in paragraphs])

        driver.quit()
        return content.strip() if content else "Full article content could not be retrieved."
    except Exception as e:
        print(f"Error fetching full article from {url} with Selenium: {e}")
        return "Full article content could not be retrieved."

# Function to fetch news from RSS feeds
def fetch_news(feeds):
    news = []
    for source, url in feeds.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if 'bleepingcomputer' in entry.link:
                full_content = fetch_full_article_with_selenium(entry.link)
            else:
                full_content = fetch_full_article(entry.link)
            news.append({
                'title': entry.title,
                'link': entry.link,
                'summary': entry.get('summary', 'No summary available'),
                'published': entry.published,
                'source': source,
                'content': full_content
            })
    return news

# Function to fetch the full article content using requests and BeautifulSoup
def fetch_full_article(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example extraction logic for different sites
        if 'krebsonsecurity' in url:
            content = soup.find('article').get_text(separator="\n")
        elif 'threatpost' in url:
            content = soup.find('article').get_text(separator="\n")
        elif 'darkreading' in url:
            content_div = soup.find('div', class_='ArticleBase-BodyContent_Article')
            if content_div:
                paragraphs = content_div.find_all('p')
                content = "\n".join([p.get_text() for p in paragraphs])
            else:
                content = "Full article content could not be retrieved."
        elif 'bleepingcomputer' in url:
            # Bypassed by Selenium, fallback logic
            article_div = soup.find('div', class_='articleBody')
            if article_div:
                paragraphs = article_div.find_all('p')
                content = "\n".join([p.get_text() for p in paragraphs])
            else:
                content = "Full article content could not be retrieved."
        elif 'securityweek' in url:
            content = soup.find('div', class_='article-content').get_text(separator="\n")
        else:
            # Generic fallback extraction logic
            paragraphs = soup.find_all('p')
            content = "\n".join([p.get_text() for p in paragraphs])

        return content.strip() if content else "Full article content could not be retrieved."
    except Exception as e:
        print(f"Error fetching full article from {url}: {e}")
        return "Full article content could not be retrieved."

# Function to aggregate news by date
def aggregate_news(news):
    aggregated_news = {}
    for article in news:
        try:
            date = parse_date(article['published'])
            date_str = date.isoformat()  # Convert date to ISO format string
        except ValueError as e:
            print(f"Skipping article due to date parsing error: {e}")
            continue
        if date_str not in aggregated_news:
            aggregated_news[date_str] = []
        aggregated_news[date_str].append(article)
    return aggregated_news

# Fetch and aggregate news
news = fetch_news(feeds)
aggregated_news = aggregate_news(news)

# Store aggregated news in a JSON file
with open('cybersecurity_news.json', 'w') as json_file:
    json.dump(aggregated_news, json_file, indent=4)

print("News aggregated and saved to 'cybersecurity_news.json'")

# Optionally, you can load and use the news from the JSON file as needed
with open('cybersecurity_news.json', 'r') as json_file:
    loaded_news = json.load(json_file)
    # Example: Print the loaded news
    for date, articles in loaded_news.items():
        print(f"News for {date}:\n")
        for article in articles:
            print(f"Title: {article['title']}")
            print(f"Source: {article['source']}")
            print(f"Link: {article['link']}")
            print(f"Summary: {article['summary']}")
            print(f"Content: {article['content']}\n")
        print("-" * 80)


Free 14-Day Trial
￼￼
