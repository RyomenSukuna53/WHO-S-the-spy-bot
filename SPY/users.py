from datetime import datetime
from SPY.db import users_col
import math

# Helper Functions
def add_user(user_id, username):
    """
    Add a new user to the database with initial stats if they don't already exist.
    """
    if not users_col.find_one({"user_id": user_id}):
        users_col.insert_one({
            "user_id": user_id,
            "firstname": first_name,
            "username": username,
            "start_date": datetime.now().strftime("%d-%m-%Y")
        })
