#!/bin/bash
set -e
REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)
ACCOUNT=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document | sed -n 's/.*"accountId" *: *"\([^"]*\)".*/\1/p')
REPO=insightgym
IMAGE="${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/${REPO}:latest"
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com"
docker pull "$IMAGE" || true
DATABASE_URL=$(aws ssm get-parameter --name /insightgym/DATABASE_URL --with-decryption --query Parameter.Value --output text --region "$REGION" 2>/dev/null || echo "")
JWT_SECRET_KEY=$(aws ssm get-parameter --name /insightgym/JWT_SECRET_KEY --with-decryption --query Parameter.Value --output text --region "$REGION" 2>/dev/null || echo "")
if [ -z "$DATABASE_URL" ] || [ -z "$JWT_SECRET_KEY" ]; then
  echo "Missing SSM params. Set /insightgym/DATABASE_URL and /insightgym/JWT_SECRET_KEY then run: sudo /opt/insightgym/run.sh"
  exit 1
fi
docker stop insightgym 2>/dev/null || true
docker rm insightgym 2>/dev/null || true
docker run -d --name insightgym --restart unless-stopped -p 8080:8080 \
  -e DATABASE_URL="$DATABASE_URL" -e JWT_SECRET_KEY="$JWT_SECRET_KEY" -e FLASK_ENV=production \
  "$IMAGE"
