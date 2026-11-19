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


class PlayerApiTestCase(ApiTestCase):
    def setUp(self):
        super().setUp()
        self.add("Imagine", "John Lennon", 183)
        self.add("Help", "The Beatles", 140)
        self.add("Yesterday", "The Beatles", 125)

    def song_ref(self, title, artist):
        return {"title": title, "artist": artist}

    def add_to_playlist(self, title, artist):
        return self.client.post("/api/playlist", json=self.song_ref(title, artist))

    def enqueue(self, title, artist):
        return self.client.post("/api/queue", json=self.song_ref(title, artist))

    def titles(self, songs):
        return [song["title"] for song in songs]

    def now_playing_title(self, state):
        if state["now_playing"] is None:
            return None
        return state["now_playing"]["title"]


class TestPlaylistRoutes(PlayerApiTestCase):
    def test_playlist_starts_empty(self):
        response = self.client.get("/api/playlist")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_add_to_playlist_keeps_order(self):
        response = self.add_to_playlist("help", "the beatles")
        self.add_to_playlist("Imagine", "John Lennon")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["title"], "Help")
        self.assertEqual(
            self.titles(self.client.get("/api/playlist").get_json()),
            ["Help", "Imagine"],
        )

    def test_same_song_can_repeat_in_playlist(self):
        self.add_to_playlist("Help", "The Beatles")
        self.add_to_playlist("Help", "The Beatles")

        self.assertEqual(
            self.titles(self.client.get("/api/playlist").get_json()),
            ["Help", "Help"],
        )

    def test_add_missing_song_to_playlist_returns_404(self):
        response = self.add_to_playlist("Nada", "Ninguem")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json(), {"error": "Musica nao encontrada."})

    def test_add_to_playlist_without_artist_returns_400(self):
        response = self.client.post("/api/playlist", json={"title": "Help"})

        self.assertEqual(response.status_code, 400)

    def test_remove_from_playlist(self):
        self.add_to_playlist("Help", "The Beatles")
        self.add_to_playlist("Imagine", "John Lennon")

        response = self.client.delete(
            "/api/playlist", query_string=self.song_ref("Help", "The Beatles")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["title"], "Help")
        self.assertEqual(
            self.titles(self.client.get("/api/playlist").get_json()), ["Imagine"]
        )

    def test_remove_song_not_in_playlist_returns_404(self):
        response = self.client.delete(
            "/api/playlist", query_string=self.song_ref("Help", "The Beatles")
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.get_json(), {"error": "A musica nao esta na playlist"}
        )


class TestQueueRoutes(PlayerApiTestCase):
    def test_queue_starts_empty(self):
        response = self.client.get("/api/queue")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_enqueue_keeps_fifo_order(self):
        response = self.enqueue("Yesterday", "The Beatles")
        self.enqueue("Help", "The Beatles")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["title"], "Yesterday")
        self.assertEqual(
            self.titles(self.client.get("/api/queue").get_json()),
            ["Yesterday", "Help"],
        )

    def test_enqueue_missing_song_returns_404(self):
        response = self.enqueue("Nada", "Ninguem")

        self.assertEqual(response.status_code, 404)

    def test_enqueue_without_body_returns_400(self):
        response = self.client.post("/api/queue")

        self.assertEqual(response.status_code, 400)


