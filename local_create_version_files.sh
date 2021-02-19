#!/bin/bash
readonly script_name=${0##*/}

set -e
set -u

readonly tc_landmark_tex_id=bt220
readonly tc_indoor_mat_id=EegeoMobile_InteriorMaterials

mkdir -p  ./build/landmark_textures_version
curl "http://teamcity/httpAuth/app/rest/buildTypes/$tc_landmark_tex_id/builds/status:success/number?guest=1" > ./build/landmark_textures_version/version.txt
mkdir -p ./build/interior_materials_version
curl "http://teamcity/httpAuth/app/rest/buildTypes/$tc_indoor_mat_id/builds/status:success/number?guest=1" > ./build/interior_materials_version/version.txt

echo "Successfully downloaded tc artifacts"

