from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

wait = WebDriverWait(driver, 15)

# List of restaurants you want to scrape
restaurants_to_search = ["Bazooka", "KFC", "McDonald"]

# Prepare CSV file once
with open("restaurants_menu.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Restaurant", "Branch", "Item Name", "Price"])

    # Loop through each restaurant name
    for restaurant_name in restaurants_to_search:
        print(f"\nSearching for: {restaurant_name}")
        driver.get("https://www.elmenus.com/")

        # Search for restaurant
        search_box = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Find a Restaurant']"))
        )
        search_box.clear()
        search_box.send_keys(restaurant_name)

        # Click search button
        go_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.submit-btn.btn.btn-primary"))
        )
        go_button.click()

        # Collect unique restaurant links for this name
        try:
            restaurant_links = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.clickable-anchor"))
            )
        except:
            print(f"No search results for {restaurant_name}")
            continue

        valid_links = {link.get_attribute("href") for link in restaurant_links
                       if restaurant_name.lower() in link.get_attribute("href").lower()}

        print(f"Found {len(valid_links)} unique links for {restaurant_name}")

        # Visit each branch page
        for url in valid_links:
            driver.get(url)
            time.sleep(2)

            # Wait for menu items
            try:
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.menu-item")))
            except:
                print(f"No menu found for {url}")
                continue

            branch_name = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()

            menu_items = driver.find_elements(By.CSS_SELECTOR, "div.menu-item")
            for item in menu_items:
                try:
                    name = item.find_element(By.CSS_SELECTOR, "h5.title").text.strip()
                except:
                    name = "No name"
                try:
                    price = item.find_element(By.CSS_SELECTOR, "p.price span.bold").text.strip()
                except:
                    price = "No price"

                writer.writerow([restaurant_name, branch_name, name, price])

            print(f"Scraped {branch_name}")

print("\nDONE! All restaurants scraped.")
driver.quit()
