# Project Cleanup Plan

## Phase 1: Frontend Unused Page Files
Files confirmed unused (not imported in App.js or other files):
- [ ] frontend/src/pages/AuthPage.js
- [ ] frontend/src/pages/AuthPageEnhanced.js
- [ ] frontend/src/pages/AdvancedTrade.js
- [ ] frontend/src/pages/AdvancedTrading.js
- [ ] frontend/src/pages/MyOrders.js

## Phase 2: Backend Test Files Organization
67 test files in root directory - should be organized:
- [ ] Move all *_test.py files to /tests directory
- [ ] Keep test_result.md in root (it's actively used)

## Phase 3: Backend Unused Service Files
Files not imported in server.py:
- [ ] backend/abantether_scraper.py (not used)
- [ ] backend/admin_advanced_services.py (not used)
- [ ] backend/admin_communication_services.py (not used)
- [ ] backend/set_openai_key.py (utility script, can keep or move to scripts/)

## Phase 4: Code Quality Cleanup
- [ ] Remove console.log statements from production frontend code
- [ ] Remove commented code blocks
- [ ] Clean up unused imports

## Phase 5: Verification Testing
- [ ] Test backend endpoints
- [ ] Test frontend pages
- [ ] Verify no broken functionality
