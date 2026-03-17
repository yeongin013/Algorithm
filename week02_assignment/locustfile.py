from locust import HttpUser, task


class ShopUser(HttpUser):
    @task
    def search_by_id(self):
        self.client.get("/search/id?id=42")

    @task
    def search_by_name(self):
        self.client.get("/search/name?q=laptop")

    @task
    def find_duplicates(self):
        self.client.get("/search/duplicates")
