from datetime import datetime as dt, date as d, timedelta
from db_manager import DatabaseManager
import pandas as pd
import re
from utils import getSoup_with_js
from utils import getWeekday

# Variables
today = dt.now().date()


### Helper##################################################################################
def classify_seehohe(seehohe, mid):
    if seehohe < (mid):
        return f'Below {mid}'
    elif seehohe > (mid):
        return f'Above {mid}'

def grouping(df, mid):
        df['Seehöhe Class'] = df['Seehöhe'].apply(classify_seehohe, mid=mid)
        # Group by resort and Seehöhe Class, and calculate the average of Schneehöhe
        result = df.groupby(['Resort', 'Seehöhe Class'])[['Seehöhe', 'Schneehöhe', '24h Differenz Schneehöhe', '48h Differenz Schneehöhe', '72h Differenz Schneehöhe', 'Temperature']].mean().reset_index()
        count_df = df.groupby(['Resort', 'Seehöhe Class'])['Schneehöhe'].count().reset_index()
        count_df.rename(columns={'Schneehöhe': 'Count'}, inplace=True)
        

        result = result.merge(count_df, on=['Resort', 'Seehöhe Class'])
        result = result.round(1)
        return result


 
def SnowForecast(df, nextdays, forecast_day):
    temp_df = df
    today_dt = pd.to_datetime(today)
    forecast_day = pd.to_datetime(forecast_day)
    if nextdays > 3 or nextdays <= 0:
        raise Exception("Nextdays Value in SnowForecast out of range")
    
    #if forecast_day < today_dt or forecast_day + timedelta (3) > today_dt + timedelta (9):
    #    raise Exception("Forecast day in SnowForecast out of range")
    today_dt = forecast_day 
    nextdays -= 1

    x_days_later = today_dt + timedelta(days=nextdays)
    temp_df['Date'] = pd.to_datetime(temp_df['Date'])
    # Filter the DataFrame for dates within the next three days
    temp_df = temp_df[(temp_df['Date'] >= today_dt) & (temp_df['Date'] <= x_days_later)]
    grouped = temp_df.groupby('SourceID')
    snow_values = grouped['Fresh Snow Mountain'].sum()
    snow_values_below = grouped['Fresh Snow Valley'].sum()
    return snow_values, snow_values_below





