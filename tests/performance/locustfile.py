from locust import HttpUser, between, task

EMAIL = 'john@simplylift.co'
PURCHASE = {
    'competition': 'Spring Festival',
    'club': 'Simply Lift',
    'places': '1',
}


class SecretaryUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.client.get('/')

    @task(3)
    def load_competitions(self):
        self.client.post(
            '/showSummary',
            data={'email': EMAIL},
            name='/showSummary (competition list)',
        )

    @task(1)
    def update_points(self):
        self.client.post(
            '/purchasePlaces',
            data=PURCHASE,
            name='/purchasePlaces (points update)',
        )

    @task(1)
    def view_points_board(self):
        self.client.get('/pointsDisplay')
