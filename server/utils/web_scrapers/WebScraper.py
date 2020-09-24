import urllib.request as requests
from bs4 import BeautifulSoup
import re
import traceback

class WebScraper:
    
    """
    Constructor for this class.
    """
    def __init__(self):
        pass
        
    """
    Function to extract the details of a recipe from the BBC good food's website.
    """
    def get_recipe_details_from_url(self,url):
        # Construct BeautifulSoup object
        HTMLstring = requests.urlopen(url).read()
        soup = BeautifulSoup(HTMLstring, features="html.parser")
        title = WebScraper._get_title(soup)
        cooking_time = WebScraper._get_cooking_time(soup)
        difficulty = WebScraper._get_difficulty(soup)
        print(difficulty)
        
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
    On BBC good food its either Easy or More effort.
    """
    def _get_difficulty(soup):
        pass