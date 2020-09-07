
class Categories:

    """
    Constructor for this class
    """
    def __init__(self,meal_cat_id=None,Pasta=None,Spicy=None,Rice=None,Noodles=None,Baked=None,
                 Pie=None,Vegetarian=None,One_pot=None,Cake=None,Casserole=None,Chocolate=None,
                 Curry=None,Gluten_Free=None,Fish=None,Meat=None):
        self.meal_cat_id = meal_cat_id
        self.Pasta = Pasta
        self.Spicy = Spicy
        self.Rice = Rice
        self.Noodles = Noodles
        self.Baked = Baked
        self.Pie = Pie
        self.Vegetarian = Vegetarian
        self.One_pot = One_pot
        self.Cake = Cake
        self.Casserole = Casserole
        self.Chocolate = Chocolate
        self.Curry = Curry
        self.Gluten_Free = Gluten_Free
        self.Fish = Fish
        self.Meat = Meat
        
    """
    Returns a list of strings where only the categories that are true are included
    """
    def get_categories_as_list(self):
        atts = [a for a in list(vars(self).keys()) if not a.startswith('__')]
        cats = []
        atts.remove('meal_cat_id')
        for x in range(len(atts)):
            if(getattr(self,atts[x])):
                cats.append(atts[x])
        return cats
        
        
    """
    Helper function for constructing categories from an array
    The array needs to be the following:
        1) Category ID
        2) Pasta
        3) Spicy
        4) Rice
        5) Noodles
        6) Baked
        7) Pie
        8) Vegetarian
        9) One pot
        10) Cake
        11) Casserole
        12) Chocolate
        13) Curry
        14) Gluten_Free
        15) Fish
        16) Meat
    """
    def construct_categories_for_recipe(row):
        new_categories = Categories()
        atts = [a for a in list(vars(new_categories).keys()) if not a.startswith('__')]
        for x in range(len(atts)):
            setattr(new_categories, atts[x],row[x]) 
        return new_categories
        
    """
    Function inorder to extract the information required from a website
    to create a new Categories object.
    Requires the request and its desired ID.
    """
    def create_categories_object_from_website(request,newID):
    
        categoriesArr = []
        categoriesArr.append(newID)
        categoriesArr.append(request.form.get('Pasta') is not None)
        categoriesArr.append(request.form.get('Spicy') is not None)
        categoriesArr.append(request.form.get('Rice') is not None)
        categoriesArr.append(request.form.get('Noodles') is not None)
        categoriesArr.append(request.form.get('Baking') is not None)
        categoriesArr.append(request.form.get('Pie') is not None)
        categoriesArr.append(request.form.get('Vegetarian') is not None)
        categoriesArr.append(request.form.get('One Pot') is not None)
        categoriesArr.append(request.form.get('Cake') is not None)
        categoriesArr.append(request.form.get('Casserole') is not None)
        categoriesArr.append(request.form.get('Chocolate') is not None)
        categoriesArr.append(request.form.get('Curry') is not None)
        categoriesArr.append(request.form.get('Gluten-Free') is not None)
        categoriesArr.append(request.form.get('Fish') is not None)
        categoriesArr.append(request.form.get('Meat') is not None)
        
        categories = Categories.construct_categories_for_recipe(categoriesArr)
        
        return categories
        
        
    """
    String representation for this class.
    """
    def __str__(self):
        return str(vars(self))
        
    """
    Function to get the number of attributes stored in the Categories object (because it might change)
    """
    def get_num_atts():
        new_categories = Categories()
        atts = [a for a in list(vars(new_categories).keys()) if not a.startswith('__')]
        return len(atts)