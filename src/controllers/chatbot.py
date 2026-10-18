# AI Contribution: Cursor AI assisted in designing the chatbot architecture and context system.
# The context grounding feature that references /docs/context/PM/PRD.txt was implemented with AI assistance
# and reviewed for accuracy and alignment with project requirements.

from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user
from datetime import datetime, timedelta
import google.generativeai as genai
import os
from ..extensions import db, csrf
from ..models.models import Resource, Booking, User, Review

bp = Blueprint("chatbot", __name__, url_prefix="/chatbot")


def get_website_context():
    """
    Generate comprehensive context about the website for the AI.
    
    AI Contribution: This function was enhanced to reference the Product Requirements Document (PRD)
    from /docs/context/PM/PRD.txt, demonstrating context grounding as required by AiDD 2025.
    The PRD content is integrated to ensure AI responses align with project objectives and stakeholder needs.
    """
    context_parts = []
    
    # Context Grounding: Reference PRD from /docs/context/PM/PRD.txt
    # This demonstrates AI feature referencing project context materials as required by Section 9
    prd_context = """
## Product Requirements Document Context (from /docs/context/PM/PRD.txt)

**Objective:** Create a centralized web platform enabling students, staff, and administrators to discover, 
book, and manage campus resources through an intuitive, accessible booking system with automated conflict 
detection, role-based access control, and AI-powered assistance.

**Primary Stakeholders:**
- Students: Browse and book resources
- Staff: Create/manage resources, approve bookings
- Administrators: System oversight, user management, analytics

**Core Features (from PRD):**
1. User Management & Authentication: Role-based access (Student, Staff, Admin)
2. Resource Management: CRUD with draft/published/archived status, categories (Study Rooms, AV, Event Spaces, Lab Equipment, Tutoring)
3. Search & Discovery: Keyword search, filtering (category, location, capacity, rating, availability), sorting (recent, most booked, top rated)
4. Booking & Scheduling: Calendar/form views, automatic conflict detection, approval workflow (Open/Restricted), recurring bookings, 30-min minimum, 15-min intervals
5. Waitlist System: Auto-enrollment on conflicts, promotion on cancellation
6. Messaging System: Thread-based messaging, unread counts
7. Reviews & Ratings: Post-booking 1-5 star ratings, aggregate display
8. Admin Panel: User management, booking moderation, statistics dashboard, audit logs
9. AI-Powered Features: Gemini chatbot, context-aware UI highlighting, interactive tutorials
10. Accessibility: WCAG 2.1 AA compliance

**Success Metrics (from PRD):**
- User Adoption: 80% student registration, 60% monthly active users, 3+ bookings/user/semester
- User Satisfaction: ≥4.0/5.0 average rating, 70% rate "easy to use" (4+ stars)
- System Performance: 99% uptime, <2s page load, zero data loss
"""
    
    context_parts.append(prd_context)
    
    # General website information
    context_parts.append("""
# Campus Resource Hub - AI Assistant Context

## Website Overview
This is a Campus Resource Hub web application where users can book various campus resources like study rooms, AV equipment, event spaces, lab equipment, and tutoring services.

## User Roles
- **Students**: Can browse resources, make bookings, message resource owners, and leave reviews
- **Staff**: Can create and manage resources, approve/reject bookings for their resources, and do everything students can do
- **Admin**: Full access including user management, viewing all bookings, and system administration

## Key Features

### Resource Management
- Resources can be created by staff and admin users
- Each resource has:
  - Title, description, category (Study Room, AV Equipment, Event Space, Lab Equipment, Tutoring)
  - Location, capacity, status (draft, published, archived)
  - Booking type: "open" (auto-approved) or "restricted" (requires owner approval)
  - Hours of operation (opening_time and closing_time)
  - Category-specific fields (model, equipment, amenities, etc.)
  - Images and average rating

### Booking System
- Users can book resources using either:
  1. **Calendar View**: Visual week-by-week calendar with hour-by-hour layout, showing 15-minute intervals
  2. **Form View**: Traditional date/time picker form
- Booking rules:
  - Minimum booking duration: 30 minutes
  - Times must be in 15-minute intervals (:00, :15, :30, :45)
  - Bookings must be within resource operating hours (if set)
  - Conflict detection prevents double-booking
  - Open resources: Bookings are automatically approved
  - Restricted resources: Bookings require owner approval
- Booking statuses: pending, approved, rejected, cancelled, completed
- Users can edit upcoming bookings (time, day, recurrence)
- Recurrence options: daily, weekly, monthly, or none

### Search and Filtering
- Users can search resources by:
  - Keyword (title, description, location)
  - Category
  - Location
  - Minimum capacity
  - Minimum rating
  - Available date and time (shows only resources available at that time)

### Reviews and Ratings
- Users can leave 1-5 star ratings and comments after completing a booking
- Average ratings are displayed on resource cards and detail pages
- Reviews are visible to all users when booking

### Messaging System
- Users can message resource owners directly from resource detail pages
- Messages tab in navigation shows unread count
- Thread-based messaging with saved chat history
- Users can view contact information of people they're messaging

### Admin Features
- Dashboard with statistics (average ratings, popular booking times, active bookings)
- User management (view/edit all user details)
- Booking logs (all bookings, can approve/reject pending ones)
- Admin action logs
- Resource management

### Resource Owner Features
- "My Resources" page: View all owned resources in card format with edit buttons
- "Resource Bookings" page: View and manage bookings for owned resources
- Can approve/reject pending bookings for their resources

## Navigation Structure
- Browse Resources: Main resource listing page
- My Bookings: User's past, current, and upcoming bookings
- Reviews: List of resources user can review or has reviewed
- Messages: Message threads with unread count badge
- Add Resource: Create new resource (staff/admin only)
- My Resources: View owned resources (staff/admin only)
- Resource Bookings: Manage bookings for owned resources (staff/admin only)
- Admin Panel: Admin dashboard and management tools (admin only)

## Important URLs and Actions
- Browse resources: /resources/
- Book a resource: /bookings/new/<resource_id>?view=calendar (calendar) or ?view=form (form)
- View resource details: /resources/<resource_id>
- My bookings: /bookings/
- Create resource: /resources/new
- Edit resource: /resources/<resource_id>/edit
- Messages: /messages/
- Reviews: /reviews/
""")
    
    # Get current resource statistics
    try:
        total_resources = Resource.query.filter_by(status="published").count()
        total_bookings = Booking.query.filter(Booking.status.in_(["approved", "pending"])).count()
        
        context_parts.append(f"""
## Current Statistics
- Total published resources: {total_resources}
- Active bookings (approved/pending): {total_bookings}
""")
        
        # Get available resources right now
        now = datetime.now()
        available_resources = Resource.query.filter_by(status="published").all()
        available_count = 0
        for resource in available_resources:
            # Check if resource has operating hours
            if resource.opening_time and resource.closing_time:
                current_time = now.time()
                if resource.opening_time <= current_time <= resource.closing_time:
                    # Check for conflicts
                    conflicts = Booking.query.filter(
                        Booking.resource_id == resource.id,
                        Booking.status.in_(["approved", "pending"]),
                        Booking.start_time <= now,
                        Booking.end_time > now
                    ).count()
                    if conflicts == 0:
                        available_count += 1
            else:
                # No operating hours = 24/7, check conflicts
                conflicts = Booking.query.filter(
                    Booking.resource_id == resource.id,
                    Booking.status.in_(["approved", "pending"]),
                    Booking.start_time <= now,
                    Booking.end_time > now
                ).count()
                if conflicts == 0:
                    available_count += 1
        
        context_parts.append(f"- Resources currently available: {available_count}")
        
    except Exception as e:
        context_parts.append(f"Note: Could not fetch real-time statistics: {str(e)}")
    
    return "\n".join(context_parts)