class TestPlayerRoutes(PlayerApiTestCase):
    def test_initial_state(self):
        response = self.client.get("/api/player")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get_json(),
            {
                "now_playing": None,
                "repeat": False,
                "playlist": [],
                "up_next": [],
                "history": [],
            },
        )

    def test_play_with_nothing_returns_state_with_null(self):
        response = self.client.post("/api/player/play")

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.get_json()["now_playing"])

    def test_play_starts_first_song_of_playlist(self):
        self.add_to_playlist("Help", "The Beatles")
        self.add_to_playlist("Imagine", "John Lennon")

        state = self.client.post("/api/player/play").get_json()

        self.assertEqual(self.now_playing_title(state), "Help")
        self.assertEqual(state["now_playing"]["formatted_duration"], "2:20")

    def test_play_twice_keeps_same_song(self):
        self.add_to_playlist("Help", "The Beatles")
        self.add_to_playlist("Imagine", "John Lennon")

        self.client.post("/api/player/play")
        state = self.client.post("/api/player/play").get_json()

        self.assertEqual(self.now_playing_title(state), "Help")
        self.assertEqual(state["history"], [])

    def test_next_advances_and_fills_history(self):
        self.add_to_playlist("Help", "The Beatles")
        self.add_to_playlist("Imagine", "John Lennon")
        self.add_to_playlist("Yesterday", "The Beatles")

        self.client.post("/api/player/play")
        self.client.post("/api/player/next")
        state = self.client.post("/api/player/next").get_json()

        self.assertEqual(self.now_playing_title(state), "Yesterday")
        # historico do mais recente para o mais antigo
        self.assertEqual(self.titles(state["history"]), ["Imagine", "Help"])

    def test_queue_has_priority_over_playlist(self):
        self.add_to_playlist("Help", "The Beatles")
        self.add_to_playlist("Imagine", "John Lennon")
        self.client.post("/api/player/play")
        self.enqueue("Yesterday", "The Beatles")

        state = self.client.post("/api/player/next").get_json()
        self.assertEqual(self.now_playing_title(state), "Yesterday")
        self.assertEqual(state["up_next"], [])

        # depois da fila, a playlist continua de onde parou
        state = self.client.post("/api/player/next").get_json()
        self.assertEqual(self.now_playing_title(state), "Imagine")

    def test_end_of_playlist_without_repeat_stops(self):
        self.add_to_playlist("Help", "The Beatles")
        self.add_to_playlist("Imagine", "John Lennon")

        self.client.post("/api/player/play")
        self.client.post("/api/player/next")
        state = self.client.post("/api/player/next").get_json()

        self.assertIsNone(state["now_playing"])

        # play recomeca do inicio
        state = self.client.post("/api/player/play").get_json()
        self.assertEqual(self.now_playing_title(state), "Help")

    def test_end_of_playlist_with_repeat_goes_back_to_first(self):
        self.add_to_playlist("Help", "The Beatles")
        self.add_to_playlist("Imagine", "John Lennon")
        self.client.put("/api/player/repeat", json={"enabled": True})

        self.client.post("/api/player/play")
        self.client.post("/api/player/next")
        state = self.client.post("/api/player/next").get_json()

        self.assertEqual(self.now_playing_title(state), "Help")

    def test_previous_goes_back_in_history(self):
        self.add_to_playlist("Help", "The Beatles")
        self.add_to_playlist("Imagine", "John Lennon")

        self.client.post("/api/player/play")
        self.client.post("/api/player/next")
        response = self.client.post("/api/player/previous")
        state = response.get_json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.now_playing_title(state), "Help")
        self.assertEqual(state["history"], [])

    def test_previous_without_history_returns_400(self):
        response = self.client.post("/api/player/previous")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json(), {"error": "Nao ha musica anterior"})

    def test_set_repeat_on_and_off(self):
        response = self.client.put("/api/player/repeat", json={"enabled": True})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["repeat"])

        state = self.client.put("/api/player/repeat", json={"enabled": False}).get_json()
        self.assertFalse(state["repeat"])
        self.assertFalse(self.client.get("/api/player").get_json()["repeat"])

    def test_set_repeat_with_invalid_value_returns_400(self):
        for body in ({}, {"enabled": "sim"}, {"enabled": 1}, {"enabled": None}):
            with self.subTest(body=body):
                response = self.client.put("/api/player/repeat", json=body)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.get_json())

    def test_wrong_method_is_not_allowed(self):
        response = self.client.get("/api/player/next")

        self.assertEqual(response.status_code, 405)


class TestRemoveSongInUse(PlayerApiTestCase):
    def assert_cannot_remove_help(self):
        response = self.client.delete(
            "/api/songs", query_string=self.song_ref("Help", "The Beatles")
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("em uso", response.get_json()["error"])
        self.assertIn("Help", self.titles(self.client.get("/api/songs").get_json()))

    def test_cannot_remove_song_in_playlist(self):
        self.add_to_playlist("Help", "The Beatles")
        self.assert_cannot_remove_help()

    def test_cannot_remove_song_in_queue(self):
        self.enqueue("Help", "The Beatles")
        self.assert_cannot_remove_help()

    def test_cannot_remove_song_playing(self):
        self.enqueue("Help", "The Beatles")
        self.client.post("/api/player/play")
        self.assert_cannot_remove_help()

    def test_can_remove_song_after_it_leaves_playlist(self):
        self.add_to_playlist("Help", "The Beatles")
        self.client.delete(
            "/api/playlist", query_string=self.song_ref("Help", "The Beatles")
        )

        response = self.client.delete(
            "/api/songs", query_string=self.song_ref("Help", "The Beatles")
        )

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
