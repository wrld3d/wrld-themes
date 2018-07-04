import sys
import json
import yaml
import requests
import argparse

def _get_interior_materials_common_descriptor(eegeo_assets_host_name, interior_materials_version):
    descriptor_url = "http://{host_name}/interior-materials/v{version}/common/descriptor.json.gz".format(
        host_name=eegeo_assets_host_name, version=interior_materials_version)
        
    descriptor_request = requests.get(descriptor_url)
    return json.loads(descriptor_request.content)


def process_manifest(source_file, version, eegeo_assets_host_name, theme_assets_host_name, landmark_textures_version, interior_materials_version):
    _, eegeo_assets_host = eegeo_assets_host_name.split("//")

    interior_materials_common_descriptor = _get_interior_materials_common_descriptor(eegeo_assets_host, interior_materials_version)
    
    with open(source_file, "r") as f:
        lines = f.readlines()
    yaml_document = yaml.load("".join(lines))['ThemeManifest']

    for k in yaml_document:
        if isinstance(yaml_document[k], str):
            yaml_document[k] = yaml_document[k].replace("%EEGEO_ASSETS_HOST_NAME%", eegeo_assets_host_name)
            yaml_document[k] = yaml_document[k].replace("%THEME_ASSETS_HOST_NAME%", theme_assets_host_name)
            yaml_document[k] = yaml_document[k].replace("%VERSION%", version)
            yaml_document[k] = yaml_document[k].replace("%LANDMARK_TEXTURES_VERSION%", landmark_textures_version)
            yaml_document[k] = yaml_document[k].replace("%INTERIOR_MATERIALS_VERSION%", interior_materials_version)
            
    yaml_document["InteriorMaterials"] = interior_materials_common_descriptor
        
    print json.dumps(yaml_document, sort_keys=True, indent=4, separators=(',', ': '))
    

def read_version_from_file(version_filename):
    with open(version_filename, 'r') as f:
        version = f.readline()

    return version.rstrip()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='build a theme manifest')
    parser.add_argument('source_file', type=str, help='source yaml file path. E.g. manifest/manifest.yaml')
    parser.add_argument('version', type=str, help='version. E.g. 123')
    parser.add_argument('eegeo_assets_host_name', type=str, help='the hostname that the theme assets provided by eegeo will be served from. E.g. cdn-resources.wrld3d.com')
    parser.add_argument('theme_assets_host_name', type=str, help='the hostname that the theme assets created by this script will be served from. E.g. cdn-resources.wrld3d.com')
    parser.add_argument('landmark_textures_version_file', type=str, help='File containing the version number of the landmark textures store.')
    parser.add_argument('interior_materials_version_file', type=str, help='File containing the version number of the interior materials store')

    args = parser.parse_args()

    process_manifest(
        args.source_file, 
        args.version,
        args.eegeo_assets_host_name,
        args.theme_assets_host_name,
        read_version_from_file(args.landmark_textures_version_file), 
        read_version_from_file(args.interior_materials_version_file))
