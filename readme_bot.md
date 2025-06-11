# Google Search Bot

This Python script automates the process of fetching keywords from an API, searching Google for those keywords, gathering website ranks, collecting autocomplete suggestions, and saving the results back to the API. The bot uses Selenium WebDriver to interact with Google search pages, extract ranking information, and perform user-like interactions like random clicks.

## Features

- Fetch keywords and associated websites from an API.
- Perform Google searches for each keyword.
- Collect the rank of specified websites in the search results.
- Gather Google autocomplete suggestions for each keyword.
- Save the results back to an API.
- Perform random clicks on search results to simulate user behavior.
- Log all actions for auditing and debugging purposes.

## Setup

### Prerequisites

- Python 3.x
- Install the necessary Python packages using `pip`:

    ```bash
    pip install -r requirements.txt
    ```

- **Selenium** and **ChromeDriver**:
  - This bot requires Chrome WebDriver for browser automation. It automatically installs the required ChromeDriver version using `webdriver_manager`.

### Configuration

1. **API URL**: The bot fetches and saves data to an API, configured via the `api_url` argument.  

- get from /keywords and post to /results

2. **Max Rank**: The maximum search result rank to check (default: 50).
3. **Wait Time**: Time (in seconds) to wait between actions such as navigating to a page or waiting for results (default: 5).
4. **Stay Time**: Time (in seconds) to stay on the website after performing a random click (default: 10).
5. **Threshold**: The number of times a keyword can be searched in a day before it is skipped (default: 100).

### Example of Initialization

bot = GoogleSearchBot(
    api_url="<http://localhost:5000>",
    max_rank=50,
    wait_time=5,
    stay_time=10,
    threshold=100
)

### How It Works

#### Fetch Keywords

- The bot fetches a list of keywords and associated websites from the API. It filters keywords based on their search count (does not search keywords that have exceeded the daily threshold).

#### Google Search

- For each keyword, the bot performs a Google search and extracts the rank of the associated website(s).

#### Collect Suggestions

- The bot collects Google autocomplete suggestions for each keyword.

#### Save Results

- After gathering the search ranks and suggestions, the bot sends the results back to the API.

### API Endpoints

- The bot interacts with the following endpoints of your API:

1. GET /keywords: To fetch the list of keywords and associated websites.
2. POST /results: To save the rank results and suggestions for each keyword.
3. GET & POST /bot: for indentifying that bot is working

- API Configuration

1. The API URL is passed as a parameter when initializing the bot (api_url).
2. The bot will send a POST request with the following JSON data:
{
  "keyword": "example keyword",
  "domain": "example.com",
  "min_rank": 1,
  "max_rank": 10,
  "avg_rank": 5.5,
  "suggestions": ["suggestion1", "suggestion2"]
}
To run the bot, simply execute the script:
    python google_search_bot.py

### Logs

The bot logs all actions, including errors, warnings, and successes. Logs are output to the console and include:

IP of the request when fetching keywords.
Match information when a website rank is found.
Any errors during the search process or while interacting with the API.
3. Manual Control
You can control the bot's behavior by adjusting parameters in the GoogleSearchBot class constructor:

- max_rank: Limit the number of search results to check (default: 50).
- wait_time: Set the wait time between actions (default: 5 seconds).
- stay_time: Set how long the bot stays on a website after clicking on it (default: 10 seconds).
- threshold: Set the maximum number of times a keyword can be searched in a day before skipping (default: 100).

4. Monitoring the Bot

You can monitor the bot's progress in the logs. Each important step, including the fetching of keywords, searching, clicking, and saving results, will be logged
