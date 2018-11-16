import argparse
import json
import os
import os.path
import shutil

import requests


def remove_suffix(string, suffix):
    if string.endswith(suffix):
        suffix_length = len(suffix)
        return string[:-suffix_length]
    else:
        return string

def get_decompressed_data(url, ignore_errors=False):
    if ignore_errors:
        return try_fetch_and_decompress_url(url)

    return fetch_and_decompress_url(url)

def try_fetch_and_decompress_url(url):
    try:
        return fetch_and_decompress_url(url)
    except requests.exceptions.RequestException:
        return None

def fetch_and_decompress_url(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.content


def read_file_or_url(path):
    if path.startswith("http://") or path.startswith("https://"):
        return get_decompressed_data(path)
    else:
        with open(path) as f:
            return f.read()


class TexturePathProvider:
    def __init__(self, asset_root_path, asset_ext, cube_asset_ext, uses_single_file_cubemap_files):
        self._asset_root_path = asset_root_path
        self._asset_ext = asset_ext
        self._cube_asset_ext = cube_asset_ext
        self._uses_single_file_cubemap_files = uses_single_file_cubemap_files

    def get_path(self, relative_path, cubemap_face_index=-1):
        suffix = ''
        asset_ext = self._asset_ext

        if cubemap_face_index != -1:
            asset_ext = self._cube_asset_ext
            if self._uses_single_file_cubemap_files:
                suffix = '_cubemap'
            else:
                cubemap_suffixes = ['_posX', '_posY', '_posZ', '_negX', '_negY', '_negZ']
                suffix = cubemap_suffixes[cubemap_face_index]

        return "{0}{1}{2}{3}".format(self._asset_root_path, relative_path, suffix, asset_ext)

    def get_cubemap_file_count(self):
        return 1 if self._uses_single_file_cubemap_files else 6


class EmbeddedManifestFactory:
    def __init__(self, theme_names, state_names, output_dir, download_textures=True, asset_root=None, partial=False):
        self._theme_names = set(theme_names)
        self._state_names = set(state_names)
        self._output_dir = output_dir if output_dir is not None else ""
        self._write_output_to_file = output_dir is not None
        self._asset_root = asset_root
        self._partial = partial
        self._should_download_textures = download_textures
        self._platform_cubemap_counts = dict()
        self._platform_files_per_cubemap = dict()


    def create_embedded_manifest(self, manifest_text):
        manifest_json = json.loads(manifest_text)
        embedded_manifest_json = self._create_embedded_manifest_from_json(manifest_json)

        if self._write_output_to_file:
            self._write_embedded_manifest_file(embedded_manifest_json)

        return manifest_json

    def _create_embedded_manifest_from_json(self, manifest_json):
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
                os.makedirs(local_asset_root)
            print "Downloading textures for: {0}/{1} ({2})".format(theme_name, state_name, platform)

        asset_root = self._asset_root or manifest_json["AssetRoot_{0}".format(platform)]
        if asset_root.startswith("//"):
            asset_root = "http:" + asset_root

        asset_ext_gz = manifest_json["AssetExtension_{0}".format(platform)]
        asset_ext = remove_suffix(asset_ext_gz, ".gz")
        use_single_file_cubemap_files = asset_ext.lower() not in {'.png', '.webgl.png'}
        dest_cube_asset_ext = asset_ext if use_single_file_cubemap_files else '.png'
        http_texture_path_provider = TexturePathProvider(asset_root, asset_ext_gz, asset_ext_gz, use_single_file_cubemap_files)
        local_texture_path_provider = TexturePathProvider(local_asset_root+os.path.sep, asset_ext, dest_cube_asset_ext, use_single_file_cubemap_files)
        cubemap_count = self._download_textures_recursive(http_texture_path_provider, local_texture_path_provider, texture_names)
        self._platform_cubemap_counts[platform] = cubemap_count
        self._platform_files_per_cubemap[platform] = http_texture_path_provider.get_cubemap_file_count()

    def _download_textures_recursive(self, http_texture_path_provider, local_texture_path_provider, items, is_cubemap=False):
        cubemap_count = 0
        try:
            for k, v in items.iteritems():
                is_cubemap = "CubeMap" in k
                cubemap_count += self._download_textures_recursive(http_texture_path_provider, local_texture_path_provider, v, is_cubemap)
        except AttributeError:
            relative_texture_path = items

            if is_cubemap:
                self._download_cubemap_from_relative_path(http_texture_path_provider, local_texture_path_provider, relative_texture_path)
                cubemap_count += 1
            else:
                self._download_texture_from_relative_path(http_texture_path_provider, local_texture_path_provider, relative_texture_path)
        return cubemap_count

    def _download_cubemap_from_relative_path(self, http_texture_path_provider, local_texture_path_provider, relative_path):
        file_count = http_texture_path_provider.get_cubemap_file_count()

        for cubemap_face_index in range(file_count):
            texture_url = http_texture_path_provider.get_path(relative_path, cubemap_face_index)
            texture_local_path = local_texture_path_provider.get_path(relative_path.replace("/", "_"), cubemap_face_index)
            if self._should_download_textures:
                self._download_texture(texture_url, texture_local_path)

    def _download_texture_from_relative_path(self, http_texture_path_provider, local_texture_path_provider, relative_path):
        texture_url = http_texture_path_provider.get_path(relative_path)
        texture_local_path = local_texture_path_provider.get_path(relative_path.replace("/", "_"))
        if self._should_download_textures:
           self._download_texture(texture_url, texture_local_path)

    def _download_texture(self, texture_url, texture_local_path):
        data = get_decompressed_data(texture_url, ignore_errors=self._partial)
        if data:
            print "  Downloaded texture {0}".format(texture_url)
            with open(texture_local_path, 'wb') as uncompressed_file:
                uncompressed_file.write(data)

    def _get_platform_path(self, platform):
        return os.path.join(self._output_dir, platform, "EmbeddedTheme")

    def _convert_to_local_texture_paths(self, items):
        local_items = {}
        for key, value in items.iteritems():
            try:
                local_items[key] = value.replace("/", "_")
            except AttributeError:
                local_items[key] = self._convert_to_local_texture_paths(value)
        return local_items

    def _ensure_texture_count_same_for_all_platforms(self, platforms):
        count = None

        for platform in platforms:
            platform_dir = self._get_platform_path(platform)
            file_count = len(os.listdir(platform_dir))
            cubemap_count = self._platform_cubemap_counts[platform]
            non_cubemap_count = file_count - self._platform_files_per_cubemap[platform] * cubemap_count

            if count == None:
                count = non_cubemap_count
            else:
                assert count == non_cubemap_count, "Number of textures differs between platforms."

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


def create_embedded_manifest(source_manifest, theme_names, state_names, output_dir, asset_root=None, partial=False):
    manifest_text = read_file_or_url(source_manifest)

    if not partial:
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    factory = EmbeddedManifestFactory(theme_names, state_names, output_dir, asset_root=asset_root, partial=partial)
    factory.create_embedded_manifest(manifest_text)


if __name__ == "__main__":
    description = """Create an embedded theme manifest by extracting themes and states from a source manifest."""
    argparser = argparse.ArgumentParser(description=description, epilog="See README.md for example usage.")
    argparser.add_argument("--source_manifest", "-i", type=str, required=True,
                           help="URL or local path of the manifest to pull themes from")
    argparser.add_argument("--theme_names", "-t", type=str, required=True, nargs="+",
                           help="the names of the themes to extract")
    argparser.add_argument("--state_names", "-s", type=str, required=True, nargs="+",
                           help="the names of the states to extract from the theme")
    argparser.add_argument("--output_dir", "-o", type=str, required=True,
                           help="the location to output the embedded textures and manifest")
    argparser.add_argument("--asset_root", "-r", type=str,
                           help="override the asset roots in the input manifest")
    argparser.add_argument("--partial", "-p", action="store_true",
                           help="ignore failed downloads - use to overwrite a subset of an existing embedded theme")
    args = argparser.parse_args()

    create_embedded_manifest(
        source_manifest=args.source_manifest,
        theme_names=args.theme_names,
        state_names=args.state_names,
        output_dir=args.output_dir,
        asset_root=args.asset_root,
        partial=args.partial)
