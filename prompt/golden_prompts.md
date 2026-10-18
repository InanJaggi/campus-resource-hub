# Golden Prompts

High-impact prompts that led to significant feature implementations or architectural decisions.

---

## MVC & DAL Clarification
"""
Design a Flask MVC app with a strict Data Access Layer so that controllers never talk to the ORM directly. Propose the minimal folder structure and one example per layer.
"""

### Implementation Summary:
- Established strict separation: controllers → DAL → ORM
- Created `data_access/` layer with functions like `create_resource()`, `search_resources()`, `get_user_by_email()`
- Controllers import from DAL, never directly from models
- Foundation for maintainable, testable architecture

---

## Comprehensive Admin Dashboard and User Management
"""
Give the admin dashboard statistics regarding average rating, most popular booking time, amount of active bookings, and any more important details an admin would need to see. They need to have total control. Also, ensure that this admin has access to logs for admin changes, as well as another log regarding all bookings. This log should show up as a listing starting with most recent and moving to older options. The admin should also be able to view each user and adjust all settings regarding that user. this could be name, email, role, description, etc. All information should be tracked and be easily accessible by the admin. Also, the user should have their own log of past bookings, current bookings, and upcoming bookings. This log should give the user the ability to view more details about each specific log (such as time, what it was, what the description of it was, etc.) Also, for upcoming ones, the user should be allowed to edit the booking. This should be an option after they view the booking directly from the log. Doing so, they can adjust the time, day, recurring, etc.).
"""

### Implementation Summary:
- Built complete admin dashboard with statistics cards (users, resources, bookings, ratings), booking breakdowns, popular times/resources, recent activity
- Created admin logging system with AdminLog model, auto-logging of all admin actions, sorted by most recent
- Implemented booking logs showing all bookings with full details, sorted chronologically
- Added comprehensive user management: full user list, edit capabilities (name/email/role/department), view user activity (bookings/resources/reviews), change tracking
- Enhanced user bookings page with tabs (Past/Current/Upcoming), detailed booking view, edit upcoming bookings (times, recurrence, conflict checking)
- Added admin dropdown menu in navbar with Dashboard, User Management, Booking Logs, Admin Logs
- This prompt established the foundation for all admin and user management features

---

## Visual Calendar Booking Interface
"""
On a completely separate topic, the calendar for each individual booking by someone should show a total calendar with the bookings for that particular week blocked out. So it should be a week by week basis (that you can toggle at the top of this) with it being hour by hour on the left side, and lines separating the hours. then, the booked time slots (lets say 9am-noon on monday for example) should be blocked out so any other user knows they cannot book it at this time. Also, make it so the user has to highlight the section, or time block, that they want the resource. The time should show up at the top for what the exact time interval they highlighted is. This allows for them to pick available slots that have not been taken by other users. And gives an easy way for booking instead of clicking two different items for picking your times.
"""

### Implementation Summary:
- Created revolutionary visual calendar booking interface with week-by-week navigation, hour labels (7am-11pm), 15-minute blocks
- Visual blocking system: booked slots (red), disabled slots (gray for outside operating hours), available slots (white/green)
- Click-and-drag selection for time blocks, real-time time display at top, auto-populate form fields
- 30-minute minimum validation, conflict detection, operating hours enforcement, visual highlighting (blue for selected blocks)
- This completely transformed the booking experience from form-based to visual/interactive

---

## AI Chatbot Integration
"""
Next, I want you to create an AI chatbot that has an icon in the lower corner of the screen for all users. This chatbot needs to know all information regarding the website, mainly about booking, what times are available, and what resources are there. It should be able to answer any questions that people have in regards to booking. Also any general questions about the website as well (whether its about how to create a resource or message someone). I have a google gemini key here: [API_KEY_REDACTED]
"""

