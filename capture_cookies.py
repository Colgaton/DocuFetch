# Import Modules
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json,os

# If cookies file exists delete it
def deleteCookies():
    try:
      os.remove('cookies.json')
    except OSError:
      pass

##
def saveCookies(driver):
    # Get and store cookies after login
    cookies = driver.get_cookies()

    # Store cookies in a file
    with open('cookies.json', 'w') as file:
        json.dump(cookies, file)
    print('New Cookies saved successfully')


########## Start

# If the cookies file exists, delete it.
deleteCookies()

# Open Chrome Browser
driver=webdriver.Chrome()

loginURL = 'https://account.docusign.com/username'
driver.get(loginURL)

while True:
    if 'send/documents' in driver.current_url:
      # After successfully login, save new session cookies to json file
      saveCookies(driver)
      break
    

# close the browser
driver.quit()

print('Finished ...')
