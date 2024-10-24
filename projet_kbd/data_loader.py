import pandas as pd

class Dataloader:

    def __init__(self , filename):
        self.filename = filename
        self.path = "/Users/user/Desktop/KBD Project/KitBigData/Data/"+filename

    def read(self) : 
        return pd.read_csv(self.path)
    
    def preprocess_data(self):

        data = self.read()

        if 'date' in data.columns:
            data['year'] = data['date'].apply(lambda x : x[:4])

        if 'submitted' in data.columns :
            data['year'] = data['submitted'].apply(lambda x : int(x[:4]))

        return data

    def loader(self):
        return self.preprocess_data()

    


