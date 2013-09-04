
rm -rf ./zipped_themes
cp -R ./themes ./zipped_themes

FILES=$(find ./zipped_themes/ -type f -name *.png);
for f in $FILES;
do 
echo "Creating .pvr for $f"
./lib/PVRTexToolCL -f PVRTC1_4 -m -flip y -legacypvr -i "$f";
status=$?
if [ $status -ne 0 ]; then
  echo "failed to generate pvr for $f see teamcity log"
  exit $status
fi
echo "Creating .ktx for $f"
./lib/PVRTexToolCL -f ETC1 -m -flip y -i "$f" -o "${f%.*}".ktx;
status=$?
if [ $status -ne 0 ]; then
  echo "failed to generate ktx for $f see teamcity log"
  exit $status
fi
done;

version=v$1
s3cmd_path=$2
find zipped_themes -name "*.png" -exec rm -rf {} \;
sed -i.bak s/%VERSION%/$version/g ./zipped_themes/manifest.txt
gzip -r ./zipped_themes
find zipped_themes -name ".*" -exec rm -rf {} \;
./lib/s3cmd-1.5.0-alpha1/s3cmd --verbose --add-header='Content-Encoding: gzip' --cf-invalidate --no-progress --force --recursive --acl-public --config $s3cmd_path put ./zipped_themes/  s3://eegeo-static/mobile-themes/$version/ > /dev/null
rm -rf ./zipped_themes