class Weather_Day_Resort:
    #user defined:
    __user_date: d
    __user_resort: str
    __time: dt

    #lwd:
    __actual_snowfall_24: float
    __actual_snowfall_48: float
    __actual_snowfall_72: float
    __actual_temp: float
    __sea_level: float

    __actual_snowfall_24_below: float
    __actual_snowfall_48_below: float
    __actual_snowfall_72_below: float
    __actual_temp_below: float
    __sea_level_below: float

    #bergfex
    __forecasted_snowfall_24: float
    __forecasted_snowfall_48: float
    __forecasted_snowfall_72: float
    __forecasted_snowfall_24_below: float
    __forecasted_snowfall_48_below: float
    __forecasted_snowfall_72_below: float
    __rain_probability: float
    __rain_volumen: float
    __sun_hours: float
    __temp_max_mt: float
    __temp_min_mt: float
    __temp_max_va: float
    __temp_min_va: float
    __wind: float
    __wind_direction: str
    __snowline: float

    #bergfex_meta
    __valley: float
    __top: float

    # Calculated Vars
    __rating: float
    __weekday: str
    


    def __init__(self, p_date: d, p_resort: str):     
        self.user_date = p_date
        self.user_resort = p_resort

        # lwd
        self.__actual_snowfall_24 = None
        self.__actual_temp = None
        self.__sea_level = None

        self.__actual_snowfall_24_below = None
        self.__actual_temp_below = None
        self.__sea_level_below = None

        # bergfex
        self.__forecasted_snowfall_24 = None
        self.__forecasted_snowfall_24_below = None
        self.__rain_probability = None
        self.__rain_volume = None
        self.__sun_hours = None
        self.__temp_max_mt = None
        self.__temp_min_mt = None
        self.__temp_max_va = None
        self.__temp_min_va = None
        self.__wind = None
        self.__wind_direction = None
        self.__snowline = None

        # bergfex_meta
        self.__valley = None
        self.__top = None

        # Calculated Vars
        self.__rating = None

        self.__weekday = getWeekday(p_date)

        
        db              = DatabaseManager()
        historical = False
        if p_date >= today:
            lwd_df          = db.loadData('lwd')
            bergfex_df      = db.loadData('bergfex')
            bergfex_meta    = db.loadData('bergfex_meta')
            stubai_df       = db.loadData('stubai')

            if lwd_df.empty:
                raise Exception("Cant create proper Agent - No LWD Data - " + str(d) +" - " + str(p_date) + "- " + p_resort)
            if bergfex_df.empty:
                raise Exception("Cant create proper Agent - No bergfex_df Data - " + str(d) +" - " + str(p_date) + "- " + p_resort)
            if bergfex_meta.empty:
                raise Exception("Cant create proper Agent - No bergfex_meta Data - " + str(d) +" - " + str(p_date) + "- " + p_resort)

        else: 
            historical = True
            lwd_df          = db.loadData('lwd_history')
            bergfex_df      = db.loadData('bergfex_history')
            bergfex_meta    = db.loadData('bergfex_meta_history')
            stubai_df       = db.loadData('stubai_history')

            if lwd_df.empty:
                raise Exception("Cant create proper Agent - No LWD Data - " + str(d) +" - " + str(p_date) + "- " + p_resort)
            if bergfex_df.empty:
                raise Exception("Cant create proper Agent - No bergfex_df Data - " + str(d) +" - " + str(p_date) + "- " + p_resort)
            if bergfex_meta.empty:
                raise Exception("Cant create proper Agent - No bergfex_meta Data - " + str(d) +" - " + str(p_date) + "- " + p_resort)
            

            lwd_df['Stored']        = pd.to_datetime(lwd_df['Stored'])
            bergfex_df['Stored']    = pd.to_datetime(bergfex_df['Stored'])
            bergfex_meta['Stored']  = pd.to_datetime(bergfex_meta['Stored'])
            stubai_df['Stored']     = pd.to_datetime(stubai_df['Stored'])
            

            lwd_df          = lwd_df[lwd_df['Stored'].dt.date               == p_date]
            bergfex_df      = bergfex_df[bergfex_df['Stored'].dt.date       == p_date]
            bergfex_meta    = bergfex_meta[bergfex_meta['Stored'].dt.date   == p_date]
            stubai_df               = stubai_df[stubai_df['Stored'].dt.date == p_date]

        lwd_df          = lwd_df[lwd_df['Resort']               == p_resort]
        bergfex_df      = bergfex_df[bergfex_df['SourceID']     == p_resort]
        bergfex_meta    = bergfex_meta[bergfex_meta['SourceID'] == p_resort]

        if lwd_df.empty:
            raise Exception("Cant create proper Agent - LWD No Data for Date - " + str(d) +" - " + str(p_date) + "- " + p_resort)
        if bergfex_df.empty:
            raise Exception("Cant create proper Agent - Bergfex_df No Data for Date - " + str(d) +" - " + str(p_date) + "- " + p_resort)
        if bergfex_meta.empty:
            raise Exception("Cant create proper Agent - bergfex_meta No Data for Date - " + str(d) +" - " + str(p_date) + "- " + p_resort)

        




        ### BergFex_Meta #############################################################################################################
        self.__valley       = bergfex_meta['Vl'].iloc[0]
        self.__top          = bergfex_meta['Mt'].iloc[0]
  
        ### LWD Data ###############################################################################################################
        if p_date > today:
            self.actual_snowfall_24 = None
            self.actual_snowfall_48 = None
            self.actual_snowfall_72 = None
            self.actual_temp        = None
        else:
            grouped_df              = grouping(lwd_df, self.__valley)

            # Above mid Snow & Temp
            temp_df = grouped_df[grouped_df['Seehöhe Class'].str.contains("Above")]
            try:    self.__actual_temp                  = grouped_df['Temperature'].iloc[0]
            except: self.__actual_temp                  = None
            try:    self.__sea_level                    = grouped_df['Seehöhe'].iloc[0]
            except: self.__sea_level                    = None
            try:    self.__actual_snowfall_24           = temp_df['24h Differenz Schneehöhe'].iloc[0]
            except: self.__actual_snowfall_48           = None
            try:    self.__actual_snowfall_48           = temp_df['48h Differenz Schneehöhe'].iloc[0]
            except: self.__actual_snowfall_48           = None
            try:    self.__actual_snowfall_72           = temp_df['72h Differenz Schneehöhe'].iloc[0]
            except: self.__actual_snowfall_72           = None

            # Below mid Snow
            temp_df = grouped_df[grouped_df['Seehöhe Class'].str.contains("Below")]
            try:    self.__actual_temp_below            = grouped_df['Temperature'].iloc[0]
            except: self.__actual_temp_below            = None
            try:    self.__sea_level_below              = grouped_df['Seehöhe'].iloc[0]
            except: self.__sea_level_below              = None
            try:    self.__actual_snowfall_24_below     = temp_df['24h Differenz Schneehöhe'].iloc[0]
            except: self.__actual_snowfall_24_below     = None
            try:    self.__actual_snowfall_48_below     = temp_df['48h Differenz Schneehöhe'].iloc[0]
            except: self.__actual_snowfall_48_below     = None
            try:    self.__actual_snowfall_72_below     = temp_df['72h Differenz Schneehöhe'].iloc[0]
            except: self.__actual_snowfall_72_below     = None




        ### BergFex ######################################################################################################
        #
        try:
            oneday      = SnowForecast(bergfex_df, 1, p_date)
            twoday      = SnowForecast(bergfex_df, 1, p_date)
            threeday    = SnowForecast(bergfex_df, 1, p_date)


            self.__forecasted_snowfall_24                   = oneday[0][0]
            self.__forecasted_snowfall_48                   = twoday[0][0]
            self.__forecasted_snowfall_72                   = threeday[0][0]
            self.__forecasted_snowfall_24_below             = oneday[1][0]
            self.__forecasted_snowfall_48_below             = twoday[1][0]
            self.__forecasted_snowfall_72_below             = threeday[1][0]
        except: print("self.__forecasted_snowfall_24    Out of Range")



        temp_df                 = bergfex_df[bergfex_df['Date'].dt.date == p_date]

        self.__rain_probability = temp_df['Rain Probability'].iloc[0]
        self.__rain_volume      = temp_df['Rain volume'].iloc[0]
        self.__sun_hours        = int(temp_df['Sun Hours'].iloc[0])
        self.__temp_max_mt      = int(temp_df['tmax Mountain'].iloc[0])
        self.__temp_min_mt      = int(temp_df['tmin Mountain'].iloc[0])
        self.__temp_max_va      = int(temp_df['tmax Valley'].iloc[0])
        self.__temp_min_va      = int(temp_df['tmin Valley'].iloc[0])
        self.__wind             = int(temp_df['Wind'].iloc[0])
        self.__wind_direction   = temp_df['Wind Direction'].iloc[0]
        self.__snowline         = temp_df['Snowfall Border'].iloc[0]
        self.__rating           = None
           

        

        if p_resort == 'Stubaier Gletscher':
            try:
                print(p_date)
                print(stubai_df)
                stubai_df['date'] = pd.to_datetime(stubai_df['date'])
                if stubai_df['date'].dt.date .iloc[0] == p_date:
                    self.__actual_snowfall_24 = stubai_df['height'].iloc[0]
            except: 
                print('error in stubai snow')





        # Bergfex Meta



        ##### Getter ####

    def set_rating(self, rating ):
        self.get_rating = rating

    def get_weekday(self):
        return self.__weekday

    def get_user_resort(self):
        return self.__user_resort

    def get_time(self):
        return self.__time

    def get_actual_snowfall_24(self):
        return self.__actual_snowfall_24

    def get_actual_snowfall_48(self):
        return self.__actual_snowfall_48

    def get_actual_snowfall_72(self):
        return self.__actual_snowfall_72

    def get_actual_temp(self):
        return self.__actual_temp

    def get_sea_level(self):
        return self.__sea_level

    def get_actual_snowfall_24_below(self):
        return self.__actual_snowfall_24_below

    def get_actual_snowfall_48_below(self):
        return self.__actual_snowfall_48_below

    def get_actual_snowfall_72_below(self):
        return self.__actual_snowfall_72_below

    def get_actual_temp_below(self):
        return self.__actual_temp_below

    def get_sea_level_below(self):
        return self.__sea_level_below

    def get_forecasted_snowfall_24(self):
        return self.__forecasted_snowfall_24

    def get_forecasted_snowfall_48(self):
        return self.__forecasted_snowfall_48

    def get_forecasted_snowfall_72(self):
        return self.__forecasted_snowfall_72

    def get_forecasted_snowfall_24_below(self):
        return self.__forecasted_snowfall_24_below

    def get_forecasted_snowfall_48_below(self):
        return self.__forecasted_snowfall_48_below

    def get_forecasted_snowfall_72_below(self):
        return self.__forecasted_snowfall_72_below

    def get_rain_probability(self):
        return self.__rain_probability

    def get_rain_volume(self):
        return self.__rain_volume

    def get_sun_hours(self):
        return self.__sun_hours

    def get_temp_max_mt(self):
        return self.__temp_max_mt

    def get_temp_min_mt(self):
        return self.__temp_min_mt

    def get_temp_max_va(self):
        return self.__temp_max_va

    def get_temp_min_va(self):
        return self.__temp_min_va

    def get_wind(self):
        return self.__wind

    def get_wind_direction(self):
        return self.__wind_direction

    def get_snowline(self):
        return self.__snowline

    def get_valley(self):
        return self.__valley

    def get_top(self):
        return self.__top

    def get_rating(self):
        return self.__rating
    

def main():
    helper = Weather_Day_Resort(day = dt.now().date(), update = dt.now().date(), resort = "Stubaier Gletscher")



if __name__ == "__main__":
    main()