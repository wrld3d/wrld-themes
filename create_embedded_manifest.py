import argparse
import gzip
import json
import os
import urllib2
import cStringIO

class TexturePathProvider:
    def __init__(self, asset_root_path, asset_ext):
        self._asset_root_path = asset_root_path
        self._asset_ext = asset_ext

    def get_path(self, relative_path):
        return "{0}{1}{2}".format(self._asset_root_path, relative_path, self._asset_ext)

class EmbeddedManifestFactory:
    def __init__(self, source_manifest, theme_name, state_name, output_dir):
        self._source_manifest = source_manifest
        self._theme_name = theme_name
        self._state_name = state_name
        self._output_dir = output_dir

    def _get_uncompressed_data(self, url):
        response = urllib2.urlopen(url)

        if response.getcode() != 200:
            raise IOError("Failed to load resource at {0}".format(url))

        if response.info().get('Content-Encoding') == 'gzip':
            buf = cStringIO.StringIO( response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()
            return data

        else:
            raise IOError("Resource at {0} is not a gzipped file".format(url))

    def _get_manifest_json(self, manifest_url):
        data = self._get_uncompressed_data(manifest_url)
        try:
            manifest_json = json.loads(data)
            return manifest_json
        except:
            raise ValueError("Failed to parse JSON manifest")

    # TODO: ensure this works against current manifest & does not regress
    def _download_texture(self, texture_url, texture_local_path):
        print "Downloading texture {0}".format(texture_url)
        data = self._get_uncompressed_data(texture_url)
        with open(texture_local_path, 'wb') as uncompressed_file:
            uncompressed_file.write(data)

    def _download_textures_recursive(self, http_texture_path_provider, local_texture_path_provider, items):
        if isinstance(items, dict):
            for k, v in items.iteritems():
                self._download_textures_recursive(http_texture_path_provider, local_texture_path_provider, v)
        elif isinstance(items, basestring):
            relative_texture_path = items
            texture_url = http_texture_path_provider.get_path(relative_texture_path)
            texture_local_path = local_texture_path_provider.get_path(relative_texture_path.replace("/", "_"))
            self._download_texture(texture_url, texture_local_path)

    def _get_local_texture_paths(self, items):
        local_items = {}
        for key, value in items.iteritems():
            try:
                local_items[key] = value.replace("/", "_")
            except AttributeError:
                local_items[key] = self._get_local_texture_paths(value)
        return local_items

    def create_embedded_manifest(self):
        manifest_json = self._get_manifest_json(self._source_manifest)

        theme_to_use = self._get_theme(manifest_json["Themes"])
        self._delete_redundant_theme_vehicles(theme_to_use)

        manifest_json["Themes"] = [theme_to_use]

        state_to_use = self._get_theme_state(theme_to_use["States"])

        theme_to_use["States"] = [state_to_use]

        platforms = self._get_supported_platforms(manifest_json)

        texture_names = state_to_use["Textures"]

        for platform in platforms:
            self._download_textures_for_platform(platform, manifest_json, texture_names)

        state_to_use["Textures"] = self._get_local_texture_paths(texture_names)

        self._write_embedded_manifest_file(manifest_json)

    def _download_textures_for_platform(self, platform, manifest_json, texture_names):
        local_asset_root = os.path.join(self._output_dir, platform) + "\\"
        if not os.path.exists(local_asset_root):
            os.mkdir(local_asset_root)
        print "downloading textures for: {0}/{1} ({2})".format(self._theme_name, self._state_name, platform)
        asset_root = manifest_json["AssetRoot_{0}".format(platform)]
        asset_ext_gz = manifest_json["AssetExtension_{0}".format(platform)]
        asset_ext = asset_ext_gz[:-3] if asset_ext_gz.endswith(".gz") else asset_ext_gz
        manifest_json["AssetExtension_{0}".format(platform)] = asset_ext
        http_texture_path_provider = TexturePathProvider(asset_root, asset_ext_gz)
        local_texture_path_provider = TexturePathProvider(local_asset_root, asset_ext)
        self._download_textures_recursive(http_texture_path_provider, local_texture_path_provider, texture_names)

    def _write_embedded_manifest_file(self, manifest_json):
        output_file_name = os.path.join(self._output_dir, "embedded_manifest.txt")
        with open(output_file_name, "w") as f:
            json.dump(manifest_json, f, indent=4, sort_keys=True)
        print "Embedded manifest written to {0}".format(output_file_name)

    def _get_theme_state(self, states):
        state_to_use = None
        for state in states:
            if state["Name"] == self._state_name:
                state_to_use = state
        if state_to_use is None:
            raise ValueError("Couldn't find state '{0}' in theme '{1}'".format(self._state_name, self._theme_name))
        return state_to_use

    def _delete_redundant_theme_vehicles(self, theme_to_use):
        keys_to_delete = [key for key in theme_to_use if "Vehicle" in key]
        for key in keys_to_delete:
            theme_to_use.pop(key)

    def _get_theme(self, themes):
        theme_to_use = None
        for theme in themes:
            if theme["Name"] == self._theme_name:
                theme_to_use = theme
        if theme_to_use is None:
            raise ValueError("Couldn't find theme named '{0}' in manifest.".format(self._theme_name))
        return theme_to_use

    def _get_supported_platforms(self, manifest_json):
        platform_strings = [key for key in manifest_json if key.startswith("AssetRoot_")]
        platforms = [string.split("_")[1] for string in platform_strings]
        return platforms


def create_embedded_manifest(source_manifest, theme_name, state_name, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    factory = EmbeddedManifestFactory(source_manifest, theme_name, state_name, output_dir)
    factory.create_embedded_manifest()

DESCRIPTION = """Create an embedded theme manifest from one state of one theme of a streamed manifest."""

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description=DESCRIPTION)
    argparser.add_argument("--source_manifest", "-i", type=str, required=True,
                           help="URL of the manifest to pull themes from")
    argparser.add_argument("--theme_name", "-t", type=str, required=True,
                           help="the name of the theme to extract")
    argparser.add_argument("--state_name", "-s", type=str, required=True,
                           help="the name of the state to extract from the theme")
    argparser.add_argument("--output_dir", "-o", type=str, required=True,
                           help="the location to output the embedded textures and manifest")
    args = argparser.parse_args()

    # todo: multiple themes/states
    create_embedded_manifest(
        source_manifest=args.source_manifest,
        theme_name=args.theme_name,
        state_name=args.state_name,
        output_dir=args.output_dir)