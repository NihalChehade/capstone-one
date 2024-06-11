
#spoonacular api :
[link](https://spoonacular.com/food-api/docs)

#Title : CookTime [link](https://capstone-one-aczl.onrender.com/)


## what my website does?
> CookTime is a recipe creation website that allows users to sign up, create and view recipes, and calculate overall nutritional values for each recipe.

## Features:
* User signup, login, logout, and profile picture upload.
* View user profile by clicking on "My Profile" on the nav bar.
* Create recipes with dynamic ingredient addition and autocomplete search using the Spoonacular API.
* Dynamically retrieve unit options based on the selected ingredient from the Spoonacular API.
* View detailed information about each recipe, including calculated overall nutritional values.
* View all user recipes in one place by clicking "My Recipes" tab on the nav bar.

## Technologies Used:
* HTML5
* Python 3.9.18
* Flask
* Flask-WTF
* JavaScript
* Bootstrap
* SQLAlchemy
* PostgreSQL
* AJAX
* axios library

## Setup Guide

### Prerequisites

Before you begin, ensure you have the following installed on your system:
* Python 3.9.18
* PostgreSQL
* Git
  

### Setting Up the Development Environment

1. **make directory for the project**
    
    ```bash
    mkdir cook-time
    cd cook-time
    ```
2. **Clone the repository:**

    ```bash
    git clone git@github.com:hatchways-community/capstone-project-one-0f9f96537b3c4085b054b1106e834613.git
    cd capstone-project-one-0f9f96537b3c4085b054b1106e834613
    ```

3. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

### Installing Dependencies

1. **Upgrade pip and install dependencies:**

    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

## Configuring the Database

1. **Create a PostgreSQL database:**

    ```bash
    createdb cook_time
    createdb test_cook_time
    ```

2. **Create a `.env` file in the project root directory and add the following configuration:**

    ```env
    DATABASE_URL=postgresql:///cook_time
    TEST_DATABASE_URL=postgresql:///test_cook_time
    SECRET_KEY=your_secret_key # choose your secret key
    SPOONACULAR_API_KEY=your_spoonacular_api_key # use the link of spoonacular api and signup for the free tier and get a spoonacular api key for this    #environment variable
    ```

## Running the Application

1. **Start the Flask development server:**

    ```bash
    flask run --debug
    ```

2. **Access the application:**

    Open your web browser and go to `http://127.0.0.1:5000/`

## Running Tests

1. **Run the tests:**
   
    ```bash
    python -m unittest discover -s tests
    ```

