# Full workflow: EC2 deployment (me-south-1) from scratch

This document describes **everything** done to deploy InsightGYM on AWS EC2 in **me-south-1 (Bahrain)** so you can repeat the workflow later (e.g. new account, new region, or after tearing down).

---

## What gets created

| Resource | Purpose |
|----------|--------|
| **CloudFormation stack** `insightgym` | ECR repo, RDS PostgreSQL, EC2 instance, Elastic IP, security groups (no ALB; account did not support it in me-south-1) |
| **EC2** | One `t3.small`, Amazon Linux 2, Docker; app runs in a container on port 8080 |
| **Elastic IP** | Stable public IP so the app is reachable at `http://<EIP>:8080` |
| **RDS PostgreSQL** | `db.t3.micro`, 20 GB, database `raha_fitness`; app uses it via `DATABASE_URL` |
| **ECR** | Repository `insightgym` in me-south-1 for the Docker image |
| **SSM Parameters** | `DATABASE_URL`, `JWT_SECRET_KEY`, `DOMAIN` (for Caddy), `run_sh_script` (script to pull image and run container) |
| **Caddy** (optional) | Reverse proxy on EC2 for HTTPS with Let's Encrypt; listens on 80/443 |
| **GitHub Actions** | **App Runner (Mumbai)** runs on push to `main`. **EC2 (me-south-1)** runs only when triggered manually (workflow_dispatch) so it is not run while EC2 is stopped. |

---

## Prerequisites

- **AWS CLI** installed and configured (credentials with permission to create CloudFormation, EC2, RDS, ECR, IAM, SSM).
- **Region:** **me-south-1** (Bahrain). All resources are created there.
- **Default VPC** in me-south-1 (or your own VPC and subnets).

---

## Step 1: Get VPC and subnets (me-south-1)

```bash
export AWS_REGION=me-south-1

# Default VPC
VPC_ID=$(aws ec2 describe-vpcs --region $AWS_REGION --filters Name=isDefault,Values=true --query 'Vpcs[0].VpcId' --output text)
echo "VPC_ID=$VPC_ID"

# Subnets (pick two in different AZs for RDS; one for EC2)
aws ec2 describe-subnets --region $AWS_REGION --filters Name=vpc-id,Values=$VPC_ID --query 'Subnets[*].[SubnetId,AvailabilityZone]' --output table
```

Note: **SubnetId1**, **SubnetId2** (two different AZs), **EC2SubnetId** (can be same as SubnetId1).

---

## Step 2: Create CloudFormation stack

The template is **`infra/aws/ec2-me-south-1.yaml`**. It creates ECR, RDS, EC2, Elastic IP, and security groups. **No ALB** (not used in this workflow).

Generate a strong DB password and JWT secret (e.g. `openssl rand -base64 24` and `openssl rand -base64 32`).

**PowerShell (Windows):**

```powershell
cd c:\Code\InsightGYM
aws cloudformation create-stack --stack-name insightgym `
  --template-body file://infra/aws/ec2-me-south-1.yaml `
  --parameters `
    ParameterKey=VpcId,ParameterValue=YOUR_VPC_ID `
    ParameterKey=SubnetId1,ParameterValue=SUBNET_ID_1 `
    ParameterKey=SubnetId2,ParameterValue=SUBNET_ID_2 `
    ParameterKey=EC2SubnetId,ParameterValue=SUBNET_ID_1 `
    ParameterKey=DBPassword,ParameterValue=YOUR_DB_PASSWORD `
    ParameterKey=JwtSecretKey,ParameterValue=YOUR_JWT_SECRET `
    ParameterKey=AWSRegion,ParameterValue=me-south-1 `
  --capabilities CAPABILITY_NAMED_IAM `
  --region me-south-1
```

**Bash (Linux/Mac):**

