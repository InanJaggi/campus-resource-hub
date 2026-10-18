# ER Diagram (Textual)

- users (id, email, name, role, password_hash, created_at, updated_at)
- resources (id, title, description, category, location, capacity, status, owner_id→users.id, avg_rating, created_at, updated_at)
- bookings (id, resource_id→resources.id, user_id→users.id, start_time, end_time, status, created_at, updated_at)
- message_threads (id, user_a_id→users.id, user_b_id→users.id, created_at, updated_at)
- messages (id, thread_id→message_threads.id, sender_id→users.id, body, created_at, updated_at)
- reviews (id, resource_id→resources.id, user_id→users.id, rating, comment, created_at, updated_at)
- admin_logs (id, action, actor_id→users.id, created_at, updated_at)
- waitlist (id, resource_id→resources.id, user_id→users.id, desired_start, desired_end, created_at, updated_at)

Key relations:
- users 1→N resources
- users 1→N bookings
- resources 1→N bookings
- resources 1→N reviews
- message_threads 1→N messages


