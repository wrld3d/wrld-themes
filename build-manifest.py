import sys
import json
import yaml

def process_manifest(source_file, version, assets_host_name):
	with open(source_file, "r") as f:
		lines = f.readlines()
        yaml_document = yaml.load("".join(lines))['ThemeManifest']

	for k in yaml_document:
		if(isinstance(yaml_document[k], str)):
			yaml_document[k] = yaml_document[k].replace("%ASSETS_HOST_NAME%", assets_host_name)
			yaml_document[k] = yaml_document[k].replace("%VERSION%", version)

	print json.dumps(yaml_document, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == '__main__':
	if len(sys.argv) == 4:	
		source_file = sys.argv[1]
		version = sys.argv[2]
		assets_host_name = sys.argv[3]
		process_manifest(source_file, version, assets_host_name)
	else:
		sys.stderr.write("Expected three command line arguments, source file, version name and asset host name.\n");
