import utils
import pandas as pd


class Dataloader:
    """Initializes the DataLoader with a directory and filename."""

    def __init__(self, directory, filename):
        self.filename = filename
        self.directory = directory
        self.path = f"{directory}/{filename}"

    def read(self):
        """Reads CSV file from the specified path."""
        try:
            return pd.read_csv(self.path)
        except FileNotFoundError:
            print(f"File not found inside {self.path}")
            return None

    def preprocess_data(self):

        data = self.read()
        if data is not None:
            data.rename(columns={"recipe_id": "id"}, inplace=True)
        return data

    def load(self):
        return self.preprocess_data()

    def add_year(self, data):
        if data is not None and "submitted" in data.columns:
            data["year"] = data["submitted"].apply(lambda x: int(x[:4]))
        return data

    def merge_recipe_interaction(self, interaction_loader):

        data_recipes = self.load()
        interaction = interaction_loader.load()
        if data_recipes is not None and interaction is not None:
            merged_recipe_inter = pd.merge(
                data_recipes, interaction, how="left", on="id"
            )
            self.add_year(merged_recipe_inter)
            return merged_recipe_inter

    def adding_nutrition(self, data):

        NutriList = ["cal", "totalFat", "sugar", "sodium", "protein", "satFat", "carbs"]
        nutrition_df = pd.DataFrame(
            data["nutrition"].apply(eval).tolist(), columns=NutriList
        )
        merged_recipe_inter = pd.concat([data, nutrition_df], axis=1)
        return merged_recipe_inter

    def adding_cuisines(self, data):
        data["cuisine"] = data["tags"].apply(utils.determine_cuisine)
        return data

    def processed_recipe_interaction(self, interaction_loader):
        return (
            self.merge_recipe_interaction(interaction_loader)
            .pipe(self.add_year)
            .pipe(self.adding_cuisines)
            .pipe(self.adding_nutrition)
        )
