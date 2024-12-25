from collections import Counter
import string
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# API credentials copied from the RapidAPI Ultra-Fast Translation API.
API_URL = "https://ultra-fast-translation.p.rapidapi.com/t"
HEADERS = {
    "content-type": "application/json",
    "X-RapidAPI-Key": "c2432b444dmsh909f603234f0c69p1a0e09jsne64b3c285be3",
    "X-RapidAPI-Host": "ultra-fast-translation.p.rapidapi.com"
}

word_counter = Counter()

def translate_text(text):
    """
    Translates the given text using the RapidAPI Ultra-Fast Translation API.
    :param text: Text to translate
    :param target_language: Target language code (default: English 'en')
    :return: Translated text
    """
    payload = {
        "from": "es",  # Input text is spanish
        "to": "en",    # Output text is  English
        "e": "",
        "q": text
    }
    
    response = requests.post(API_URL, json=payload, headers=HEADERS)
    
    if response.status_code == 200:
        return response.json()[0]    # Accessing the translated text
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return "Translation failed"

# Selenium setup
chrome_service = Service(executable_path='/usr/local/bin/chromedriver')  # replace the path with the chromedriver path to run the script
driver = webdriver.Chrome(service=chrome_service)

try:
    # Navigate to a webpage with text to translate
    driver.get("https://elpais.com/")
    time.sleep(1)  # Wait for the page to load
    
    # code to close the modal which appears on the start of page
    try:
        accept_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        accept_button.click()  # Click the "Accept" button
        print("Cookies accepted and modal closed!")
    except Exception as e:
        print(f"An error occurred: {e}")


    # Locate the element containing the text
    opinion_button = driver.find_element(By.LINK_TEXT, "Opinión")  # Selecting the "Opinión" element
    opinion_button.click() 

    try:
        # fetching first 5 articles in the page
        articles = driver.find_elements(By.TAG_NAME, "article")[:5]
        text_file = "text_file.txt"
        


        for indx, article in enumerate(articles,1):
            article_title = article.find_element(By.TAG_NAME, "h2")
            article_content = article.find_element(By.TAG_NAME , "p")
            
            # saving the cover image if exists
            try:
                article_img = article.find_element(By.TAG_NAME , "img")
                article_img_url = article_img.get_attribute("src")
                img_response = requests.get(article_img_url)
                img_response.raise_for_status()
                img_response_name = f"image_{int(time.time())}.jpg"
                with open(img_response_name , "wb") as file:
                    file.write(img_response.content)

            except Exception as e:
                print(f"No image found in the article : {e}")

            with open(text_file, "a", encoding="utf-8") as file:
                file.write(f"Article:{indx} - {article_title.text}\n")
                file.write(article_content.text + "\n")
        
            # translating the header of the article
            translated_text_file = "translated_text.txt"
            translated_title = translate_text(article_title.text)
            with open(translated_text_file,"a",encoding="utf-8") as file:
                file.write(f"Article:{indx} - {translated_title}\n")
            
            # analyzing the translated text
            word_counter.update(translated_title.lower().translate(str.maketrans('', '', string.punctuation)).split())


    except Exception as e :
        print(f"An error occurred in selenium driver: {e}")
    

finally:
    # print the repeated words in all the headers
    print({word:count for word,count in word_counter.items() if count>2})
    # Quit the browser
    print("closing the script!")
    driver.quit()


