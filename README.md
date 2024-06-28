# IDEAS Startup Insights

IDEAS Startup Insights is a web application that allows users to manage and analyze information about startups and companies. It provides features for storing company names, data sources, and extracting insights from various web sources.

## Features

- Store and manage company names
- Manage data sources for company information
- Extract and display company insights from sources like Zauba Corp and Tofler
- Generate PDF reports of company insights
- User-friendly interface built with Streamlit

## Project Structure

- `home.py`: Main application file with the Streamlit interface
- `startup_gui.py`: GUI for managing company names
- `data_sources_gui.py`: GUI for managing data sources
- `insights_gui.py`: GUI for displaying and managing company insights
- `db.py`: Database operations using DuckDB
- `scrape.py`: Web scraping functionality for extracting company information

## Requirements

- Python 3.7+
- Dependencies listed in `requirements.txt`

## Installation

### Using pip

1. Clone the repository:
```
git clone https://github.com/your-username/ideas-startup-insights.git
cd ideas-startup-insights
```
2. Create a virtual environment (optional but recommended):
```
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
```
3. Install the required packages:
```
pip install -r requirements.txt
```

### Using Conda

1. Clone the repository:
```
git clone https://github.com/your-username/ideas-startup-insights.git
cd ideas-startup-insights
```
2. Create a Conda environment:
```
conda create --name ideas-startup-insights
conda activate ideas-startup-insights
```
3. Install the required packages:
```
conda env update --name ideas-startup-insights --file environment.yml
```
## Usage

1. Ensure you're in the project directory and your virtual environment is activated.

2. Run the Streamlit app:
```
streamlit run .\home.py
```
3. Open your web browser (if not automatically opened) and navigate to the URL displayed in the terminal (usually `http://localhost:8501`).

4. Use the application to manage company information, data sources, and extract insights.

## To-Do

1. Modify the `scrape.py` file to run selenium in headless mode.
2. Add functionalities for extraction profile.

## Contributing

Contributions to IDEAS Startup Insights are welcome! Please feel free to submit a Pull Request.

## License

[Specify your license here]

## Acknowledgements

- IDEAS-TIH for project support
- Streamlit for the web application framework
- Selenium for web scraping capabilities