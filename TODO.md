# Weather App — TODO

## In Progress
- [ ] Implement `weather_code_to_string` for remaining weather codes (TDD red-green-refactor)

## Backlog

### Features
- [ ] Add error state UI for failed geocoding lookup
- [ ] Handle edge case: geocoding returns zero results
- [ ] Style the address selection modal (native `<dialog>`)
- [ ] Display weather icon or visual indicator alongside weather code string
- [ ] Add support for multiple saved cities (beyond single cookie-based city)

### Code Quality
- [ ] Add docstrings to `address_service.py` public functions
- [ ] Review router layer for any HTTP logic leaking into service files
- [ ] Audit logging calls — confirm all modules use `logging.getLogger(__name__)`

### Testing
- [ ] Expand pytest coverage for geocoding edge cases
- [ ] Add tests for cookie-based city persistence logic
- [ ] Test `hx-trigger="load"` partial swap behavior (manual or integration test)

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
