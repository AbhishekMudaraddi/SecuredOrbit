# Docker Files Explanation
## Understanding Dockerfile and docker-compose.yml Files

---

## 📁 Files in Your Project

### 1. **`Dockerfile`** (Root Directory)
**Location:** `/Final/Dockerfile`

**Purpose:** 
- **Builds the Docker image** from your source code
- Used by **Jenkins CI/CD pipeline** to create the image
- Image is pushed to **AWS ECR** (Elastic Container Registry)

**When it's used:**
- ✅ **Jenkins pipeline** → Builds image → Pushes to ECR
- ✅ **Local development** → `docker build -t password-manager:local .`
- ✅ **Makefile** → `make docker-build`

**Do you need it?**
- ✅ **YES!** Essential for CI/CD pipeline
- ✅ **YES!** Needed to build Docker images
- ❌ **NO** - Don't delete it!

---

### 2. **`docker-compose.yml`** (Root Directory)
**Location:** `/Final/docker-compose.yml`

**Purpose:**
- **Local development and testing**
- Builds image from source code (not from ECR)
- Runs on your local machine or development environment

**Key Features:**
```yaml
build:
  context: .
  dockerfile: Dockerfile
```
- **Builds** image from source code
- Port mapping: `5001:5001` (for local testing)
- Uses `.env` file for configuration

**When it's used:**
- ✅ **Local development** → `docker compose up`
- ✅ **Testing before deployment**
- ✅ **Makefile** → `make docker-run`

**Do you need it?**
- ✅ **YES!** Useful for local development
- ✅ **YES!** Helps test Docker setup before deployment
- ⚠️ **Optional** - Can delete if you only deploy via Jenkins

---

### 3. **`infra/docker-compose.ec2.yml`** (Infrastructure Directory)
**Location:** `/Final/infra/docker-compose.ec2.yml`

**Purpose:**
- **Template/reference** for EC2 deployment
- Shows what docker-compose.yml should look like on EC2
- **NOT used directly** - copied to EC2 manually

**Key Features:**
```yaml
image: ${ECR_IMAGE:-ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/password-manager:${TAG:-latest}}
```
- **Pulls** pre-built image from ECR (doesn't build)
- Port mapping: `80:5001` (for production HTTP)
- Uses `.env` file (created by `fetch-env.sh`)

**When it's used:**
- ✅ **Reference** - Shows EC2 setup
- ✅ **Manual copy** - You copy this to EC2 and customize it
- ❌ **NOT used automatically** - Just a template

**Do you need it?**
- ⚠️ **Optional** - Just a reference/template
- Can delete if you remember the EC2 setup

---

### 4. **`docker-compose.yml`** (On EC2)
**Location:** `/opt/password-manager/docker-compose.yml` (on EC2 server)

**Purpose:**
- **Production deployment** on EC2
- Pulls image from ECR (doesn't build)
- Actually runs your application

**Key Features:**
- Uses **pre-built image** from ECR
- Port mapping: `80:5001` (maps HTTP port 80 to container 5001)
- Environment variables from `.env` (fetched from SSM)

**When it's used:**
- ✅ **Production** - Runs your live application
- ✅ **Jenkins deployment** - Updates this file during deployment
- ✅ **Manual updates** - When you SSH and restart

**Do you need it?**
- ✅ **YES!** Essential for production
- ✅ **YES!** This is what actually runs your app

---

## 🔄 How They Work Together

### Development Flow:

```
1. Developer writes code
   ↓
2. docker-compose.yml (root) → Builds & tests locally
   ↓
3. Push to GitHub
   ↓
4. Jenkins pipeline triggers
   ↓
5. Dockerfile → Builds image → Pushes to ECR
   ↓
6. Jenkins deploys to EC2
   ↓
7. docker-compose.yml (EC2) → Pulls image from ECR → Runs
```

---

## 📊 Comparison Table

| File | Location | Purpose | Builds Image? | Port Mapping | Used By |
|------|----------|---------|----------------|--------------|---------|
| **Dockerfile** | Root | Build image | ✅ Yes | N/A | Jenkins, Local |
| **docker-compose.yml** | Root | Local dev | ✅ Yes | 5001:5001 | Developer |
| **docker-compose.ec2.yml** | infra/ | Template | ❌ No | 80:5001 | Reference |
| **docker-compose.yml** | EC2 | Production | ❌ No | 80:5001 | EC2 Server |

---

## 🎯 Key Differences

### Root `docker-compose.yml` vs EC2 `docker-compose.yml`:

**Root (Local Development):**
```yaml
build:
  context: .
  dockerfile: Dockerfile
ports:
  - "5001:5001"  # Local testing port
```

**EC2 (Production):**
```yaml
image: 503561414328.dkr.ecr.us-east-1.amazonaws.com/password-manager:latest
ports:
  - "80:5001"  # Production HTTP port
```

**Why Different?**
- **Root:** Builds from source, tests locally
- **EC2:** Uses pre-built image from ECR, serves on port 80

---

## ✅ What You Should Keep

### Essential Files (Don't Delete):

1. ✅ **`Dockerfile`** - Needed for Jenkins CI/CD
2. ✅ **`docker-compose.yml`** (root) - Useful for local testing
3. ⚠️ **`infra/docker-compose.ec2.yml`** - Optional (just a template)

### On EC2 (Don't Delete):

1. ✅ **`/opt/password-manager/docker-compose.yml`** - Essential for production

---

## 🗑️ What You Can Delete (Optional)

**If you only deploy via Jenkins and never test locally:**

- ⚠️ **`docker-compose.yml`** (root) - Can delete if you don't test locally
- ⚠️ **`infra/docker-compose.ec2.yml`** - Can delete (just a template)

**But keep:**
- ✅ **`Dockerfile`** - **NEVER DELETE** - Jenkins needs it!

---

## 💡 Best Practice

**Keep all files:**
- **Dockerfile** - Essential for CI/CD
- **docker-compose.yml** (root) - Useful for local testing
- **infra/docker-compose.ec2.yml** - Reference for EC2 setup

**Why?**
- Different environments need different configurations
- Local development vs Production deployment
- Better to have templates/references

---

## 🔍 Quick Reference

**To build locally:**
```bash
# Uses Dockerfile + docker-compose.yml (root)
docker compose up
# or
make docker-build
make docker-run
```

**On EC2:**
```bash
# Uses docker-compose.yml (EC2) - pulls from ECR
cd /opt/password-manager
docker compose up -d
```

**Jenkins Pipeline:**
```groovy
// Uses Dockerfile to build
docker build -t ${ECR_REPO}:${IMAGE_TAG} .
docker push ${ECR_REPO}:${IMAGE_TAG}
```

---

## 📝 Summary

**Dockerfile:**
- ✅ **KEEP** - Essential for building images
- Used by Jenkins to create Docker images
- Pushes images to ECR

**docker-compose.yml (root):**
- ✅ **KEEP** - Useful for local development
- Builds and tests locally
- Optional but helpful

**docker-compose.yml (EC2):**
- ✅ **KEEP** - Essential for production
- Runs your live application
- Pulls images from ECR

**infra/docker-compose.ec2.yml:**
- ⚠️ **Optional** - Just a template/reference
- Can delete if you remember EC2 setup

---

*Last Updated: 2024*

