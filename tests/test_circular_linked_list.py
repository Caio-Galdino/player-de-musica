import unittest

from backend.structures.circular_linked_list import CircularLinkedList


class TestCircularLinkedList(unittest.TestCase):
    def test_new_list_is_empty(self):
        playlist = CircularLinkedList()
        self.assertTrue(playlist.is_empty())
        self.assertEqual(playlist.size(), 0)
        self.assertEqual(playlist.to_list(), [])

    def test_navigation_on_empty_list_raises(self):
        playlist = CircularLinkedList()
        for operation in (playlist.next, playlist.prev, playlist.current):
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(IndexError):
                    operation()

    def test_single_node_wraps_in_both_directions(self):
        playlist = CircularLinkedList()
        playlist.append("Imagine")
        self.assertEqual(playlist.current(), "Imagine")
        self.assertEqual(playlist.next(), "Imagine")
        self.assertEqual(playlist.prev(), "Imagine")
        self.assertEqual(playlist.size(), 1)

    def test_append_preserves_order_and_current_song(self):
        playlist = CircularLinkedList()
        playlist.append(1)
        playlist.append(2)
        playlist.next()
        playlist.append(3)
        self.assertEqual(playlist.to_list(), [1, 2, 3])
        self.assertEqual(playlist.current(), 2)
        self.assertEqual(playlist.size(), 3)

    def test_navigation_wraps_in_both_directions(self):
        playlist = CircularLinkedList()
        for value in (1, 2, 3):
            playlist.append(value)
        self.assertEqual([playlist.next() for _ in range(4)], [2, 3, 1, 2])
        self.assertEqual([playlist.prev() for _ in range(4)], [1, 3, 2, 1])

    def test_remove_head_middle_and_tail_preserves_navigation(self):
        for removed, expected in ((1, [2, 3]), (2, [1, 3]), (3, [1, 2])):
            with self.subTest(removed=removed):
                playlist = CircularLinkedList()
                for value in (1, 2, 3):
                    playlist.append(value)
                playlist.remove(removed)
                self.assertEqual(playlist.to_list(), expected)
                self.assertEqual(playlist.size(), 2)
                self.assertEqual(playlist.current(), expected[0])
                self.assertEqual(playlist.prev(), expected[-1])
                self.assertEqual(playlist.next(), expected[0])

    def test_remove_current_advances_to_next_song(self):
        for removed, expected_current in ((2, 3), (3, 1)):
            with self.subTest(removed=removed):
                playlist = CircularLinkedList()
                for value in (1, 2, 3):
                    playlist.append(value)
                while playlist.current() != removed:
                    playlist.next()
                playlist.remove(removed)
                self.assertEqual(playlist.current(), expected_current)

    def test_remove_only_first_occurrence_from_head(self):
        playlist = CircularLinkedList()
        for value in (1, 2, 1):
            playlist.append(value)
        playlist.prev()
        playlist.remove(1)
        self.assertEqual(playlist.to_list(), [2, 1])
        self.assertEqual(playlist.current(), 1)
        self.assertEqual(playlist.next(), 2)

    def test_remove_missing_value_does_not_modify_list(self):
        playlist = CircularLinkedList()
        with self.assertRaises(ValueError):
            playlist.remove(99)
        playlist.append(1)
        playlist.append(2)
        with self.assertRaises(ValueError):
            playlist.remove(99)
        self.assertEqual(playlist.to_list(), [1, 2])
        self.assertEqual(playlist.current(), 1)
        self.assertEqual(playlist.size(), 2)

    def test_remove_last_song_and_reuse_list(self):
        playlist = CircularLinkedList()
        playlist.append(1)
        playlist.remove(1)
        self.assertTrue(playlist.is_empty())
        self.assertEqual(playlist.size(), 0)
        self.assertEqual(playlist.to_list(), [])
        for operation in (playlist.next, playlist.prev, playlist.current):
            with self.assertRaises(IndexError):
                operation()
        playlist.append(2)
        playlist.append(3)
        self.assertEqual(playlist.to_list(), [2, 3])
        self.assertEqual(playlist.prev(), 3)
        self.assertEqual(playlist.next(), 2)

    def test_none_is_a_valid_value(self):
        playlist = CircularLinkedList()
        playlist.append(None)
        self.assertFalse(playlist.is_empty())
        self.assertIsNone(playlist.current())
        self.assertEqual(playlist.to_list(), [None])
        playlist.remove(None)
        self.assertTrue(playlist.is_empty())

    def test_is_at_end_on_empty_list_raises(self):
        playlist = CircularLinkedList()
        with self.assertRaisesRegex(IndexError, "^A lista esta vazia$"):
            playlist.is_at_end()

    def test_is_at_end_tracks_last_node_and_wraparound(self):
        playlist = CircularLinkedList()
        for value in (1, 2, 3):
            playlist.append(value)
        self.assertFalse(playlist.is_at_end())
        self.assertEqual(playlist.current(), 1)
        playlist.next()
        self.assertFalse(playlist.is_at_end())
        playlist.next()
        self.assertTrue(playlist.is_at_end())
        self.assertEqual(playlist.current(), 3)
        playlist.next()
        self.assertFalse(playlist.is_at_end())
        self.assertEqual(playlist.current(), 1)

    def test_is_at_end_with_single_element(self):
        playlist = CircularLinkedList()
        playlist.append(1)
        self.assertTrue(playlist.is_at_end())

    def test_is_at_end_distinguishes_nodes_with_duplicate_values(self):
        playlist = CircularLinkedList()
        for value in (1, 2, 1):
            playlist.append(value)
        self.assertFalse(playlist.is_at_end())
        playlist.prev()
        self.assertTrue(playlist.is_at_end())
        playlist.next()
        self.assertFalse(playlist.is_at_end())

    def test_remove_current_on_empty_list_raises(self):
        playlist = CircularLinkedList()
        with self.assertRaisesRegex(IndexError, "^A lista esta vazia$"):
            playlist.remove_current()

    def test_remove_current_returns_value_and_advances(self):
        playlist = CircularLinkedList()
        for value in (1, 2, 3):
            playlist.append(value)
        self.assertEqual(playlist.remove_current(), 1)
        self.assertEqual(playlist.current(), 2)
        self.assertEqual(playlist.to_list(), [2, 3])
        self.assertEqual(playlist.size(), 2)
        self.assertEqual(playlist.prev(), 3)
        self.assertEqual(playlist.next(), 2)

    def test_remove_current_removes_selected_duplicate(self):
        playlist = CircularLinkedList()
        for value in (1, 2, 1):
            playlist.append(value)
        playlist.next()
        playlist.next()
        self.assertEqual(playlist.remove_current(), 1)
        self.assertEqual(playlist.to_list(), [1, 2])
        self.assertEqual(playlist.size(), 2)
        self.assertEqual(playlist.current(), 1)
        self.assertEqual(playlist.prev(), 2)

    def test_remove_current_only_element_allows_reuse(self):
        playlist = CircularLinkedList()
        playlist.append(1)
        self.assertEqual(playlist.remove_current(), 1)
        self.assertTrue(playlist.is_empty())
        self.assertEqual(playlist.size(), 0)
        self.assertEqual(playlist.to_list(), [])
        with self.assertRaisesRegex(IndexError, "^A lista esta vazia$"):
            playlist.current()
        playlist.append(2)
        self.assertEqual(playlist.current(), 2)
        self.assertEqual(playlist.size(), 1)
        self.assertEqual(playlist.to_list(), [2])
        self.assertTrue(playlist.is_at_end())
        self.assertEqual(playlist.next(), 2)
        self.assertEqual(playlist.prev(), 2)

    def test_remove_current_last_node_wraps_to_head(self):
        playlist = CircularLinkedList()
        for value in (1, 2, 3):
            playlist.append(value)
        playlist.prev()
        self.assertEqual(playlist.remove_current(), 3)
        self.assertEqual(playlist.current(), 1)
        self.assertEqual(playlist.to_list(), [1, 2])
        self.assertEqual(playlist.size(), 2)
        self.assertFalse(playlist.is_at_end())
        self.assertEqual(playlist.prev(), 2)
        self.assertTrue(playlist.is_at_end())
        self.assertEqual(playlist.next(), 1)


if __name__ == "__main__":
    unittest.main()
