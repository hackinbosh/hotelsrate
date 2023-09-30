from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import csv

# Create a new instance of the Firefox driver
driver = webdriver.Firefox()
driver.maximize_window()  # Open the browser window in maximized mode

def load_all_content(driver):
    attempts = 0
    show_more_clicks = 0
    while True:
        try:
            # Wait for the 'Show More' button to be clickable, and click it
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='show_more']"))
            )
            # Scroll to the 'Show More' button
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", show_more_button)
            time.sleep(2)  # Wait a moment for the page to adjust
            print("Clicking 'Show More' button...")
            if show_more_button.is_displayed():
                show_more_button.click()
                show_more_clicks += 1
                if show_more_clicks >= 2:
                    break
            else:
                print("'Show More' button is not visible. Trying to scroll it into view again...")
                continue
            # Wait for the new content to load
            time.sleep(20)  # Increased wait time to 20 seconds
            attempts = 0  # Reset attempts counter after successful click
        except TimeoutException:
            attempts += 1
            if attempts > 5:  # Break out of the loop after 5 unsuccessful attempts
                print("'Show More' button not found after 5 attempts. Exiting loop...")
                break
            print("'Show More' button not found. Retrying...")
            time.sleep(2)  # Wait a moment before retrying

try:
    # Navigate to the URL
    driver.get('https://www.cheekytrip.com/results?t=sun&r=194&p=c&a=25%2C33%2C36%2C30&d=2023-10-22&f=7&n=7&b=AI&h=4&s=0&l=0&_its=JTdCJTIydmlkJTIyJTNBJTIyY2VjM2YyNTAtYjE3YS00NGNhLWJlYmItMzgyN2Y2MWQ1ODE5JTIyJTJDJTIyc3RhdGUlMjIlM0ElMjJybHR%2BMTY5NTk5NzM3M35sYW5kfjJfNTAxOF9kaXJlY3RfMzE4MTJjMGU0M2NiOTNjNDVmMGE1NTg4ZTBlN2FhOTAlMjIlMkMlMjJzaXRlSWQlMjIlM0ExODI2JTdE')
    print(f"Current URL: {driver.current_url}")

    # Wait for a specific element on the page to be present to ensure the page has loaded
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#results_container"))
    )

    # Dismiss the cookie consent banner
    try:
        cookie_banner_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[11]/div/div/div[2]/button"))
        )
        cookie_banner_button.click()
    except TimeoutException:
        print("Cookie consent banner not found. Proceeding without dismissing...")

    # Load all content by clicking 'Show More' and scrolling
    print("Loading all content...")
    load_all_content(driver)

    # Extract hotel names, prices and star ratings using `find_elements` and `By.CSS_SELECTOR`
    print("Extracting hotel names, prices and star ratings...")
    hotels = driver.find_elements(By.CSS_SELECTOR, "#results_container div div.col-12.col-sm-8 div div:nth-child(2) strong")
    prices = driver.find_elements(By.XPATH, "//*[@id='results_container']/div/div/div[2]/div/div[1]/div[1]/div[2]/span[1]")
    star_ratings = [len(hotel.find_elements(By.CSS_SELECTOR, ".fa.fa-star.solid")) for hotel in driver.find_elements(By.XPATH, "//*[@id='results_container']/div/div/div[2]/div/div[3]")]
    
    print("Writing hotel names, prices and star ratings to CSV file...")
    with open('hotels.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Index", "Hotel Name", "Price", "Star Rating"])
        for index, (hotel, price, star_rating) in enumerate(zip(hotels, prices, star_ratings), start=1):
            writer.writerow([f"{index}", hotel.text, price.text, star_rating])

except (Exception, WebDriverException) as e:
    print(f"An error occurred: {e}")
finally:
    time.sleep(10)  # Wait for 10 seconds before closing the browser window
    # Close the browser window
    # driver.quit()