output "cloudfront_domain" {
  description = "Set TILES_CDN in frontend/app/map/tile-config.ts to this value"
  value       = "https://${aws_cloudfront_distribution.tiles.domain_name}"
}

output "cloudfront_distribution_id" {
  description = "Add to GitHub Secrets as CLOUDFRONT_DISTRIBUTION_ID"
  value       = aws_cloudfront_distribution.tiles.id
}

output "s3_bucket_name" {
  description = "Add to GitHub Secrets as S3_TILES_BUCKET"
  value       = aws_s3_bucket.tiles.bucket
}

output "deploy_role_arn" {
  description = "Add to GitHub Secrets as AWS_MAP_TILES_ROLE_ARN"
  value       = aws_iam_role.deploy_map_tiles.arn
}
