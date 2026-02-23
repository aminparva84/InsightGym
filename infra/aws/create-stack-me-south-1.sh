#!/usr/bin/env bash
# Create InsightGYM stack in me-south-1 (Bahrain).
# Prerequisites: AWS CLI configured, default VPC and subnets in me-south-1.
# Usage:
#   1. Get VPC and subnets:
#      aws ec2 describe-vpcs --region me-south-1 --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text
#      aws ec2 describe-subnets --region me-south-1 --filters Name=vpc-id,Values=<VPC_ID> --query 'Subnets[*].[SubnetId,AvailabilityZone]' --output table
#   2. Create a key pair in me-south-1 if you want SSH: aws ec2 create-key-pair --key-name insightgym-key --region me-south-1
#   3. Run this script (set params below or pass as env).

set -e
REGION=me-south-1
STACK_NAME=insightgym

# Required: set these or pass as env
VPC_ID="${VPC_ID:?Set VPC_ID (default VPC in me-south-1)}"
SUBNET_ID_1="${SUBNET_ID_1:?Set SUBNET_ID_1}"
SUBNET_ID_2="${SUBNET_ID_2:?Set SUBNET_ID_2}"
EC2_SUBNET_ID="${EC2_SUBNET_ID:-$SUBNET_ID_1}"
DB_PASSWORD="${DB_PASSWORD:?Set DB_PASSWORD (RDS master password)}"
JWT_SECRET="${JWT_SECRET:?Set JWT_SECRET (long random string for the app)}"

# Optional
DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-raha_fitness}"
KEY_NAME="${KEY_NAME:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE="${SCRIPT_DIR}/ec2-me-south-1.yaml"

PARAMS=(
  "ParameterKey=VpcId,ParameterValue=$VPC_ID"
  "ParameterKey=SubnetId1,ParameterValue=$SUBNET_ID_1"
  "ParameterKey=SubnetId2,ParameterValue=$SUBNET_ID_2"
  "ParameterKey=EC2SubnetId,ParameterValue=$EC2_SUBNET_ID"
  "ParameterKey=DBUsername,ParameterValue=$DB_USER"
  "ParameterKey=DBPassword,ParameterValue=$DB_PASSWORD"
  "ParameterKey=DBName,ParameterValue=$DB_NAME"
  "ParameterKey=JwtSecretKey,ParameterValue=$JWT_SECRET"
  "ParameterKey=AWSRegion,ParameterValue=$REGION"
)
if [ -n "$KEY_NAME" ]; then
  PARAMS+=("ParameterKey=KeyName,ParameterValue=$KEY_NAME")
fi

echo "Creating stack $STACK_NAME in $REGION..."
aws cloudformation create-stack \
  --stack-name "$STACK_NAME" \
  --template-body "file://$TEMPLATE" \
  --parameters "${PARAMS[@]}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --region "$REGION"

echo "Waiting for stack create to complete..."
aws cloudformation wait stack-create-complete --stack-name "$STACK_NAME" --region "$REGION"

echo "Stack created. Outputs:"
aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" \
  --query 'Stacks[0].Outputs' --output table

echo ""
echo "Next steps:"
echo "1. Push Docker image to ECR in me-south-1 (run the GitHub Actions workflow or build and push manually)."
echo "2. Set SSM parameters (see CreateSSMParamsCommand in stack outputs; replace YOUR_DB_PASSWORD and YOUR_JWT_SECRET)."
echo "3. On the EC2 instance, run: sudo /opt/insightgym/run.sh"
echo "   (SSH with the key pair, or use Session Manager if no key)."
echo "4. Open the ALB URL from the outputs."
