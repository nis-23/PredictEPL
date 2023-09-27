import pandas as pd 

import numpy as np 
import seaborn as sns 
import matplotlib.pyplot as plt 
from sklearn.preprocessing import StandardScaler





class CleanDataset():
    
    def __init__(self,raw_data):
        
        self.raw_data = raw_data.copy()
        
        
        
    
    def drop_uninformative_columns(self, raw_data):
        
        raw_data.drop(['comp', 'match report', 'attendance', 'notes', 'Unnamed: 0','round', 'referee', 'captain'], axis = 1, inplace = True)
        return raw_data

    
    
    def make_datetime_columns(self, raw_data):
        
        import datetime
        from datetime import date, time 
        
        raw_data['date'] = pd.to_datetime(raw_data.date).dt.date
        raw_data['time'] = pd.to_datetime(raw_data.time).dt.time
        raw_data['datetime'] = raw_data.apply(lambda r : pd.datetime.combine(r['date'],r['time']),1)
        raw_data['hour'] = raw_data.datetime.apply(lambda x: x.hour)
        
        
        return raw_data 
    
    
    
    
    def label_categoricals(self, raw_data):
        
        from sklearn.preprocessing import LabelEncoder
        
        encoder = LabelEncoder()
        
        raw_data.venue = encoder.fit_transform(raw_data.venue)
        raw_data.day = encoder.fit_transform(raw_data.day)
        raw_data.formation = encoder.fit_transform(raw_data.formation)
        raw_data.result = encoder.fit_transform(raw_data.result)
        
        
        return raw_data
    
    
    def main(self):
        
    
        from functools import reduce 
        
        obj = CleanDataset(self.raw_data)
        function_list = [getattr(obj, method) for method in dir(obj) if callable(getattr(obj, method)) and not method.startswith("__") and method != 'main']

        
        cleaned_data = reduce(lambda data, func: func(data), function_list, self.raw_data)
        
        return cleaned_data


        
    

class FeatureAddition():
    
    
    def __init__(self, cleaned_data):
        
        
        self.cleaned_data = cleaned_data.copy()
    
    
    def add_target(self, cleaned_data):
        
        cleaned_data['target'] = cleaned_data.result.apply(lambda x: 1 if x < 2 else 0)
        
        return cleaned_data
    
    
    def add_opp_code(self, cleaned_data):
        
        from sklearn.preprocessing import LabelEncoder
        
        encoder = LabelEncoder()
        
        cleaned_data['opp_code'] = encoder.fit_transform(cleaned_data.opponent)
        
        return cleaned_data
    
    
    def add_rolling_averages(self, cleaned_data):
        
        cols = ["gf","ga","sh","sot","dist","fk","pk","pkatt", "xg", "xga"]
        new_cols = [f"{c}_rolling" for c in cols ]

        def get_rolling_avg(col, new_cols, group):
            
            group = group.sort_values('date')
            rolling_stats = group[cols].rolling(3, closed = 'left').mean()
            group[new_cols] = rolling_stats
            group = group.dropna(subset = new_cols)
            
            return group


        cleaned_data_rolling  = cleaned_data.groupby('team').apply(lambda x: get_rolling_avg(cols, new_cols,x))
        cleaned_data_rolling = cleaned_data_rolling.droplevel('team')

        cleaned_data_rolling.index = range(cleaned_data_rolling.index.shape[0])


        cleaned_data_rolling.columns

        cleaned_data_rolling.drop(cols, axis=1, inplace = True)
        
        
        cleaned_data_rolling['pkr'] = cleaned_data_rolling['pk_rolling']/cleaned_data_rolling['pkatt_rolling']
        cleaned_data_rolling['skr'] = cleaned_data_rolling['sot_rolling']/cleaned_data_rolling['sh_rolling']
        
        
        
        return cleaned_data_rolling
    
    
    

    
    def main(self):
        
        from functools import reduce 
        
        obj = FeatureAddition(self.cleaned_data)
        function_list = [getattr(obj, method) for method in dir(obj) if callable(getattr(obj, method)) and not method.startswith("__") and method != 'main']

        
        processed_data = reduce(lambda data, func: func(data), function_list, self.cleaned_data)
        
        return processed_data
    
    
    
    
def main(raw_data):
    
    DataCleaner = CleanDataset(raw_data)
    cleaned_data = DataCleaner.main()
    DataTransformer = FeatureAddition(cleaned_data)
    
    procesed_data = DataTransformer.main()
    
    return procesed_data




def standardize_data(processed_data):
    
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(processed_data)
    X = pd.DataFrame(X_scaled)
    
    return X 
        
        
       
    

    
    
        
        
        
    
        
    