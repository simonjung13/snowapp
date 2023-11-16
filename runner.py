from snowapp import Snowapp
from datetime import datetime as dt
from datetime import timedelta
from db_manager import DatabaseManager

# Evt Stationen hier mit rein ["Dresdner Hütte", "Eissee", "Schaulfeljoch",  "Rotadel"]
resort_url_list = [
        ['Stubaier Gletscher',  'https://www.bergfex.at/stubaier-gletscher/wetter/prognose/', ] 
        #,['St.Anton',          'https://www.bergfex.at/stanton-stchristoph/wetter/prognose/']
        ,['Axamer Lizum',       'https://www.bergfex.at/axamer-lizum/wetter/prognose/']
        ,['Kühtai',             'https://www.bergfex.at/kuehtai/wetter/prognose/']
        ,['Nordkette',          'https://www.bergfex.at/innsbruck-nordkette/wetter/prognose/']
        #,['Seefeld',           'https://www.bergfex.at/seefeld-tirol/wetter/prognose/']
        #,['Sölden',            'https://www.bergfex.at/soelden/wetter/prognose/']
        ,['Hintertux',         'https://www.bergfex.at/hintertux/wetter/prognose/']
    ]

class runner:

    def __init__(self):
        print("\n\n\n")
        self.snowapp_helper = Snowapp(resort_url_list= resort_url_list, powder_alert = 30, Test = False)

    def run_00(self):  
        self.snowapp_helper.fetchData_nightrun()


    def run_06(self):  
        self.snowapp_helper.fetchData()
        self.snowapp_helper.MorningCall()
        self.snowapp_helper.sendInfo()
        

    def run_18(self):
        self.snowapp_helper.fetchData()
        self.snowapp_helper.EveningCall()
        self.snowapp_helper.sendInfo()

 
def main():
    db = DatabaseManager()
    helper = runner()
    helper.run_06()






if __name__ == "__main__":
    main()