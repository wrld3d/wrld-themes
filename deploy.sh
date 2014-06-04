#!/bin/sh

rm -rf ./zipped_themes
cp -R ./themes ./zipped_themes

version=$1
s3cmd_access_key=$2
s3cmd_secret=$3

rm -f ./lib/s3ini.poked
cp ./lib/s3ini ./lib/s3ini_poked
sed -i.bak -e s/%S3_ACCESS_KEY%/$(echo $s3cmd_access_key | sed -e 's/\\/\\\\/g' -e 's/\//\\\//g' -e 's/&/\\\&/g')/g -e s/%S3_SECRET_KEY%/$(echo $s3cmd_secret | sed -e 's/\\/\\\\/g' -e 's/\//\\\//g' -e 's/&/\\\&/g')/g ./lib/s3ini_poked
rm -f ./lib/s3ini_poke.bak

json_path="./zipped_themes/manifest.txt"

cat <<-EOF | python -
import json 
import sys
try:
    json.loads(open("$json_path").read())
except:
    exit(1)
exit(0)
EOF

if [ $? = 1 ] ; then
	echo "Json manifest could not be parsed - build failed!"
	exit 1
else
	echo "Json manifest parse succeeded"
fi

FILES=$(find ./zipped_themes/ -type f -name *.png);
for f in $FILES;
do 
echo "Creating .pvr for $f"
./lib/PVRTexToolCL.exe -f PVRTC1_4 -m -flip y -legacypvr -i "$f";
status=$?
if [ $status -ne 0 ]; then
  echo "failed to generate pvr for $f see teamcity log"
  exit $status
fi
echo "Creating .ktx for $f"
./lib/PVRTexToolCL.exe -f ETC1 -m -flip y -i "$f" -o "${f%.*}".ktx;
status=$?
if [ $status -ne 0 ]; then
  echo "failed to generate ktx for $f see teamcity log"
  exit $status
fi
done;

find zipped_themes -name "*.png" -exec rm -rf {} \;

gzip -r ./zipped_themes
find zipped_themes -name ".*" -exec rm -rf {} \;
./lib/s3cmd-1.0.1/s3cmd --verbose --add-header='Content-Encoding: gzip' --no-progress --force --recursive --acl-public --config ./lib/s3ini_poked put ./zipped_themes/  s3://myworld_developer_destination_resources/mobile-themes-new/$version/ > /dev/null
rm -rf ./zipped_themes
rm -f ./lib/s3ini_poked
