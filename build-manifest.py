import json
import yaml

def process_manifest():
	with open("manifest/manifest.yaml.prep", "r") as f:
		lines = f.readlines()
        yaml_document = yaml.load("".join(lines))['ThemeManifest']
        print json.dumps(yaml_document, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == '__main__':
    process_manifest()