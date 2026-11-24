# Map tiles infrastructure

Terraform for the map tile CDN infrastructure: S3 bucket, CloudFront distribution, and a GitHub Actions IAM role (OIDC-federated — no long-lived access keys).

## Prerequisites

1. Install [Terraform](https://developer.hashicorp.com/terraform/install)
2. Ensure the AWS CLI is configured: `aws configure` using credentials that can create S3, CloudFront, and IAM resources

## First-time setup

```bash
cd infra/map-tiles
terraform init
terraform apply
```

Review the plan and type `yes`. Once complete, Terraform prints four outputs:

| Output | What to do with it |
|--------|--------------------|
| `cloudfront_domain` | Set `TILES_CDN` in [frontend/app/map/tile-config.ts](../../frontend/app/map/tile-config.ts) and commit |
| `cloudfront_distribution_id` | Add to GitHub Secrets as `CLOUDFRONT_DISTRIBUTION_ID` |
| `s3_bucket_name` | Add to GitHub Secrets as `S3_TILES_BUCKET` |
| `deploy_role_arn` | Add to GitHub Secrets as `AWS_MAP_TILES_ROLE_ARN` |

GitHub Secrets are at: https://github.com/iamlogand/republic-of-rome-online/settings/secrets/actions

## State

Terraform state is stored locally in `infra/map-tiles/terraform.tfstate` and is gitignored.