### Implementation Summary:
- Created AI chatbot widget with floating icon in lower right corner, chat window with message history, typing indicator
- Integrated Google Gemini API with model fallback system (tries multiple models in order of preference)
- Built `get_website_context()` function that provides comprehensive website information to AI (roles, features, booking rules, resources, statistics)
- Created endpoints: `/chatbot/chat` (main chat), `/chatbot/resources` (resource list), `/chatbot/availability/<resource_id>` (availability info)
- Added error handling, responsive design, CSRF exemption, API key via `.env`
- This established the foundation for all AI-powered features including highlighting and tutorials

---

## Guided Tutorial System
"""
instead of only highlighting the specific tab, I want you to only do it if someone asks what the website does or is all about. If they want to learn how it works, then you can go through and highlight each option, in the same dark manner, and have a text bubble pop up near the middle of the screen explaining that specific button or feature. Do this for many features. Also, if possible, click into the "add resources" button and show that person how to add a resource by highlighting the different options, in the same dark outline way you did for highlighting navigation buttons. Do the same for how to book (so highlight one of the cards on the explore page, write a little bit about what each card means, then click into the "view details" button, when they tap the screen, then show them what the different categories of information mean."
"""

### Implementation Summary:
- Created comprehensive guided tutorial system with three tutorials: Navigation Tour, Add Resource Tutorial (staff/admin), Booking Tutorial
- Tutorial bubbles with title/description, progress indicator, Next/Close buttons, smart positioning (avoids covering elements)
- Step-by-step walkthroughs with element highlighting, text bubbles, auto-navigation between pages, role-based conditional steps
- Session persistence via sessionStorage to resume tutorials after page navigation
- AI trigger via `[TUTORIAL:tutorial-name]` in chatbot responses
- This created an interactive onboarding experience that guides users through key workflows

---

## Chatbot Highlighting Improvements
"""
Modify the ai chatbot so it highlights portions of the screen (like navigation buttons) only when there's a question directly focused towards where to find a navigation button. Often times, when asking like how to edit a resource, after already being in the "My resources" page, it will try to highlight the navigation button again when it does not have to."
"""

### Implementation Summary:
- Enhanced chatbot intelligence to only highlight navigation when questions explicitly ask about finding/locating navigation elements
- Added current page context awareness: frontend sends current page URL, backend detects page context and informs AI
- Updated prompt with explicit rules and "CRITICAL RULE" preventing highlights for "how do I [do something]" questions when user is already on relevant page
- Added page context detection for resources, bookings, messages, reviews pages
- This significantly improved user experience by preventing unnecessary highlighting when users are already on the correct page

---

## Product Requirements Document Creation
"""
Create a product requirements document that has the objective, stakeholders, non-goals, core features, success metrics. Make this prd one page long and cover any product management concepts needed to relate to all of these PRD requirements."
"""

### Implementation Summary:
- Created comprehensive PRD document (`docs/PRD.txt`) with all required sections in one-page format
- Included: Objective, Stakeholders (Primary/Secondary with bullet points), Non-goals (bullet points), Core Features (10 features), Success Metrics (6 categories with bullet points), Product Management Concepts (MVP scope, user stories, MoSCoW prioritization, risk management, iterative development)
- Document formatted for easy conversion to .docx and professional presentation
- This established clear product vision and requirements documentation

---

## AI Chatbot Test Suite
"""
can you add a test into the ai_eval folder for testing the viability of the ai bot that i had you create through gemini? Have a py test that can be used to ensure this is working correctly."
"""

### Implementation Summary:
- Created comprehensive test suite (`tests/ai_eval/test_chatbot.py`) with 13 test cases covering all chatbot functionality
- Tests use mocking to avoid real API calls (faster, no costs, more reliable)
- Tests verify: endpoint accessibility, message validation, response format, context awareness, highlight/tutorial detection, smart highlighting logic, error handling
- Updated README with comprehensive documentation and troubleshooting guide
- Added to master test runner for automated testing
- This ensures chatbot reliability and catches regressions in AI behavior

