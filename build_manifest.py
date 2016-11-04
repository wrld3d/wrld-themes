import sys
import json
import yaml
import requests
import argparse

def _get_interior_materials_common_descriptor(assets_host_name, interior_materials_version):
    descriptor_url = "http://{host_name}/interior-materials/v{version}/common/descriptor.json.gz".format(
        host_name=assets_host_name, version=interior_materials_version)
        
    descriptor_request = requests.get(descriptor_url)
    return json.loads(descriptor_request.content)


def process_manifest(source_file, version, assets_host_name, landmark_textures_version, interior_materials_version):
    _, host = assets_host_name.split("//")

    interior_materials_common_descriptor = _get_interior_materials_common_descriptor(host, interior_materials_version)
    
    with open(source_file, "r") as f:
        lines = f.readlines()
    yaml_document = yaml.load("".join(lines))['ThemeManifest']

    for k in yaml_document:
        if isinstance(yaml_document[k], str):
            yaml_document[k] = yaml_document[k].replace("%ASSETS_HOST_NAME%", assets_host_name)
            yaml_document[k] = yaml_document[k].replace("%VERSION%", version)
            yaml_document[k] = yaml_document[k].replace("%LANDMARK_TEXTURES_VERSION%", landmark_textures_version)
            yaml_document[k] = yaml_document[k].replace("%INTERIOR_MATERIALS_VERSION%", interior_materials_version)
            
    yaml_document["InteriorMaterials"] = interior_materials_common_descriptor
        
    print json.dumps(yaml_document, sort_keys=True, indent=4, separators=(',', ': '))
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='build a theme manifest')
    parser.add_argument('source_file', type=str, help='source yaml file path. E.g. manifest/manifest.yaml')
    parser.add_argument('version', type=str, help='version. E.g. 123')
    parser.add_argument('assets_host_name', type=str, help='the hostname that the assets will be served from. E.g. d2xvsc8j92rfya.cloudfront.net')
    parser.add_argument('landmark_textures_version', type=str, help='Version number of the landmark textures store. E.g. 1')
    parser.add_argument('interior_materials_version', type=str, help='Version number of the interior materials store. E.g. 3')

    args = parser.parse_args()

    process_manifest(
        args.source_file, 
        args.version, 
        args.assets_host_name, 
        args.landmark_textures_version, 
        args.interior_materials_version)