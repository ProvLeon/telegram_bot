from collections import defaultdict

class UserProfileManager:
    def __init__(self):
        self.profiles = defaultdict(dict)

    def set_profile(self, user_id, profile_data):
        self.profiles[user_id] = profile_data

    def get_profile(self, user_id):
        return self.profiles.get(user_id, {})