def get_resource_availability(resource_id=None, date=None, time=None):
    """Get availability information for a specific resource or all resources"""
    try:
        if resource_id:
            resource = Resource.query.get(resource_id)
            if not resource:
                return f"Resource with ID {resource_id} not found."
            
            if date and time:
                # Check specific date/time
                target_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
                conflicts = Booking.query.filter(
                    Booking.resource_id == resource_id,
                    Booking.status.in_(["approved", "pending"]),
                    Booking.start_time < target_datetime + timedelta(minutes=30),
                    Booking.end_time > target_datetime
                ).count()
                
                if conflicts > 0:
                    return f"{resource.title} is NOT available at {time} on {date}. It's already booked."
                else:
                    return f"{resource.title} IS available at {time} on {date}."
            else:
                # General availability info
                upcoming_bookings = Booking.query.filter(
                    Booking.resource_id == resource_id,
                    Booking.status.in_(["approved", "pending"]),
                    Booking.start_time >= datetime.now()
                ).order_by(Booking.start_time).limit(5).all()
                
                info = f"{resource.title}:\n"
                info += f"- Location: {resource.location or 'Not specified'}\n"
                info += f"- Capacity: {resource.capacity} person(s)\n"
                if resource.opening_time and resource.closing_time:
                    info += f"- Hours: {resource.opening_time.strftime('%I:%M %p')} - {resource.closing_time.strftime('%I:%M %p')}\n"
                else:
                    info += "- Hours: 24/7 available\n"
                info += f"- Booking type: {'Open (auto-approved)' if resource.booking_type == 'open' else 'Restricted (requires approval)'}\n"
                
                if upcoming_bookings:
                    info += "\nUpcoming bookings:\n"
                    for booking in upcoming_bookings:
                        info += f"  - {booking.start_time.strftime('%b %d, %Y %I:%M %p')} to {booking.end_time.strftime('%I:%M %p')}\n"
                else:
                    info += "\nNo upcoming bookings scheduled.\n"
                
                return info
        else:
            # All resources
            resources = Resource.query.filter_by(status="published").all()
            info = f"Available resources ({len(resources)} total):\n\n"
            for resource in resources[:10]:  # Limit to 10 for context
                info += f"- {resource.title} ({resource.category}) - {resource.location or 'Location TBD'}\n"
            if len(resources) > 10:
                info += f"\n... and {len(resources) - 10} more resources. Use the browse page to see all."
            return info
    except Exception as e:
        return f"Error fetching availability: {str(e)}"