```bash
aws cloudformation create-stack --stack-name insightgym \
  --template-body file://infra/aws/ec2-me-south-1.yaml \
  --parameters \
    ParameterKey=VpcId,ParameterValue=YOUR_VPC_ID \
    ParameterKey=SubnetId1,ParameterValue=SUBNET_ID_1 \
    ParameterKey=SubnetId2,ParameterValue=SUBNET_ID_2 \
    ParameterKey=EC2SubnetId,ParameterValue=SUBNET_ID_1 \
    ParameterKey=DBPassword,ParameterValue=YOUR_DB_PASSWORD \
    ParameterKey=JwtSecretKey,ParameterValue=YOUR_JWT_SECRET \
    ParameterKey=AWSRegion,ParameterValue=me-south-1 \
  --capabilities CAPABILITY_NAMED_IAM \
  --region me-south-1
```

Wait for the stack to complete (RDS takes several minutes):

```bash
aws cloudformation wait stack-create-complete --stack-name insightgym --region me-south-1
```

Get outputs (RDS endpoint, EC2 instance ID, Elastic IP):

```bash
aws cloudformation describe-stacks --stack-name insightgym --region me-south-1 --query "Stacks[0].Outputs" --output table
```

---

## Step 3: Set SSM parameters (secrets for the app)

The app and the run script read **DATABASE_URL** and **JWT_SECRET_KEY** from SSM. Use the **same** DB password and JWT secret you used in the stack.

```bash
export AWS_REGION=me-south-1
export RDS_ENDPOINT=your-rds-endpoint-from-stack-output   # e.g. insightgym-db.xxxx.me-south-1.rds.amazonaws.com
export DB_PASSWORD=your_db_password
export JWT_SECRET=your_jwt_secret

aws ssm put-parameter --name /insightgym/DATABASE_URL \
  --value "postgresql://postgres:${DB_PASSWORD}@${RDS_ENDPOINT}:5432/raha_fitness" \
  --type SecureString --region $AWS_REGION --overwrite

aws ssm put-parameter --name /insightgym/JWT_SECRET_KEY \
  --value "$JWT_SECRET" --type SecureString --region $AWS_REGION --overwrite
```

**Run script:** The EC2 instance runs the app by executing a script that pulls the image from ECR and runs the container. That script is stored in SSM as **`/insightgym/run_sh_script`**. The content is the same as what’s in **`infra/aws/run-sh-content.sh`** (see repo). You can store it in SSM via the AWS Console (paste the script) or by building a JSON payload and using `aws ssm put-parameter` with the script body. After that, the instance fetches it with:

```bash
aws ssm get-parameter --name /insightgym/run_sh_script --query Parameter.Value --output text --region me-south-1 | sudo tee /opt/insightgym/run.sh
sudo chmod +x /opt/insightgym/run.sh
```

(Or use the SSM “fetch and run” command from the repo: **`infra/aws/ssm-fetch-and-run.json`**.)

---

## Step 4: Build and push Docker image to ECR (me-south-1)

```bash
export AWS_REGION=me-south-1
export ECR_REPO=insightgym
export ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
docker build -f Dockerfile -t $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest .
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO:latest
```

---

## Step 5: Run the app on EC2

After the run script is in place on the instance (either from UserData + SSM params, or by fetching from SSM and writing to `/opt/insightgym/run.sh`), execute it:

**Via SSM (from your machine):**

```bash
aws ssm send-command --instance-ids YOUR_EC2_INSTANCE_ID \
  --document-name "AWS-RunShellScript" \
  --parameters file://infra/aws/ssm-fetch-and-run.json \
  --region me-south-1
```

Or, if the script is already at `/opt/insightgym/run.sh`:

```bash
aws ssm send-command --instance-ids YOUR_EC2_INSTANCE_ID \
  --document-name "AWS-RunShellScript" \
  --parameters file://infra/aws/ssm-params.json \
  --region me-south-1
```

(**ssm-params.json** contains `{"commands":["sudo /opt/insightgym/run.sh"]}`.)

The app will be reachable at **http://<Elastic-IP>:8080**.

---

## Step 6 (Optional): HTTPS with Caddy

1. **Open ports 80 and 443** on the EC2 security group (if not already in the template).
2. **Set domain** in SSM:  
   `aws ssm put-parameter --name /insightgym/DOMAIN --value "app.yourdomain.com" --type String --region me-south-1 --overwrite`
