# Import Modules
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json,os,time,requests,re

options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver=webdriver.Chrome(options=options)


def loadCookies():
    # Check if cookies file exists
    if 'cookies.json' in os.listdir():
        # Load cookies to a vaiable from a file
        with open('cookies.json', 'r') as file:
            cookies = json.load(file)

        # Set stored cookies to maintain the session
        for cookie in cookies:
            driver.add_cookie(cookie)
    else:
        print('No cookies file found...exiting.')
        exit()
    
    driver.refresh() # Refresh Browser after login

##
def loadCookiesforRequests():
    cookies_dict=[]
    # Check if cookies file exists
    if 'cookies.json' in os.listdir():
        # Load cookies to a variable from a file
        with open('cookies.json', 'r') as file:
            cookies = json.load(file)

        # Set stored cookies to maintain the session
        for cookie in cookies:
            cookies_dict.append([cookie['name'],cookie['value']])
    else:
        print('No cookies file found...exiting.')
        exit()

    cookies_dict = dict(cookies_dict)
    return cookies_dict;

##
#
# Fetch list of envelopes
def fetch_envelopes_list(cookies, url):

 print(url)
 try:
   r=requests.get(url, cookies=cookies)
 except requests.exceptions.RequestException as e: 
   raise SystemExit(e)
 open('envelopes.json', 'wb').write(r.content)
 return r.content

####################### Main ########################

loginURL="https://apps.docusign.com/send/documents?label=completed"
driver.get(loginURL)

# Load old session into the browser
loadCookies()

# Have to wait until all the http requests are done
time.sleep(5);

# Access requests list via the `requests` attribute
# Try to catch the api request that pulls the list of envelopes
for request in driver.requests:
    if 'envelopes' in request.url:
      if request.response:
         envelopesURL = request.url;

# If this var is not set, something went wrong trying to load the website.
# Have the cookies expired maybe?
if 'envelopesURL' not in locals():
   print('Something is wrong with the cookies, try to fetch them again...')
   print('Exiting...')
   exit()

# close the browser
driver.quit()

# Get accountId from envelopes url, we will need it to construct the download url
mysearch = re.search('accounts/(.+?)/envelopes', envelopesURL)
if mysearch:
    accountId = mysearch.group(1)

# Replace the from_date so we can list all the files within the account
envelopesURLAll = re.sub(r'from_date=(.+?)&to_date', '2003-01-01T07:00:00.000Z', envelopesURL)

# reInitialize the cookies in the format for the requests lib
cookies_for_requests=[];
cookies_for_requests=loadCookiesforRequests();

# Fetch list of envelopes
envelopes_list_json = fetch_envelopes_list(cookies_for_requests,envelopesURLAll)

json_data = json.loads(envelopes_list_json);
envelopes=json_data['envelopes'];
for en in envelopes:
  try:
    downloadURL="https://apps.docusign.com/api/send/api/accounts/" + accountId + "/envelopes/" + en['envelopeId'] + "/documents/combined?escape_non_ascii_filenames=true&language=en"
    # Replace special chars with underscore
    newfile = re.sub("([\s\/~#%*<>?{}|])", '_', en['emailSubject'])
    # Download files
    r=requests.get(downloadURL, cookies=cookies_for_requests)
  except requests.exceptions.RequestException as e: 
    raise SystemExit(e)
  print('Writing file ', newfile) # what if the file exists? And files without an extension?
  open(newfile, 'wb').write(r.content)

print('Finished ...')
