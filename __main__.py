import datetime
import os
import tempfile
import zipfile

import pulumi
import pulumi_gcp as gcp
from dotenv import load_dotenv

load_dotenv()

PROJECT_NAME = f"{pulumi.get_project()}-{pulumi.get_stack()}"
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def create_zip(files_to_zip):
    temp_dir = tempfile.TemporaryDirectory().name
    os.makedirs(temp_dir)
    zip_file = os.path.join(temp_dir, "function.zip")
    with zipfile.ZipFile(zip_file, "w") as zipf:
        for file in files_to_zip:
            zipf.write(file, os.path.basename(file))
    return zip_file


zip_path = create_zip(["main.py", "calculator.py", "requirements.txt"])
archive_name = f"{PROJECT_NAME}-function-{TIMESTAMP}.zip"

bucket = gcp.storage.Bucket("bucket", name=f"{PROJECT_NAME}-bucket", location="ASIA")
archive = gcp.storage.BucketObject(
    "archive", bucket=bucket.name, name=archive_name, source=pulumi.FileAsset(zip_path)
)

function = gcp.cloudfunctionsv2.Function(
    "function",
    name=f"{PROJECT_NAME}-function",
    location="asia-southeast1",
    description="Telegram Bot for calculating the OLED black pixels percentage from images",
    build_config=gcp.cloudfunctionsv2.FunctionBuildConfigArgs(
        runtime="python312",
        entry_point="main",
        environment_variables={
            "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        },
        source=gcp.cloudfunctionsv2.FunctionBuildConfigSourceArgs(
            storage_source=gcp.cloudfunctionsv2.FunctionBuildConfigSourceStorageSourceArgs(
                bucket=bucket.name, object=archive.name
            )
        ),
    ),
    service_config=gcp.cloudfunctionsv2.FunctionServiceConfigArgs(
        max_instance_count=1,
        available_memory="256M",
        timeout_seconds=60,
        environment_variables={
            "TELEGRAM_BOT_TOKEN": TELEGRAM_BOT_TOKEN,
        },
    ),
)

gcp.cloudfunctionsv2.FunctionIamMember(
    "function-invoker",
    project=function.project,
    location=function.location,
    cloud_function=function.name,
    role="roles/cloudfunctions.invoker",
    member="allUsers",
)

gcp.cloudrun.IamMember(
    "cloudrun-invoker",
    location=function.location,
    project=function.project,
    service=function.name,
    role="roles/run.invoker",
    member="allUsers",
)


pulumi.export("bucket_object_name", archive.output_name)
pulumi.export("function_url", function.url)
