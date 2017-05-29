import sys
import yaml
import argparse
import collections
from os import path
from os import walk
import fnmatch


def _validate_texture(texture_path, allowed_textures, theme_name, state_name):
    all_valid = True

    if texture_path not in allowed_textures:
        if texture_path.endswith("cube_map"):
            cube_suffixes = ["_negX", "_posX", "_negY", "_posY", "_negZ", "_posZ"]

            for suffix in cube_suffixes:
                all_valid &= _validate_texture(texture_path + suffix, allowed_textures, theme_name, state_name)
        else:
            all_valid = False
            print "Unknown Texture:\t%s\tTheme:\t%s State:\t%s." % (texture_path, theme_name, state_name)

    return all_valid


def _validate_state_textures(texture_yaml, allowed_textures, theme_name, state_name):
    all_valid = True

    for texture_key in texture_yaml:
        texture_value = texture_yaml[texture_key]
        if isinstance(texture_value, str):
            all_valid &= _validate_texture(texture_value, allowed_textures, theme_name, state_name)
        elif isinstance(texture_value, collections.Sequence):
            for texture_path in texture_value:
                all_valid &= _validate_texture(texture_path, allowed_textures, theme_name, state_name)

    return all_valid


def _validate_state(state_yaml, allowed_textures, theme_name):
    state_name = state_yaml["Name"]
    state_textures = state_yaml["Textures"]
    return _validate_state_textures(state_textures, allowed_textures, theme_name, state_name)


def _validate_theme(theme_yaml, allowed_textures):
    all_valid = True
    theme_name = theme_yaml["Name"]

    for s in theme_yaml["States"]:
        all_valid &= _validate_state(s, allowed_textures, theme_name)

    return all_valid


def _collect_texture_paths(texture_root_dir):
    texture_file_paths = [path.join(dirpath, f) for dirpath, dirnames, files in walk(texture_root_dir) for f in
                          fnmatch.filter(files, '*.png')]
    allowed_textures = set([path.splitext(p)[0].replace("\\", "/").replace(texture_root_dir, "")
                            for p in texture_file_paths])

    return allowed_textures


def _load_yaml(yaml_path):
    with open(yaml_path, "r") as yaml_file:
        raw_lines = yaml_file.readlines()

    return yaml.load("".join(raw_lines))


def _validate_manifest(manifest_path, allowed_textures):
    all_valid = True
    yaml_document = _load_yaml(manifest_path)
    theme_manifest = yaml_document['ThemeManifest']

    for t in theme_manifest["Themes"]:
        all_valid &= _validate_theme(t, allowed_textures)

    return all_valid


def validate_manifests(manifest_paths, texture_root):
    all_valid = True
    allowed_textures = _collect_texture_paths(texture_root)

    for manifest_path in manifest_paths:
        all_valid &= _validate_manifest(manifest_path, allowed_textures)

    return all_valid


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='build a theme manifest')
    parser.add_argument('--source_files', "-s", nargs='+', type=str, help='source yaml file path. E.g. manifest/manifest.yaml')
    parser.add_argument('--texture_directory', "-t", type=str, help='texture directory E.g. "themes/"')
    args = parser.parse_args()

    if not validate_manifests(args.source_files, args.texture_directory):
        print "Errors found when checking theme texture paths."
    else:
        print "Theme texture path check ran successfully."
