# Weather App — TODO

## In Progress
- [ ] Fix weather tests.
- [X] Implement Weather class method to populate key fields
- [ ] Cleaner way to create an address directly from the address response.
- [X] Figure out where the response from the API should be converted into a data object (list) to be used by the app.  Have the api call convert it or the calling funtion?
- [ ] Implement `weather_code_to_string` for remaining weather codes (TDD red-green-refactor)
- [X] The get forecast from api.open-meteo.com is expecting a lat and a long.  But in some cases they are null.  The get Address by postal code is not returning a true Address object but the response from the API call.  Do we convert the response to only get the data we need or modify to pull the data from the response.

## Backlog
- [ ] Weather class allow the user to switch between C & F
- [ ] Weather class allow to switch between mph and kph

### Features
- [ ] Add error state UI for failed geocoding lookup
- [ ] Handle edge case: geocoding returns zero results
- [ ] Style the address selection modal (native `<dialog>`)
- [ ] Display weather icon or visual indicator alongside weather code string
- [ ] Add support for multiple saved cities (beyond single cookie-based city)
- [ ] Return 0 results if the postal code is 00000, set an error condition

### Code Quality
- [ ] Add docstrings to `address_service.py` public functions
- [ ] Review router layer for any HTTP logic leaking into service files
- [ ] Audit logging calls — confirm all modules use `logging.getLogger(__name__)`

### Testing
- [ ] Expand pytest coverage for geocoding edge cases
- [ ] Add tests for cookie-based city persistence logic
- [ ] Test `hx-trigger="load"` partial swap behavior (manual or integration test)
- [X] Finishing migrating address_service_test.py
- [ ] Finishing migrating weather_service_test.py

### Frontend / CSS
- [ ] Revisit flexbox layout on mobile viewports
- [ ] Confirm inline vs external styles are consistent across all templates
- [ ] Review partial vs full-page template split for any redundancy

## Done
- [x] FastAPI + HTMX project scaffold (routers, services, templates)
- [x] Separation of concerns: `address_service.py` with no HTTP logic
- [x] `setup_logging()` configured once at entry point
- [x] Cookie-based city persistence with FastAPI `Cookie()` dependency
- [x] `hx-trigger="load"` pattern for cookie-driven city auto-load
- [x] Inline address selection with HTMX partial swap
- [x] Native `<dialog>` modal for address search
- [x] Two-column dashboard layout in pure CSS
- [x] Sticky header with mobile hamburger menu (personal hobby page)
- [x] `/current-time` HTMX endpoint

---
_Update this file at the start or end of each session._
