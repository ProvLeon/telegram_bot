import random
import json

def get_image_url_for_class(class_name):
    # Define mappings between class names and image categories
    class_to_category = {
        'AI': 'ai_images',
        'Coding': 'coding_images',
        'Python': 'python_images',
        'JavaScript': 'javascript_images',
        'Cybersecurity': 'cybersecurity_images',
        'Data Analytics': 'data_analytics_images',
        'Web Development': 'web_development_images'
    }

    # Determine the category based on the class name
    category = next((cat for key, cat in class_to_category.items() if key.lower() in class_name.lower()), 'coding_images')

    # Load the appropriate JSON file
    with open(f'assets/images/{category}.json', 'r') as f:
        images = json.load(f)

    # Randomly select an image URL
    return random.choice(images)['url']
