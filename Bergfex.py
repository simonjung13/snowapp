from bergfex_call import BergFexExtractor
import pandas as pd
import re
import numpy as np



# Apply the function to the DataFrame
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



class bergfex:
    bergfex_df = None
    bergfex_meta = None
    resort_url_list = None
    logger = ""

    def __init__(self, resort_url_list):
        self.resort_url_list = resort_url_list
        self.resort_list = [item[0] for item in resort_url_list]
        self.url_list = [item[1] for item in resort_url_list]


    def fetchData(self):
        df = None  # Initialize an empty DataFrame
        df_meta = None
        Error = False
        for resort, url in self.resort_url_list:
            try:
                self.logger += ("Fetching Bergfex Data for: " + resort)
                temp_extractor = BergFexExtractor(url)
                temp_df = temp_extractor.getBergFexForecastData()
                temp_df_meta = temp_extractor.getBergFexMetaData()
                
            except:
                Error = True
                raise Exception ("Error in Fecthing data: " + str(url))
            temp_df['SourceID'] = resort


            if df is not None:
                df = pd.concat([df, temp_df], ignore_index=True)
            else:
                df = temp_df

            temp_df_meta['SourceID'] = resort
            if df_meta is not None:
                df_meta = pd.concat([df_meta, temp_df_meta], ignore_index=True)
            else:
                df_meta = temp_df_meta

            self.logger +=("Successful: " + resort)
           
        self.setDF(df)
        self.setDF_meta(df_meta)
        if Error:
            print("ERROR - Check log")
        else: self.logger +=("All Data from Bergfex loaded")
        

    def setDF(self, df):
        df['Fresh Snow Mountain']       = df['Fresh Snow Mountain'].apply(clean_fresh_snow).astype(float)
        df['Fresh Snow Valley']         = df['Fresh Snow Valley'].apply(clean_fresh_snow).astype(float)
        df['Snowfall Border']           = df['Snowfall Border'].replace({'-': np.nan})
        df['Snowfall Border']           = df['Snowfall Border'].replace({'m': '', '\.': ''}, regex=True).astype(float)
        df['tmin Mountain']             = df['tmin Mountain'].str.extract(r'(-?[0-9,.\u202f]+)°C').replace('\u202f', '', regex=True).replace(',', '.', regex=True).astype(float)
        df['tmax Mountain']             = df['tmax Mountain'].str.extract(r'(-?[0-9,.\u202f]+)°C').replace('\u202f', '', regex=True).replace(',', '.', regex=True).astype(float)
        df['tmin Valley']               = df['tmin Valley'].str.extract(r'(-?[0-9,.\u202f]+)°C').replace('\u202f', '', regex=True).replace(',', '.', regex=True).astype(float)
        df['tmax Valley']               = df['tmax Valley'].str.extract(r'(-?[0-9,.\u202f]+)°C').replace('\u202f', '', regex=True).replace(',', '.', regex=True).astype(float)
        df['Sun Hours']                 = df['Sun Hours'].str.replace("h", "").replace("-", "0").astype(int)
        pattern = re.compile(r'([A-Z]+(?:-[A-Z]+)?)\s+(\d+)')
        df[['Wind Direction', 'Wind']]  = df['Wind'].str.extract(pattern)
        df['Wind']                      = df['Wind'].astype(int)
        self.bergfex_df=df

    def setDF_meta(self, df):
        self.bergfex_meta = df

    def getDF_complete(self):
        return self.bergfex_df
    def getDF_meta_complete(self):
        return self.bergfex_meta

    




