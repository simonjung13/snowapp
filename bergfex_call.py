#bergfex_call

import requests
import pandas as pd
from utils import getSoup_with_js
from datetime import datetime, timedelta
import re
from IPython.display import display

#  Helper
def map_to_real_date(input_str):
    current_date = datetime.now()
    base_date = current_date.date()
    current_year = current_date.year
    current_month = current_date.month

    if input_str == 'Heute':
        return base_date
    elif input_str == 'Morgen':
        return base_date + timedelta(days=1)
    elif input_str == 'Übermorgen':
        return base_date + timedelta(days=2)
    elif input_str in ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']:
        # Map day names to weekday numbers (Monday=0, Sunday=6)
        weekday_mapping = {
            'Montag': 0, 'Dienstag': 1, 'Mittwoch': 2, 'Donnerstag': 3, 'Freitag': 4, 'Samstag': 5, 'Sonntag': 6
        }
        today_weekday = base_date.weekday()
        target_weekday = weekday_mapping.get(input_str)
        days_until_target_weekday = (target_weekday - today_weekday + 7) % 7
        return base_date + timedelta(days=days_until_target_weekday)
    else:
        try:
            parts = input_str.split(', ')
            if len(parts) == 2:
                day_name, day_number = parts
            day_number = int(day_number.rstrip('.'))
            return datetime(current_year, current_month, day_number).date()
        except ValueError:
            return None
    # Default to None if mapping is not found
    return None

    # Helper
def exctractElement(i, searchclass, index = 0):
    x = index
    element = i.findAll(class_= searchclass)
    if element[x] and element[x].a:
        out = element[x].a.get_text().replace("\n", "")
    elif element[x]:
        out = element[x].get_text().replace("\n", "")
    else:
        out = None
    return out


def extractAttribute(i, attr, list):
    element = exctractElement(i, attr)
    list.append(element)

def getNumeric(string):
    if string:
        numeric_part = re.search(r'\d+', string)
        if numeric_part:
            extracted_value = int(numeric_part.group())
        else:
            extracted_value = 0
        return extracted_value
    else:
        return None

class BergFexExtractor:
    def __init__(self, url):
        self.master_soup = getSoup_with_js(url, "page-container", "ID")

    #Code
    def getBergFexForecastData(self):
        soup = self.master_soup.find('div', class_='touch-scroll-x')

        attributesArray = [
        ["date", "Date", 0],
        ["nschnee", "Fresh Snow Mountain", 0],
        ["tmin", "tmin Mountain", 0],
        ["tmax", "tmax Mountain", 0],
        ["nschnee", "Fresh Snow Valley", 1],
        ["tmin", "tmin Valley", 1],
        ["tmax", "tmax Valley", 1],
        ["rrp", "Rain Probability", 0],
        ["rrr", "Rain volume", 0],
        ["sonne", "Sun Hours", 0],
        ["sgrenze", "Snowfall Border", 0],
        ["rrr", "Rain volume", 0],
        ["wgew", "Thunderstorm Probability", 0],
        ["ff", "Wind", 0]
        ]

        for row in attributesArray:
            row.append([])

        # Find all elements with class "day" that contain the data
        day_elements = soup.find_all(class_='day')

        for day in day_elements:
            # Extract Date
            for x in attributesArray:
                temp = exctractElement(day, x[0], x[2])
                x[3].append(temp)


        data_dict = {}

        # Iterate through the rows in arr and populate the dictionary
        for row in attributesArray:
            column_header = row[1]  # Get the column header
            values = row[3]  # Get the values
            data_dict[column_header] = values

        # Create a pandas DataFrame from the dictionary
        df = pd.DataFrame(data_dict)
        df['Date'] = df['Date'].apply(map_to_real_date)
        df['ExtractionDate'] = datetime.now()
        df['SourceID'] = self.master_soup.find('div', class_='name').get_text()
        return df


    def getBergFexMetaData(self):
        soup = self.master_soup.find('div', class_='legend labels')
        metadata = []
        metadata.append(soup.find('div', class_='name').get_text())
        metadata.append(soup.find('span', class_='time').get_text())
        metadata.append(soup.findAll('div', class_='elevation')[0].get_text().replace('m', '').replace('.', ''))
        metadata.append(soup.findAll('div', class_='elevation')[1].get_text().replace('m', '').replace('.', ''))
        metadata_df = pd.DataFrame([metadata], columns=['Name', 'Update', 'Mt', 'Vl'])
        return metadata_df



    