3. **Run the Caddy setup script** on the instance. Script: **`infra/aws/setup-caddy-https.sh`**. It reads `/insightgym/DOMAIN`, installs Caddy, writes `/etc/caddy/Caddyfile`, and starts Caddy. Run it via SSM (e.g. base64-encode the script and run `echo <base64> | base64 -d | sudo bash`) or via SSH/Session Manager.
4. **Point DNS:** A record for your domain → Elastic IP of the EC2 instance.

Details: **docs/AWS_EC2_HTTPS_CADDY.md**.

---

## Step 7: GitHub Actions

- **Deploy to AWS App Runner (Mumbai):** Runs automatically on **push to `main`**. Use this when EC2 is stopped; App Runner serves the app from Mumbai.
- **Deploy to AWS EC2 (me-south-1):** Runs **only when triggered manually** (Actions tab → select workflow → Run workflow). It does **not** run on push to main, so it won’t run while EC2 is stopped. When you start EC2 again, you can run this workflow to build and deploy the latest image to EC2.

Secrets/variable for the EC2 workflow (when you use it):

1. **Secrets:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (IAM user with ECR push + SSM SendCommand).
2. **Variable or secret:** `AWS_EC2_ME_SOUTH_1_INSTANCE_ID` (EC2 instance ID).

**gh CLI:**

```bash
gh secret set AWS_ACCESS_KEY_ID --body "YOUR_ACCESS_KEY_ID"
gh secret set AWS_SECRET_ACCESS_KEY --body "YOUR_SECRET_ACCESS_KEY"
gh variable set AWS_EC2_ME_SOUTH_1_INSTANCE_ID --body "i-xxxxxxxxx"
```

---

## How to stop the server and RDS (save cost)

Run these when you want to stop charges. Replace `YOUR_EC2_INSTANCE_ID` with your instance ID (e.g. `i-0fad77d726660bbd7`). Region: **me-south-1**.

### 1. Stop the EC2 instance

```bash
aws ec2 stop-instances --instance-ids YOUR_EC2_INSTANCE_ID --region me-south-1
```

- Stops EC2 instance billing. You still pay for the **EBS volume** and the **Elastic IP** while they exist.
- Check status: `aws ec2 describe-instances --instance-ids YOUR_EC2_INSTANCE_ID --region me-south-1 --query 'Reservations[0].Instances[0].State.Name' --output text` (should become `stopped`).

### 2. Stop the RDS instance

```bash
aws rds stop-db-instance --db-instance-identifier insightgym-db --region me-south-1
```

- Stops RDS instance billing. Data is retained; the same endpoint is used when you start again.
- Check status: `aws rds describe-db-instances --db-instance-identifier insightgym-db --region me-south-1 --query 'DBInstances[0].DBInstanceStatus' --output text` (should become `stopped`).
- **Note:** After stopping, AWS may enforce a minimum stopped period (e.g. 7 days) before you can stop again. Starting is always allowed.

---

## How to resume the server and RDS

When you want to use the EC2 app again, do the following in order. Region: **me-south-1**.

### 1. Start RDS first

```bash
aws rds start-db-instance --db-instance-identifier insightgym-db --region me-south-1
```

- Wait until the instance is **available** (a few minutes):
  ```bash
  aws rds wait db-instance-available --db-instance-identifier insightgym-db --region me-south-1
  ```
- Or check: `aws rds describe-db-instances --db-instance-identifier insightgym-db --region me-south-1 --query 'DBInstances[0].DBInstanceStatus' --output text`

### 2. Start the EC2 instance

```bash
aws ec2 start-instances --instance-ids YOUR_EC2_INSTANCE_ID --region me-south-1
```

- Wait until the instance is **running**:
  ```bash
  aws ec2 wait instance-running --instance-ids YOUR_EC2_INSTANCE_ID --region me-south-1
  ```

### 3. Run the app on EC2

The container is not automatically started after a stop/start. Run the run script via SSM:

```bash
aws ssm send-command --instance-ids YOUR_EC2_INSTANCE_ID \
  --document-name "AWS-RunShellScript" \
  --parameters file://infra/aws/ssm-params.json \
  --region me-south-1
```

(Ensure you’re in the repo directory so `infra/aws/ssm-params.json` is found.)

