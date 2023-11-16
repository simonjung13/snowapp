#Caller
from db_manager import DatabaseManager 
from lwd_call import lwd_extractor
from Bergfex import bergfex
import pandas as pd
from utils import getSoup_with_js

def stubai_snow():
    url = "https://www.stubaier-gletscher.com/stubai-live/schneebericht/"
    xpath = "/html/body/div[1]/main/div[4]/div/div"
    soup = getSoup_with_js(url, xpath, "XPATH")
    
    
    fresh_snow_soup = soup.find('div', 'snowreport__item bg-light-box__item fresh-snow')
    fresh_snow_date_soup = soup.find('div', 'snowreport__item bg-light-box__item last-powder')


    fresh_snow = fresh_snow_soup.find('div', 'bg-light-box__item-value bg-light-box__item-value--small').text
    fresh_snow_date = fresh_snow_date_soup.find('div', 'bg-light-box__item-value bg-light-box__item-value--small').text
    fresh_snow_date= pd.to_datetime(fresh_snow_date).date()
    fresh_snow = int(fresh_snow.replace(' cm', ''))
    snow_df = pd.DataFrame({'height': [fresh_snow], 'date': [fresh_snow_date]})
    return snow_df

class url_caller:
    stubai_df = None

    def __init__(self, url_resort_list):
        self.db_manager = DatabaseManager()
        self.lwd_helper = lwd_extractor()
        self.bergfex_helper = bergfex(url_resort_list)

    def __fetchData(self):
        self.lwd_helper.fetchData()
        self.bergfex_helper.fetchData()
        self.stubai_df = stubai_snow()


    def __storeData(self):
        self.db_manager.saveData(self.lwd_helper.getDF(), 'lwd')
        self.db_manager.saveData(self.bergfex_helper.getDF_complete(), 'bergfex')
        self.db_manager.saveData(self.bergfex_helper.getDF_meta_complete(), 'bergfex_meta')
        self.db_manager.saveData(self.stubai_df, 'stubai')

    def __storeData_history(self):
        self.db_manager.saveData_nightrun(self.lwd_helper.getDF(), 'lwd')
        self.db_manager.saveData_nightrun(self.bergfex_helper.getDF_complete(), 'bergfex')
        self.db_manager.saveData_nightrun(self.bergfex_helper.getDF_meta_complete(), 'bergfex_meta')
        self.db_manager.saveData_nightrun(self.stubai_df, 'stubai')


    def update(self):
        self.__fetchData()
        self.__storeData()

    def night_run_update(self):
        self.__fetchData()
        self.__storeData_history()

    