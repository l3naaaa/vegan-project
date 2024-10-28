# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, redirect, url_for
from flask_login import login_required , current_user
from jinja2 import TemplateNotFound
import json
import requests

# define a function 
def get_places():

  vegan_places = []
  new_lat = 52.3555
  new_lon = 1.1743  
  url = "https://api.foursquare.com/v3/places/search"
  headers = {"accept": "application/json", "Authorization": "fsq34A3b2OgLGnmBOkOV9SZJp5MB8o+Ah2nmbP2Gth/Pa0k="}

  # Loop until 10 vegan places are found
  while len(vegan_places) < 15:
      # Calculate new latitude and longitude with a small offset
      offset = 0.1
      new_lat = new_lat + offset
      new_lon = new_lon + offset

      # Add parameters for the new coordinates
      params = {
          'll': f'{new_lat},{new_lon}',
          'radius': 100000
      }

      # Make API request
      response = requests.get(url, headers=headers, params=params)
      json_list = json.loads(response.text)

      # Process the response and add vegan places to the list
      for item in json_list.get('results', []):
          for cat in item.get('categories', []):
              if cat['id'] >= 13000  and cat['id'] <= 13390: # filter dinning and drinking 
                  vegan_places.append(item)
                  break
  return vegan_places

def get_details_for_a_place(fsq_id):

    url = f"https://api.foursquare.com/v3/places/{fsq_id}"
    headers = {"accept": "application/json" , "Authorization": "fsq34A3b2OgLGnmBOkOV9SZJp5MB8o+Ah2nmbP2Gth/Pa0k=" }

    params = {
        'fsq_id':fsq_id
    }
    response = requests.get(url, headers=headers)
    place_info = json.loads(response.text)
    print(place_info['name'])
    try:
        desc = place_info['location']['address']
    except:
        desc = "A Nice Place to eat !"
    return place_info['name'], desc

def get_images_for_food(fsq_id):

    url = f"https://api.foursquare.com/v3/places/{fsq_id}/photos"
    headers = {"accept": "application/json" , "Authorization": "fsq34A3b2OgLGnmBOkOV9SZJp5MB8o+Ah2nmbP2Gth/Pa0k=" }
    params = {
        'fsq_id':fsq_id,
        'classifications':'food'
    }
    response = requests.get(url, headers=headers,  params=params)
    print(response.text)
    json_list = json.loads(response.text)
    img_list = []
    for item in json_list:
        img_list.append(f"{item['prefix']}original{item['suffix']}")  
        break
    return img_list

def get_images_for_a_place(fsq_id):

    url = f"https://api.foursquare.com/v3/places/{fsq_id}/photos"
    headers = {"accept": "application/json" , "Authorization": "fsq34A3b2OgLGnmBOkOV9SZJp5MB8o+Ah2nmbP2Gth/Pa0k=" }
    params = {
        'fsq_id':fsq_id,
        'classifications':'outdoor'
    }
    response = requests.get(url, headers=headers,  params=params)
    print(response.text)
    json_list = json.loads(response.text)
    img_list = []
    for item in json_list:
        img_list.append(f"{item['prefix']}original{item['suffix']}")  
        break
    return img_list

# Add function for recipes 
def get_random_meals(num_meals = 10):

    url = "https://www.themealdb.com/api/json/v1/1/random.php"
    meals_rec = dict()

    for i in range(num_meals):
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            # Extracting information
            meal_data = data['meals'][0]
            # Get strInstructions
            instructions = meal_data['strInstructions']
            # Get strCategory
            category = meal_data['strCategory']
            # Get strMeal
            meal_name = meal_data['strMeal']
            # Extract all strIngredient1 values
            ingredients = [meal_data[f'strIngredient{i}'] for i in range(1, 21) if meal_data[f'strIngredient{i}']]
            # Concatenate strIngredient1 values into a single string
            all_ingredients = ', '.join(ingredients)
            strMealThumb = meal_data['strMealThumb']
            # Add meal information to the dictionary
            meals_rec[f'{meal_name}'] = {'category': category, 'all_ingredients': all_ingredients,
                                          'instructions': instructions, 'strMealThumb': strMealThumb}
        else:
            print(f"Error for meal {i + 1}:", response.status_code)

    return meals_rec

def get_list_from_json(json_file_path):

    with open(json_file_path, 'r') as file:
        meal_list = json.load(file)
        return meal_list

