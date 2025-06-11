# SEO Dashboard - Frontend

This project is the frontend part of an SEO Dashboard application, built with Vue.js (using the Composition API) and styled using Vuetify. It allows users to track and analyze SEO performance, including keyword ranking trends, reviews, and site ranking comparisons. Additionally, it includes a feature for managing websites and keywords, which allows users to view, add, edit, and delete websites and associated keywords.

## Features

### 1. **Trend Chart**

- **Description**: Displays a line chart showing keyword rank changes over time for selected keywords and sites.
- **Functionality**:
  - Users can filter the chart by keyword_site
  - The chart displays how rank changing over time
- **Technology**:
  - Uses **Chart.js** for rendering the line chart.
  - Data is fetched from the backend via **Axios** and displayed dynamically.

### 2. **Number of Reviews Chart**

- **Description**: Displays a bar chart showing the number of reviews collected for each keyword.
- **Functionality**:
  - Allows users to track how many times a keyword has been reviewed.
  - Filters based on keywords and days.
- **Technology**:
  - Uses **Chart.js** for the bar chart visualization.
  - Data is retrieved from the API and dynamically displayed.

### 3. **Logs Viewer (Table)**

- **Description**: Displays logs of bot activity and API requests in a table format.
- **Functionality**:
  - Users can view detailed logs, including timestamps, actions, status codes, and more.
  - Allows sorting and filtering logs for better analysis.
  - Each log entry shows the following details:
    - **Timestamp**: The time when the action occurred.
    - **Action**: Description of the bot activity.
    - **Status Code**: The status code returned by the action.
    - **Details**: Additional information about the activity.
- **Technology**:
  - Built using **Vuetify** components for the table and filtering options.
  - Data is fetched from the backend using **Axios**.
  - Filters allow sorting by action type, timestamp, and status.

### 4. **Bot Status**

- **Description**: Shows whether the SEO bot is active or inactive, with the last recorded activity time(in logs).
- **Functionality**:
  - Displays real-time bot status (active/inactive).
  - If inactive, it shows the last time the bot performed an action.
- **Technology**:
  - Uses **Vuetify** for layout and status display.
  - Real-time status is fetched from the backend using **Axios**.

### 5. **Suggestions Search**

- **Description**: Allows the user to search for keyword suggestions based on collected data.
- **Functionality**:
  - Users can search for suggestions for a given keyword.
  - Displays the suggestions with details on the rank and number of reviews.
- **Technology**:
  - Implemented using **Vuetify** for the input field and list display.
  - Suggestions are fetched from the API using **Axios**.

### 6. **Manage Websites and Keywords**

- **Description**: Allows users to manage websites and their associated keywords through a CRUD interface.
- **Functionality**:
  - **Add Websites**: Users can add new websites to the system.
  - **Edit Websites**: Users can update details of an existing website, such as name and domain.
  - **Delete Websites**: Users can delete websites from the system.
  - **Add Keywords**: Users can add keywords associated with a website.
  - **Edit Keywords**: Users can modify keyword details for a website.
  - **Delete Keywords**: Users can remove keywords associated with a website.
  - **Bulk Upload**: Allows users to upload an Excel file for bulk keyword entry.
- **Technology**:
  - Built using **Vue.js** (Composition API) and **Vuetify** for form components.
  - Data is stored in a backend database, which is accessed via **Axios**.
  - Users interact with the system through forms, which are dynamically generated.
  - The CRUD operations are performed through API calls to the backend.

### 7. **Table Filtering Feature**

The SEO Dashboard includes a data table that displays the keyword and website performance data. The table supports multiple filtering options to help users narrow down the displayed results based on selected criteria.

- **Filtering Options**:
  - **Site Filter**: Users can select one or more sites to filter the data based on the website(s).
  - **Keyword Filter**: Users can select specific keywords to view their respective data.
  - **Day Filter**: Users can filter the data based on the days when the performance data was recorded.

---

## Technology Stack

- **Frontend**:
  - **Vue.js** (Composition API)
  - **Vuetify** (for UI components)
  - **Chart.js** (for visualizations)
  - **Axios** (for API requests)

- **Backend**:
  - **Flask** (for API endpoints and database interaction)

---

## Installation

- Install dependencies:

 npm install

- Run the development server:

 npm run dev

- Open the app in your browser:

<http://localhost:3000>
