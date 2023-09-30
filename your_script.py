from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time
import csv
import os
import pandas as pd
from datetime import datetime

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
                if show_more_clicks >= 10:
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

def get_tripadvisor_score(hotel_name):
    # Navigate to the TripAdvisor website
    driver.get('https://www.tripadvisor.co.uk/Hotels')

    # Locate the search box and input the hotel name
    search_box = driver.find_element_by_xpath('/html/body/div[2]/div/div[1]/div/div/div/div/div/div/div[2]/div[1]/div/div[2]/div/form/div/div/input')
    search_box.send_keys(hotel_name)
    search_box.submit()

    # Wait for the search results page to load
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), 'Top result matching \"{hotel_name}\"')]"))
    )

    # Locate the TripAdvisor score
    score_element = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div[4]/div/div[1]/div[4]/div/div/div/div/div[2]/div[1]/div[1]/span')
    score = float(score_element.text)  # Extract the score from the text

    return score

def get_file_info_and_confirm_skip():
    # Check if the `hotels.csv` file exists
    if os.path.exists('./hotels.csv'):
        # Get the last updated date of the file
        last_updated = datetime.fromtimestamp(os.path.getmtime('./hotels.csv')).strftime('%Y-%m-%d %H:%M:%S')

        # Read the file and count the number of hotel names, star ratings, and prices
        df = pd.read_csv('./hotels.csv')
        num_hotels = df['Hotel Name'].count()
        num_star_ratings = df['Star Rating'].count()
        num_prices = df['Price'].count()

        print(f"The 'hotels.csv' file was last updated on {last_updated}. It contains {num_hotels} hotel names, {num_star_ratings} star ratings, and {num_prices} prices.")
        confirm_skip = input("Do you want to skip to the TripAdvisor extraction step? (yes/no): ")
        return confirm_skip.lower() == 'yes'
    else:
        return False

try:
    skip_to_tripadvisor = get_file_info_and_confirm_skip()

    if not skip_to_tripadvisor:
        # Navigate to the URL
        driver.get('https://www.cheekytrip.com/results?t=sun&r=194&p=c&a=25,33,36,30&d=2023-10-22&f=7&n=7&b=AI&h=3&s=0&l=0')
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
    else:
        # Read the hotel names from the `hotels.csv` file
        df = pd.read_csv('./hotels.csv')
        hotels = df['Hotel Name'].tolist()

    print("Writing hotel names, prices, star ratings, and TripAdvisor scores to CSV file...")
    with open('./hotels.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Index", "Hotel Name", "Price", "Star Rating", "TripAdvisor Score"])
        for index, (hotel, price, star_rating) in enumerate(zip(hotels, prices, star_ratings), start=1):
            tripadvisor_score = get_tripadvisor_score(hotel.text)
            writer.writerow([f"{index}", hotel.text, price.text, star_rating, tripadvisor_score])

except (Exception, WebDriverException) as e:
    print(f"An error occurred: {e}")
finally:
    time.sleep(10)  # Wait for 10 seconds before closing the browser window
    # Close the browser window
    driver.quit()