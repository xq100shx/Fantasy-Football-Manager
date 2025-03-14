# Fantasy football manager
Fantasy Football Manager is an interactive online platform where football fans can create their own dream teams using players from the top five leagues in the world. Users earn points based on the real-life performances of their selected players in matches. 

## Time spent on project

![image](https://github.com/user-attachments/assets/6f2b49ae-9271-4813-b5f6-50fb007f320f)

Measured using [Darkyen's Time Tracker](https://plugins.jetbrains.com/plugin/9286-darkyen-s-time-tracker)

## Features
- User Authentication: Secure login and registration system.
- Team Management: Users can create their own fantasy football teams and earn points.
- Leaderboard: Track and compare user performance.
- Responsive Design: Optimized for both desktop and mobile devices.

## Technology stack
- Python: django, requests, beautifulsoup4
- CSS: Bootstrap
- Javascript
- HTML
- SQlite

## Screenshots
**Login Page**

![Zrzut ekranu 2025-03-14 203405](https://github.com/user-attachments/assets/62c913f4-b7d3-4406-abe2-63505c26cdcb)

Simple login page created using custom django form.

**Sign up Page**

![Zrzut ekranu 2025-03-14 203431](https://github.com/user-attachments/assets/bcc23bbf-7f97-4272-b1bc-6d87bf932daa)

Simple register page created using custom django form. It contains tooltips for each field with helptext of what are requirements for this field.

**Home Page**

![Zrzut ekranu 2025-03-14 200730](https://github.com/user-attachments/assets/70463747-f0b9-4a34-ad2a-800cc1ea7e12)

It shows matches in current week. Green colour of match card indicates that this match will take place today or was already played.

**Leaderboard Page**

![Zrzut ekranu 2025-03-14 200752](https://github.com/user-attachments/assets/8815484b-684c-408b-8502-3e945ed036dc)

Comparision of users' performances made by using bootstrap tables.

**About Page**

![Zrzut ekranu 2025-03-14 201504](https://github.com/user-attachments/assets/fd6bf4ba-ad1b-45e8-93b2-8786744fe0a5)

It explaines rules of the game to user: which player stats are worth how many points.

**Fantasy team creation example**

https://github.com/user-attachments/assets/9b2f0103-1376-46fb-bb0e-25f7d13ecf6e

The video shows creation of fantasy team. What is not shown in the video but is implemented is:
- player choice validation: user can't have 2 same players in one squad as well as choose midfielder to be his goalkeeper,
- number of player validation: user cannot save squad until there are 11 players.

**User squad after assigning points**

![Zrzut ekranu 2025-03-14 224255](https://github.com/user-attachments/assets/7c64d71c-a122-4fc9-be05-7a7fab66d1eb)

By using `python manage.py reward` command statistics of played matches are scraped, points are calculated and assigned to user and his squad. Colorful squares visible in the photo indicates different levels of player's performance:
- points >= 100 - Green
- 50 < points < 100 - Turquoise
- 25 < points <= 50 - White
- points <= 25 - Red

## Overview
My first problem to solve for this project was to find a reliable football data source which was free. After couple of days i finally found site called [FBREF](https://fbref.com/en/) which was very easy to scrape and as a result i created couple of scrapers. To integrate scrapers with django project i simply implemented them as django commands used as `python manage.py scraper_name`:

- `get_stats.py` collects detailed player statistics such as goals, assists etc.
- `get_upcoming_matches.py` collects data about upcoming matches such as home and away team as well as date of match
- `scrap_base_data.py` collects base informations about top 5 leagues such as leagues names, teams in this league and players in that team

`get_stats.py` and `scrap_base_data.py` scrapers use method:
```
    def safe_request(self, url, min_delay=6, max_delay=8, retries=3):
        scraper = cloudscraper.create_scraper()

        for _ in range(retries):
            try:
                response = scraper.get(url)
                response.raise_for_status()
                time.sleep(random.uniform(min_delay, max_delay))
                return response
            except cloudscraper.exceptions.CloudflareChallengeError as e:
                print(f"Request failed: {e}")
                time.sleep(random.uniform(min_delay, max_delay))

        return None
```
The reason to use that method is to avoid violating FBREF's data use policy as it states:

*Currently we will block users sending requests to:*
- *FBref and Stathead sites more often than ten requests in a minute.*
- *our other sites more often than twenty requests in a minute.*
- *This is regardless of bot type and construction and pages accessed.*
- *If you violate this rule your session will be in jail for up to a day.*

So we are sending delayed requests and for maximal safety we randomize delay.

## What could be done better?
- Scraping automation (Celery, RabbitMQ etc.) - currently every scrap and point assignation must be done manually.
- Pagination on team page - currently we just send all our players at once when user enter this page. This would be problematic if there were many users.
- Gameplay - and by that i mean basically i wanted to let users periodically choose squads, for example one squad on one week but currently one user can have only one permanent squad.
And many many more but...
# I am a student and i don't have time ;)

