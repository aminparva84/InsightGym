# InsightGYM – Deployed on AWS EC2 (me-south-1)

Deployment completed. Your account does not support creating Application Load Balancers in this region, so the app is served directly from EC2 with an Elastic IP.

## Application URLs

- **HTTPS (recommended):** **https://app.insightgym.com** — Use this once DNS for `app.insightgym.com` points to **15.185.88.160**. Caddy on the instance serves HTTPS with a Let's Encrypt certificate.
- **HTTP (direct):** **http://15.185.88.160:8080** — Still works; use if you haven’t set up a domain yet.

To use your own domain, see **docs/AWS_EC2_HTTPS_CADDY.md**.

## What was created (region: me-south-1, Bahrain)

| Resource | Details |
|----------|---------|
| **EC2** | Instance `i-0fad77d726660bbd7`, t3.small, Amazon Linux 2, Docker |
| **Elastic IP** | 15.185.88.160 (stable public IP) |
| **RDS PostgreSQL** | `insightgym-db.cvokiuug2z3c.me-south-1.rds.amazonaws.com`, db.t3.micro, database `raha_fitness` |
| **ECR** | Repository `insightgym` in me-south-1 (image pushed) |
| **SSM** | `/insightgym/DATABASE_URL`, `/insightgym/JWT_SECRET_KEY`, `/insightgym/run_sh_script` |

Secrets (DB password, JWT secret) are in **AWS Systems Manager Parameter Store** in me-south-1. They were generated during setup; do not commit them to the repo.

## Useful commands

```bash
# Stack outputs
aws cloudformation describe-stacks --stack-name insightgym --region me-south-1 --query "Stacks[0].Outputs"

# Restart app on EC2 (after pushing a new image to ECR)
aws ssm send-command --instance-ids i-0fad77d726660bbd7 --document-name "AWS-RunShellScript" --parameters file://infra/aws/ssm-fetch-and-run.json --region me-south-1
```

## GitHub Actions

- **Deploy to AWS App Runner (Mumbai):** Runs on **push to `main`**. Use this while EC2 is stopped.
- **Deploy to AWS EC2 (me-south-1):** Runs **only when you trigger it manually** (Actions → workflow → Run workflow). It does **not** run on push to main, so it won’t run while EC2 is stopped. When EC2 is running, run this workflow to build and deploy the latest image to this instance.

**One-time setup for EC2 workflow:** Add variable **`AWS_EC2_ME_SOUTH_1_INSTANCE_ID`** = **`i-0fad77d726660bbd7`** (and AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY secrets). **IAM:** the IAM user must be allowed **`ssm:SendCommand`** for this instance.

## HTTPS (done)

**Caddy** is installed on the EC2 instance and provides HTTPS with Let's Encrypt. Ports **80** and **443** are open. Set SSM parameter `/insightgym/DOMAIN` to your domain and point DNS A record to **15.185.88.160**, then restart Caddy. Full details: **docs/AWS_EC2_HTTPS_CADDY.md**.

## Stopping and starting the server and RDS (save cost)

**Stop both (run when you want to stop charges):**
```bash
aws ec2 stop-instances --instance-ids i-0fad77d726660bbd7 --region me-south-1
aws rds stop-db-instance --db-instance-identifier insightgym-db --region me-south-1
```

**Resume both (run when you want to use the app again):**
1. Start RDS and wait until available:  
   `aws rds start-db-instance --db-instance-identifier insightgym-db --region me-south-1`  
   then `aws rds wait db-instance-available --db-instance-identifier insightgym-db --region me-south-1`
2. Start EC2 and wait until running:  
   `aws ec2 start-instances --instance-ids i-0fad77d726660bbd7 --region me-south-1`  
   then `aws ec2 wait instance-running --instance-ids i-0fad77d726660bbd7 --region me-south-1`
3. Run the app on EC2:  
   `aws ssm send-command --instance-ids i-0fad77d726660bbd7 --document-name "AWS-RunShellScript" --parameters file://infra/aws/ssm-params.json --region me-south-1`

Full workflow (create EC2, stop, resume) is in **docs/AWS_EC2_FULL_WORKFLOW.md**.

## Template change (for future stacks)

The CloudFormation template was updated to use a **LiteralDollar** parameter so the EC2 UserData run script is correct on first boot. Existing instances use the script stored in SSM (`/insightgym/run_sh_script`) and fetched at run time.
