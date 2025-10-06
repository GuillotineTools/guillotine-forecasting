#!/usr/bin/env python3
"""
Download GitHub Actions artifacts to local outputs folder.
This script will pull the latest forecast outputs from GitHub Actions runs.
"""
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_command(cmd):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        return None

def download_latest_artifacts():
    """Download the latest GitHub Actions artifacts to outputs folder."""
    print("🔽 Downloading GitHub Actions artifacts...")

    # Ensure outputs directory exists
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)

    # Get recent workflow runs
    try:
        # List recent workflow runs
        runs_json = run_command('gh run list --limit 5 --json createdAt,status,conclusion,databaseId')
        if not runs_json:
            print("❌ Failed to get workflow runs. Is GitHub CLI installed and authenticated?")
            return False

        runs = json.loads(runs_json)

        for run in runs:
            if run.get('conclusion') == 'success':
                run_id = run['databaseId']
                created_at = run['createdAt']
                print(f"📦 Found successful run: {run_id} ({created_at})")

                # List artifacts for this run
                artifacts_json = run_command(f'gh run view {run_id} --json artifacts')
                if artifacts_json:
                    artifacts_data = json.loads(artifacts_json)

                    for artifact in artifacts_data.get('artifacts', []):
                        if 'forecast-outputs' in artifact['name']:
                            artifact_name = artifact['name']
                            print(f"  📄 Downloading artifact: {artifact_name}")

                            # Download artifact
                            zip_path = f"/tmp/{artifact_name}.zip"
                            download_cmd = f'gh run download {run_id} --name "{artifact_name}" --dir /tmp/'
                            if run_command(download_cmd):
                                # Extract to outputs folder
                                extract_cmd = f'unzip -o "{zip_path}" -d outputs/'
                                if run_command(extract_cmd):
                                    print(f"  ✅ Extracted {artifact_name} to outputs/")
                                    # Clean up zip file
                                    run_command(f'rm "{zip_path}"')
                                else:
                                    print(f"  ❌ Failed to extract {artifact_name}")
                            else:
                                print(f"  ❌ Failed to download {artifact_name}")

                # Only download the most recent successful run
                break

    except Exception as e:
        print(f"❌ Error downloading artifacts: {e}")
        return False

    print("✅ Artifact download completed!")
    return True

def main():
    """Main function."""
    print(f"🤖 GitHub Actions Artifact Downloader")
    print(f"📅 Running at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # Check if GitHub CLI is available
    if not run_command('which gh'):
        print("❌ GitHub CLI (gh) is not installed or not in PATH")
        print("💡 Install it from: https://cli.github.com/")
        return False

    # Check if authenticated
    auth_status = run_command('gh auth status')
    if not auth_status or 'not logged in' in auth_status.lower():
        print("❌ GitHub CLI is not authenticated")
        print("💡 Run: gh auth login")
        return False

    print("✅ GitHub CLI is authenticated")

    # Download artifacts
    success = download_latest_artifacts()

    if success:
        print("\n🎉 All artifacts downloaded successfully!")
        print(f"📁 Check the outputs/ folder for forecast files")

        # List downloaded files
        outputs_dir = Path("outputs")
        if outputs_dir.exists():
            print(f"\n📄 Files in outputs/:")
            for file in sorted(outputs_dir.glob("*.md")):
                size_kb = file.stat().st_size / 1024
                print(f"  - {file.name} ({size_kb:.1f} KB)")
    else:
        print("\n❌ Failed to download artifacts")
        return False

    return True

if __name__ == "__main__":
    main()