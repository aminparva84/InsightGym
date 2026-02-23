# AWS EC2 deployment in me-south-1 (Bahrain)

This guide sets up **InsightGYM** on **EC2 + RDS PostgreSQL + ALB** in **Middle East (Bahrain), me-south-1**, for production use.

## What gets created

| Resource | Purpose |
|----------|--------|
| **EC2** | One `t3.small` instance running your Docker image (Flask + React) |
| **RDS PostgreSQL** | `db.t3.micro`, 20 GB, no public access; app connects via `DATABASE_URL` |
| **ALB** | Application Load Balancer on port 80; health check `/health` |
| **ECR** | Repository `insightgym` in me-south-1 for your Docker image |
| **SSM** | Secrets in Parameter Store: `/insightgym/DATABASE_URL`, `/insightgym/JWT_SECRET_KEY` |

The app listens on **port 8080** inside the container; ALB forwards traffic to it.

---

## 1. Prerequisites

- **AWS CLI** installed and configured (with credentials that can create CF stacks, ECR, RDS, EC2, IAM).
- **Default VPC** in **me-south-1** (or note your VPC and subnets).

### Get default VPC and subnets (me-south-1)

```bash
export AWS_REGION=me-south-1

# Default VPC
VPC_ID=$(aws ec2 describe-vpcs --region $AWS_REGION --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)
echo "VPC_ID=$VPC_ID"

# Two subnets (different AZs for ALB/RDS)
aws ec2 describe-subnets --region $AWS_REGION --filters Name=vpc-id,Values=$VPC_ID --query 'Subnets[*].[SubnetId,AvailabilityZone]' --output table
# Pick two subnet IDs (e.g. SubnetId1 and SubnetId2).
```

---

## 2. Create the stack

### Option A: AWS Console

1. **CloudFormation** → Create stack → Upload template.
2. Upload `infra/aws/ec2-me-south-1.yaml`.
3. Parameters (required):
   - **VpcId**: your VPC ID (e.g. from step 1).
   - **SubnetId1**, **SubnetId2**: two subnets (different AZs).
   - **EC2SubnetId**: subnet for EC2 (can be same as SubnetId1).
   - **DBPassword**: RDS master password (min 8 characters).
   - **JwtSecretKey**: long random string for JWT (e.g. `openssl rand -base64 32`).
4. Optional: **KeyName**: EC2 key pair name in me-south-1 if you want SSH.
5. Create stack and wait until status **CREATE_COMPLETE**.

### Option B: Script (bash)

```bash
cd infra/aws
export VPC_ID=vpc-xxxx
export SUBNET_ID_1=subnet-xxxx
export SUBNET_ID_2=subnet-yyyy
export DB_PASSWORD=your_secure_db_password
export JWT_SECRET=$(openssl rand -base64 32)
# Optional: export KEY_NAME=insightgym-key
chmod +x create-stack-me-south-1.sh
./create-stack-me-south-1.sh
```

### Option C: AWS CLI (one-off)

```bash
aws cloudformation create-stack --stack-name insightgym \
  --template-body file://infra/aws/ec2-me-south-1.yaml \
  --parameters \
    ParameterKey=VpcId,ParameterValue=vpc-xxxx \
    ParameterKey=SubnetId1,ParameterValue=subnet-xxxx \
    ParameterKey=SubnetId2,ParameterValue=subnet-yyyy \
    ParameterKey=EC2SubnetId,ParameterValue=subnet-xxxx \
    ParameterKey=DBPassword,ParameterValue=YOUR_DB_PASSWORD \
    ParameterKey=JwtSecretKey,ParameterValue=YOUR_JWT_SECRET \
  --capabilities CAPABILITY_NAMED_IAM \
  --region me-south-1
```

---

## 3. Push Docker image to ECR (me-south-1)

The stack creates an empty ECR repo. You must build and push your image at least once.

### From your machine

```bash
export AWS_REGION=me-south-1
export ECR_REPO=insightgym
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker build -f Dockerfile -t $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest .
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest
```

### Or use GitHub Actions

Use the workflow **Deploy to AWS EC2 (me-south-1)** (see below). It builds and pushes to ECR in me-south-1 and can optionally run the app update on EC2 via SSM.

