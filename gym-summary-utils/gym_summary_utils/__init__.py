def generate_booking_summary(username, bookings):
    """Create a simple summary of a user's gym bookings."""
    return {
        "username": username,
        "total_bookings": len(bookings),
        "classes": [
            booking["name"] for booking in bookings
        ],
    }