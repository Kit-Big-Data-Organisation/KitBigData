def determine_cuisine(tags):
        """
        Determines the cuisine of a recipe based on tags.
        
        Parameters:
            tags (list of str): The tags associated with a recipe.
        
        Returns:
            str: The determined cuisine, or 'other' if no cuisine matches.
        """
        cuisines = {
            'asian': 0,
            'mexican': 0,
            'italian': 0,
            'african': 0,
            'american': 0,
            'french': 0,
            'greek': 0,
            'indian': 0
        }

    
        for cuisine in cuisines.keys():
            if cuisine in tags:
                return cuisine
        return 'other'