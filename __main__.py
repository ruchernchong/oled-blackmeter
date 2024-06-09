import os
import tempfile
import zipfile

import pulumi
import pulumi_gcp as gcp
from dotenv import load_dotenv

load_dotenv()

PROJECT_NAME = f"{pulumi.get_stack()}-{pulumi.get_project()}"

config = pulumi.Config()
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")


def create_zip(files_to_zip):
    temp_dir = tempfile.TemporaryDirectory().name
    os.makedirs(temp_dir)
    zip_file = os.path.join(temp_dir, "function.zip")
    with zipfile.ZipFile(zip_file, "w") as zipf:
        for file in files_to_zip:
            zipf.write(file, os.path.basename(file))
    return zip_file


zip_path = create_zip(["main.py", "calculator.py", "requirements.txt"])

bucket = gcp.storage.Bucket("bucket", name=f"{PROJECT_NAME}-bucket", location="ASIA")

archive = gcp.storage.BucketObject(
    "archive", bucket=bucket.name, source=pulumi.FileAsset(zip_path)
)

function = gcp.cloudfunctions.Function(
    "function",
    name=f"{PROJECT_NAME}-function",
    region="asia-southeast1",
    description="Telegram Bot for calculating true black percentage from images",
    runtime="python312",
    available_memory_mb=256,
    source_archive_bucket=bucket.name,
    source_archive_object=archive.name,
    trigger_http=True,
    https_trigger_security_level="SECURE_ALWAYS",
    entry_point="main",
    environment_variables={
        "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
    },
)

invoker = gcp.cloudfunctions.FunctionIamMember(
    "invoker",
    project=function.project,
    region=function.region,
    cloud_function=function.name,
    role="roles/cloudfunctions.invoker",
    member="allUsers",
)

pulumi.export("bucket_object_name", archive.output_name)
pulumi.export("function_url", function.https_trigger_url)
