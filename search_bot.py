import time
import json
import random
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def normalize_url(url):
    """
    Normalize the URL by removing 'http://', 'https://', 'www.', and path/query/fragment.
    """
    parsed_url = urlparse(url.lower())
    domain = parsed_url.netloc
    return domain.replace("www.", "")


class GoogleSearchBot:
    def __init__(self, api_url, max_rank=50, wait_time=5, stay_time=10,threshold=100):
        """
        Initialize the GoogleSearchBot with API URL, maximum rank to check, wait time, and stay time on sites.
        """
        self.api_url = api_url
        self.max_rank = max_rank
        self.wait_time = wait_time
        self.stay_time = stay_time
        self.threshold = threshold
        self.driver = self._init_driver()

    @staticmethod
    def _init_driver():
        """
        Initialize and return a Selenium WebDriver with appropriate options.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )

    def fetch_keywords(self):
        """
        Fetch keywords and associated websites from the API.
        """
        try:
            response = requests.get(f"{self.api_url}/bot")
            response.raise_for_status()
            response = requests.get(f"{self.api_url}/keywords")
            response.raise_for_status()
            logging.info(f"Request made from IP: {response.request.headers.get('X-Forwarded-For', 'N/A')}")
            data = response.json()
            if not isinstance(data, list):
                raise ValueError("Invalid keywords format")
            logging.info(f"Fetched {len(data)} keywords.")
            return data
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching keywords: {e}")
            return []
        except ValueError as e:
            logging.error(f"Error processing keywords data: {e}")
            return []

    def search_keyword(self, keyword, domain):
        """
        Perform a Google search for the keyword and find the ranks of the given website.
        """
        try:
            self.driver.get("https://www.google.com/")
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            time.sleep(self.wait_time)

            rank = 1
            ranks = []

            while rank <= self.max_rank:
                results = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".tF2Cxc"))
                )

                for result in results:
                    try:
                        link = result.find_element(By.TAG_NAME, "a").get_attribute("href")
                        link_normalized = normalize_url(link)

                        if domain in link_normalized:
                            logging.info(f"Match found for {domain} at rank {rank}.")
                            ranks.append(rank)

                            # Perform a random click and stay on the site
                            result.find_element(By.TAG_NAME, "a").click()
                            logging.info(f"Random click performed on {domain}. Staying on site for {self.stay_time} seconds.")
                            time.sleep(self.stay_time)
                            self.driver.back()
                        rank += 1
                        if rank > self.max_rank:
                            break

                    except Exception as e:
                        logging.warning(f"Error parsing result: {e}")
                        continue

                if  rank > self.max_rank:
                    break

                try:
                    next_button = self.driver.find_element(By.ID, "pnnext")
                    next_button.click()
                    time.sleep(self.wait_time)
                except Exception:
                    logging.info("No more pages to navigate.")
                    break

            if ranks:
                return {
                    "min_rank": min(ranks),
                    "max_rank": max(ranks),
                    "avg_rank": sum(ranks) / len(ranks),
                }
            return {"min_rank": None, "max_rank": None, "avg_rank": None}
        except Exception as e:
            logging.error(f"Error during keyword search: {e}")
            return {"min_rank": None, "max_rank": None, "avg_rank": None}

    def collect_suggestions(self, keyword):
        """
        Collect Google autocomplete suggestions for the given keyword.
        """
        suggestions = []
        try:
            self.driver.get("https://www.google.com/")
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.send_keys(keyword)
            time.sleep(2)
            suggestion_elements = self.driver.find_elements(By.CSS_SELECTOR, ".erkvQe li span")
            suggestions = [s.text for s in suggestion_elements if s.text]
        except Exception as e:
            logging.warning(f"Error collecting suggestions: {e}")
        return suggestions

    def save_results(self, data):
        """
        Save the search results and suggestions to the API.
        """
        try:
            response = requests.post(f"{self.api_url}/bot", json=data)
            response = requests.post(f"{self.api_url}/results", json=data)
            if response.status_code == 200:
                logging.info(f"Results saved successfully for keyword: {data['keyword']}")
            else:
                logging.error(f"Failed to save results: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error saving results: {e}")

    def run(self):
        """
        Main method to run the bot: fetch keywords, perform searches, collect suggestions, and save results.
        """
        try:
            keywords = self.fetch_keywords()
            for item in keywords:
                keyword = item.get("keyword")
                websites = item.get("websites", [])
                if item.get("search_count", 0) >= self.threshold:
                    logging.info(f"Skipping keyword '{keyword}' as it reached its daily search threshold.")
                    continue

                for website in websites:
                    domain = website.get("domain")
                    ranks = self.search_keyword(keyword, domain)
                    suggestions = self.collect_suggestions(keyword)
                    result_data = {
                        "keyword": keyword,
                        "domain": domain,
                        "min_rank": ranks["min_rank"],
                        "max_rank": ranks["max_rank"],
                        "avg_rank": ranks["avg_rank"],
                        "suggestions": suggestions,
                    }
                    self.save_results(result_data)

        except Exception as e:
            logging.error(f"Critical error: {e}")
        finally:
            self.driver.quit()


if __name__ == "__main__":
    bot = GoogleSearchBot(api_url="http://localhost:5000", max_rank=50, wait_time=5, stay_time=1,threshold=100)
    bot.run()
