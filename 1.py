# import os
# import zipfile
# import shutil
# import requests
# from io import BytesIO
# from flask import Flask, render_template, request, send_file
# import pandas as pd
# from bs4 import BeautifulSoup
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.edge.service import Service
# from selenium.webdriver.edge.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from werkzeug.utils import secure_filename
# from selenium.webdriver.support import expected_conditions as EC
# import time

# app = Flask(__name__)

# # Temporary directories for input and output
# UPLOAD_FOLDER = 'uploaded_folder'
# OUTPUT_FOLDER = 'processed_output'
# DRIVER_FOLDER = r'C:\Users\edge_driver'  # Folder to store the driver, using raw string to prevent backslash issues.
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(OUTPUT_FOLDER, exist_ok=True)
# os.makedirs(DRIVER_FOLDER, exist_ok=True)

# EDGE_DRIVER_VERSION = "LATEST_STABLE"  # This fetches the latest stable version
# BASE_URL = f"https://msedgedriver.azureedge.net/{EDGE_DRIVER_VERSION}/edgedriver_win64.zip"

# def download_and_extract_edge_driver():
#     """Downloads and extracts the Edge driver."""
#     try:
#         response = requests.get(BASE_URL)
#         response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

#         with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
#             zip_ref.extractall(DRIVER_FOLDER)

#         # Find the extracted executable
#         for filename in os.listdir(DRIVER_FOLDER):
#             if filename.endswith("msedgedriver.exe"):
#                 return os.path.join(DRIVER_FOLDER, filename)

#         return None  # Driver not found

#     except requests.exceptions.RequestException as e:
#         print(f"Error downloading Edge driver: {e}")
#         return None
#     except zipfile.BadZipFile as e:
#         print(f"Error extracting Edge driver: {e}")
#         return None
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         return None

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/scrape', methods=['POST'])
# def scrape():
#     if 'files' not in request.files:
#         return "No files uploaded!", 400

#     files = request.files.getlist('files')

#     if not files:
#         return "No files selected!", 400

#     # Clean up previous uploads
#     shutil.rmtree(UPLOAD_FOLDER, ignore_errors=True)
#     os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#     for file in files:
#         if file.filename.endswith('.xlsx'):
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(UPLOAD_FOLDER, filename)
#             file.save(file_path)
#             print(f"Saved file: {file_path}")  # Debugging information

#     # Download and extract the Edge driver
#     driver_path = download_and_extract_edge_driver()
#     if not driver_path:
#         return "Failed to download or extract Edge driver.", 500

#     service = Service(driver_path)
#     edge_options = Options()
#     edge_options.add_argument("--start-maximized")
#     edge_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

#     driver = webdriver.Edge(service=service, options=edge_options)

#     try:
#         # ... (Rest of your scraping logic remains the same) ...

#         driver.get("https://apps.motor.com/login")
#         WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys("wstuck")
#         WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys("India@123")
#         WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))).click()

#         time.sleep(5)
#         WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.CLASS_NAME, 'card-img-top'))).click()
#         time.sleep(5)

#         for filename in os.listdir(UPLOAD_FOLDER):
#             if filename.endswith('.xlsx'):
#                 file_path = os.path.join(UPLOAD_FOLDER, filename)
#                 print(f"Processing file: {file_path}")  # Debugging information
#                 df = pd.read_excel(file_path, engine='openpyxl')

#                 df['Superseded By'] = ''
#                 df['Current Part Number'] = ''
#                 df['Part Description'] = ''

#                 for index, row in df.iterrows():
#                     # ... (rest of your scraping logic) ...

#                     part_number = row['Part Number']
#                     search_input = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.NAME, "enterPartNumber")))
#                     search_input.clear()
#                     search_input.send_keys(part_number)
#                     WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//button[@id='submitQuickSearchButton']"))).click()

#                     time.sleep(5)

#                     page_source = driver.page_source
#                     soup = BeautifulSoup(page_source, 'html.parser')
#                     rows = soup.find_all('tr')

#                     superseded_by_list = []
#                     current_part_number_list = []
#                     part_description_set = set()

#                     for row in rows:
#                         columns = row.find_all('td')
#                         if len(columns) > 4:
#                             superseded_by = columns[4].text.strip()
#                             current_part_number = columns[5].text.strip()

#                             if len(columns) > 2:
#                                 description = columns[2].text.strip()
#                                 part_description_set.add(description)

#                             superseded_by_list.append(superseded_by)
#                             current_part_number_list.append(current_part_number)

#                     df.at[index, 'Superseded By'] = ', '.join(sorted(set(superseded_by_list))).lstrip(', ')
#                     df.at[index, 'Current Part Number'] = ', '.join(sorted(set(current_part_number_list)))
#                     df.at[index, 'Part Description'] = ' | '.join(sorted(part_description_set))

#                     specific_url = "https://apps.motor.com/supersessions/researchparts"
#                     driver.get(specific_url)

#                 output_file_path = os.path.join(OUTPUT_FOLDER, filename)
#                 print(f"Saving processed file to: {output_file_path}")  # Debugging information
#                 df.to_excel(output_file_path, index=False)

#         # Create a zip file of the output folder
#         zip_filename = 'processed_output.zip'
#         with zipfile.ZipFile(zip_filename, 'w') as zipf:
#             for root, dirs, files in os.walk(OUTPUT_FOLDER):
#                 for file in files:
#                     zipf.write(os.path.join(root, file), file)

#     except Exception as e:
#         print("An error occurred:", e)
#         driver.save_screenshot("error_debug.png")

#     finally:
#         driver.quit()

#     return send_file(zip_filename, as_attachment=True)

# if __name__ == '__main__':
#     app.run(debug=True, port=5000, host="0.0.0.0")