Alternatively, trigger the **Deploy to AWS EC2 (me-south-1)** workflow manually from the GitHub Actions tab; it will build, push to ECR, and run the update on the instance.

### 4. App URL

- **HTTP:** `http://<Elastic-IP>:8080` (Elastic IP is in CloudFormation stack outputs).
- **HTTPS:** If Caddy is configured, use `https://<your-domain>` once DNS points to the Elastic IP.

---

## Tear down (delete everything)

To remove all resources and stop all charges:

1. **Delete the CloudFormation stack:**  
   `aws cloudformation delete-stack --stack-name insightgym --region me-south-1`  
   This removes EC2, RDS (with a final snapshot if configured), EIP, ECR repo, security groups, etc. SSM parameters are **not** deleted by the stack; delete them manually if desired.
2. **Optionally delete SSM parameters:**  
   `aws ssm delete-parameter --name /insightgym/DATABASE_URL --region me-south-1` (and similarly for other `/insightgym/*` parameters).

---

## File reference

| File | Purpose |
|------|--------|
| **infra/aws/ec2-me-south-1.yaml** | CloudFormation template (EC2, RDS, ECR, EIP, SGs; no ALB) |
| **infra/aws/create-stack-me-south-1.sh** | Script to create stack (bash) |
| **infra/aws/run-sh-content.sh** | Script that runs on EC2 to pull image and start container (store in SSM as run_sh_script) |
| **infra/aws/ssm-params.json** | SSM Send Command: `sudo /opt/insightgym/run.sh` |
| **infra/aws/ssm-fetch-and-run.json** | SSM Send Command: fetch run script from SSM, write to run.sh, run it |
| **infra/aws/setup-caddy-https.sh** | Install Caddy and configure HTTPS (domain from SSM /insightgym/DOMAIN) |
| **.github/workflows/deploy-aws-ec2-me-south-1.yml** | Build, push to ECR, update EC2 via SSM; **manual trigger only** (no push to main) |
| **.github/workflows/deploy-aws-apprunner.yml** | Deploy to App Runner (Mumbai); **runs on push to main** |
| **docs/AWS_EC2_ME_SOUTH_1_SETUP.md** | Setup guide (overview and options) |
| **docs/AWS_EC2_HTTPS_CADDY.md** | HTTPS with Caddy |
| **docs/AWS_EC2_ME_SOUTH_1_DEPLOYED.md** | Post-deploy summary and URLs |

---

## Summary checklist

### Create EC2 (full workflow, repeat from scratch)

1. Get VPC + subnets in me-south-1 (Step 1).  
2. Create CloudFormation stack with `ec2-me-south-1.yaml` (Step 2).  
3. Set SSM: `/insightgym/DATABASE_URL`, `/insightgym/JWT_SECRET_KEY`, and optionally `/insightgym/run_sh_script` (Step 3).  
4. Build and push Docker image to ECR in me-south-1 (Step 4).  
5. Run app on EC2 via SSM (Step 5).  
6. (Optional) HTTPS: set `/insightgym/DOMAIN`, run Caddy setup script, point DNS to EIP (Step 6).  
7. GitHub: set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_EC2_ME_SOUTH_1_INSTANCE_ID for EC2 workflow (Step 7).

### Stop (server and RDS)

- Stop EC2: `aws ec2 stop-instances --instance-ids YOUR_EC2_INSTANCE_ID --region me-south-1`  
- Stop RDS: `aws rds stop-db-instance --db-instance-identifier insightgym-db --region me-south-1`  
- Push to main will only trigger **App Runner (Mumbai)**; EC2 workflow does not run on push.

### Resume (server and RDS)

- Start RDS: `aws rds start-db-instance --db-instance-identifier insightgym-db --region me-south-1`; wait until `available`.  
- Start EC2: `aws ec2 start-instances --instance-ids YOUR_EC2_INSTANCE_ID --region me-south-1`; wait until `running`.  
- Run app on EC2: `aws ssm send-command --instance-ids YOUR_EC2_INSTANCE_ID --document-name "AWS-RunShellScript" --parameters file://infra/aws/ssm-params.json --region me-south-1` (or run the EC2 workflow manually from GitHub Actions).
