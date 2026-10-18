# API Documentation

This document provides detailed API endpoint documentation with request/response examples for the Campus Resource Hub application.

## Authentication Endpoints

### POST /auth/register
Create a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@campus.edu",
  "password": "SecurePass123!",
  "role": "student"
}
```

**Response (Success - 302 Redirect):**
- Redirects to login page
- Flash message: "Registration successful. Please log in."

**Response (Error - 400):**
- Flash message with validation error (e.g., "Password must contain at least one uppercase letter.")

---

### POST /auth/login
Authenticate user and create session.

**Request Body:**
```
email: john@campus.edu
password: SecurePass123!
```

**Response (Success - 302 Redirect):**
- Redirects to homepage
- Flash message: "Logged in."
- Session created with user ID

**Response (Error - 200 with flash):**
- Flash message: "Invalid credentials"

---

### GET /auth/logout
Logout current user.

**Response (302 Redirect):**
- Redirects to homepage
- Flash message: "Logged out."
- Session destroyed

---

## Resource Endpoints

### GET /resources
List and search resources.

**Query Parameters:**
- `q` (optional): Keyword search (title, description, location)
- `category` (optional): Filter by category (study, av, event, lab, tutoring)
- `location` (optional): Filter by location
- `min_capacity` (optional): Minimum capacity
- `min_rating` (optional): Minimum rating (1-5)
- `available_date` (optional): Date filter (YYYY-MM-DD)
- `available_time` (optional): Time filter (HH:MM)
- `sort` (optional): Sort order (recent, most_booked, top_rated)

**Example Request:**
```
GET /resources?q=study&category=study&sort=top_rated
```

**Response (200):**
- HTML page with resource listings

---

### GET /resources/<id>
Get resource detail page.

**Example Request:**
```
GET /resources/5
```

**Response (200):**
- HTML page with resource details, booking calendar, reviews

**Response (404):**
- Error page if resource not found

---

### POST /resources
Create a new resource (requires authentication, staff/admin only).

**Request Body (multipart/form-data):**
```
title: Study Room 101
description: Quiet study space with whiteboard
category: study
location: Library 2nd Floor
capacity: 4
booking_type: open
status: published
image: [file upload]
```

**Response (302 Redirect):**
- Redirects to resource detail page
- Flash message: "Resource created successfully."

**Response (403):**
- Flash message: "Staff or admin access required."

---

### PUT /resources/<id>
Update a resource (via form submission at `/resources/<id>/edit`).

**Request Body (multipart/form-data):**
```
title: Study Room 101 (Updated)
description: Updated description
[other fields...]
```

**Response (302 Redirect):**
- Redirects to resource detail page
- Flash message: "Resource updated successfully."

---

### DELETE /resources/<id>
Delete a resource (API endpoint, owner/admin only).

**Request Method:** DELETE

**Response (200 JSON):**
```json
{
  "success": true,
  "message": "Resource deleted successfully"
}
```

**Response (403 JSON):**
```json
{
  "error": "Permission denied"
}
```

---

## Booking Endpoints

### POST /bookings/new/<resource_id>
Request a new booking.

**Query Parameters:**
- `view` (optional): "calendar" or "form" (default: "form")

**Request Body (form):**
```
start_time: 2025-11-20T10:00:00
end_time: 2025-11-20T11:30:00
recurrence: none
```

**Response (302 Redirect):**
- For open resources: Redirects with "Booking confirmed! Your booking has been automatically approved."
- For restricted resources: Redirects with "Booking request submitted. Waiting for owner approval."

**Response (400):**
- Flash message with validation error (e.g., "Time slot conflicts with existing booking")

---

### GET /bookings/my
Get user's bookings dashboard.

**Response (200):**
- HTML page with tabs: Past, Current, Upcoming, Waitlist
- Shows booking details, status, resource information

---

### GET /bookings/<id>
Get booking detail (API endpoint, JSON response).

**Response (200 JSON):**
```json
{
  "id": 1,
  "resource_id": 5,
  "resource_title": "Study Room 101",
  "start_time": "2025-11-20T10:00:00",
  "end_time": "2025-11-20T11:30:00",
  "status": "approved",
  "user_id": 2,
  "user_name": "John Doe"
}
```

---

### PUT /bookings/<id>/approve
Approve a booking (staff/admin/owner only).

**Response (302 Redirect):**
- Flash message: "Booking approved"
- Creates notification message to requester

---

### POST /bookings/<id>/cancel
Cancel a booking.

**Response (302 Redirect):**
- Flash message: "Booking cancelled"
- If waitlist exists, promotes next candidate

---

### POST /bookings/<id>/edit
Edit booking (time, recurrence) - upcoming bookings only.

**Request Body (form):**
```
start_time: 2025-11-20T14:00:00
end_time: 2025-11-20T15:30:00
recurrence: weekly
```

**Response (302 Redirect):**
- Flash message: "Booking updated successfully"

---

## Message Endpoints

### GET /messages
List message threads for current user.

**Response (200):**
- HTML page with list of message threads
- Shows unread count badge

---

### GET /messages/thread/<id>
View a message thread.

**Response (200):**
- HTML page with thread messages
- Form to send new message

---

### POST /messages
Send a message (API endpoint).

**Request Body (JSON):**
```json
{
  "thread_id": 5,
  "body": "Hello, I'm interested in booking this resource."
}
```

**OR:**
```json
{
  "receiver_id": 3,
  "body": "Hello, I'm interested in booking this resource."
}
```

**Response (200 JSON):**
```json
{
  "success": true,
  "message_id": 12
}
```

---

## Review Endpoints

### GET /reviews/new/<resource_id>
Get review form (requires completed booking).

**Response (200):**
- HTML page with review form (1-5 stars, comment)

**Response (403):**
- Flash message: "You must have a completed booking to leave a review"

---

### POST /reviews
Submit a review (API endpoint).

**Request Body (JSON):**
```json
{
  "resource_id": 5,
  "rating": 5,
  "comment": "Great study space, very quiet!"
}
```

**Response (200 JSON):**
```json
{
  "success": true,
  "review_id": 8
}
```

---

### GET /reviews
List all reviews.

**Response (200):**
- HTML page with all reviews, filterable by resource

---

## Admin Endpoints

### GET /admin
Admin dashboard.

**Response (200):**
- HTML page with statistics cards, booking breakdowns, popular resources

---

### GET /admin/stats
Get usage metrics (API endpoint, admin only).

**Response (200 JSON):**
```json
{
  "total_users": 150,
  "total_resources": 45,
  "total_bookings": 320,
  "average_rating": 4.2,
  "active_bookings": 28
}
```

---

### POST /admin/promote/<user_id>
Promote user to staff role.

**Response (302 Redirect):**
- Flash message: "User promoted to staff"
- Logs action in admin_logs

---

### GET /admin/users
User management page.

**Response (200):**
- HTML page with list of all users, edit capabilities

---

### GET /admin/bookings
Booking logs page.

**Response (200):**
- HTML page with all bookings, sorted by most recent

---

### GET /admin/logs
Admin action logs page.

**Response (200):**
- HTML page with all admin actions, sorted by most recent

---

## AI/MCP Endpoints (Read-only)

### GET /ai/resources
List resources (JSON, supports search).

**Query Parameters:**
- `q` (optional): Keyword search

**Example Request:**
```
GET /ai/resources?q=study
```

**Response (200 JSON):**
```json
[
  {
    "id": 1,
    "title": "Study Room 101",
    "category": "study",
    "location": "Library",
    "capacity": 4,
    "rating": 4.5,
    "status": "published"
  }
]
```

---

### GET /ai/resource/<id>/schedule
Get resource booking schedule (JSON).

**Response (200 JSON):**
```json
[
  {
    "start": "2025-11-20T10:00:00",
    "end": "2025-11-20T11:30:00",
    "user_id": 2
  }
]
```

---

### GET /ai/resource/<id>/reviews
Get resource reviews (JSON).

**Response (200 JSON):**
```json
[
  {
    "rating": 5,
    "comment": "Great space!",
    "user_id": 2,
    "created_at": "2025-11-15T14:30:00"
  }
]
```

---

## Chatbot Endpoint

### POST /chatbot/chat
AI chatbot endpoint (requires GEMINI_API_KEY).

**Request Body (JSON):**
```json
{
  "message": "How do I book a study room?",
  "current_page": "/resources/"
}
```

**Response (200 JSON):**
```json
{
  "reply": "To book a study room, click on a resource card and then click 'Book with Calendar' or 'Book with Form'...",
  "timestamp": "2025-11-20T10:30:00",
  "highlight": null,
  "tutorial": null
}
```

**Response with Highlight:**
```json
{
  "reply": "You can find your bookings by clicking on the 'Bookings' link in the navigation bar.",
  "timestamp": "2025-11-20T10:30:00",
  "highlight": "nav-bookings",
  "tutorial": null
}
```

**Response with Tutorial:**
```json
{
  "reply": "This website helps you discover, book, and manage campus resources. Let me show you around!",
  "timestamp": "2025-11-20T10:30:00",
  "highlight": null,
  "tutorial": "navigation"
}
```

**Response (500):**
```json
{
  "error": "Gemini API key not configured. Please check your .env file."
}
```

---

## Error Responses

All endpoints may return standard HTTP error codes:

- **400 Bad Request**: Invalid input data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

Error responses typically include flash messages (for HTML responses) or JSON error objects (for API endpoints).

---

## Authentication

Most endpoints require authentication via Flask-Login session. Admin endpoints require `role="admin"`. Resource creation/management requires `role="staff"` or `role="admin"`.

CSRF protection is enabled for all form submissions. Include CSRF token in form data or use the `csrf_token()` function in templates.

