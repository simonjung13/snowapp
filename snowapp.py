#snowapp
from datetime import datetime as dt, timedelta, date
import pandas as pd
import pywhatkit as kit
from Weather_Day_Region import Weather_Day_Resort
from Caller import url_caller
from utils import getWeekday
from pywhatkit import whats  

pd.set_option('mode.chained_assignment', None)
today = dt.now().date()
tomorrow = today + timedelta (days = 1)
yesterday = today - timedelta (days = 1)
weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def map_value_to_rating(value, value_min, value_max, rating_min, rating_max):
    # Ensure value is within the specified range
    clamped_value = max(value_min, min(value_max, value))
    
    # Map the clamped value to the rating range
    rating = ((clamped_value - value_min) / (value_max - value_min)) * (rating_max - rating_min) + rating_min
    
    return max(rating_min, min(rating_max, rating))


def map_value_to_rating_reverse(value, value_min, value_max, rating_min, rating_max):
    # Ensure value is within the specified range
    clamped_value = max(value_min, min(value_max, value))
    
    # Map the clamped value to the reversed rating range
    rating = ((clamped_value - value_min) / (value_max - value_min)) * (rating_min - rating_max) + rating_max
    
    return max(rating_min, min(rating_max, rating))




class Snowapp:
    powder_alert = 20
    info = ""
    test = False
    agent_list = []
    resort_url_list = []

    def __init__(self, resort_url_list, powder_alert = 10, Test = False):

        self.resort_url_list = resort_url_list
        self.powder_alert = powder_alert
        self.test = Test
        self.url_caller_helper = url_caller(resort_url_list)

    
    def fetchData(self):
        if self.test:
            print("Test Mode On")
        else:
            self.url_caller_helper.update()

    def fetchData_nightrun(self):
        if self.test:
            print("Test Mode On")
        else:
            self.url_caller_helper.night_run_update()
                
    def createAllAgent(self, day):
        for resort, url in self.resort_url_list:
            self.agent_list.append([resort, day, today, Weather_Day_Resort(p_date=day , p_resort = resort)])

    def createAgent(self, p_resort, p_day):
        #Cgeck if agente already exist
        for r, d, a  in self.agent_list:
            if r == p_resort and d == p_day:
                return a

        temp_agent = Weather_Day_Resort(p_date=p_day , p_resort = p_resort)
        self.agent_list.append([p_resort, p_day,  temp_agent])

        return temp_agent

    def getAgent(self, p_resort, p_day):
        temp_list = self.agent_list

        for r, d, a in temp_list:
            if r == p_resort and d == p_day:
                return a
            
    def getRating_today(self, p_resort):
        a_yesterday = self.createAgent(p_resort= p_resort, p_day= yesterday)
        a_today = self.createAgent(p_resort= p_resort, p_day= today)

        sun = a_today.get_sun_hours()
        tmin = a_today.get_temp_min_mt()
        tmax = a_today.get_temp_max_mt()
        wind = a_today.get_wind()
        newsnow_today = a_today.get_actual_snowfall_24() 
        newsnow_yesterday = a_yesterday.get_actual_snowfall_24() 
        wind_yesterday = a_yesterday.get_wind()
        avy = a_today.getAvy()

        sun_good, sun_bad = 0, 10
        tmin_bad = -15
        tmax_bad = -2
        wind_min, wind_max = 7, 0

        #snow_rating

    def prepareAgents(self):
        temp_list_today = []
        temp_list_tomorrow = []
        for resort, url in self.resort_url_list:
            temp_agent_today = self.createAgent(resort, today)
            temp_agent_tomorrow = self.createAgent(resort, tomorrow)
            temp_list_today.append([resort, temp_agent_today])
            temp_list_tomorrow.append([resort, temp_agent_tomorrow])
        return(temp_list_today, temp_list_tomorrow)


   
    def powderAlert(self):
        temp_list = self.prepareAgents()[0]
        powder_list = []
        for r, a in temp_list:
            if a.get_forecasted_snowfall_48() > self.powderAlert:
                powder_list.append([r, a])
        return powder_list


    def getRating_future(self, p_resort, days):
        if days < 1 or days > 3:
            raise Exception("must be in the fututre")
        
        prog_day = today + timedelta(days=days)
        day_before = today + timedelta(days=days-1) #Bei einem Tag heute
        days_before_2 = today + timedelta(days=days-2) #Bei zwei tagen Heute 
        days_before_3 = today + timedelta(days=days-3) #Bei drei tagen Heute 
        


        a_prog_day = self.createAgent(p_resort= p_resort, p_day= prog_day)
        a_before = self.createAgent(p_resort= p_resort, p_day= day_before)
        #a_days_before_2 = self.createAgent(p_resort= p_resort, p_day= days_before_2, p_update= today)
        #a_days_before_2 = self.createAgent(p_resort= p_resort, p_day= days_before_2, p_update= days_before_3)

        sun_before = a_before.get_sun_hours()
        tmin_before = a_before.get_temp_min_mt()
        tmax_before = a_before.get_temp_max_mt()
        wind_before = a_before.get_wind()
        if day_before == today:
            newsnow_before = a_before.get_actual_snowfall_24() 
        else:
            newsnow_before = a_before.get_forecasted_snowfall_24()

        if days == 2:
            newsnow_before = a_before.get_forecasted_snowfall_48()

        if days == 3:
            newsnow_before = a_before.get_forecasted_snowfall_72()

        sun_future = a_prog_day.get_sun_hours()
        tmin_future = a_prog_day.get_temp_min_mt()
        tmax_future = a_prog_day.get_temp_max_mt()
        wind_future = a_prog_day.get_wind()

        
        snow_min, snow_max = -2, 30
        sun_bad, sun_good = 0, 8
        tmin_bad = -15
        tmax_bad = -2
        wind_min, wind_max = 0, 7

        snow_rating = map_value_to_rating(newsnow_before, snow_min, snow_max, 0, 10)
        vision_rating = map_value_to_rating(sun_future, sun_bad, sun_good, 0, 10)
        avy = map_value_to_rating(wind_before, wind_min, wind_max, 0, 5)
        snow = snow_rating - avy

        rating = (snow_rating + vision_rating) / 20 *10
        rating = str(round(rating,1))
        if avy > 4:
            rating += "/10 \nSnow most likely affected"
            return rating
        if avy > 2:
            rating += "/10 \nSnow may be wind affected"
            return rating
        return rating
    

    def calculate_rating(self, p_resort, p_date: date):
        days_difference = (p_date - today).days
        if days_difference > 7 or days_difference <= 0:
            raise Exception("Date not valid")
        
        prog_day    =   p_date
        days_prior1 =   p_date   - timedelta(days= 1) 
        days_prior2 =   p_date   - timedelta(days= 2) 
        days_prior3 =   p_date   - timedelta(days= 3) 
        


        a_prog_day      = self.createAgent(p_resort= p_resort, p_day= prog_day,     p_update= today)
        a_days_prior1   = self.createAgent(p_resort= p_resort, p_day= days_prior1,  p_update= today)
        a_days_prior2   = self.createAgent(p_resort= p_resort, p_day= days_prior2,  p_update= today)
        a_days_prior3   = self.createAgent(p_resort= p_resort, p_day= days_prior3,  p_update= today)

        sun_before = a_before.get_sun_hours()
        tmin_before = a_before.get_temp_min_mt()
        tmax_before = a_before.get_temp_max_mt()
        wind_before = a_before.get_wind()
        if day_before == today:
            newsnow_before = a_before.get_actual_snowfall_24() 
        else:
            newsnow_before = a_before.get_forecasted_snowfall_24()

        if days == 2:
            newsnow_before = a_before.get_forecasted_snowfall_48()

        if days == 3:
            newsnow_before = a_before.get_forecasted_snowfall_72()

        sun_future = a_prog_day.get_sun_hours()
        tmin_future = a_prog_day.get_temp_min_mt()
        tmax_future = a_prog_day.get_temp_max_mt()
        wind_future = a_prog_day.get_wind()

        
        snow_min, snow_max = -2, 30
        sun_bad, sun_good = 0, 8
        tmin_bad = -15
        tmax_bad = -2
        wind_min, wind_max = 0, 7

        snow_rating = map_value_to_rating(newsnow_before, snow_min, snow_max, 0, 10)
        vision_rating = map_value_to_rating(sun_future, sun_bad, sun_good, 0, 10)
        avy = map_value_to_rating(wind_before, wind_min, wind_max, 0, 5)
        snow = snow_rating - avy

        rating = (snow_rating + vision_rating) / 20 *10
        rating = str(round(rating,1))
        if avy > 4:
            rating += "/10 \nSnow most likely affected"
            return rating
        if avy > 2:
            rating += "/10 \nSnow may be wind affected"
            return rating
        return rating
        

    def getEveningMsg(self, p_resort):
        a_today = self.createAgent(p_resort= p_resort, p_day= today)
        a_tomorrow = self.createAgent(p_resort= p_resort, p_day= tomorrow)

        sun = a_tomorrow.get_sun_hours()
        tmin = a_tomorrow.get_temp_min_mt()
        tmax = a_tomorrow.get_temp_max_mt()
        wind = a_tomorrow.get_wind()
        val = a_today.get_valley() 
        newsnow_above = a_today.get_actual_snowfall_24() 
        prog_snow = a_tomorrow.get_forecasted_snowfall_24()

        rating = self.getRating_future(p_resort, 1)
        

        if wind > 5:
            wmsg = "Stormy"
        elif wind > 3:
            wmsg = "Strong"
        elif wind > 1:
            wmsg = "Moderate"
        else: wmsg = "No wind"

        msg = "\n*" + p_resort + ":*\n"
        msg += "Powder rating: " + rating + "\n" 
        if newsnow_above > 15:
            msg += "New Snow @ " + str(val) +"m: " + str(newsnow_above) +  "cm\n" 
        else:
            msg += "New Snow @ " + str(val) +"m: *" + str(newsnow_above) +  "*cm\n" 
        msg += "Forecasted Snow (24h): " + str(prog_snow) +  "cm\n" 
        msg += "Sun hours: " + str(sun) + "h\n" 
        msg += "Temp (min/max): " + str(tmin) +"°C / " + str(tmax) + "°C\n"
        msg += "Wind: " + wmsg
        
        out = msg
        return out
    

    def getMorningMsg(self, p_resort):
        msg = ""
        a_today = self.createAgent(p_resort= p_resort, p_day= today)

        sun = a_today.get_sun_hours()
        tmin = a_today.get_temp_min_mt()
        tmax = a_today.get_temp_max_mt()
        wind = a_today.get_wind()
        val = a_today.get_valley() 
        newsnow_above = a_today.get_actual_snowfall_24() 
        prog_snow = a_today.get_forecasted_snowfall_24()

        

        if wind > 5:
            wmsg = "Stormy"
        elif wind > 3:
            wmsg = "Strong"
        elif wind > 1:
            wmsg = "Moderate"
        else: wmsg = "No wind"


        msg += "-----------------"
        msg = "\n*" + p_resort + ":*\n"
        msg += "New Snow @ " + str(val) +"m: " + str(newsnow_above) +  "cm\n" 
        msg += "Forecasted Snow (24h): " + str(prog_snow) +  "cm\n" 
        msg += "Today will have " + str(sun) + " hours of sun,\n" 
        msg += "Temperatures between " + str(tmin) +"°C and " + str(tmax) + "°C\n"
        msg += "And the Wind will be " + wmsg

        return msg
    


       
    def MorningCall(self):
        day_list = self.prepareAgents()[0]
        msg = "*Snow Report* last 24h | 48h\n"
        for r, a in day_list:
            last24 = str(a.get_actual_snowfall_24())
           # temp_a = self.createAgent(r, yesterday)
            day_before = "hi" #str(temp_a.get_actual_snowfall_24())
            msg += r + ": " + last24 + "cm | " + day_before +"cm \n"
        msg += "-----------------"
        msg += self.getMorningMsg("Stubaier Gletscher")
        self.info = msg

    def EveningCall(self):
        day_list = self.prepareAgents()[0]
        msg = ""    

        pow_msg = "*Powder incoming*\nTomorrow" +  "|" +  getWeekday(tomorrow) + "|" + getWeekday(tomorrow + timedelta(days = 1)) + " \n"
        pow = False
        for r, a in day_list:
            if a.get_forecasted_snowfall_72() > self.powder_alert:
                a_tomorrow = self.createAgent(p_resort= r, p_day= tomorrow)
                a_tomorrow2 = self.createAgent(p_resort= r, p_day= tomorrow + timedelta(days = 1))
                a_tomorrow3 = self.createAgent(p_resort= r, p_day= tomorrow + timedelta(days = 2))
                snow_tomorrow = a_tomorrow.get_forecasted_snowfall_24()
                snow_tomorrow2 = a_tomorrow2.get_forecasted_snowfall_24()
                snow_tomorrow3 = a_tomorrow3.get_forecasted_snowfall_24()
                pow =True
                pow_msg += r + ": " + str(snow_tomorrow) + "cm | " + str(snow_tomorrow2) + "cm | " + str(snow_tomorrow3) + "cm\n"
        if pow:
            msg += pow_msg
        msg += self.getEveningMsg("Stubaier Gletscher")
        self.info = msg



    def GetThreeDaysRating(self, resort):
        print(self.getRating_future(resort, 1))
        #print(self.getRating_future(resort, 2))
        #print(self.getRating_future(resort, 3))
        


        
    def sendInfo(self):
        #phone_number = "+491629374795" #maxl
        phone_number = "+4915124212943" # simon
        #phone_number = "+4915156118412" # julia
        #phone_number = "+4916099695553" # Marie
        
        msg =  self.info + "\n\nxoxo Simon's Snow Report"

        if self.test:
            print (msg)
            #whats.sendwhatmsg_instantly_channel(phone_number, msg, 30)

        else:
            kit.sendwhatmsg_instantly(phone_number, msg, 30)
            #kit.sendwhatmsg_instantly_channel(phone_number, msg, 30)