def save_dict_to_json(dictionary, filename):
    try:
        json_data = json.dumps(list(dictionary.values()), indent=4)
        with open(filename, 'w') as file:
            file.write(json_data)
    except Exception as e:
        print(f"Error occurred while saving dictionary to JSON file: {e}")

def load_dicts_from_json(filename):
    try:
        with open(filename, 'r') as file:
            json_data = json.load(file)
        return json_data
    except Exception as e:
        print(f"Error occurred while loading JSON file: {e}")
        return None

def save_dict_file(dictionary, filename):
   with open(filename, 'w') as file:
        json.dump(dictionary, file, indent=4)


def read_dict_from_json(filename):
    with open(filename, 'r') as file:
        dictionary = json.load(file)
    return dictionary


@blueprint.route('/index')
@login_required
def index():

    flag = False # Specifies wether we are loading from the api or from the stored data 

    if(flag):
        places_list = get_places()
        fsq_list = []
        for pl in places_list:
            fsq_list.append(pl['fsq_id'])
        
        
        img_list = dict()
        outdoor_place = dict()
        description_list = dict()

        meals_rec = get_random_meals()

        for fsq in fsq_list:
            places_info , place_desc = get_details_for_a_place(fsq)
            img_list[places_info] =  get_images_for_food(fsq)
            outdoor_place[places_info] = get_images_for_a_place(fsq)
            description_list[places_info] = place_desc
        # Store the dictionaries 
        save_dict_file(img_list , 'apps\static\data\img_list.json')
        save_dict_file(outdoor_place , 'apps\static\data\outdoor_place.json')
        save_dict_file(description_list , 'apps\static\data\description_list.json')
        save_dict_file(meals_rec , 'apps\static\data\meals_rec.json')
    else:
        img_list = read_dict_from_json('apps\static\data\img_list.json')
        outdoor_place = read_dict_from_json('apps\static\data\outdoor_place.json')
        description_list = read_dict_from_json('apps\static\data\description_list.json')
        meals_rec = read_dict_from_json('apps\static\data\meals_rec.json')
  
    meal_kit_list = get_list_from_json('apps\static\data\meal_kits.json')
    nutrition_list = get_list_from_json('apps\\static\\data\\nutrition_food.json')
    reviews = get_list_from_json('apps\\static\\data\\reviews.json')

    return render_template('home/index.html', segment='index', places = img_list, 
                           outdoor_img = outdoor_place, places_desc = description_list, meals = meals_rec,
                           meal_kit_list = meal_kit_list, nutrition_food = nutrition_list, user = current_user,
                           reviews = reviews)


@blueprint.route('/index_blog')
@login_required
def index_blog():

    json_file_path = 'apps/static/data/blogs.json'

    # Read the JSON file
    with open(json_file_path, 'r') as file:
        vegan_food_data = json.load(file)

    return render_template('home/index_blog.html', segment = 'index_blog', blog_list = vegan_food_data , user = current_user)

@blueprint.route('/about')
@login_required
def about():
    return render_template('home/about.html', segment = 'about', user = current_user)

@blueprint.route('/profile')
@login_required
def profile():
    return render_template('home/profile.html', segment = 'profile', user = current_user )

@blueprint.route('/single/<int:blog_id>')
def single(blog_id):

    with open('apps/static/data/blogs.json', 'r') as file:
        blogs = json.load(file)

    blog = next((blog for blog in blogs if int(blog['id']) == blog_id), None)

    return render_template('home/single.html', segment='single', user = current_user , blog = blog )

# Route to handle form submission and save reviews
@blueprint.route('/submit_review', methods=['POST'])
def submit_review():
    # Load existing reviews from JSON file
    try: 
        with open('apps/static/data/reviews.json', 'r') as file:
            existing_reviews = json.load(file)
    except:
        existing_reviews = []
        print('no reviews yet')

    # Get data from the form
    message = request.form.get('message')

    # Create a new review object
    new_review = {
        'message': message,
        'user_id': current_user.id if current_user.is_authenticated else None,
        'user_name': current_user.username if current_user.is_authenticated else "Anonymous"
    }

    # Append the new review to existing reviews
    existing_reviews.append(new_review)

    # Write the updated reviews back to the JSON file
    with open('apps/static/data/reviews.json', 'w') as file:
        json.dump(existing_reviews, file, indent = 4)

    return redirect(url_for('home_blueprint.index'))


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
