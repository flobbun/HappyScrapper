# Imports
from selenium import webdriver;
from selenium.webdriver.common.by import By;
from selenium.webdriver.support.ui import WebDriverWait;
from selenium.webdriver.support import expected_conditions as EC;
from selenium.webdriver.edge.service import Service
import os;
import sys;
import json;
import smtplib;
import time;

# Read JSON file
def getJSONConfig():
    with open("HappyScrappy.json") as f:
        data = json.load(f);
        f.close()
    return data['CONFIG'];

def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS;
    except Exception:
        base_path = os.path.dirname(__file__);
    return os.path.join(base_path, relative_path);

# Constants
CONFIG = getJSONConfig();
HOST = CONFIG['EMAIL']['HOST'];
PORT = CONFIG['EMAIL']['PORT'];
EMAIL_FROM = CONFIG['EMAIL']['EMAIL_FROM'];
EMAIL_TO = CONFIG['EMAIL']['EMAIL_TO'];
EMAIL_PASSWORD = CONFIG['EMAIL']['EMAIL_PASSWORD'];
PING_INTERVAL = CONFIG['ADVANCED']['PING_INTERVAL'];
N_LINKS_PER_PAGE = CONFIG['ADVANCED']['N_LINKS_PER_PAGE'];
URL = 'https://news.google.com/topstories?hl=es-419&gl=US&ceid=US:es-419';
DRIVER = CONFIG['ADVANCED']['DRIVER'];
DRIVER_PATH = CONFIG['ADVANCED']['DRIVER_PATH'];
DURATION = CONFIG['ADVANCED']['DURATION'];

MSG_WELCOME = "\n▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒.•○`Welcome to HappyScrappy by Jhon Aguiar`○•.▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒\n";
MSG_SCRAPPING_STARTED = "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒.•○ Scrapping started! ○•.▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒";
MSG_SCRAPPING_FAILED = "▒▒▒▒▒▒▒▒▒▒▒.•○ Scrapping failed! ○•.▒▒▒▒▒▒▒▒▒▒▒";
MSG_SCRAPPING_INCOMPLETED = "▒▒▒▒▒▒▒▒▒▒▒.•○ Scrapping incompleted, we will send the E-mail anyways... ○•.▒▒▒▒▒▒▒▒▒▒▒";
MSG_SCRAPPING_FINISHED = "▒▒▒▒▒▒▒▒▒▒▒.•○ Scrapping finished! ○•.▒▒▒▒▒▒▒▒▒▒▒";
MSG_EMAIL_FAILED = "▒▒▒▒▒▒▒▒▒▒▒.•○ Email sending failed! ○•.▒▒▒▒▒▒▒▒▒▒▒";
MSG_EMAIL_SENT = "▒▒▒▒▒▒▒▒▒▒▒.•○ Email sent! ○•.▒▒▒▒▒▒▒▒▒▒▒";

# Variables
keywords = ["empty"];
linksFound = [];

def clear_console(): return os.system('cls' if os.name == 'nt' else 'clear')

# Send email
def sendEmail():
    with smtplib.SMTP_SSL(HOST, PORT) as smtp:
        try:
            smtp.login(EMAIL_FROM, EMAIL_PASSWORD);
            subject = ".•○ News Scrapper "+time.strftime("%d/%m/%Y %H:%M:%S", time.localtime())+" ○•.";
            body = "\n".join(linksFound);
            msg = f'Subject: {subject} \n\n {body}';
            smtp.sendmail(EMAIL_FROM, EMAIL_TO, msg.format(EMAIL_FROM, EMAIL_TO, msg).encode('utf-8'));
        except Exception as e:
            print(linksFound);
            print(MSG_EMAIL_FAILED);
            return 0;
        print(MSG_EMAIL_SENT);

# Getting links
def getAllLinksElements(browser):
    try:
        return (WebDriverWait(browser, PING_INTERVAL).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[class='DY5T1d RZIKme']"))));
    except:
        browser.quit();
        return (0);

# Searching for keywords
def searchKeyword(browser, keyword): browser.get(f'https://news.google.com/search?q={keyword}&hl=pt-PT&gl=PT&ceid=PT%3Apt-150');

# Start scraping
def startScrapper(keywords):
    clear_console();
    print(MSG_SCRAPPING_STARTED);
    browser = webdriver.Edge(resource_path(DRIVER_PATH));
    browser.get(URL);
    links = [];

    # Accepting cookies
    browser.find_elements(By.CSS_SELECTOR, '[type="submit"]')[0].click();

    # Searching for keywords
    for i in range(len(keywords)):
        searchKeyword(browser, keywords[i]);
        links = getAllLinksElements(browser);
        if links != 0:
            for j in range(N_LINKS_PER_PAGE):
                if links[j].get_attribute('href') not in linksFound:
                    linksFound.append(f"{j+1} 📰 {links[j].text} {links[j].get_attribute('href')}");
                    print(f"{keywords[i]} Scrapped: {j+1}📰 {links[j].text}");
        else:
            if (len(linksFound) == 0):
                print(MSG_SCRAPPING_FAILED);
                browser.quit();
            else:
                print(MSG_SCRAPPING_INCOMPLETED);
                sendEmail();
    browser.quit();
    print(MSG_SCRAPPING_FINISHED);

# Get keywords
def getKeywords():
    clear_console();
    print(MSG_WELCOME);
    keywords = input("Enter all keywords separated by a comma (max 12): ").split(",");
    if(input("Start scraping? [Y/n]: ") == "n"):
        getKeywords();
    else:
        startScrapper(keywords);
        sendEmail();

# Main
def main():
    getKeywords();
    time.sleep(DURATION);
if __name__ == "__main__":
   main();