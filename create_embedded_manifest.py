import argparse
import gzip
import json
import os
import urllib2
import cStringIO


def remove_suffix(string, suffix):
    if string.endswith(suffix):
        suffix_length = len(suffix)
        return string[:-suffix_length]
    else:
        return string


class TexturePathProvider:
    def __init__(self, asset_root_path, asset_ext):
        self._asset_root_path = asset_root_path
        self._asset_ext = asset_ext

    def get_path(self, relative_path):
        return "{0}{1}{2}".format(self._asset_root_path, relative_path, self._asset_ext)


class EmbeddedManifestFactory:
    def __init__(self, source_manifest, theme_names, state_names, output_dir, download_textures=True):
        self._source_manifest = source_manifest
        self._theme_names = set(theme_names)
        self._state_names = set(state_names)
        self._output_dir = output_dir
        self._should_download_textures = download_textures

    def create_embedded_manifest(self):
        manifest_json = self._get_manifest_json(self._source_manifest)
        embedded_manifest_json = self.create_embedded_manifest_from_json(manifest_json)
        self._write_embedded_manifest_file(embedded_manifest_json)

    def create_embedded_manifest_from_json(self, manifest_json):
        all_landmark_postfixes = self._get_all_landmark_postfixes(manifest_json)
        manifest_json["LandmarkTexturePostfixes"] = all_landmark_postfixes

        themes_to_use = self._get_themes(manifest_json["Themes"])

        manifest_json["Themes"] = themes_to_use

        platforms = self._get_supported_platforms(manifest_json)

        for theme in themes_to_use:
            self._delete_redundant_theme_vehicles(theme)
            states_to_use = self._get_theme_states(theme)
            theme["States"] = states_to_use

            for state in states_to_use:
                texture_names = state["Textures"]

                for platform in platforms:
                    self._download_textures_for_platform(
                        platform, manifest_json, texture_names, theme["Name"], state["Name"])

                state["Textures"] = self._convert_to_local_texture_paths(texture_names)

        self._remove_gz_extensions(manifest_json, platforms)

        if self._should_download_textures:
            self._ensure_texture_count_same_for_all_platforms(platforms)

        return manifest_json

    def _get_all_landmark_postfixes(self, manifest_json):
        postfixes = set()
        for theme in manifest_json["Themes"]:
            for state in theme["States"]:
                if "LandmarkPostfix" in state:
                    postfixes.add(state["LandmarkPostfix"])
        return list(postfixes)

    def _get_manifest_json(self, manifest_url):
        data = self._get_uncompressed_data(manifest_url)
        try:
            manifest_json = json.loads(data)
            return manifest_json
        except:
            raise ValueError("Failed to parse JSON manifest")

    def _get_uncompressed_data(self, url):
        try:
            response = urllib2.urlopen(url)
        except urllib2.HTTPError:
            raise IOError("Failed to download resource at {0}".format(url))

        if response.info().get('Content-Encoding') == 'gzip':
            buf = cStringIO.StringIO( response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
            return data

        else:
            raise ValueError("Resource at {0} is not a gzipped file".format(url))

    def _get_themes(self, themes):
        themes_to_use = [theme for theme in themes if theme["Name"] in self._theme_names]
        found_themes = set(theme["Name"] for theme in themes_to_use)
        missing_themes = self._theme_names - found_themes
        if missing_themes:
            raise ValueError("Couldn't find any of these themes: {0}".format(", ".join(missing_themes)))
        return themes_to_use

    def _get_supported_platforms(self, manifest_json):
        platform_strings = [key for key in manifest_json if key.startswith("AssetRoot_")]
        platforms = [string.split("_")[1] for string in platform_strings]
        return platforms

    def _delete_redundant_theme_vehicles(self, theme):
        keys_to_delete = [key for key in theme if "Vehicle" in key]
        for key in keys_to_delete:
            theme.pop(key)

    def _get_theme_states(self, theme):
        theme_states = theme["States"]
        states_to_use = [state for state in theme_states if state["Name"] in self._state_names]
        found_states = set(state["Name"] for state in states_to_use)
        missing_states = self._state_names - found_states
        if missing_states:
            theme_name = theme["Name"]
            raise ValueError("Could not find any of the following states in {0}: {1}".format(
                theme_name, ", ".join(missing_states)))
        return states_to_use

    def _download_textures_for_platform(self, platform, manifest_json, texture_names, theme_name, state_name):
        local_asset_root = self._get_platform_path(platform)
        if self._should_download_textures:
            if not os.path.exists(local_asset_root):
                os.mkdir(local_asset_root)
            print "Downloading textures for: {0}/{1} ({2})".format(theme_name, state_name, platform)
        asset_root = manifest_json["AssetRoot_{0}".format(platform)]
        asset_ext_gz = manifest_json["AssetExtension_{0}".format(platform)]
        asset_ext = remove_suffix(asset_ext_gz, ".gz")
        http_texture_path_provider = TexturePathProvider(asset_root, asset_ext_gz)
        local_texture_path_provider = TexturePathProvider(local_asset_root+"\\", asset_ext)
        self._download_textures_recursive(http_texture_path_provider, local_texture_path_provider, texture_names)

    def _download_textures_recursive(self, http_texture_path_provider, local_texture_path_provider, items):
        try:
            for k, v in items.iteritems():
                self._download_textures_recursive(http_texture_path_provider, local_texture_path_provider, v)
        except AttributeError:
            relative_texture_path = items
            texture_url = http_texture_path_provider.get_path(relative_texture_path)
            texture_local_path = local_texture_path_provider.get_path(relative_texture_path.replace("/", "_"))
            if self._should_download_textures:
                self._download_texture(texture_url, texture_local_path)

    def _download_texture(self, texture_url, texture_local_path):
        print "  Downloading texture {0}".format(texture_url)
        data = self._get_uncompressed_data(texture_url)
        with open(texture_local_path, 'wb') as uncompressed_file:
            uncompressed_file.write(data)

    def _get_platform_path(self, platform):
        return os.path.join(self._output_dir, platform)

    def _convert_to_local_texture_paths(self, items):
        local_items = {}
        for key, value in items.iteritems():
            try:
                local_items[key] = value.replace("/", "_")
            except AttributeError:
                local_items[key] = self._convert_to_local_texture_paths(value)
        return local_items

    def _ensure_texture_count_same_for_all_platforms(self, platforms):
        platform_dirs = [self._get_platform_path(platform) for platform in platforms]
        file_counts = [len(os.listdir(dir)) for dir in platform_dirs]
        for count in file_counts:
            assert count == file_counts[0], "Number of textures differs between platforms."

    def _write_embedded_manifest_file(self, manifest_json):
        output_file_name = os.path.join(self._output_dir, "embedded_manifest.txt")
        with open(output_file_name, "w") as f:
            json.dump(manifest_json, f, indent=4, sort_keys=True)
        print "\nEmbedded manifest written to {0}".format(output_file_name)

    def _remove_gz_extensions(self, manifest_json, platforms):
        for platform in platforms:
            asset_ext_gz = manifest_json["AssetExtension_{0}".format(platform)]
            asset_ext = remove_suffix(asset_ext_gz, ".gz")
            manifest_json["AssetExtension_{0}".format(platform)] = asset_ext


def create_embedded_manifest(source_manifest, theme_names, state_names, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    factory = EmbeddedManifestFactory(source_manifest, theme_names, state_names, output_dir)
    factory.create_embedded_manifest()


if __name__ == "__main__":
    description = """Create an embedded theme manifest by extracting themes and states from a source manifest."""
    argparser = argparse.ArgumentParser(description=description, epilog="See README.md for example usage.")
    argparser.add_argument("--source_manifest", "-i", type=str, required=True,
                           help="URL of the manifest to pull themes from")
    argparser.add_argument("--theme_names", "-t", type=str, required=True, nargs="+",
                           help="the names of the themes to extract")
    argparser.add_argument("--state_names", "-s", type=str, required=True, nargs="+",
                           help="the names of the states to extract from the theme")
    argparser.add_argument("--output_dir", "-o", type=str, required=True,
                           help="the location to output the embedded textures and manifest")
    args = argparser.parse_args()

    create_embedded_manifest(
        source_manifest=args.source_manifest,
        theme_names=args.theme_names,
        state_names=args.state_names,
        output_dir=args.output_dir)