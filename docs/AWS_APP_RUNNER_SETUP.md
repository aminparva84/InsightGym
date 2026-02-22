# AWS App Runner one-time setup (Mumbai)

Deployments use **GitHub Actions** to build the Docker image, push to **Amazon ECR** in **Mumbai (ap-south-1)**, and create/update the **App Runner** service. You only need to do the steps below once.

## 1. IAM role for App Runner (ECR access)

App Runner needs an IAM role that can pull images from your ECR repository.

### Option A: AWS Console

1. Open **IAM → Roles → Create role**.
2. **Trusted entity type:** Custom trust policy.
3. **Trust policy:** (App Runner uses `build.apprunner.amazonaws.com` to assume this role for ECR pull)

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "build.apprunner.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

4. **Permissions:** Attach the **AWS managed policy** `AWSAppRunnerServicePolicyForECRAccess` (gives ECR pull). Alternatively use a custom policy with `ecr:GetDownloadUrlForLayer`, `ecr:BatchGetImage`, `ecr:BatchCheckLayerAvailability` (and `ecr:GetAuthorizationToken` with `"Resource": "*"` if needed).
5. **Role name:** e.g. `AppRunnerECRAccessRole`.
6. Create the role and copy its **ARN** (e.g. `arn:aws:iam::123456789012:role/AppRunnerECRAccessRole`).

### Option B: AWS CLI

Run in a terminal (region not required for IAM):

```bash
# Create trust policy file (principal: build.apprunner.amazonaws.com per AWS docs)
cat > /tmp/apprunner-trust.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "build.apprunner.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role
aws iam create-role \
  --role-name AppRunnerECRAccessRole \
  --assume-role-policy-document file:///tmp/apprunner-trust.json

# Attach AWS managed policy for ECR access (recommended)
aws iam attach-role-policy \
  --role-name AppRunnerECRAccessRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess

# Get role ARN (use this in GitHub secret AWS_APP_RUNNER_ECR_ACCESS_ROLE_ARN)
aws iam get-role --role-name AppRunnerECRAccessRole --query 'Role.Arn' --output text
```

## 2. GitHub secrets

In **GitHub → Repo → Settings → Secrets and variables → Actions**, add:

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user access key (must have ECR + App Runner permissions). |
| `AWS_SECRET_ACCESS_KEY` | IAM user secret key. |
| `AWS_APP_RUNNER_ECR_ACCESS_ROLE_ARN` | ARN of the role from step 1 (e.g. `arn:aws:iam::123456789012:role/AppRunnerECRAccessRole`). |
| `DATABASE_URL` | (Optional) PostgreSQL URL for the app. |
| `JWT_SECRET_KEY` | (Optional) JWT secret for the app. |

The workflow creates the **ECR repository** (`insightgym`) in **ap-south-1** if it does not exist. The first run will **create** the App Runner service; later runs will **update** it.

## 3. Push to main

Push (or merge) to the `main` branch. The workflow **Deploy to AWS App Runner (Mumbai)** will:

1. Build the Docker image (same Dockerfile as Cloud Run).
2. Push to ECR in **ap-south-1**.
3. Create the App Runner service (first time) or update it with the new image.

After the first run, the service URL is in **AWS Console → App Runner → Service `insightgym`** (e.g. `https://xxxxx.ap-south-1.awsapprunner.com`).

## Region

- **App Runner + ECR:** **Mumbai** (`ap-south-1`).

## Troubleshooting

- **Access denied / ECR:** Ensure the role used in `AWS_APP_RUNNER_ECR_ACCESS_ROLE_ARN` has the ECR actions above and that the trust policy allows `build.apprunner.amazonaws.com` (or `apprunner.amazonaws.com`) to assume the role.
- **Service not updating:** Check the workflow log for the “Create or update App Runner service” step; confirm the image tag and ECR repo are correct.
- **Health check fails:** The app must listen on **port 8080** and respond to **GET /health**. The Dockerfile and app already do this.
