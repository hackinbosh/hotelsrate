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
                if show_more_clicks >= 2:  # Limit the number of 'Show More' button clicks to two
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

# Rest of the code...

# Extract hotel names, prices, star ratings, airport and departure date using `find_elements` and `By.XPATH`
print("Extracting hotel names, prices, star ratings, airport and departure date...")
hotels = driver.find_elements(By.CSS_SELECTOR, "#results_container div div.col-12.col-sm-8 div div:nth-child(2) strong")
prices = driver.find_elements(By.XPATH, "//*[@id='results_container']/div/div/div[2]/div/div[1]/div[1]/div[2]/span[1]")
star_ratings = [len(hotel.find_elements(By.CSS_SELECTOR, ".fa.fa-star.solid")) for hotel in driver.find_elements(By.XPATH, "//*[@id='results_container']/div/div/div[2]/div/div[3]")]
airports = driver.find_elements(By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div[1]/div[2]/div[1]/div/div[2]/div/div[4]/div[3]/strong")
departure_dates = driver.find_elements(By.XPATH, "//*[@id='results_container']/div[1]/div/div[2]/div/div[4]/div[5]/text()")

# Rest of the code...

# Write hotel names, prices, star ratings, airport, departure date, and TripAdvisor scores to CSV file
print("Writing hotel names, prices, star ratings, airport, departure date, and TripAdvisor scores to CSV file...")
with open('/hotels.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Index", "Hotel Name", "Price", "Star Rating", "Airport", "Departure Date", "TripAdvisor Score"])
    for index, (hotel, price, star_rating, airport, departure_date) in enumerate(zip(hotels, prices, star_ratings, airports, departure_dates), start=1):
        tripadvisor_score = get_tripadvisor_score(hotel.text)
        writer.writerow([f"{index}", hotel.text, price.text, star_rating, airport.text, departure_date.text, tripadvisor_score])

# Rest of the code...