---

## 4. Set SSM parameters (secrets)

After the stack is created, set the app secrets so the EC2 run script can start the container.

1. In **CloudFormation** → stack **insightgym** → **Outputs**.
2. Copy **RDSEndpoint** and the **CreateSSMParamsCommand** text.
3. Run the two `aws ssm put-parameter` commands from the output, replacing:
   - `YOUR_DB_PASSWORD` with the **same** RDS password you used in the stack.
   - `YOUR_JWT_SECRET` with a long random string (or the same `JwtSecretKey` you used).

Example (replace placeholders and run in me-south-1):

```bash
export REGION=me-south-1
export RDS_ENDPOINT=insightgym-db.xxxx.me-south-1.rds.amazonaws.com   # from stack output

aws ssm put-parameter --name /insightgym/DATABASE_URL \
  --value "postgresql://postgres:YOUR_DB_PASSWORD@$RDS_ENDPOINT:5432/raha_fitness" \
  --type SecureString --region $REGION --overwrite

aws ssm put-parameter --name /insightgym/JWT_SECRET_KEY \
  --value "YOUR_JWT_SECRET" --type SecureString --region $REGION --overwrite
```

---

## 5. Start the app on EC2

After SSM parameters are set and the image is in ECR:

- **With SSH** (if you set KeyName):  
  `ssh -i your-key.pem ec2-user@<EC2-public-IP>`  
  Then:  
  `sudo /opt/insightgym/run.sh`

- **With Session Manager** (no key):  
  **EC2** → select instance → **Connect** → **Session Manager** → Connect, then:  
  `sudo /opt/insightgym/run.sh`

The script pulls the latest image, reads secrets from SSM, and runs the container. The app will be available at the **ALB URL** (stack output **ALBUrl**).

---

## 6. GitHub Actions (optional)

A workflow **Deploy to AWS EC2 (me-south-1)** can:

1. Build the Docker image and push to ECR in **me-south-1**.
2. Optionally run `sudo /opt/insightgym/run.sh` on the EC2 instance via **SSM Send Command** to pull and restart.

**Secrets / variables** (repo → Settings → Secrets and variables → Actions):

| Name | Type | Description |
|------|------|-------------|
| `AWS_ACCESS_KEY_ID` | Secret | IAM user with ECR push + (optional) SSM SendCommand |
| `AWS_SECRET_ACCESS_KEY` | Secret | IAM user secret |
| `AWS_EC2_ME_SOUTH_1_INSTANCE_ID` | Variable or Secret | (Optional) EC2 instance ID for SSM deploy; if set, workflow runs `sudo /opt/insightgym/run.sh` on the instance after push |

**IAM** (for SSM deploy): the IAM user used by GitHub needs something like:

```json
{
  "Effect": "Allow",
  "Action": ["ssm:SendCommand"],
  "Resource": ["arn:aws:ec2:me-south-1:ACCOUNT:instance/INSTANCE_ID", "arn:aws:ssm:me-south-1:ACCOUNT:*"]
}
```

And the target instance must have the **AmazonSSMManagedInstanceCore** policy (already attached by the template).

---

## 7. HTTPS (optional)

- Request an **ACM certificate** in me-south-1 (e.g. for `app.yourdomain.com`).
- Add an **HTTPS listener** (443) to the ALB in the console, forwarding to the same target group, and attach the certificate.
- Point your domain to the ALB DNS (e.g. CNAME).

You can do this manually or by extending the CloudFormation template with an HTTPS listener and certificate.

---

## 8. Summary

| Step | Action |
|------|--------|
| 1 | Get VPC + 2 subnets in me-south-1 |
| 2 | Create CloudFormation stack (Console, script, or CLI) |
| 3 | Build and push Docker image to ECR in me-south-1 |
| 4 | Set SSM parameters `/insightgym/DATABASE_URL` and `/insightgym/JWT_SECRET_KEY` |
| 5 | On EC2 run `sudo /opt/insightgym/run.sh` |
| 6 | Open **ALBUrl** from stack outputs |

**Region:** all resources are in **me-south-1 (Middle East – Bahrain)**.
