#!/bin/bash
readonly script_name=${0##*/}

set -eu

function script_failure {
   echo "failed at $script_name:$1"
   exit 1
}

trap 'script_failure $LINENO' ERR

function print_usage {
    echo "" >&2
    echo "Usage:    ${script_name} aws_access_key_id aws_secret_access_key cloudfront_id webgl_cloudfront_id" >&2
}

if [[ "$#" -ne 4 ]] || [[ -z "$1" ]] || [[ -z "$2" ]] || [[ -z "$3" ]] || [[ -z "$4" ]]; then
    echo "$# arguments provided, expected 4 arguments" >&2
    print_usage
    exit 1
fi

readonly aws_access_key_id=$1
readonly aws_secret_access_key=$2
readonly invalidate=$3
readonly invalidate_webgl=$4

readonly s3_bucket="s3://myworld_developer_destination_resources"
readonly versions_file="versions.json"

echo "Obtaining latest version from S3..."

AWS_ACCESS_KEY_ID="$aws_access_key_id" \
AWS_SECRET_ACCESS_KEY="$aws_secret_access_key" \
aws s3 cp \
--region us-east-1 \
"${s3_bucket}/mobile-themes-new/latest/${versions_file}" \
"${versions_file}.gz"

gunzip -f ${versions_file}.gz

echo "Copying theme manifests to 'latest'..."

jq -rc 'keys[]' ${versions_file} | while read theme ; do
    theme_directory=$(jq -rc ".$theme" ${versions_file})
    AWS_ACCESS_KEY_ID="$aws_access_key_id" \
    AWS_SECRET_ACCESS_KEY="$aws_secret_access_key" \
    aws s3 cp \
    --region us-east-1 \
    --recursive \
    --acl public-read \
    "${s3_bucket}/${theme_directory}" \
    "${s3_bucket}/mobile-themes-new/latest/${theme}"
done

echo "Issuing cache invalidations for 'latest' directory..."

AWS_ACCESS_KEY_ID="$aws_access_key_id" \
AWS_SECRET_ACCESS_KEY="$aws_secret_access_key" \
aws configure set preview.cloudfront true

AWS_ACCESS_KEY_ID="$aws_access_key_id" \
AWS_SECRET_ACCESS_KEY="$aws_secret_access_key" \
aws cloudfront create-invalidation --distribution-id $invalidate --paths /mobile-themes-new/latest/*

AWS_ACCESS_KEY_ID="$aws_access_key_id" \
AWS_SECRET_ACCESS_KEY="$aws_secret_access_key" \
aws cloudfront create-invalidation --distribution-id $invalidate_webgl --paths /mobile-themes-new/latest/*
