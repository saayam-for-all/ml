# Containerizing Lambda Function
## This Doc provides a step by step process that can be followed to containerize the Lambda Functions

---

## 🚀 Why Containerize AWS Lambda?

### 🔧 Traditional Method (Zip-based)
- Limited to 250 MB unzipped package size (including dependencies)
- Can't install OS-level packages easily
- Not ideal for ML models with large libraries and complex dependencies such as PyTorch and TensorFlow
### 🐳 Containerized Lambda (Docker-based)
- Package size up to **10 GB**
- Full control and transparency over the **runtime and OS level libraries**
- Use/Define any dependencies not supported by AWS Lambda runtime
- Easier **local testing and reproducibility**

---

## High level Steps
- Create the logic code that contains the handler class for lambda function
- Define dependencies in the requirements.txt
- Create the Docker file, inside docker file make sure to define
  - Commands to install dependencies
  - Add the function code
  - set the handler function
  - any other required dependency jars/libraries installation
- Create an amazon ECR registry repo
  - To deploy a containerized Lambda, you must upload the image to Amazon ECR (Elastic Container Registry) first. That’s the only way AWS Lambda can pull your container image.
- Authenticate Docker ot ECR, tag the Docker image to ECR and push the image to ECR

## Once the lambda is containerized and pushed to ECR, it can be deployed from the ECR image.
```bash
Sampple Code

aws lambda create-function \
    --function-name provide_func_name \
    --package-type Image \
    --code ImageUri=<ecr_image_uri> \
    --role give_the_required_iam_role