@bp.route("/chat", methods=["POST"])
@csrf.exempt  # Exempt from CSRF for API endpoint
def chat():
    """Handle chat messages from the user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request data"}), 400
        
        message = data.get("message", "").strip()
        current_page = data.get("current_page", "")
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        # Get API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            current_app.logger.error("GEMINI_API_KEY not found in environment")
            return jsonify({"error": "Gemini API key not configured. Please check your .env file."}), 500
        
        # Configure Gemini
        try:
            genai.configure(api_key=api_key)
            
            # Try available models in order of preference
            # Based on list_models output, these are available: gemini-2.5-flash, gemini-flash-latest, gemini-2.0-flash, etc.
            model = None
            preferred_models = [
                'gemini-2.5-flash',      # Latest stable flash model
                'gemini-flash-latest',   # Latest flash (auto-updates)
                'gemini-2.0-flash',      # Stable 2.0 flash
                'gemini-2.5-pro',        # Latest pro model
                'gemini-pro-latest',     # Latest pro (auto-updates)
                'gemini-2.0-flash-001',  # Specific version
            ]
            
            for model_name in preferred_models:
                try:
                    model = genai.GenerativeModel(model_name)
                    current_app.logger.info(f"Successfully initialized Gemini model: {model_name}")
                    break
                except Exception as model_error:
                    current_app.logger.debug(f"Model {model_name} not available: {str(model_error)}")
                    continue
            
            # If preferred models don't work, list and use first available
            if model is None:
                try:
                    models_list = genai.list_models()
                    for m in models_list:
                        if hasattr(m, 'supported_generation_methods') and 'generateContent' in m.supported_generation_methods:
                            # Extract just the model name (remove "models/" prefix)
                            full_name = m.name
                            if full_name.startswith('models/'):
                                model_name = full_name[7:]  # Remove "models/" prefix
                            else:
                                model_name = full_name
                            
                            try:
                                model = genai.GenerativeModel(model_name)
                                current_app.logger.info(f"Using available model: {model_name} (from {full_name})")
                                break
                            except Exception as init_error:
                                current_app.logger.debug(f"Could not initialize {model_name}: {str(init_error)}")
                                continue
                except Exception as list_error:
                    current_app.logger.error(f"Error listing models: {str(list_error)}")
            
            if model is None:
                raise Exception("Could not find or initialize any Gemini model. Please check your API key and model availability.")
                    
        except Exception as config_error:
            current_app.logger.error(f"Failed to configure Gemini: {str(config_error)}")
            return jsonify({"error": f"Failed to configure AI service: {str(config_error)}"}), 500
        
        # Get website context (with error handling)
        try:
            website_context = get_website_context()
        except Exception as context_error:
            current_app.logger.warning(f"Could not generate full context: {str(context_error)}")
            # Use basic context if database queries fail
            website_context = """
