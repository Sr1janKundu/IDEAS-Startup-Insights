import re
import time
import json
from selenium import webdriver
from selenium.webdriver import ChromeOptions, ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def close_tabs(driver):
    original_window = driver.current_window_handle
    windows = driver.window_handles

    if len(windows) > 1:
        for window in reversed(windows[1:]):  # Skip the original window
            driver.switch_to.window(window)
            driver.close()
        driver.switch_to.window(original_window)

def scrape(name, source, source_url):
    # Define the path to the ChromeDriver executable
    #MYCHROME = "E:/TIH-ISI/Scraping_Selenium/test/chromedriver.exe"
    ADBLOCKER_EXTENSION_PATH = "E:/TIH-ISI/Scraping_Selenium/test/AdBlock_6.2.0.0.crx"
    # Set up Chrome options
    chrome_options = ChromeOptions()
    chrome_options.add_extension(ADBLOCKER_EXTENSION_PATH)
    # Add arguments for headless mode
    #chrome_options.add_argument("--headless=new")
    #chrome_options.add_argument("--disable-gpu")
    # Create a Service object with the path to the ChromeDriver
    #service = ChromeService(MYCHROME)
    service = ChromeService()


    if source == 'Zauba Corp':

        # Initialize the WebDriver with the service and options
        driver = webdriver.Chrome(service=service, options=chrome_options)
        #driver.maximize_window()

        time.sleep(5)

        # Check if there are multiple tabs and close from the last opened tabs
        close_tabs(driver)
        # Navigate to the URL
        driver.get(source_url)
        # driver.get("https://www.zaubacorp.com/")

        #html_source = driver.page_source

        # Print the HTML source
        #print(html_source)

        #driver.implicitly_wait(10)  # Wait for up to 10 seconds for the elements to be present
    
        input_element = driver.find_element(By.ID, "searchid")
        input_element.clear()
        input_element.send_keys(name + Keys.ENTER)

        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table#results"))
        )
        # Find the rows in the table
        rows = table.find_elements(By.CSS_SELECTOR, "tbody > tr")

        # Iterate through the rows to find the perfect match
        for row in rows:
            cells = row.find_elements(By.CSS_SELECTOR, "td")
            if len(cells) >= 2:
                company_name = cells[1].text.strip()
                if company_name == name:
                    # Click on the link in the company name cell
                    link = cells[1].find_element(By.CSS_SELECTOR, "a")
                    link.click()
                    break
        
        # Define the wait instance with a timeout of 10 seconds
        wait = WebDriverWait(driver, 10)

        container_info_div = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.container.information")))

        # Get the text content of the "container information" div
        #container_info_text = container_info_div.text
        container_info_text = container_info_div.find_element(By.XPATH, ".").text

        company_info = container_info_text.split("\n")

        json_data = {
            "Basic Information": "",
            "Company Details": {}
        }

        try:
            index = company_info.index('Company Details')
            # Extract the text before 'Company Details'
            txt = [''.join(company_info[i]) for i in range(index)]
            txt = [s + '.' if s and not s.endswith('.') else s for s in txt]
            txt = ['\n\n' if i == '' else i for i in txt]
            text_before_company_details = ''.join(txt)
        except ValueError:
            # Handle the case where 'Company Details' is not found
            text_before_company_details = company_info[:1]
        json_data["Basic Information"] = text_before_company_details

        # Define key-value mappings for company details
        detail_keys = [
            'CIN', 'Company Name', 'Company Status', 'RoC', 'Registration Number',
            'Company Category', 'Company Sub Category', 'Class of Company',
            'Date of Incorporation', 'Age of Company', 'Activity', 'Authorised Capital',
            'Paid up capital', 'Date of Latest Balance Sheet'
        ]

        # Extract and populate company details
        company_details = {}
        for i, key in enumerate(detail_keys):
            for j in range(len(company_info)):
                if company_info[j] == key:
                    company_details[key] = company_info[j + 1]

        json_data["Company Details"] = company_details

        cin_link_element = driver.find_element(By.XPATH, '//*[@id="block-system-main"]/div[2]/div[1]/div[1]/div[1]/table/thead/tr/td[2]/p/a')

        cin = cin_link_element.text
        # Get the text of the link
        json_data['Company Details']['CIN'] = cin

        json_data['Company Details']['Authorised Capital'] = json_data['Company Details']['Authorised Capital'].replace('\u20b9', 'INR ').replace('\u0024', 'USD ')
        json_data['Company Details']['Paid up capital'] = json_data['Company Details']['Paid up capital'].replace('\u20b9', 'INR ').replace('\u0024', 'USD ')

        # Convert to JSON string with indentation for readability
        json_output = json.dumps(json_data, indent=4)
        
        driver.quit()
    elif source == 'Tofler':
        driver = webdriver.Chrome(service=service, options=chrome_options)
        time.sleep(5)
        close_tabs(driver)
        driver.get(source_url)
        input_element = driver.find_element(By.XPATH, '//*[@id="searchbox"]')
        input_element.clear()
        input_element.send_keys(name + Keys.ENTER)
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="DataTables_Table_0"]'))
        )
        rows = table.find_elements(By.CSS_SELECTOR, "table.search-result-table tbody tr")

        for row in rows:
            company_link = row.find_element(By.CSS_SELECTOR, 'td a.complink')
            company_name = company_link.text
            if company_name == name:
                company_link.click()
                break
        
        json_data = {
            "Basic Information": "",
            "Registration Details": {},
            "Financials": {}
        }
        
        wait = WebDriverWait(driver, 5)
        # overview = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.XPATH, '//*[@id="overview"]/div')).text.split("\n")
        # )
        overview = driver.find_element(By.XPATH, '//*[@id="overview"]/div').text.split("\n")[1:]
        overview_text = ['\n' if i == '' else i for i in overview]
        overview_text_full = ' '.join(overview_text)

        json_data['Basic Information'] = overview_text_full

        registration_details_text = driver.find_element(By.XPATH, '//*[@id="vitals"]/div').text.split("\n")
        reg_detail_keys = [
            'CIN', 'INCORPORATION DATE / AGE', 'LAST REPORTED AGM DATE', 'AUTHORIZED CAPITAL',
            'PAIDUP CAPITAL', 'INDUSTRY*', 'TYPE', 'CATEGORY', 'SUBCATEGORY'
        ]
        reg_details = {}
        for i, key in enumerate(reg_detail_keys):
            for j in range(len(registration_details_text)):
                if registration_details_text[j] == key:
                    reg_details[key] = registration_details_text[j+1]

        json_data["Registration Details"] = reg_details

        financials_tab = driver.find_element(By.XPATH, '//*[@id="financials-tab"]')
        financials_tab.click()

        wait = WebDriverWait(driver, 5)
        def find_index_with_prefix(lst, prefix):
            for i, element in enumerate(lst):
                if re.match(f"^{re.escape(prefix)}", element):
                    return i
            return -1

        # Function to check if any content is blurred
        def is_content_blurred(driver):
            blurred_elements = driver.find_elements(By.CLASS_NAME, 'blur-content')
            return len(blurred_elements) > 0

        # Scrape data
        financial_details = driver.find_element(By.XPATH, '//*[@id="financial-details-financial-tab"]/div').text
        financial_details_text = financial_details.split("\n")

        # Check if content is blurred
        if is_content_blurred(driver):
            json_data["Financials"] = "Not available for free"
        else:
            ind = find_index_with_prefix(financial_details_text, 'Current Ratio')
            financial_details_text_cleaned = [strng for strng in financial_details_text[:ind+1] if strng != 'For a detailed balance sheet']
            brief_financial_report = financial_details_text_cleaned[2:7]

            # Extracting specific financial metrics
            metrics = {
                'Operating Revenue': financial_details_text_cleaned[7].split()[-3:],
                'EBITDA': financial_details_text_cleaned[8].split()[-2],
                'Networth': financial_details_text_cleaned[9].split()[-2],
                'Debt/Equity Ratio': financial_details_text_cleaned[10].split()[-1],
                'Return on Equity': financial_details_text_cleaned[11].split()[-2],
                'Total Assets': financial_details_text_cleaned[12].split()[-2],
                'Fixed Assets': financial_details_text_cleaned[13].split()[-2],
                'Current Assets': financial_details_text_cleaned[14].split()[-2],
                'Current Liabilities': financial_details_text_cleaned[15].split()[-2],
                'Trade Receivables': financial_details_text_cleaned[16].split()[-2],
                'Trade Payables': financial_details_text_cleaned[17].split()[-2],
                'Current Ratio': financial_details_text_cleaned[18].split()[-1]
            }

            # Formatting the metrics values
            for key, value in metrics.items():
                # Join the split parts for 'Operating Revenue'
                if isinstance(value, list):
                    value = ' '.join(value)
                # Add plus sign for positive values if not present
                if value[0] not in ['+', '-']:
                    value = '+' + value
                metrics[key] = value

            # Creating the final dictionary
            financial_report = {
                'Brief Financial Report': brief_financial_report,
                'Operating Revenue': metrics['Operating Revenue'],
                'EBITDA': metrics['EBITDA'],
                'Networth': metrics['Networth'],
                'Debt/Equity Ratio': metrics['Debt/Equity Ratio'],
                'Return on Equity': metrics['Return on Equity'],
                'Total Assets': metrics['Total Assets'],
                'Fixed Assets': metrics['Fixed Assets'],
                'Current Assets': metrics['Current Assets'],
                'Current Liabilities': metrics['Current Liabilities'],
                'Trade Receivables': metrics['Trade Receivables'],
                'Trade Payables': metrics['Trade Payables'],
                'Current Ratio': metrics['Current Ratio']
            }
            json_data["Financials"] = financial_report
        # financial_details = driver.find_element(By.XPATH, '//*[@id="financial-details-financial-tab"]/div').text
        # financial_details_text = financial_details.split("\n")
        # def find_index_with_prefix(lst, prefix):
        #     for i, element in enumerate(lst):
        #         if re.match(f"^{re.escape(prefix)}", element):
        #             return i
        #     return -1
        # ind = find_index_with_prefix(financial_details_text, 'Current Ratio')
        # financial_details_text_cleaned = [strng for strng in financial_details_text[:ind+1] if strng != 'For a detailed balance sheet']
        # brief_financial_report = financial_details_text_cleaned[2:7]
        # # Extracting specific financial metrics
        # metrics = {
        #     'Operating Revenue': financial_details_text_cleaned[7].split()[-3:],
        #     'EBITDA': financial_details_text_cleaned[8].split()[-2],
        #     'Networth': financial_details_text_cleaned[9].split()[-2],
        #     'Debt/Equity Ratio': financial_details_text_cleaned[10].split()[-1],
        #     'Return on Equity': financial_details_text_cleaned[11].split()[-2],
        #     'Total Assets': financial_details_text_cleaned[12].split()[-2],
        #     'Fixed Assets': financial_details_text_cleaned[13].split()[-2],
        #     'Current Assets': financial_details_text_cleaned[14].split()[-2],
        #     'Current Liabilities': financial_details_text_cleaned[15].split()[-2],
        #     'Trade Receivables': financial_details_text_cleaned[16].split()[-2],
        #     'Trade Payables': financial_details_text_cleaned[17].split()[-2],
        #     'Current Ratio': financial_details_text_cleaned[18].split()[-1]
        # }

        # # Formatting the metrics values
        # for key, value in metrics.items():
        #     # Join the split parts for 'Operating Revenue'
        #     if isinstance(value, list):
        #         value = ' '.join(value)
        #     # Add plus sign for positive values if not present
        #     if value[0] not in ['+', '-']:
        #         value = '+' + value
        #     metrics[key] = value

        # # Creating the final dictionary
        # financial_report = {
        #     'Brief Financial Report': brief_financial_report,
        #     'Operating Revenue': metrics['Operating Revenue'],
        #     'EBITDA': metrics['EBITDA'],
        #     'Networth': metrics['Networth'],
        #     'Debt/Equity Ratio': metrics['Debt/Equity Ratio'],
        #     'Return on Equity': metrics['Return on Equity'],
        #     'Total Assets': metrics['Total Assets'],
        #     'Fixed Assets': metrics['Fixed Assets'],
        #     'Current Assets': metrics['Current Assets'],
        #     'Current Liabilities': metrics['Current Liabilities'],
        #     'Trade Receivables': metrics['Trade Receivables'],
        #     'Trade Payables': metrics['Trade Payables'],
        #     'Current Ratio': metrics['Current Ratio']
        # }
        # json_data["Financials"] = financial_report

        json_output = json.dumps(json_data, indent=4)
        
        driver.quit()
    else:
        print("Failure: Source not yet supported!")
        # driver.quit()
        exit()

    return json_output


# if __name__ == '__main__':
#     print(scrape("MAZAGON DOCK SHIPBUILDERS LIMITED", "Zauba Corp"))