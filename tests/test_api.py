import unittest
from backend.api.app import create_app


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        # app novo a cada teste: biblioteca e player comecam vazios
        self.client = create_app().test_client()

    def add(self, title, artist, duration):
        return self.client.post(
            "/api/songs",
            json={"title": title, "artist": artist, "duration": duration},
        )


class TestLibraryRoutes(ApiTestCase):
    def test_add_song_returns_201_and_song(self):
        response = self.add("Imagine", "John Lennon", 183)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.get_json(),
            {
                "title": "Imagine",
                "artist": "John Lennon",
                "duration": 183,
                "formatted_duration": "3:03",
            },
        )

    def test_add_song_accepts_duration_as_numeric_string(self):
        response = self.add("Imagine", "John Lennon", "183")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["duration"], 183)

    def test_add_duplicate_song_returns_400(self):
        self.add("Imagine", "John Lennon", 183)
        response = self.add("imagine", "john lennon", 200)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_add_same_title_other_artist_is_allowed(self):
        self.add("Imagine", "John Lennon", 183)
        response = self.add("Imagine", "A Perfect Circle", 288)

        self.assertEqual(response.status_code, 201)

    def test_add_song_without_json_body_returns_400(self):
        response = self.client.post("/api/songs", data="nao e json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_add_song_with_json_list_returns_400(self):
        response = self.client.post("/api/songs", json=["Imagine"])

        self.assertEqual(response.status_code, 400)

    def test_add_song_missing_fields_returns_400(self):
        for body in (
            {"artist": "John Lennon", "duration": 183},
            {"title": "Imagine", "duration": 183},
            {"title": "Imagine", "artist": "John Lennon"},
        ):
            with self.subTest(body=body):
                response = self.client.post("/api/songs", json=body)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.get_json())

    def test_add_song_with_wrong_types_returns_400(self):
        for title, artist, duration in (
            (123, "John Lennon", 183),
            ("Imagine", ["x"], 183),
            ("   ", "John Lennon", 183),
            ("Imagine", "John Lennon", True),
            ("Imagine", "John Lennon", 3.5),
            ("Imagine", "John Lennon", "abc"),
            ("Imagine", "John Lennon", 0),
            ("Imagine", "John Lennon", -10),
        ):
            with self.subTest(title=title, artist=artist, duration=duration):
                response = self.add(title, artist, duration)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.get_json())

    def test_list_songs_empty(self):
        response = self.client.get("/api/songs")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_list_songs_by_title_is_default(self):
        self.add("Yesterday", "The Beatles", 125)
        self.add("Imagine", "John Lennon", 183)
        self.add("Help", "The Beatles", 140)

        titles = [song["title"] for song in self.client.get("/api/songs").get_json()]

        self.assertEqual(titles, ["Help", "Imagine", "Yesterday"])

    def test_list_songs_by_duration(self):
        self.add("Yesterday", "The Beatles", 125)
        self.add("Imagine", "John Lennon", 183)
        self.add("Help", "The Beatles", 90)

        response = self.client.get("/api/songs?order=duration")
        durations = [song["duration"] for song in response.get_json()]

        self.assertEqual(durations, [90, 125, 183])

    def test_list_songs_invalid_order_returns_400(self):
        response = self.client.get("/api/songs?order=artist")

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_search_returns_all_songs_with_title(self):
        self.add("Imagine", "John Lennon", 183)
        self.add("Imagine", "A Perfect Circle", 288)
        self.add("Help", "The Beatles", 140)

        response = self.client.get("/api/songs/search?title=  IMAGINE ")
        artists = sorted(song["artist"] for song in response.get_json())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(artists, ["A Perfect Circle", "John Lennon"])

    def test_search_not_found_returns_empty_list(self):
        response = self.client.get("/api/songs/search?title=Nada")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_search_without_title_returns_400(self):
        response = self.client.get("/api/songs/search")

        self.assertEqual(response.status_code, 400)

    def test_remove_song(self):
        self.add("Imagine", "John Lennon", 183)

        response = self.client.delete(
            "/api/songs", query_string={"title": "imagine", "artist": "JOHN LENNON"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["title"], "Imagine")
        self.assertEqual(self.client.get("/api/songs").get_json(), [])

    def test_remove_missing_song_returns_404_with_clean_message(self):
        response = self.client.delete(
            "/api/songs", query_string={"title": "Imagine", "artist": "John Lennon"}
        )

        self.assertEqual(response.status_code, 404)
        # mensagem sem as aspas extras que str(KeyError) colocaria
        self.assertEqual(response.get_json(), {"error": "Musica nao encontrada."})

    def test_remove_without_artist_returns_400(self):
        response = self.client.delete("/api/songs", query_string={"title": "Imagine"})

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
