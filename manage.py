#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FFM.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

#TODO: squad editing
#TODO: automatic scraping match details
#TODO: league,team, player info update
#TODO: cdn for images
#TODO: repair leaderboard
#TODO: lazy loading of players in team page + pagination
#solved: repair index page to show matches in week
#TODO: add logo to navbar and footer
#TODO: add email help text
#TODO: repair signup tooltips
#TODO: add tests