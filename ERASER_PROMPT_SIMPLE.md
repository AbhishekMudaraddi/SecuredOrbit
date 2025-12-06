# Simple DevSecOps Architecture Prompt for Eraser.io

## Prompt for Eraser.io

Create a simple DevSecOps architecture diagram for "Secured Orbit" password manager with this flow:

**LEFT TO RIGHT LAYOUT:**

### 1. DEVELOPMENT LAYER (Left Side)
- Developer with code
- Git client
- GitHub Repository (Private)
  - Branch: "main" (development)
  - Branch: "production" (deployment)

### 2. CI/CD PIPELINE (Center)

**CONTINUOUS INTEGRATION (CI)** - Triggered by push to "main":
```
GitHub Actions CI Pipeline:
├─ Checkout Code
├─ Setup Python 3.11
├─ Install Dependencies
├─ [Unit Tests - Pytest] (2-3 min)
│  └─ 15 tests: routes, helpers, health
│
└─ [Security Testing - Parallel] (after tests pass)
   ├─ [SonarCloud] (2-5 min)
   │  └─ Static Analysis (SAST)
   │     └─ Scans source code
   │
   └─ [OWASP ZAP] (5-10 min)
      └─ Dynamic Analysis (DAST)
         ├─ Start Flask app
         ├─ Run security scan
         └─ Generate reports
```

**DECISION POINT:**
- All tests pass? → Continue
- Tests fail? → Stop (red X)

**CONTINUOUS DEPLOYMENT (CD)** - Triggered by push to "production":
```
GitHub Actions CD Pipeline:
├─ [Validation]
│  ├─ Syntax check
│  └─ Dependency check
│
└─ [Deploy to AWS]
   └─ Elastic Beanstalk
```

### 3. PRODUCTION LAYER (Right Side)
- **AWS Cloud** (simple cloud icon)
  - Running Application
  - DynamoDB Database
  - HTTPS: securedorbit.com

### 4. USERS (Far Right)
- Web Browser
- Access via HTTPS

---

**SECURITY TOOLS (External Services):**
- SonarCloud (cloud icon) - connected to CI pipeline
- OWASP ZAP (shield icon) - runs in Docker during CI

**DATA FLOW ARROWS:**
1. Developer → GitHub (code commit)
2. GitHub → CI Pipeline (trigger)
3. CI Pipeline → Security Tools (scan)
4. CI Pipeline → CD Pipeline (if pass)
5. CD Pipeline → AWS (deploy)
6. AWS → Users (HTTPS)

**COLOR SCHEME:**
- Development: Light Blue
- CI Stages: Blue
- CD Stages: Green  
- AWS/Production: Orange
- Security Tools: Red
- Users: Purple

**KEEP IT SIMPLE:**
- Use boxes for stages
- Arrows for flow direction
- Icons for tools/services
- Decision diamond for pass/fail
- No detailed AWS infrastructure breakdown

---

## Alternative Even Simpler Version

Create a simple 3-stage DevSecOps diagram:

**STAGE 1 - DEVELOP (Left):**
- Developer
- GitHub Repository

**STAGE 2 - TEST & SECURE (Center - Large Box):**
"CI/CD Pipeline - GitHub Actions"
- [Unit Tests]
- [Security Scan - SonarCloud]
- [Security Test - ZAP]

**STAGE 3 - DEPLOY (Right):**
- AWS Cloud
- Live Application

Arrows: Develop → Test & Secure → Deploy

Colors: Blue → Yellow → Green

