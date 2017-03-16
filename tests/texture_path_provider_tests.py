import unittest
import ddt
from create_embedded_manifest import TexturePathProvider


@ddt.ddt
class TexturePathProviderTests(unittest.TestCase):
    @ddt.data(
        ("", ".png", ".png"),
        ("texture", ".ktx", "texture.ktx"),
        ("texture.ktx", ".png", "texture.ktx.png"),
        ("tex", ".png.gz", "tex.png.gz")
    )
    def test_correct_extension_given(self, data):
        filename, extension, result = data
        tpp = TexturePathProvider("", extension, False)
        self.assertEqual(tpp.get_path(filename), result)

    @ddt.data(
        ("", "assets/", "assets/"),
        ("texture", "/", "/texture"),
        ("texture", "assets/", "assets/texture"),
        ("texture.png", "assets/", "assets/texture.png"),
        ("tex", "http://cnd.thing.com/", "http://cnd.thing.com/tex")
    )
    def test_correct_root_path_given(self, data):
        filename, rootpath, result = data
        tpp = TexturePathProvider(rootpath, "", False)
        self.assertEqual(tpp.get_path(filename), result)

    @ddt.data(
        ("", "assets/.ktx.gz"),
        ("tex", "assets/tex.ktx.gz"),
        ("sanfran/tex", "assets/sanfran/tex.ktx.gz"),
        ("tex.png", "assets/tex.png.ktx.gz")
    )
    def test_correct_path(self, data):
        filename, result = data
        tpp = TexturePathProvider("assets/", ".ktx.gz", False)
        self.assertEqual(tpp.get_path(filename), result)


if __name__ == "__main__":
    unittest.main()