import gzip
import json
import os
from sys import stderr
import urllib2
import cStringIO

class TexturePathProvider:
    def __init__(self, asset_root_path, asset_ext):
        self._asset_root_path = asset_root_path
        self._asset_ext = asset_ext

    def get_path(self, relative_path):
        return "{0}{1}{2}".format(self._asset_root_path, relative_path, self._asset_ext)

class EmbeddedManifestFactory:
    def __init__(self, source_manifest, theme_name, state_name, output_path):
        self._source_manifest = source_manifest
        self._theme_name = theme_name
        self._state_name = state_name
        self._output_path = output_path

    def _get_manifest_json(self, source_manifest):
        response = urllib2.urlopen(source_manifest)

        if response.info().get('Content-Encoding') == 'gzip':
            buf = cStringIO.StringIO( response.read())
            f = gzip.GzipFile(fileobj=buf)
            data = f.read()

            try:
                manifest_json = json.loads(data)
                return manifest_json
            except:
                print >> stderr, u"Cannot parse manifest at {0}".format(source_manifest)
                raise
        else:
            print >> stderr, u"Cannot load manifest at {0}".format(source_manifest)
            raise

    # TODO: ensure this works against current manifest & does not regress
    def _download_texture(self, texture_url, texture_local_path):
        response = urllib2.urlopen(texture_url)
        print "downloading {0}".format(texture_url)
        with open(texture_local_path, 'wb') as texture_file:
            texture_file.write(response.read())


    def _download_textures_recursive(self, http_texture_path_provider, local_texture_path_provider, items):
        if isinstance(items, dict):
            for k, v in items.iteritems():
                self._download_textures_recursive(http_texture_path_provider, local_texture_path_provider, v)
        elif isinstance(items, basestring):
            relative_texture_path = items
            texture_url = http_texture_path_provider.get_path(relative_texture_path)
            texture_local_path = local_texture_path_provider.get_path(relative_texture_path.replace("/", "_"))
            self._download_texture(texture_url, texture_local_path)


    def create_embedded_manifest(self):
        manifest_json = self._get_manifest_json(self._source_manifest)

        # find the relevant theme
        original_themes = manifest_json["Themes"] #copy.deepcopy(manifest_json["Themes"])

        theme_to_use = self._get_theme(manifest_json["Themes"])
        self._delete_redundant_theme_vehicles(theme_to_use)

        manifest_json["Themes"] = [theme_to_use]

        state_to_use = self._get_theme_state(theme_to_use["States"])

        theme_to_use["States"] = [state_to_use]

        local_asset_root = os.path.join(self._output_path, "iOS") + "\\"

        if not os.path.exists(local_asset_root):
            os.mkdir(local_asset_root)

        print "downloading textures for: {0}/{1}".format(self._theme_name, self._state_name)

        # todo: extend to run P times, once per platform
        asset_root_ios = manifest_json["AssetRoot_iOS"]
        asset_ext_ios = manifest_json["AssetExtension_iOS"]
        http_texture_path_provider = TexturePathProvider(asset_root_ios, asset_ext_ios)
        local_texture_path_provider = TexturePathProvider(local_asset_root, asset_ext_ios)

        items = state_to_use["Textures"]
        self._download_textures_recursive(http_texture_path_provider, local_texture_path_provider, items)

        # todo: modify the json, save subset of manifest

    def _get_theme_state(self, states):
        state_to_use = None
        for state in states:
            if state["Name"] == self._state_name:
                state_to_use = state
        if state_to_use is None:
            raise ValueError("Couldn't find state '{0}' in theme '{1}'".format(self._state_name, self._theme_name))
        return state_to_use

    def _delete_redundant_theme_vehicles(self, theme_to_use):
        keys_to_delete = []
        for k in theme_to_use:
            if "Vehicle" in k:
                keys_to_delete.append(k)
        for k in keys_to_delete:
            print "removing key: {0}".format(k)
            theme_to_use.pop(k)

    def _get_theme(self, themes):
        theme_to_use = None
        for theme in themes:
            if theme["Name"] == self._theme_name:
                theme_to_use = theme
        if theme_to_use is None:
            raise ValueError("Couldn't find theme named '{0}' in manifest.".format(self._theme_name))
        return theme_to_use


def create_embedded_manifest(source_manifest, theme_name, state_name, output_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    factory = EmbeddedManifestFactory(source_manifest, theme_name, state_name, output_path)
    factory.create_embedded_manifest()


if __name__ == "__main__":
    # todo: proper entrypoint
    create_embedded_manifest(
        source_manifest="http://d2xvsc8j92rfya.cloudfront.net/mobile-themes-new/v407/manifest.txt.gz",
        theme_name="SummerSanFrancisco",
        state_name="DayDefault",
        output_path="C:/temp/embedded_theme_test")