# constants.py
# Cookie names — single source of truth for all cookie keys used across the app.
# JS-readable cookies are passed to templates via context rather than hardcoded in JS.

COOKIE_RECENT_SEARCHES = "recent_city_searches"
COOKIE_LAST_LOCATION   = "last_weather_location"
COOKIE_FLASHCARD_OPTIONS = "flashcard_options"
COOKIE_FLASHCARD_GAME_SESSION = "flashcard_game_session"
MAX_RECENT_SEARCHES = 10