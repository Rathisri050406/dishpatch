#!/bin/bash
# Launches (deploys) Dishpatch using your IAM user's credentials.
# Run from the project folder:  bash deploy.sh
set -e
BUCKET=dishpatch-rathisri
API=https://uv1weiza55.execute-api.ap-southeast-2.amazonaws.com
export AWS_DEFAULT_REGION=ap-southeast-2

echo "== Deploying as this IAM user =="
aws sts get-caller-identity --query Arn --output text

echo "== 1. Website to S3 =="
sed "s#window.API_URL = \"\";#window.API_URL = \"$API\";#" index.html > /tmp/index-s3.html
grep -q "$API" /tmp/index-s3.html || { echo "API address was not inserted. Stopping."; exit 1; }
aws s3 cp /tmp/index-s3.html "s3://$BUCKET/index.html" --content-type "text/html; charset=utf-8"

echo "== 2. Backend code to Lambda =="
rm -f lambda-site.zip
powershell.exe -NoProfile -Command "Get-ChildItem backend -File | Compress-Archive -DestinationPath lambda-site.zip -Force"
for FN in dishpatch-site dishpatch-order-worker; do
  aws lambda update-function-code --function-name $FN --zip-file fileb://lambda-site.zip --query FunctionName --output text
  aws lambda wait function-updated --function-name $FN
done

echo "== 3. Checking the live website =="
curl -s --ssl-no-revoke -o /dev/null -w "API Gateway site: HTTP %{http_code}\n" "$API/"
curl -s --ssl-no-revoke -o /dev/null -w "S3 site:          HTTP %{http_code}\n" "http://$BUCKET.s3-website-ap-southeast-2.amazonaws.com/"
echo "Done. Open: http://$BUCKET.s3-website-ap-southeast-2.amazonaws.com"
