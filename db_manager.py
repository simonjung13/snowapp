import pandas as pd
import datetime
from datetime import timedelta
import os




def checkFile(path):
    file_path = path
    if os.path.exists(file_path):
        return True
    else:
        print("File not found: " + path)
        return False
    
    
def getLastUpdate(df):

    out = None
    temp_df = df
    update_time = temp_df['Stored'].iloc[0]
    
    date_format = "%Y-%m-%d %H:%M:%S"
    date_object = datetime.datetime.strptime(update_time, date_format)   
    return date_object


def getLastUpdate(df):
    update_time = df['Stored'].iloc[0]

    # Check if 'Stored' column is already in datetime format
    if isinstance(update_time, pd.Timestamp):
        return update_time
    else:
        # Convert the 'Stored' column to datetime format
        df['Stored'] = pd.to_datetime(df['Stored'])
        return df['Stored'].iloc[0]




class DatabaseManager:

    def __init__(self, path = "C:/Users/jungs/Documents/Git/snowapp-1/.gitignore/Database/"):
        self.logger = ""
        self.path = path

    def saveData(self, df, name):
        today = datetime.datetime.now().replace(second=0, microsecond=0) 
        df['Stored'] = today
        path = self.path + name + ".csv"
        df.to_csv(path, sep=',')
    
    
    
    def saveData_nightrun(self, df, name):
        if name not in ['bergfex', 'bergfex_meta', 'lwd', 'stubai']:
            raise Exception ("Wrong name")
        today = datetime.datetime.now().date()
        yesterday= today - timedelta(days = 1)
        store_date = today
        if name == 'lwd':
            store_date = yesterday
        
        temp_df = df
        temp_df['Stored'] = store_date
        path = self.path + name + "_history.csv" 
        if checkFile(path ):
            old                 = pd.read_csv(path, sep=',')
            old['Stored']       = pd.to_datetime(old['Stored'], errors='coerce')
            old_without_today   = old[old['Stored'].dt.date < store_date]

            cols = temp_df.columns
            old_without_today_df = old_without_today[cols]
            old_without_today_df = old_without_today_df.copy()
            old_without_today_df.to_csv(self.path + "old_temp.csv" , sep=',')
            old_df =        pd.read_csv(self.path + "old_temp.csv" , sep=',')
            # Reset indices

            # Concatenate DataFrames
            frames = [old_df, temp_df]
            out = pd.concat(frames)
            
            out = out[cols]
            out.to_csv(path, sep=',')
        else:
            temp_df.to_csv(path, sep=',')
            print("New File created - " + path)
        


    def loadData(self, name):
        try:
            temp_path = self.path + name + ".csv"
            df = pd.read_csv(temp_path, sep=',')
            self.logger += str(datetime.datetime.now()) +  " - Loaded: " + temp_path + "\n"
            return df
        except:
            self.logger += "ERROR: " + str(datetime.datetime.now()) +  " - Could not load: " + temp_path + "\n"
            return None
        
    
    def getLastUpdate(self):
        try:
            list = ['bergfex', 'bergfex_meta', 'lwd']
            out = None
            for i in list:
                temp_df = self.loadData(i)
                update_time = temp_df['Stored'].iloc[0]
                date_format = "%Y-%m-%d %H:%M:%S.%f"
                date_object = datetime.datetime.strptime(update_time, date_format)   
                if out:
                    if date_object<out:
                        out=date_object
                else:
                    out = date_object
            return date_object
        except:
            return None

    