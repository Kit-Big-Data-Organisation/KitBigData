import pandas as pd

class Dataloader:

    """Initializes the DataLoader with a directory and filename."""

    def __init__(self , directory ,  filename):
        self.filename = filename
        self.directory = directory
        self.path = f"{directory}/{filename}"

    def read(self) : 

        """Reads CSV file from the specified path."""
        try:
            return pd.read_csv(self.path)
        except FileNotFoundError:
            print(f"File not found inside {self.path}")
            return None
    
    
    def preprocess_data(self):

        data = self.read()
        if data is not None:
            data.rename(columns = {'recipe_id' : 'id'} , inplace=True)
        return data
    
    def load(self):
        return self.preprocess_data()
    
    def add_year(self , data):
        if data is not None and 'submitted' in data.columns:
            data['year'] = data['submitted'].apply(lambda x : int(x[:4]))
        return data
        
    def merge_recipe_interaction(self , interaction_loader):
        data_recipes = self.load()
        interaction = interaction_loader.load()
        if data_recipes is not None and interaction is not None:
            merged_recipe_inter = pd.merge(data_recipes , interaction , how ='left' , on ='id')
            self.add_year(merged_recipe_inter)
            return merged_recipe_inter
    
    def processed_recipe_interaction(self , interaction_loader):
        data = self.merge_recipe_interaction(interaction_loader)
        return data.add_year()
    

