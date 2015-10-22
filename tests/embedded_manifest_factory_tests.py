import unittest
import ddt
from create_embedded_manifest import EmbeddedManifestFactory


TEST_THEME = "SummerSanFrancisco"
TEST_STATE = "DayDefault"

TEST_THEMES = ["SummerSanFrancisco", "WinterSanFrancisco"]
TEST_STATES = ["DayDefault", "DayRainy"]


@ddt.ddt
class EmbeddedManifestFactoryTests(unittest.TestCase):

    def _create_test_factory(self):
        factory = EmbeddedManifestFactory(None, [TEST_THEME], [TEST_STATE], "", download_textures=False)
        return factory

    def _create_multi_theme_test_factory(self):
        factory = EmbeddedManifestFactory(None, TEST_THEMES, TEST_STATES, "", download_textures=False)
        return factory

    @ddt.data(
        [],
        [{"Name": "SummerNewYork", "States": []}],
        [{"Name": "WinterSanFrancisco", "States": []}],
    )
    def test_raises_exception_if_missing_single_theme(self, data):
        manifest_json = {"Themes": data}
        factory = self._create_test_factory()
        self.assertRaises(ValueError, lambda: factory.create_embedded_manifest_from_json(manifest_json))

    @ddt.data(
        [],
        [{"Name": "SummerSanFrancisco", "States": []}],
        [{"Name": "WinterSanFrancisco", "States": []}, {"Name": "SummerNewYork", "States": []}],
    )
    def test_raises_exception_if_missing_some_themes(self, data):
        manifest_json = {"Themes": data}
        factory = self._create_multi_theme_test_factory()
        self.assertRaises(ValueError, lambda: factory.create_embedded_manifest_from_json(manifest_json))

    @ddt.data(
        [],
        [{"Name": "DayRainy", "States": []}],
        [{"Name": "DayRainy", "States": []}, {"Name": "NightDefault", "States": []}]
    )
    def test_raises_exception_if_missing_single_state(self, data):
        manifest_json = {"Themes": [{"Name": TEST_THEME, "States": data}]}
        factory = self._create_test_factory()
        self.assertRaises(ValueError, lambda: factory.create_embedded_manifest_from_json(manifest_json))

    @ddt.data(
        [],
        [{"Name": "DayRainy", "States": []}],
        [{"Name": "DayDefault", "States": []}, {"Name": "NightDefault", "States": []}]
    )
    def test_raises_exception_if_missing_some_states(self, data):
        manifest_json = {"Themes": [{"Name": TEST_THEMES[0], "States": data},
                                    {"Name": TEST_THEMES[1], "States": data}]}
        factory = self._create_multi_theme_test_factory()
        self.assertRaises(ValueError, lambda: factory.create_embedded_manifest_from_json(manifest_json))

    def test_correct_theme_chosen(self):
        correct_states = [{"Name": TEST_STATE, "Textures": {} }]
        correct_theme = {"Name": TEST_THEME, "States": correct_states}
        manifest_json = {
            "Themes": [
                {"Name": "SummerNewYork", "States": correct_states},
                {"Name": "WinterSanFrancisco", "States": correct_states},
                correct_theme
            ]
        }
        factory = self._create_test_factory()
        output_json = factory.create_embedded_manifest_from_json(manifest_json)
        self.assertEqual(output_json["Themes"], [correct_theme])

    def test_correct_state_chosen(self):
        correct_state = {"Name": TEST_STATE, "Textures": {}}
        manifest_json = {
            "Themes": [{
                 "Name": TEST_THEME,
                 "States": [
                     {"Name": "DayRainy", "Textures": {}},
                     correct_state,
                     {"Name": "NightDefault", "Textures": {}}
                 ]
            }]
        }
        factory = self._create_test_factory()
        output_json = factory.create_embedded_manifest_from_json(manifest_json)
        self.assertEqual(output_json["Themes"][0]["States"], [correct_state])

    def test_correct_themes_chosen(self):
        correct_states = [{"Name": TEST_STATES[0], "Textures": {} }, {"Name": TEST_STATES[1], "Textures": {} }]
        correct_theme0 = {"Name": TEST_THEMES[0], "States": correct_states}
        correct_theme1 = {"Name": TEST_THEMES[1], "States": correct_states}
        manifest_json = {
            "Themes": [correct_theme1,
                       {"Name": "WinterNewYork", "States": correct_states},
                       correct_theme0]
        }
        factory = self._create_multi_theme_test_factory()
        output_json = factory.create_embedded_manifest_from_json(manifest_json)
        correct_themes = [correct_theme0, correct_theme1]
        self.assertTrue(
            all(((theme in correct_themes)
                 for theme in output_json["Themes"])))

    def test_correct_states_chosen(self):
        correct_state0 = {"Name": TEST_STATES[0], "Textures": {}}
        correct_state1 = {"Name": TEST_STATES[1], "Textures": {}}
        manifest_json = {
            "Themes": [{
                 "Name": TEST_THEMES[0],
                 "States": [
                     correct_state0,
                     correct_state1,
                     {"Name": "NightDefault", "Textures": {}}
                 ]
            },
            {
                 "Name": TEST_THEMES[1],
                 "States": [
                     correct_state1,
                     {"Name": "NightDefault", "Textures": {}},
                     correct_state0,
                 ]
            }]
        }
        factory = self._create_multi_theme_test_factory()
        output_json = factory.create_embedded_manifest_from_json(manifest_json)
        correct_states = [correct_state0, correct_state1]
        themes = output_json["Themes"]
        all_states = [state
                      for theme in themes
                      for state in theme["States"]]
        self.assertTrue(
            all((state in correct_states)
                for state in all_states))

    @ddt.data(
        (".png.gz", ".png"),
        (".png", ".png"),
        (".ktx.gz", ".ktx"),
        (".ktx", ".ktx"),
        (".pvr.gz", ".pvr"),
        (".pvr", ".pvr"),
        (".dds.gz", ".dds"),
        (".dds", ".dds")
    )
    def test_correct_texture_file_extensions_given(self, data):
        pre_ext, post_ext = data
        manifest_json = {
            "AssetRoot_Platform": "http://url.com",
            "AssetExtension_Platform": pre_ext,
            "Themes": [{
                "Name": TEST_THEME,
                "States": [{
                    "Name": TEST_STATE,
                    "Textures": {}
                }]
            }]
        }
        factory = self._create_test_factory()
        output_json = factory.create_embedded_manifest_from_json(manifest_json)
        self.assertEqual(post_ext, output_json["AssetExtension_Platform"])

    def test_textures_renamed_recursively(self):
        pre_texture_name = "Under/Score"
        post_texture_name = "Under_Score"
        manifest_json = {
            "Themes": [{
                "Name": TEST_THEME,
                "States": [{
                    "Name": TEST_STATE,
                    "Textures": {
                        "Texture0": pre_texture_name,
                        "TextureDict0": {
                            "Texture1": pre_texture_name,
                            "Texture2": pre_texture_name,
                            "TextureDict1": {
                                "Texture3": pre_texture_name
                            }
                        }
                    }
                }]
            }]
        }
        factory = self._create_test_factory()
        output_json = factory.create_embedded_manifest_from_json(manifest_json)
        textures = output_json["Themes"][0]["States"][0]["Textures"]
        texture_names = [
            textures["Texture0"],
            textures["TextureDict0"]["Texture1"],
            textures["TextureDict0"]["Texture2"],
            textures["TextureDict0"]["TextureDict1"]["Texture3"]
        ]
        self.assertTrue(all(name == post_texture_name for name in texture_names))

    @ddt.data(
        ("Texture", "Texture"),
        ("Texture_0", "Texture_0"),
        ("Textures/Texture_1", "Textures_Texture_1"),
        ("Theme/Texture_Files/Texture_1", "Theme_Texture_Files_Texture_1")
    )
    def test_texture_name_slashes_to_underscores(self, data):
        pre_texture_name, post_texture_name = data
        manifest_json = {
            "Themes": [{
                "Name": TEST_THEME,
                "States": [{
                    "Name": TEST_STATE,
                    "Textures": {
                        "Texture0": pre_texture_name
                    }
                }]
            }]
        }
        factory = self._create_test_factory()
        output_json = factory.create_embedded_manifest_from_json(manifest_json)
        texture_name = output_json["Themes"][0]["States"][0]["Textures"]["Texture0"]
        self.assertEqual(post_texture_name, texture_name)

    def test_vehicles_removed_from_manifest(self):
        manifest_json = {
            "Themes": [{
                "Name": TEST_THEME,
                "States": [{
                    "Name": TEST_STATE,
                    "Textures": {}
                }],
                "PlaneVehicles": [],
                "RailVehicles": [],
                "TramVehicles": [],
                "RoadVehicles": [],
                "SpaceVehicles": []
            }]
        }
        factory = self._create_test_factory()
        output_json = factory.create_embedded_manifest_from_json(manifest_json)
        theme = manifest_json["Themes"][0]
        vehicle_keys = ["PlaneVehicles", "RailVehicles", "TramVehicles", "RoadVehicles", "SpaceVehicles"]
        self.assertFalse(any(key in theme for key in vehicle_keys))

    def test_landmark_postfix_for_one_theme_stored(self):
        manifest_json = {
            "Themes": [{"Name": TEST_THEME,
                        "States": [
                            {"Name": TEST_STATE, "Textures": {}, "LandmarkPostfix": "A"},
                            {"Name": "WinterNewYork", "Textures": {}, "LandmarkPostfix": "B"},
                            {"Name": "WinterIsComing", "Textures": {} },
                        ]}]
        }
        factory = self._create_test_factory()
        output_json = factory.create_embedded_manifest_from_json(manifest_json)
        self.assertEqual(set(output_json["LandmarkTexturePostfixes"]), set(("A", "B")))

    def test_landmark_postfix_for_multiple_themes_stored(self):
        manifest_json = {
            "Themes": [{"Name": TEST_THEMES[0],
                        "States": [
                            {"Name": TEST_STATES[0], "Textures": {}, "LandmarkPostfix": "A"},
                            {"Name": TEST_STATES[1], "Textures": {}, "LandmarkPostfix": "B"},
                            {"Name": "WinterIsComing", "Textures": {}, "LandmarkPostfix": "C"},
                        ]},
                       {"Name": TEST_THEMES[1],
                        "States": [
                            {"Name": TEST_STATES[0], "Textures": {}, "LandmarkPostfix": "D"},
                            {"Name": TEST_STATES[1], "Textures": {}, "LandmarkPostfix": "E"},
                            {"Name": "WinterIsComing", "Textures": {} },
                        ]}]
        }
        factory = self._create_multi_theme_test_factory()
        output_json = factory.create_embedded_manifest_from_json(manifest_json)
        self.assertEqual(set(output_json["LandmarkTexturePostfixes"]), set(("A", "B", "C", "D", "E")))


if __name__ == "__main__":
    unittest.main()
