# GitHub secrets for "Deploy to AWS App Runner (Mumbai)"

The workflow needs **three secrets**. Add them in **GitHub → Repo → Settings → Secrets and variables → Actions → Secrets**.

## Required secrets

| Secret | Description |
|--------|-------------|
| **AWS_ACCESS_KEY_ID** | IAM user access key (same as for EC2 workflow; needs ECR + App Runner permissions). |
| **AWS_SECRET_ACCESS_KEY** | IAM user secret key. |
| **AWS_APP_RUNNER_ECR_ACCESS_ROLE_ARN** | ARN of the IAM role that App Runner uses to pull images from ECR. |

## Your App Runner ECR role ARN

The role **AppRunnerECRAccessRole** already exists in your account. Use this value for **AWS_APP_RUNNER_ECR_ACCESS_ROLE_ARN**:

```
arn:aws:iam::255315172922:role/AppRunnerECRAccessRole
```

## Set secrets with gh CLI

If you haven’t set the AWS keys yet:

```bash
gh secret set AWS_ACCESS_KEY_ID --body "YOUR_ACCESS_KEY_ID"
gh secret set AWS_SECRET_ACCESS_KEY --body "YOUR_SECRET_ACCESS_KEY"
```

Set the App Runner role ARN (required for this workflow):

```bash
gh secret set AWS_APP_RUNNER_ECR_ACCESS_ROLE_ARN --body "arn:aws:iam::255315172922:role/AppRunnerECRAccessRole"
```

Or run without `--body` and paste when prompted:

```bash
gh secret set AWS_APP_RUNNER_ECR_ACCESS_ROLE_ARN
# Paste: arn:aws:iam::255315172922:role/AppRunnerECRAccessRole
```

## After adding secrets

- The workflow **Deploy to AWS App Runner (Mumbai)** runs on every **push to main**.
- Push a commit or use **Actions → Deploy to AWS App Runner (Mumbai) → Run workflow** to test.
