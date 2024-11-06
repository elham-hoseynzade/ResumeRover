import requests
from bs4 import BeautifulSoup
from email_extractor import extract_emails_from_link
import logging
from threading import current_thread
import time

logger_error = logging.getLogger('error')

def fetch_emails_from_url(url, extracted_emails, session, url_cache, retries=3):
    """Fetch emails from a given URL using the provided session and cache mechanism."""
    try:
        # Check if URL is in cache
        if url in url_cache:
            logger_error.info(f"URL found in cache: {url}")
            emails = url_cache[url]
            extracted_emails.extend([email for email in emails if email not in extracted_emails])
            return

        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'
        }
        response = session.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            links = soup.find_all("a")
            emails = []

            for link in links:
                href = link.get("href")
                # Ensure href is a valid URL
                if href and (href.startswith("http://") or href.startswith("https://")):
                    email_links = extract_emails_from_link(href, extracted_emails)  # Pass the filename
                    if email_links:
                        for email in email_links:
                            if email not in extracted_emails:
                                extracted_emails.append(email)
                                emails.append(email)

            # Cache the results
            url_cache[url] = emails

    except requests.exceptions.RequestException as req_err:
        logger_error.error(f"Request error: {req_err} - {current_thread().name}")
        if retries > 0:
            time.sleep(2)
            fetch_emails_from_url(url, extracted_emails, session, url_cache, retries - 1)
    except Exception as err:
        logger_error.error(f"General error: {err} - {current_thread().name}")
