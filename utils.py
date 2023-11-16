#utils

import os
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import chromedriver_autoinstaller
from bs4 import BeautifulSoup
import re
 

weekday_mapping = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}
def getWeekday(date):
    weekday_number = date.weekday()
    weekday_string = weekday_mapping.get(weekday_number, "Unknown")
    return weekday_string

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def clean_fresh_snow(value):
    # Pattern to match one or more digits
    digit_pattern = r'\d+'

    # Pattern to match ranges like '5-10cm'
    range_pattern = rf'({digit_pattern})-({digit_pattern})cm'

    # Pattern to match '<2cm'
    less_than_pattern = r'<(\d+)cm'

    # Check for each pattern and extract the relevant value
    if re.match(digit_pattern, value):
        return int(re.search(digit_pattern, value).group())
    elif re.match(range_pattern, value):
        match = re.search(range_pattern, value)
        return (int(match.group(1)) + int(match.group(2))) / 2
    elif re.match(less_than_pattern, value):
        return int(re.search(less_than_pattern, value).group(1))
    else:
        return 0  # Default to 0 if no pattern matches


def getSoup_with_js(url, element, type):

    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver = webdriver.Chrome(options=op)
    driver.get(url)
    delay = 15 # seconds

    if type == "Class":
        try:
            myElem = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.CSS_SELECTOR, element)))
        except TimeoutException:
            print ("Loading took too much time!")

    if type == "ID":
        try:
            myElem = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.ID, element)))
        except TimeoutException:
            print ("Loading took too much time!")

    if type == "XPATH":
        try:
            myElem = WebDriverWait(driver, delay).until(EC.visibility_of_element_located((By.XPATH, element)))
        except TimeoutException:
            print ("Loading took too much time!")

    



    html = driver.page_source
    soup = BeautifulSoup(html, features="lxml")
    return soup


def getInfoFromDF(df, col, search_in_col, search_value):
    temp_df = df
    header = temp_df.columns
    if search_in_col in header and col in header:
        temp_df = temp_df[search_in_col] == search_value
        if temp_df:
            col = temp_df[col]
            out =col.iloc[0]
            return out
        else:
            print("No matches in col: " +search_in_col + " for value " + search_value )
            return None
    else:
        print("Column is not exisiting")

    