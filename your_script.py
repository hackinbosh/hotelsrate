from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import csv

# Create a new instance of the Firefox driver
driver = webdriver.Firefox()

def load_all_content(driver):
    while True:
        try:
            # Wait for the 'Show More' button to be clickable, and click it
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Show More']"))
            )
            print("Clicking 'Show More' button...")
            show_more_button.click()
            # Wait for the new content to load
            time.sleep(20)  # Increased wait time to 20 seconds
            # Scroll down to reveal the 'Show More' button again
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait a moment before attempting to click 'Show More' again
            time.sleep(2)
        except TimeoutException:
            # Break out of the loop if 'Show More' button is not found / not clickable (all results are loaded)
            print("'Show More' button not found. Exiting loop...")
            break

try:
    # Navigate to the URL
    driver.get('https://www.cheekytrip.com/results?t=sun&r=194&p=c&a=25%2C33%2C36%2C30&d=2023-10-22&f=7&n=7&b=AI&h=4&s=0&l=0&_its=JTdCJTIydmlkJTIyJTNBJTIyY2VjM2YyNTAtYjE3YS00NGNhLWJlYmItMzgyN2Y2MWQ1ODE5JTIyJTJDJTIyc3RhdGUlMjIlM0ElMjJybHR%2BMTY5NTk5NzM3M35sYW5kfjJfNTAxOF9kaXJlY3RfMzE4MTJjMGU0M2NiOTNjNDVmMGE1NTg4ZTBlN2FhOTAlMjIlMkMlMjJzaXRlSWQlMjIlM0ExODI2JTdE')
    print(f"Current URL: {driver.current_url}")

    # Wait for a specific element on the page to be present to ensure the page has loaded
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#results_container"))
    )

    # Load all content by clicking 'Show More' and scrolling
    print("Loading all content...")
    load_all_content(driver)

    # Extract hotel names using `find_elements` and `By.CSS_SELECTOR`
    print("Extracting hotel names...")
    hotels = driver.find_elements(By.CSS_SELECTOR, "#results_container div div.col-12.col-sm-8 div div:nth-child(2) strong")
    print("Writing hotel names to CSV file...")
    with open('hotels.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for index, hotel in enumerate(hotels, start=1):
            writer.writerow([f"{index}", hotel.text])

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the browser window
    driver.quit()