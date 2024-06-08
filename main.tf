terraform {
  required_providers {
    archive = {
      source  = "hashicorp/archive"
      version = "2.4.2"
    }
    google = {
      source  = "hashicorp/google"
      version = "5.32.0"
    }
  }

  required_version = "1.8.4"
}


provider "google" {
  project = "true-black-calculator-service"
  region  = "asia-southeast1"
}

# resource "null_resource" "lambda_layer" {
#   triggers = {
#     requirements = filesha1("${path.module}/requirements.txt")
#   }
#
#   provisioner "local-exec" {
#     command = <<EOT
#       set -e
#       pip install -r requirements.txt -t python/
#       zip -r python.zip python/
#     EOT
#   }
# }

data "archive_file" "function" {
  type = "zip"
  source {
    content  = file("${path.module}/main.py")
    filename = "main.py"
  }
  source {
    content  = file("${path.module}/calculator.py")
    filename = "calculator.py"
  }
  source {
    content  = file("${path.module}/requirements.txt")
    filename = "requirements.txt"
  }
  output_path = "${path.module}/function.zip"
}

# data "archive_file" "python" {
#   type        = "zip"
#   output_path = "${path.module}/python.zip"
#   source_dir  = "${path.module}/python"
#   depends_on  = [null_resource.lambda_layer]
# }


resource "google_storage_bucket" "bucket" {
  name     = "true-black-calculator-${var.environment}-bucket"
  location = "ASIA"
}

resource "google_storage_bucket_object" "object" {
  name         = "function.${data.archive_file.function.output_md5}.zip"
  bucket       = google_storage_bucket.bucket.name
  source       = data.archive_file.function.output_path
  content_type = "application/zip"
}

resource "google_cloudfunctions_function" "function" {
  name                         = "true-black-calculator-${var.environment}-function"
  description                  = "Telegram Bot for calculating true black percentage from images"
  runtime                      = "python312"
  entry_point                  = "main"
  available_memory_mb          = 128
  source_archive_bucket        = google_storage_bucket.bucket.name
  source_archive_object        = google_storage_bucket_object.object.name
  trigger_http                 = true
  https_trigger_security_level = "SECURE_ALWAYS"

  environment_variables = {
    TELEGRAM_BOT_TOKEN = var.telegram_bot_token
  }
}

resource "google_cloudfunctions_function_iam_binding" "true-black-calculator-function_iam" {
  project        = google_cloudfunctions_function.function.project
  region         = google_cloudfunctions_function.function.region
  cloud_function = google_cloudfunctions_function.function.name

  role    = "roles/cloudfunctions.invoker"
  members = ["allUsers"]
}


output "function_url" {
  value = google_cloudfunctions_function.function.https_trigger_url
}

# provider "aws" {
#   region = "ap-southeast-1"
# }
#
# data "aws_iam_policy_document" "assume_role" {
#   version = "2012-10-17"
#   statement {
#     effect = "Allow"
#
#     principals {
#       identifiers = ["lambda.amazonaws.com"]
#       type        = "Service"
#     }
#
#     actions = ["sts:AssumeRole"]
#   }
# }
#
# resource "aws_iam_role" "role" {
#   assume_role_policy = data.aws_iam_policy_document.assume_role.json
# }
#
#
# resource "aws_iam_role_policy_attachment" "policy_attachment" {
#   role       = aws_iam_role.role.name
#   policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
# }
#
#
# resource "aws_lambda_function" "true-black-calculator-function" {
#   function_name = "true-black-calculator-function"
#   handler       = "main.main"
#   role          = aws_iam_role.role.arn
#   filename      = data.archive_file.function.output_path
#
#   source_code_hash = data.archive_file.function.output_base64sha256
#
#   runtime = "python3.12"
#
#   environment {
#     variables = {
#       TELEGRAM_BOT_TOKEN = "7391592830:AAEf8PPtvx80zCM6BTIjKx4RIggBT6KeA5E"
#     }
#   }
#
#   layers = [aws_lambda_layer_version.true-black-calculator-layer.arn]
# }
#
# resource "aws_lambda_function_url" "function_url" {
#   function_name      = aws_lambda_function.true-black-calculator-function.function_name
#   authorization_type = "NONE"
# }
#
# resource "aws_lambda_layer_version" "true-black-calculator-layer" {
#   layer_name          = "python"
#   filename            = data.archive_file.python.output_path
#   compatible_runtimes = ["python3.12"]
#   compatible_architectures = ["arm64"]
# }
#
# output "function_url" {
#   value = aws_lambda_function_url.function_url.function_url
# }
