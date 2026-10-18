# Manual Test Plan - Booking System

## Feature: Resource Booking System

This manual test plan covers the core booking functionality of the Campus Resource Hub application. The tests include both positive (happy path) and negative (error handling) scenarios.

---

## Positive Test Cases

### Test Case 1: Successful Booking Creation (Open Resource)
**Objective:** Verify that a user can successfully create a booking for an open resource (no approval required).

**Prerequisites:**
- User is logged in as a student
- At least one resource exists with `booking_type="open"`
- Resource has available time slots

**Test Steps:**
1. Navigate to the "Browse" page
2. Click on a resource card with "Open" badge
3. Click "View Details"
4. Click "Book with Calendar" or "Book with Form"
5. Select a future date and time (within resource operating hours)
6. Ensure booking duration is at least 30 minutes
7. Select start time and end time
8. Click "Confirm Booking" or "Request Booking"

**Expected Result:**
- Booking is created successfully
- Flash message displays: "Booking confirmed! Your booking has been automatically approved."
- User is redirected to the resource detail page or booking confirmation page
- Booking appears in "My Bookings" under "Upcoming" tab
- Booking status is "approved"

**Test Data:**
- Resource: Study Room 101 (Open)
- Start Time: Tomorrow, 10:00 AM
- End Time: Tomorrow, 11:30 AM

---

### Test Case 2: Successful Booking Approval (Restricted Resource)
**Objective:** Verify that a resource owner can approve a pending booking request.

**Prerequisites:**
- User A (student) is logged in
- User B (staff/admin) owns a resource with `booking_type="restricted"`
- User A has created a pending booking request

**Test Steps:**
1. Log in as User B (resource owner)
2. Navigate to "Resources" → "Resource Bookings"
3. Locate the pending booking request from User A
4. Verify booking details (resource, user, time, date)
5. Click the green checkmark (✓) button to approve

**Expected Result:**
- Booking status changes from "pending" to "approved"
- Flash message displays: "Booking approved"
- User A receives a message from "Campus Booking Services" confirming approval
- Booking appears in User A's "My Bookings" under "Upcoming" tab with "approved" status
- Booking no longer appears in "Pending" section for resource owner

**Test Data:**
- Resource: Lab Equipment - Microscope (Restricted)
- Booking User: student@example.com
- Approved By: owner@example.com

---

### Test Case 3: Successful Waitlist Enrollment and Promotion
**Objective:** Verify that a user can join a waitlist when a resource is fully booked, and is automatically promoted when a booking is cancelled.

**Prerequisites:**
- Resource exists with an approved booking for a specific time slot
- User wants to book the same time slot

**Test Steps:**
1. Log in as User A (student)
2. Navigate to a resource that has an approved booking for a specific time
3. Attempt to book the same time slot using the calendar view
4. Select the already-booked time slot (highlighted in red)
5. Click "Join Waitlist" or confirm booking
6. Verify waitlist enrollment
7. Log in as the user who has the approved booking
8. Cancel the approved booking
9. Log back in as User A
10. Check "My Bookings" → "Waitlist" tab

**Expected Result:**
- User A is added to the waitlist
- Flash message indicates waitlist enrollment
- Waitlist entry appears in "My Bookings" → "Waitlist" tab
- When the original booking is cancelled, User A is automatically promoted
- User A receives a new booking (pending or approved, depending on resource type)
- Waitlist entry is removed
- User A receives a notification about the promotion

**Test Data:**
- Resource: Study Room 102
- Original Booking: User B, Tomorrow 2:00 PM - 3:00 PM
- Waitlist User: User A
- Time Slot: Tomorrow 2:00 PM - 3:00 PM

---

## Negative Test Cases

### Test Case 4: Booking Conflict Detection
**Objective:** Verify that the system prevents double-booking by detecting time conflicts.

**Prerequisites:**
- Resource exists with an approved booking for a specific time slot
- User attempts to book an overlapping time slot

**Test Steps:**
1. Log in as User A
2. Create and get approved a booking for Resource X, Tomorrow 10:00 AM - 11:00 AM
3. Log in as User B
4. Navigate to Resource X
5. Attempt to book an overlapping time: Tomorrow 10:30 AM - 11:30 AM
6. Submit the booking request

**Expected Result:**
- System detects the time conflict
- Flash message displays: "Time slot not available. You have been added to the waitlist." OR "Time slot conflicts with existing booking"
- Booking is NOT created (or is added to waitlist instead)
- User B is informed that the time slot is unavailable
- No duplicate booking is created

**Test Data:**
- Resource: Study Room 103
- Existing Booking: User A, Tomorrow 10:00 AM - 11:00 AM (approved)
- Conflicting Booking Attempt: User B, Tomorrow 10:30 AM - 11:30 AM

---

### Test Case 5: Booking Outside Operating Hours
**Objective:** Verify that the system prevents bookings outside the resource's operating hours.

**Prerequisites:**
- Resource exists with operating hours (e.g., 7:00 AM - 11:59 PM)
- User attempts to book outside these hours

**Test Steps:**
1. Log in as a student
2. Navigate to a resource with operating hours (e.g., 7:00 AM - 11:59 PM)
3. Click "Book with Form"
4. Select a date
5. Enter start time: 6:00 AM (before operating hours)
6. Enter end time: 7:30 AM
7. Submit the booking request

**Expected Result:**
- System validates operating hours
- Flash message displays: "This resource is only available from [opening_time] to [closing_time]. Your booking is outside these hours."
- Booking is NOT created
- User is shown the error message
- Form remains with the entered data (for correction)

**Test Data:**
- Resource: Study Room 104
- Operating Hours: 7:00 AM - 11:59 PM
- Booking Attempt: 6:00 AM - 7:30 AM

---

### Test Case 6: Booking Duration Below Minimum
**Objective:** Verify that the system enforces a minimum booking duration (30 minutes).

**Prerequisites:**
- User attempts to create a booking with duration less than 30 minutes

**Test Steps:**
1. Log in as a student
2. Navigate to a resource
3. Click "Book with Form"
4. Select a future date and time
5. Enter start time: Tomorrow 10:00 AM
6. Enter end time: Tomorrow 10:20 AM (20 minutes duration)
7. Submit the booking request

**Expected Result:**
- System validates minimum booking duration
- Flash message displays: "Minimum booking duration is 30 minutes"
- Booking is NOT created
- User is shown the error message
- Form remains with the entered data (for correction)

**Test Data:**
- Resource: Study Room 105
- Start Time: Tomorrow 10:00 AM
- End Time: Tomorrow 10:20 AM (20 minutes - below minimum)

---

## Test Execution Summary

| Test Case | Type | Status | Notes |
|-----------|------|--------|-------|
| TC1: Successful Booking (Open) | Positive | ⬜ Pending | |
| TC2: Booking Approval | Positive | ⬜ Pending | |
| TC3: Waitlist Enrollment | Positive | ⬜ Pending | |
| TC4: Conflict Detection | Negative | ⬜ Pending | |
| TC5: Operating Hours Validation | Negative | ⬜ Pending | |
| TC6: Minimum Duration Validation | Negative | ⬜ Pending | |

## Notes

- All tests should be executed in a test environment with sample data
- Test data should be cleaned up after test execution
- Screenshots should be taken for failed test cases
- Any deviations from expected results should be documented

