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

def contains_any_tag(tag_string, target_tags):
            try:
                # Safely evaluate the string to a list
                tags_list = ast.literal_eval(tag_string)
                # Check if any target tag is in the list of tags
                return any(tag in target_tags for tag in tags_list)
            except:
                # In case of any error during evaluation, return False
                return False