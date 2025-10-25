import json
import os
from logs import logger
import config

# The file where we will store the list of approved user IDs
APPROVAL_FILE = config.APPROVAL_FILE

def load_approved_users():
    """Loads the set of approved user IDs from the JSON file."""
    if not os.path.exists(APPROVAL_FILE):
        return set()  # Return an empty set if the file doesn't exist
    
    try:
        with open(APPROVAL_FILE, 'r') as f:
            user_ids = json.load(f)
            # Convert the list from the file into a set for fast lookups
            return set(user_ids)
    except json.JSONDecodeError:
        logger.error(f"Error reading approval file {APPROVAL_FILE}. Creating a new one.")
        return set()
    except Exception as e:
        logger.error(f"An error occurred loading approved users: {e}")
        return set()

def save_approved_users(user_set):
    """Saves the set of approved user IDs back to the JSON file."""
    try:
        with open(APPROVAL_FILE, 'w') as f:
            # Convert the set to a list to save it in JSON format
            json.dump(list(user_set), f, indent=4)
    except Exception as e:
        logger.error(f"Failed to save approval file: {e}")

def add_user(user_id):
    """Adds a new user ID to the approved list."""
    try:
        user_id_int = int(user_id)
        approved_users = load_approved_users()
        
        if user_id_int in approved_users:
            return False  # User was already approved
            
        approved_users.add(user_id_int)
        save_approved_users(approved_users)
        logger.info(f"User {user_id_int} has been added to the approval list.")
        return True  # User successfully added
    except Exception as e:
        logger.error(f"Failed to add user {user_id}: {e}")
        return False

def is_user_approved(user_id):
    """Checks if a user ID is in the approved list."""
    # Always approve the Admin
    if user_id == config.ADMIN_USER_ID:
        return True
        
    approved_users = load_approved_users()
    return user_id in approved_users
