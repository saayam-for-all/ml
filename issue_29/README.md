# Containerizing Lambda Function
## This Doc provides a step by step process that can be followed to containerize the Lambda Fucntions

---

## 🚀 Why Containerize AWS Lambda?

### 🔧 Traditional Lambda (Zip-based)
- Easy and quick to deploy
- Limited to 250 MB unzipped package size (including dependencies)
- Can't install OS-level packages easily
- Not ideal for ML models with large libraries (e.g. PyTorch, TensorFlow)

### 🐳 Containerized Lambda (Docker-based)
- Package size up to **10 GB**
- Full control over the **runtime and OS libraries**
- Use any ML/DL/DS dependencies not supported by AWS Lambda runtime
- Easier **local testing and reproducibility**
- Better alignment with **CI/CD pipelines** and container-based workflows

---