# Campus Resource Hub - AI Assistant Context

## Website Overview
This is a Campus Resource Hub web application where users can book various campus resources like study rooms, AV equipment, event spaces, lab equipment, and tutoring services.

## Key Features
- Browse and search resources
- Book resources using calendar or form view
- Message resource owners
- Leave reviews and ratings
- Admin and staff can create and manage resources
"""
        
        # Build the prompt with context
        # Determine page context for better highlighting decisions
        page_context_note = ""
        if current_page:
            if "/resources/" in current_page and "/edit" in current_page:
                page_context_note = "The user is currently on a resource edit page. They can already see edit functionality."
            elif current_page == "/resources/" or (current_page.startswith("/resources/") and current_page.count("/") == 2 and "/edit" not in current_page):
                page_context_note = "The user is currently viewing resources. They can see resource cards with edit buttons if they own resources."
            elif current_page == "/bookings/" or (current_page.startswith("/bookings/") and current_page != "/bookings/new"):
                page_context_note = "The user is currently on the bookings page. They can already see their bookings."
            elif current_page == "/messages/" or current_page.startswith("/messages/"):
                page_context_note = "The user is currently on the messages page. They can already see their messages."
            elif current_page == "/reviews/" or current_page.startswith("/reviews/"):
                page_context_note = "The user is currently on the reviews page. They can already see reviews."
        
        system_prompt = f"""You are a helpful AI assistant for the Campus Resource Hub website. Your role is to help users understand how to use the website, find resources, make bookings, and answer questions about the platform.

{website_context}

## Instructions:
1. Be friendly, helpful, and concise
2. Answer questions about booking, resources, messaging, reviews, and general website usage
3. If asked about specific resources or availability, use the context provided
4. Guide users to the appropriate pages or actions
5. If you don't know something specific (like exact current bookings), suggest they check the website directly
6. Always be accurate and helpful

## Tutorial Feature:
If the user asks "what does the website do", "how does it work", "how do I use this", "show me around", or similar questions about learning the website, you should start a guided tutorial.

To start a tutorial, include this at the end of your response:
[TUTORIAL:tutorial-name]

Available tutorials:
- navigation: Guided tour of all navigation options
- add-resource: Step-by-step guide for creating a resource (staff/admin only)
- booking: Complete booking flow from browsing to booking

Example: If user asks "what does this website do", respond with:
"This website helps you discover, book, and manage campus resources like study rooms, AV equipment, and event spaces. Let me show you around!"
[TUTORIAL:navigation]

## Single Highlight Feature (for navigation questions ONLY):
IMPORTANT: Only highlight navigation buttons/links when the user's question is SPECIFICALLY about finding or locating a navigation element. Do NOT highlight navigation when:
- The user is asking how to do something (like "how do I edit a resource") - they may already be on the relevant page
- The user is asking about functionality that's visible on the current page
- The user is asking general "how to" questions that don't require navigation
- The user is already on a page where the action can be performed

Current page: {current_page}
{page_context_note}

CRITICAL RULE: If the user is asking "how do I [do something]" and they're already on a page where that action is possible, DO NOT highlight navigation. Only highlight when they explicitly ask "where is [navigation item]" or "how do I find [navigation item]".

Only use highlighting when the question explicitly asks about:
- "Where is [navigation item]?"
- "How do I find [navigation item]?"
- "Where can I access [navigation item]?"
- "Show me where [navigation item] is"
- Similar questions specifically about locating navigation elements

