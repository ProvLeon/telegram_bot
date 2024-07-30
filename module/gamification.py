from collections import defaultdict

class GamificationManager:
    def __init__(self):
        self.points = defaultdict(int)
        self.badges = defaultdict(list)

    def add_points(self, user_id, points):
        self.points[user_id] += points

    def get_points(self, user_id):
        return self.points[user_id]

    def add_badge(self, user_id, badge):
        self.badges[user_id].append(badge)

    def get_badges(self, user_id):
        return self.badges[user_id]
