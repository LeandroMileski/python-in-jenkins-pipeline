import boto3
import sys
import subprocess
import os

REGION          = os.environ.get("AWS_REGION", "eu-west-1")
REPOSITORY_NAME = os.environ.get("ECR_REPOSITORY_NAME", "repo1")
HOST        = os.environ.get("HOST", "172.237.115.218")
USER        = os.environ.get("EC2_USER", "root")
SSH_KEY         = os.environ.get("SSH_KEY","~/.ssh/id_rsa")
SELECTED_TAG    = os.environ.get("SELECTED_TAG","1.0")




def validate_env():
    missing = [k for k, v in {
        "HOST":     HOST,
        "USER":     USER,
        "SSH_KEY":      SSH_KEY,
        "SELECTED_TAG": SELECTED_TAG
    }.items() if not v]

    if missing:
        print(f"ERROR: Missing environment variables: {', '.join(missing)}", file=sys.stderr)
        sys.exit(1)


def get_ecr_registry():
    ecr_client    = boto3.client("ecr", region_name=REGION)
    auth_response = ecr_client.get_authorization_token()
    auth_data     = auth_response["authorizationData"][0]
    registry      = auth_data["proxyEndpoint"].replace("https://", "")
    return registry


def ssh(host, user, key, command):
    result = subprocess.run(
        [
            "ssh",
            "-i", key,
            "-o", "StrictHostKeyChecking=no",
            f"{user}@{host}",
            command
        ],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"SSH ERROR: {result.stderr}", file=sys.stderr)
        sys.exit(1)


def main():
    validate_env()

    print("AWS_ACCESS_KEY_ID set:    ", bool(os.environ.get("AWS_ACCESS_KEY_ID")))
    print("AWS_SECRET_ACCESS_KEY set:", bool(os.environ.get("AWS_SECRET_ACCESS_KEY")))

    try:
        print("\nFetching ECR registry URL...")
        registry = get_ecr_registry()
        image_uri = f"{registry}/{REPOSITORY_NAME}:{SELECTED_TAG}"
        print(f"Image URI: {image_uri}")

        print("\nLogging Server into ECR...")
        ssh(HOST, USER, SSH_KEY, f"aws ecr get-login-password --region {REGION} | "
            f"docker login --username AWS --password-stdin {registry}")

        print(f"\nPulling image on EC2: {image_uri}")
        ssh(HOST, USER, SSH_KEY, f"docker pull {image_uri}")

        print("\nDeploying container...")
        ssh(HOST, USER, SSH_KEY, f"docker stop app || true && "
            f"docker rm app || true && "
            f"docker run -d --name app -p 80:80 {image_uri}")

        print(f"\nDeployment complete: {image_uri}")
        sys.exit(0)

    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

