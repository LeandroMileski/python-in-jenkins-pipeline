import boto3
import sys
import os

REGION = os.environ.get("AWS_REGION", "eu-west-1")
REPOSITORY_NAME = os.environ.get("ECR_REPOSITORY_NAME", "repo1")

def main():
    try:
        ecr_client = boto3.client("ecr", region_name=REGION)

        paginator = ecr_client.get_paginator("describe_images")
        all_images = []
        for page in paginator.paginate(repositoryName=REPOSITORY_NAME):
            all_images.extend(page['imageDetails'])

        if not all_images:
            print(f"ERROR: No images found in {REPOSITORY_NAME}", file=sys.stderr)
            sys.exit(1)

        all_images.sort(key=lambda x: x["imagePushedAt"], reverse=True)

        for image in all_images:
            if "imageTags" in image:
                tag = image['imageTags'][0]
                pushed_at = image['imagePushedAt'].strftime("%Y-%m-%d %H:%M")
                print(f"{tag} ( pushed: {pushed_at} )")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()