# blueJaysApp Project Documentation

Welcome to the documentation for the blueJaysApp project. This documentation provides an overview of the project, its requirements, installation instructions, and usage guidelines. blueJaysApp is a Django-based web application designed to interact with APIs and display baseball-related data.

## Table of Contents

1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
5. [Contributing](#contributing)
6. [License](#license)

---

## Requirements

To run blueJaysApp, ensure that you have the following dependencies installed on your system:

- Python 3.x
- Django 3.x
- Virtualenv (recommended for creating isolated Python environments)

---

## Installation

Follow these steps to set up and run blueJaysApp:

### 1. Clone the Repository

Clone the blueJaysApp repository to your local machine:

```shell
git clone https://github.com/dnahon/blueJaysApp.git
```

### 2. Navigate to the blueJaysApp Directory

Navigate to the blueJaysApp directory:

```shell
cd blueJaysApp
```

### 3. Create a Virtual Environment (Optional)

It's a good practice to create a virtual environment to isolate project dependencies. To create one, run:

```shell
python -m venv venv_blueJaysApp
source venv_blueJaysApp/bin/activate  # On Windows, use: venv_blueJaysApp\Scripts\activate
```

### 4. Install Dependencies

Install the required Python packages using `pip`:

```shell
pip install -r requirements.txt
```

### 5. Run the Development Server

Start the Django development server:

```shell
python manage.py runserver
```

blueJaysApp should now be running locally. Access the application at `http://localhost:8000/`.

---

## Configuration

### Environment Variables

blueJaysApp may use environment variables for configuration. You can set these in a `.env` file in the project's root directory or configure them directly in your server environment.

Here are the possible environment variables that you may need to configure, depending on your specific use case:

- `SECRET_KEY`: Django secret key for security.
- `DEBUG`: Set to `True` for development and `False` for production.

---

## App Usage

There are three main pages on the blueJaysApp:

- The homepage contains two tabs: one with MLB divisional standings, news, and that day's game results, and the other tab with updated league leaders.
- The team page contains information about every player on the roster. Users can switch between viewing the hitters and pitchers of the team.
- The player page contains season-by-season stats for that player.
- If the user goes to a random URL, there is an error page with a redirect button back to the home page.

This is how users can navigate between pages:

- The homebase icon in the top bar navigatest to the homepage
- Users can click on a news story hyperlink to open the article
- Users can click on a team name abbreviation within the standings tables to navigate to the team's page
- Users can click on a team name abbreviation within the league leaders tables to navigate to the team's page
- Users can click on a player's name within the league leaders tables to navigate to the player's page
- Users can click on a player's name within the team roster table to navigate to the player's page
- User's can click on any team in the player stats table to navigate to the team's page

---
