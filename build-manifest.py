import sys
import json
import yaml
import requests

def _get_interior_materials_common_descriptor(assets_host_name, interior_materials_version):
    descriptor_url = "http://{host_name}/interior-materials/v{version}/common/descriptor.json.gz"
        .format(host_name=assets_host_name, version=interior_materials_version)
        
    descriptor_request = requests.get(descriptor_url)
    return json.loads(descriptor_request.content)


def process_manifest(source_file, version, assets_host_name, landmark_textures_version, interior_materials_version):
    interior_materials_common_descriptor = _get_interior_materials_common_descriptor(assets_host_name, interior_materials_version)
    
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


def read_version_from_file(version_filename):
    with open(version_filename, 'r') as f:
        version = f.readline()
    return version.rstrip()


if __name__ == '__main__':
    if len(sys.argv) == 6:
        source_file = sys.argv[1]
        version = sys.argv[2]
        assets_host_name = sys.argv[3]
        landmark_textures_version_file = sys.argv[4]
        interior_materials_version_file = sys.argv[5]

        landmark_textures_version = read_version_from_file(landmark_textures_version_file)
        interiors_materials_version = read_version_from_file(interior_materials_version_file)

        process_manifest(source_file, version, assets_host_name, landmark_textures_version, interiors_materials_version)
    else:
        sys.stderr.write("Invalid usage.")
        sys.stderr.write("Usage: build-manifest.py source_file version asset_host_name landmark_textures_version_file interior_materials_version_file");
        sys.stderr.write("E.g.: build-manifest.py manifest/manifest.yaml 123 d2xvsc8j92rfya.cloudfront.net build/landmark_textures_version/version.txt build/interior_materials_version/version.txt");
