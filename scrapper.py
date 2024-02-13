# Import packages
import re
import os
import time
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
import config
import db_handler

# Performance measurement
start_time = time.time()

# Clean image folder
# folder_path = r"C:\Users\Roberto\OneDrive\Projetos\Tinder Profiler\pics"
# files = os.listdir(folder_path)
# for file in files:
#     file_path = os.path.join(folder_path, file)
#     os.remove(file_path)

# Startup crawler
options = Options()
options.add_argument('start-maximized')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Navigate
url = 'https://www.tinder.com'
driver.get(url)
handles = driver.window_handles
original_window_handle = driver.current_window_handle
print(driver.title)

# Authenticate
login_txt = 'Log in'
login_btn = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, f"//*[contains(text(),'{login_txt}')]/ancestor::a"))
)
login_btn.click()
login_fb_txt = 'Log in with Facebook'
while True:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//*[contains(text(),'{login_fb_txt}')]/ancestor::button"))
    )
    login_fb_btn = driver.find_element(By.XPATH,f"//*[contains(text(),'{login_fb_txt}')]/ancestor::button")
    try:
        print(login_fb_btn.get_attribute('class'))
    except StaleElementReferenceException:
        time.sleep(5)
        login_fb_btn = driver.find_element(By.XPATH,f"//*[contains(text(),'{login_fb_txt}')]/ancestor::button")
    login_fb_btn.click()
    popup_window_handle = WebDriverWait(driver, 10).until(
        EC.new_window_is_opened(handles)
    )
    driver.switch_to.window(driver.window_handles[-1])
    email_form = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//input[@id="email"]'))
    )
    email_form.send_keys(config.USER)
    pass_form = driver.find_element(By.XPATH, '//input[@id="pass"]')
    pass_form.send_keys(config.PASS)
    login_frm = driver.find_element(By.XPATH, '//input[@name="login"]')
    login_frm.click()
    time.sleep(5)
    driver.switch_to.window(original_window_handle)
    if driver.current_url != 'https://tinder.com/':
        print('Logged in.')
        break

# Get rid of modals
try:
    allow_location_btn = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f"//*[contains(text(),'Allow')]/ancestor::button"))
    )
    allow_location_btn.click()
except TimeoutException:
    pass

# Define crawler function, with decisor parameter
def scrape_pictures(card_number):
    print(f'Progress is: {card_number}.')
    # Check if there is still likes available
    try:
        driver.find_element(By.XPATH,f'//h3[text()="You\'re Out of Likes!"]')
        print('Out of likes.')
        return False
    except NoSuchElementException:
        pass

    # Get rid of popups
    try:
        not_notify_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(),'Not interested')]/ancestor::button"))
        )
        not_notify_btn.click()
    except TimeoutException:
        pass
    try:
        not_notify_btn = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(),'Maybe Later')]/ancestor::button"))
        )
        not_notify_btn.click()
    except TimeoutException:
        pass
    # Scrape picture
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, f'//div[@data-keyboard-gamepad="true" and @aria-hidden="false"]'))
    )
    person_deck_xpath = f'//div[@data-keyboard-gamepad="true" and @aria-hidden="false"]'
    person_cards_xpath = f'/div[contains(@class,"tappable-view")]/div/span[@aria-hidden="false"]'
    deck_btns_xpath = f'/div[contains(@class,"tappable-view")]/div/button'
    img_xpath = f'/div[@role="img"]'
    name_xpath = f'//span[@itemprop="name"]'
    age_xpath = f'//span[@itemprop="age"]'
    distance_xpath = f'//div[contains(text(),"kilometers away")]'
    work_xpath = f'//span[@itemprop="work"]'
    academics_xpath = f'//span[@itemprop="academics"]'
    like_xpath = f'//span[text()="Like" and @class="Hidden"]/ancestor::button'
    dislike_xpath = f'//span[text()="Nope" and @class="Hidden"]/ancestor::button'
    matched_card_xpath = f'//span[contains(text(),"likes you too")]'
    matched_exit_btn_xpath = f'//button[@title="Back to Tinder"]'
    # Get deck count
    deck_btns = driver.find_elements(By.XPATH,person_deck_xpath+deck_btns_xpath)
    deck_count = len(deck_btns)
    print(f'This element contains {deck_count} photos.')
    # Iterate through deck
    for i in range(deck_count):
        # Click btn
        time.sleep(1) # Give enough time for image to load
        deck_btns[i].click()

        # Set profile id
        if i == 0:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            # Extract data
            name = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH,person_deck_xpath+name_xpath))
            )
            try:
                age = int(driver.find_element(By.XPATH,person_deck_xpath+age_xpath).text)
            except:
                print('No age info found.')
                age = None
            try:
                work = driver.find_element(By.XPATH,person_deck_xpath+work_xpath).text
            except:
                print('No work info found.')
                work = None
            try:
                academics = driver.find_element(By.XPATH,person_deck_xpath+academics_xpath).text
            except:
                print('No academics info found.')
                academics = None
            try:
                distance_text = driver.find_element(By.XPATH,person_deck_xpath+distance_xpath).text
                pattern = r'(\d?)\s'
                distance = int(re.search(pattern,distance_text).group(1))
            except:
                print('No distance info found.')
                distance = None
            db_handler.insert_into(name.text, age, timestamp, work, academics, distance)
            print('Data saved to DB.')

        # Extract url
        img = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,person_deck_xpath+person_cards_xpath+img_xpath))
        )
        print(img.get_attribute("outerHTML"))
        style = img.get_attribute('style')
        pattern = r'url\("(.+)"'
        url = re.search(pattern,style).group(1)
        print(url)
        # Save image
        response = requests.get(url)
        with open(f'pics/{timestamp}_{i}.jpg', 'wb') as file:
            file.write(response.content)
            print('Picture saved.')
    # Send Like
    dislike_btn = driver.find_element(By.XPATH,dislike_xpath)
    like_btn = driver.find_element(By.XPATH,like_xpath)
    like_btn.click()
    print('Like clicked.')

    # Check if matched
    try:
        WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.XPATH, matched_exit_btn_xpath))
        )
        matched_exit_btn = driver.find_element(By.XPATH,matched_exit_btn_xpath)
        matched_exit_btn.click()
        print('Got a match.')
    except TimeoutException:
        pass

if __name__ == '__main__':
    # Scrape data
    for progress in range(80):
        check = scrape_pictures(progress)
        if check == False:
            break
        print(f'{progress}th scrape done.')
    print('Done.')
    # Close the driver
    driver.quit()

# Performance measurement
end_time = time.time()
total_time = end_time - start_time
print(f"Total time taken: {total_time:.2f} seconds")
