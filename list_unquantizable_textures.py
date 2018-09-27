import sys
import yaml
import argparse
import collections
from os import path, walk, remove
import fnmatch
from subprocess import call


QUANTIZATION_BLACKLIST = ['BuildingDiffuse', 'PlaceholderNoDataDiffuse']


def _collect_blacklisted_textures_from_state(state_yaml):
    for blacklisted_key in QUANTIZATION_BLACKLIST:
       if blacklisted_key in state_yaml:
            yield state_yaml[blacklisted_key]


def _collect_blacklisted_textures_from_theme(theme_yaml):
    for state in theme_yaml["States"]:
        for texture_path in _collect_blacklisted_textures_from_state(state["Textures"]):
            expanded_path = "themes/" + texture_path + ".png"
            yield expanded_path.lower()


def collect_blacklisted_texture_paths(manifest_root_dir):
    manifest_paths = [path.join(dirpath, f) for dirpath, dirnames, files in walk(manifest_root_dir) for f in
                          fnmatch.filter(files, '*.yaml.prep')]
    result = set()

    for manifest_path in manifest_paths:
        manifest = _load_yaml(manifest_path)

        theme_manifest = manifest["ThemeManifest"]

        for theme in theme_manifest["Themes"]:
            result.update(_collect_blacklisted_textures_from_theme(theme))

    return result


def _load_yaml(yaml_path):
    with open(yaml_path, "r") as yaml_file:
        raw_lines = yaml_file.readlines()

    return yaml.load("".join(raw_lines))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='list textures that are blacklisted for compression (too important to be quantized)')
    parser.add_argument(
        '--manifest_directory', "-m", type=str, help='source yaml.prep root. E.g. build/manifest', required=True)
    args = parser.parse_args()

    for p in collect_blacklisted_texture_paths(args.manifest_directory):
        print p
