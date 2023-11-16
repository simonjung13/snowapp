import pandas as pd
from utils import getSoup_with_js
import re

def extractTable(soup, table_name):

    try:
        table = soup.find('table')

    except:
        raise TypeError("No Table found")

    # Headers
    headers = []

    for i in table.find_all('th'):
        original_string = i.text.split(':', 1)[0]
        characters_to_remove = int(len(original_string)/2)
        title = original_string[:characters_to_remove] + original_string[characters_to_remove + len(original_string):]
        title = title.split('(', 1)[0]
        headers.append(title)

    mydata = pd.DataFrame(columns = headers)

    #Rows
    for row in table.find_all('tr')[1:]:
        row_data = []
        for td in row.find_all('td'):
            pattern = r'\bsnow\d+\b'
            if td.find('span', class_=re.compile(pattern)):
                row_data.append(td.find('span', class_=re.compile(pattern)).text)
            else:
                row_data.append(td.text)
        mydata.loc[len(mydata)] = row_data

    return mydata


def custom_split(row):

    if row['Station'].count('(') < 2:
        first_open = row['Station'].find('(')
        first_close = row['Station'].find(')')
        return row['Station'][:first_open], row['Station'][first_open + 1:first_close], row['Station'][first_close + 1:]

    else:
        first_open = row['Station'].find('(')
        first_close = row['Station'].find(')')
        second_open = row['Station'].find('(', first_close + 1)
        second_close = row['Station'].find(')', second_open + 1)
        return row['Station'][:first_open], row['Station'][first_open + 1:first_close], row['Station'][second_open + 1:second_close]

    return


def replace_hyphen_with_none(value):
    if '–' in value:
        return None
    return value


def resort_mapping(df):
    # Create a mapping of 'Region' to 'Resort'
    region_resort_mapping = {
        "Zentrale Stubaier": "Stubaier Gletscher",
        "Kalkkögel": "Axamer Lizum",
        "Kühtai": "Kühtai",
        "Westliches Karwendel": "Nordkette",
        "Mieminger": "Seefeld",
        "Weißkugelgruppe": "Sölden",
        "Vorarlberg": "St.Anton",
        "Westliche Tuxer Alpen" : "Glungezer"
    }

    station_resort_mapping = {
        "Dresdner Hütte": "Stubaier Gletscher",
        "Eissee": "Stubaier Gletscher",
        "Schaulfeljoch": "Stubaier Gletscher",
        "Rotadel": "Stubaier Gletscher",

        "Schlicker Alm": "Axamer Lizum",
        "Speicherteich Axamer Lizum": "Axamer Lizum",

        "Magdeburger Hütte": "Nordkette",
        "Seegrube": "Nordkette",
        "Innsbruck Seegrube": "Nordkette",

        "Lizumer Boden" : "Glungezer",

        "Kühtai Längental" : "Kühtai",
        "Breiter Grieskogel Schneestation" : "Kühtai",
        "Hairlachbach (Wasserfassung)" : "Kühtai",
        "Breiter Grieskogel Schneestation" : "Kühtai",

        "Hintertux-Zillertal" : "Hintertux",
        "Hintertux-Zillertal" : "Hintertux"



        

        

        
    }

    #Resort by Region
    # Use the mapping to create a new 'Resort' column
    #df['Resort'] = df['Region'].apply(lambda x: next((resort for region, resort in region_resort_mapping.items() if region in x), x))

    #Resort by Station
    df['Resort'] = df['Station'].apply(lambda x: next((resort for station, resort in station_resort_mapping.items() if station in x), x))

    # If 'Region' is not in the mapping, set 'Resort' to the original 'Region' value
    df['Resort'].fillna(df['Region'], inplace=True)





class lwd_extractor:
    lwd_df = None



    def __init__(self):
        pass
       
    
    def setDF(self, df):
        self.lwd_df = df

    def getDF(self):
        return self.lwd_df


    def fetchData(self):
        url = "https://lawinen.report/weather/measurements"
        xpath = "/html/body/div[1]/main/section[3]/div/table/tbody/tr[1]/td[1]"
        soup = getSoup_with_js(url, xpath, "XPATH")
        df = extractTable(soup, "table-measurements")

        df[['Station', 'Source', 'Update']] = df.apply(custom_split, axis=1, result_type='expand')
        format_string = "%d.%m.%Y, %H:%M"
        df['Update'] = pd.to_datetime(df['Update'], format=format_string, errors='coerce')




        # Convert "Schneehöhe 24h" to a numeric value by stripping non-numeric characters
        df['Schneehöhe'] = df['Schneehöhe'].apply(replace_hyphen_with_none)
        df['24h Differenz Schneehöhe']  = df['24h Differenz Schneehöhe'].apply(replace_hyphen_with_none)
        df['48h Differenz Schneehöhe']  = df['48h Differenz Schneehöhe'].apply(replace_hyphen_with_none)
        df['72h Differenz Schneehöhe']  = df['72h Differenz Schneehöhe'].apply(replace_hyphen_with_none)
        df['Seehöhe']                   = df['Seehöhe'].apply(replace_hyphen_with_none)
        df['Temperatur']                = df['Temperatur'].apply(replace_hyphen_with_none)
        df = df[df['Schneehöhe'].notna()]
        df['Schneehöhe']                = df['Schneehöhe'].str.replace('\u202fcm', '', regex=True).astype(float)
        df['24h Differenz Schneehöhe']  = df['24h Differenz Schneehöhe'].str.replace('\u202fcm', '', regex=True).astype(float)
        df['48h Differenz Schneehöhe']  = df['48h Differenz Schneehöhe'].str.replace('\u202fcm', '', regex=True).astype(float)
        df['72h Differenz Schneehöhe']  = df['72h Differenz Schneehöhe'].str.replace('\u202fcm', '', regex=True).astype(float)
        df['Seehöhe']                   = df['Seehöhe'].str.replace('\u202fm', '', regex=True).astype(float)
        df['Temperature']     = df['Temperatur'].str.extract(r'(-?[0-9,.\u202f]+)°C').replace('\u202f', '', regex=True).replace(',', '.', regex=True).astype(float)
    
        resort_mapping(df)
        
        self.setDF(df)



def main():
    helper = lwd_extractor()
    helper.stubai_snow()
    



if __name__ == "__main__":
    main()



 

 
