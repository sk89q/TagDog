from unittest import TestCase
from tagdog import genre_case

class GenreNameCaseTest(TestCase):
    def test_case(self):
        self.assertEquals("Punk", genre_case("punk"))
        self.assertEquals("Post-Hardcore", genre_case("post-hardcore"))
        self.assertEquals("8-Bit", genre_case("8-bit"))
        self.assertEquals("Pop Punk", genre_case("pop punk"))
        self.assertEquals("Drum and Bass", genre_case("drum and bass"))
        self.assertEquals("80s", genre_case("80s"))
        self.assertEquals("R&B", genre_case("r&b"))