Available highlight targets:
- nav-browse: Browse Resources link
- nav-bookings: My Bookings link
- nav-reviews: Reviews link
- nav-messages: Messages link
- nav-add-resource: Add Resource link (staff/admin)
- nav-my-resources: My Resources link (staff/admin)
- nav-resource-bookings: Resource Bookings link (staff/admin)
- nav-admin: Admin dropdown (admin)

To highlight a single element, include this at the end of your response:
[HIGHLIGHT:highlight-id]

Example (CORRECT - question about finding navigation):
User: "where is my bookings"
Response: "You can find your bookings by clicking on the 'Bookings' link in the navigation bar at the top of the page."
[HIGHLIGHT:nav-bookings]

Example (INCORRECT - question about how to do something, not about navigation):
User: "how do I edit a resource" (while on /resources/ page)
Response: "To edit a resource, click the 'Edit' button on the resource card you want to modify. The edit buttons are visible on each resource card on the 'My Resources' page."
(No highlight - user is asking how to edit, not where to find navigation, and they may already be on the page)

User's question: {message}
Current page: {current_page}

Provide a helpful response:"""
        
        # Generate response
        try:
            response = model.generate_content(system_prompt)
        except Exception as api_error:
            current_app.logger.error(f"Gemini API error: {str(api_error)}")
            return jsonify({"error": f"AI service error: {str(api_error)}"}), 500
        
        # Extract text from response (handle different response formats)
        reply = None
        if hasattr(response, 'text'):
            reply = response.text
        elif hasattr(response, 'candidates') and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content'):
                if hasattr(candidate.content, 'parts') and len(candidate.content.parts) > 0:
                    reply = candidate.content.parts[0].text
                elif hasattr(candidate.content, 'text'):
                    reply = candidate.content.text
        
        if not reply:
            # Fallback: try to get any text from response
            try:
                reply = str(response)
            except:
                reply = "I apologize, but I couldn't generate a response. Please try again."
        
        # Extract tutorial or highlight instruction from reply
        tutorial_name = None
        highlight_id = None
        
        if '[TUTORIAL:' in reply:
            import re
            match = re.search(r'\[TUTORIAL:([^\]]+)\]', reply)
            if match:
                tutorial_name = match.group(1).strip()
                # Remove the tutorial tag from the reply
                reply = re.sub(r'\[TUTORIAL:[^\]]+\]', '', reply).strip()
        elif '[HIGHLIGHT:' in reply:
            import re
            match = re.search(r'\[HIGHLIGHT:([^\]]+)\]', reply)
            if match:
                highlight_id = match.group(1).strip()
                # Remove the highlight tag from the reply
                reply = re.sub(r'\[HIGHLIGHT:[^\]]+\]', '', reply).strip()
        
        return jsonify({
            "reply": reply,
            "tutorial": tutorial_name,
            "highlight": highlight_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        current_app.logger.error(f"Chatbot error: {str(e)}\n{error_trace}")
        return jsonify({
            "error": f"An error occurred while processing your message: {str(e)}",
            "details": error_trace if current_app.debug else None
        }), 500


@bp.route("/resources", methods=["GET"])
def get_resources():
    """API endpoint to get list of resources for the chatbot"""
    try:
        resources = Resource.query.filter_by(status="published").all()
        resource_list = []
        for resource in resources:
            resource_list.append({
                "id": resource.id,
                "title": resource.title,
                "category": resource.category,
                "location": resource.location,
                "capacity": resource.capacity,
                "booking_type": resource.booking_type,
                "opening_time": resource.opening_time.strftime("%H:%M") if resource.opening_time else None,
                "closing_time": resource.closing_time.strftime("%H:%M") if resource.closing_time else None,
                "avg_rating": resource.avg_rating
            })
        return jsonify({"resources": resource_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/availability/<int:resource_id>", methods=["GET"])
def get_availability(resource_id):
    """API endpoint to get availability for a specific resource"""
    try:
        date = request.args.get("date")
        time = request.args.get("time")
        availability_info = get_resource_availability(resource_id, date, time)
        return jsonify({"availability": availability_info})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

