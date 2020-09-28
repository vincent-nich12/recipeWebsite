import urllib.request as requests
from bs4 import BeautifulSoup
import re
import traceback
from utils.models.recipe import Recipe

class WebScraper:
    
    """
    Constructor for this class.
    """
    def __init__(self):
        pass
        
    """
    Function to extract the details of a recipe from the BBC good food's website.
    Returns a Recipe object.
    """
    def get_recipe_from_url(self,url):
        # Construct BeautifulSoup object
        HTMLstring = requests.urlopen(url).read()
        soup = BeautifulSoup(HTMLstring, features="html.parser")
        details = []
        details.append(WebScraper._get_title(soup))
        cooking_time_tuple = WebScraper._get_cooking_time(soup)
        if cooking_time_tuple is None:
            details.append(None)
            details.append(None)
        else:
            details.append(cooking_time_tuple[0])
            details.append(cooking_time_tuple[1])
        details.append(WebScraper._get_difficulty(soup))
        details.append(WebScraper._get_num_servings(soup))
        details.append(WebScraper._get_ingredients(soup))
        details.append(WebScraper._get_method(soup))
        details.append(WebScraper._get_notes(soup))
        # Convert to a Recipe object
        recipe = Recipe(recipe_name=details[0],hours=details[1],minutes=details[2],skill_level=details[3],
                        servings=details[4],ingredients=details[5],method=details[6],notes=details[7])
        #print(recipe)
        return recipe
        
    """
    Private function for getting the title of a recipe in BBC good food.
    Returns None if it cannot find the title of the recipe.
    """
    def _get_title(soup):
        try:
            headers = soup.findAll("h1", {"class": "masthead__title heading-1"})
            return headers[0].getText()
        except:
            return None
        
    """
    Private function for getting the cooking time of a recipe in BBC good food.
    Returned as a tuple - (num hrs, num mins)
    Returns none if it cannot extract the cooking time.
    """
    def _get_cooking_time(soup):
        try:
            #Get the first time given (usually prep)
            lis = soup.findAll("li", {"class": "body-copy-small list-item"})
            children = lis[0].findChildren("span", recursive=False)
            firstTimeString = children[1].findChildren("time", recursive=False)[0].getText()
            if len(lis) > 1:
                #Get the second time (usually cooking time)
                children = lis[1].findChildren("span", recursive=False)
                secondTimeString = children[1].findChildren("time", recursive=False)[0].getText()
                hrsFirst = WebScraper._get_hrs_from_string(firstTimeString)
                minsFirst = WebScraper._get_mins_from_string(firstTimeString)
                hrsSecond = WebScraper._get_hrs_from_string(secondTimeString)
                minsSecond = WebScraper._get_mins_from_string(secondTimeString)
                return (hrsFirst+hrsSecond, minsFirst+minsSecond)
            else:
                #Incase it only has one time given
                hrs = WebScraper._get_hrs_from_string(firstTimeString)
                mins = WebScraper._get_mins_from_string(firstTimeString)
                return (hrs,mins)
        except Exception as e:
            #traceback.print_exc()
            return None
        
    """
    Private function used to extract the number of hours in a string.
    Returns None if the string doesn't contain 'hrs'.
    """
    def _get_hrs_from_string(string):
        hrs = re.findall("[0-9]+ hrs", string)
        if len(hrs) == 0:
            return 0
        else:
            hrsInt = int(hrs[0].replace('hrs', ''))
            return hrsInt
    
    """
    Private function used to extract the number of minutes in a string.
    Returns 0 if the string doesn't contain 'mins'.
    """
    def _get_mins_from_string(string):
        mins = re.findall("[0-9]+ mins", string)
        if len(mins) == 0:
            return 0
        else:
            minsInt = int(mins[0].replace('mins', ''))
            return minsInt
    
    """
    Private function used to extract the difficulty of the recipe.
    On BBC good food its either Easy or More effort (converted to 'Medium').
    Returns None if it cannot extract the difficulty.
    """
    def _get_difficulty(soup):
        try:
            divs = soup.findAll("div", {"class": "icon-with-text__children"})
            text = divs[1].getText()
            if text == "More effort":
                return "Medium"
            return text
        except:
            return None
            
    """
    Private function used to extract the number of servings of the recipe.
    Returns None if it cannot extract the number of servings.
    """
    def _get_num_servings(soup):
        try:
            divs = soup.findAll("div", {"class": "icon-with-text__children"})
            text = divs[2].getText()
            servings = re.findall("[0-9]+", text)
            return int(servings[0])
        except:
            return None
        
    """
    Private function used to extract the ingredients of the recipe.
    Returns None if it cannot extract the ingredients.
    """
    def _get_ingredients(soup):
        try:
            ingredientsWhole = soup.findAll("section", {"class": "recipe-template__ingredients col-12 mt-md col-lg-6"})[0]
            children = ingredientsWhole.findChildren("section", recursive=False)
            ingredients = []
            for child in children:
                ul = child.findChildren("ul", recursive=False)[0]
                for li in ul.findAll('li'):
                    ingredients.append(li.getText())
            # Convert the ingredients array into a string        
            stringRep = ""
            count = 0
            for x in ingredients:
                if count < (len(ingredients) - 1):
                    stringRep = stringRep + x + "\n"
                else:
                    stringRep = stringRep + x
                count += 1
            return stringRep
        except:
            return None
        
    """
    Private function used to extract the method of the recipe.
    Returns None if it cannot extract the method.
    """    
    def _get_method(soup):
        try:
            ul = soup.findAll("ul", {"class": "grouped-list__list list"})[0]
            method = []
            for li in ul.findAll('li'):
                text = li.getText()
                #Remove STEP number in text
                text = re.sub('STEP [0-9]+', '', text)
                method.append(text)
            # Convert the methods array into a string        
            stringRep = ""
            count = 0
            for x in method:
                if count < (len(method) - 1):
                    stringRep = stringRep + x + "\n"
                else:
                    stringRep = stringRep + x
                count += 1
            return stringRep
        except:
            return None
    
    """
    Private function used to extract the notes of the recipe.
    Returns None if it cannot extract the notes.
    """
    def _get_notes(soup):
        try:
            div = soup.findAll("div", {"class": "editor-content"})[0]
            p = div.findChildren("p", recursive=False)[0]
            return p.getText()
        except:
            return None