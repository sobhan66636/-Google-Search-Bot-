# Flask SEO Data Management API

This is a Flask-based API for managing SEO data. The API allows users to perform CRUD operations on websites and keywords, upload keyword data via Excel files, track search results, and view logs. It also includes logging for every request made to the API.

## Features

- **Website Management**: Add, update, delete websites and associate them with keywords.
- **Keyword Management**: Add, update, delete keywords and associate them with websites.
- **Results Management**: Store SEO results (min, max, and average ranks) along with suggestions.
- **Excel Upload**: Upload keywords and associated websites via Excel files.
- **Logging**: Track API requests and errors.
- **Bot Interface**: Placeholder endpoint for SEO bot integration.

## Requirements

- Python 3.x
- Flask
- Flask-SQLAlchemy
- Flask-Cors
- Flask-RESTful
- OpenPyXL (for Excel file parsing)
- SQLite (used for database)

### Installation

1. Clone the repository.
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt

#### The API will be available at <http://127.0.0.1:5000/>

#### API Endpoints

##### /websites

- Methods:

###### GET: Retrieve a list of all websites

- Response: Returns a list of websites with their id, name, and domain.
- Usage: Fetch all registered websites.

###### POST: Add a new website

- Request Body:
- json
{
  "name": "Example Website",
  "domain": "example.com"
}
- Response: Returns a success message and the added website's details.
- Usage: Add a new website to the database.

###### PUT: Update an existing website

- Request Body:
- json
{
  "id": 1,
  "name": "Updated Website",
  "domain": "updated-example.com"
}
- Response: Returns a success message and the updated website's details.
- Usage: Update an existing website's details.

###### DELETE: Delete a website

- Request Body:
- json
{
  "id": 1
}
- Response: Returns a success message if the website was deleted.
- Usage: Delete a website and its associations.

##### /keywords

Methods:

###### GET: Retrieve a list of all keywords

- Response: Returns a list of keywords with their id and associated websites.
- Usage: Fetch all registered keywords.

###### POST: Add a new keyword

- Request Body:
- json
{
  "keyword": "example keyword",
  "website_ids": [1, 2]
}
- Response: Returns a success message and the added keyword's details.
- Usage: Add a new keyword and associate it with existing websites.

###### PUT: Update an existing keyword

- Request Body:
- json
{
  "id": 1,
  "keyword": "updated keyword",
  "website_ids": [1, 3]
}
- Response: Returns a success message and the updated keyword's details.
- Usage: Update an existing keyword and its associated websites.

###### DELETE: Delete a keyword

- Request Body:
- json
{
  "id": 1
}
- Response: Returns a success message if the keyword was deleted.
- Usage: Delete a keyword and its associations.

##### /results

Methods:

###### POST: Submit a search result for a keyword and website

- Request Body:
- json
- Copy code
{
  "keyword": "example keyword",
  "domain": "example.com",
  "min_rank": 1,
  "max_rank": 10,
  "avg_rank": 5.5,
  "suggestions": {"related_keywords": ["suggestion1", "suggestion2"]}
}
- Response: Returns a success message and confirmation that the result was processed.
- Usage: Submit search results for a keyword and website.

###### GET: Retrieve search results with optional filters

Query Parameters:

- keyword: Filter by keyword.
- start_date: Filter by start date.
- end_date: Filter by end date.
- Response: Returns a list of search results, including keyword, website, min_rank, max_rank, avg_rank, suggestions, and timestamp.
- Usage: Fetch search results with optional filters.

##### /upload_excel

Methods:

###### POST: Upload an Excel file to bulk add keywords and websites

- Request Body: Multipart form data (Excel file).
- Response: Returns a success message if the file was processed successfully.
- Usage: Upload an Excel file with keywords and website domains. The file should be in .xlsx format.

##### /logs

Methods:

###### GET: Retrieve logs of actions performed in the system

- Response: Returns a list of logs with id, action, details, timestamp, ip_address, http_method, path, and status_code.
- Usage: Fetch system logs for auditing purposes.

##### /bot

Methods:

###### GET: show that bot getting data

###### POST: show that bot is sending result

#### Models Overview

##### Website

Represents a website with id, name, and domain. Websites are associated with keywords through the keyword_website table.

##### Keyword

Represents a keyword with id and keyword. Keywords are associated with websites and search results.

##### Result

Stores search results for a keyword and website combination, including min_rank, max_rank, avg_rank, and suggestions.

##### Log

Tracks all actions and API requests, including details like the action performed, IP address, HTTP method, and status code.
