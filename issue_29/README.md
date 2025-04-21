# Containerizing Lambda Function
## This Doc provides a step by step process that can be followed to containerize the Lambda Fucntions

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
