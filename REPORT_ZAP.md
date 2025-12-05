# OWASP ZAP Integration Report
## Dynamic Application Security Testing (DAST)

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [What is OWASP ZAP?](#what-is-owasp-zap)
3. [Dynamic Analysis vs Static Analysis](#dynamic-analysis-vs-static-analysis)
4. [Integration Overview](#integration-overview)
5. [Complete Workflow Process](#complete-workflow-process)
6. [What ZAP Tests](#what-zap-tests)
7. [Types of Vulnerabilities Detected](#types-of-vulnerabilities-detected)
8. [Configuration Details](#configuration-details)
9. [Benefits and Impact](#benefits-and-impact)
10. [Workflow Diagram](#workflow-diagram)

---

## Executive Summary

**OWASP ZAP (Zed Attack Proxy)** is integrated into the Secured Orbit project to perform **Dynamic Application Security Testing (DAST)**. Unlike static analysis, ZAP tests the **running application** by sending real HTTP requests and analyzing responses to find runtime security vulnerabilities.

**Key Metrics:**
- **Type**: Dynamic Analysis (DAST)
- **Execution Time**: ~5-10 minutes per scan
- **Trigger**: Automatically after unit tests pass
- **Test Scope**: Running Flask application on `http://localhost:5000`
- **Vulnerabilities Found**: Missing security headers, XSS, injection flaws, authentication issues

---

## What is OWASP ZAP?

### Definition
**OWASP ZAP (Zed Attack Proxy)** is a free, open-source security testing tool designed to find security vulnerabilities in web applications during development and testing phases.

### Core Purpose
ZAP performs **automated penetration testing** by:
- Acting as a "man-in-the-middle" proxy between browser and server
- Intercepting and modifying HTTP/HTTPS requests
- Analyzing application responses for security issues
- Testing for OWASP Top 10 vulnerabilities in running applications
- Identifying security misconfigurations

### Technology Stack
- **Type**: Proxy-based security scanner
- **Protocols**: HTTP, HTTPS, WebSocket
- **Attack Methods**: Automated scanning, fuzzing, spider crawling
- **Standards**: OWASP Testing Guide, OWASP Top 10
- **Deployment**: Docker container or standalone application

### OWASP Foundation
- **Organization**: Open Web Application Security Project
- **Mission**: Make software security visible
- **Standards**: OWASP Top 10 (most critical web app vulnerabilities)
- **Tool**: ZAP is one of OWASP's flagship projects

---

## Dynamic Analysis vs Static Analysis

### Dynamic Application Security Testing (DAST)
**What it is:**
- Tests the **running application** by sending real requests
- Examines HTTP requests/responses, headers, cookies
- Requires application to be deployed/running
- Finds runtime vulnerabilities that static analysis can't detect

**Advantages:**
- ✅ Tests actual application behavior
- ✅ Finds runtime vulnerabilities (missing headers, XSS in responses)
- ✅ Tests authentication/authorization
- ✅ Identifies configuration issues
- ✅ Tests the complete stack (server, framework, dependencies)

**Limitations:**
- ❌ Requires application to be running
- ❌ Slower than static analysis (minutes to hours)
- ❌ Cannot analyze source code directly
- ❌ May not cover all code paths

### Comparison with Static Testing (SAST - SonarCloud)
| Aspect | DAST (ZAP) | SAST (SonarCloud) |
|--------|------------|-------------------|
| **When** | During execution | Before execution |
| **What** | Running application | Source code |
| **Finds** | Runtime vulnerabilities | Code-level issues |
| **Speed** | Slower (5-10 min) | Fast (2-5 min) |
| **Examples** | Missing security headers, XSS in responses | Hardcoded secrets, SQL injection patterns |

**In This Project:**
- **SonarCloud (SAST)**: Analyzes Python code for security issues
- **ZAP (DAST)**: Tests the running Flask application for runtime vulnerabilities

**Combined Coverage:**
- SAST finds code-level issues (before deployment)
- DAST finds runtime issues (in running application)
- Together they provide comprehensive security testing

---

## Integration Overview

### Integration Point
ZAP is integrated into the GitHub Actions CI/CD pipeline as a separate job that:
1. Starts the Flask application
2. Runs ZAP Baseline Scan against the running app
3. Generates security reports
4. Stops the application

### Files Involved
1. **`.github/workflows/test.yml`** - GitHub Actions workflow file
   - Defines the `zap-baseline` job
   - Configures Flask startup, ZAP scan, cleanup

2. **GitHub Action**: `zaproxy/action-baseline@v0.11.0`
   - Pre-configured ZAP Baseline Scan action
   - Handles Docker container, scanning, reporting

### Execution Environment
- **Platform**: GitHub Actions (Ubuntu latest)
- **Trigger**: Automatically after `test` job completes
- **Application**: Flask app runs on `http://localhost:5000`
- **Scanner**: ZAP runs in Docker container

### ZAP Scan Types
This project uses **Baseline Scan**:
- **Type**: Lightweight, fast scan
- **Duration**: 5-10 minutes
- **Coverage**: Checks for common vulnerabilities
- **Use Case**: CI/CD integration, automated testing

Other ZAP scan types (not used here):
- **Full Scan**: Comprehensive, takes hours
- **API Scan**: Tests REST APIs specifically
- **Ajax Spider**: Dynamic JavaScript application scanning

---

## Complete Workflow Process

### Step-by-Step Flow

#### **Phase 1: Trigger and Dependencies**
```
Test job completes successfully
    ↓
ZAP Baseline job starts
    ↓
Job waits for test job (needs: test)
```

#### **Phase 2: Environment Setup**
```
1. Checkout Code
   - Clones repository to GitHub Actions runner
   - Gets latest application code

2. Set up Python Environment
   - Installs Python 3.11
   - Sets up pip cache for faster dependency installation

3. Install Application Dependencies
   - Installs Flask and all requirements from requirements.txt
   - Sets up test environment variables
```

#### **Phase 3: Application Startup**
```
1. Configure Environment Variables
   - SECRET_KEY: Test secret key
   - AWS_REGION: us-east-1
   - AWS_ACCESS_KEY_ID: Test credentials
   - DYNAMODB_USERS_TABLE: Test table name
   - PORT: 5000

2. Start Flask Application
   - Runs: python app.py
   - Starts in background (nohup)
   - Logs output to flask.log
   - Stores process ID in flask.pid

3. Wait for Application to Start
   - Initial wait: 10 seconds
   - Health check retry loop: 15 attempts, 2 seconds apart
   - Checks: http://localhost:5000/health endpoint
   - Verifies: Process is still running

4. Verify Application is Running
   - Curl health endpoint
   - Check process status
   - Read application logs if failed
```

**Why This Step is Critical:**
- ZAP needs a running application to test
- Application must be fully initialized
- Health endpoint confirms Flask is ready
- Process monitoring ensures stability

#### **Phase 4: ZAP Baseline Scan Execution**
```
1. ZAP Docker Container Startup
   - Pulls ZAP Docker image (ghcr.io/zaproxy/zaproxy:stable)
   - Starts ZAP proxy server
   - Configures scan parameters

2. Application Discovery (Spider)
   - ZAP crawls the application starting from http://localhost:5000
   - Discovers all accessible endpoints:
     * GET / (homepage)
     * GET /register (registration page)
     * POST /register (registration endpoint)
     * GET /login (login page)
     * POST /login (login endpoint)
     * GET /dashboard (dashboard - requires auth)
     * GET /health (health check)
     * API endpoints: /api/passwords

3. Active Scanning
   - ZAP sends malicious/modified requests to each endpoint
   - Tests for vulnerabilities:
     * SQL Injection attempts
     * XSS (Cross-Site Scripting) payloads
     * Command Injection attempts
     * Path Traversal attempts
     * Authentication bypass attempts
     * Session fixation tests

4. Response Analysis
   - Analyzes HTTP responses for:
     * Security headers (X-Frame-Options, CSP, etc.)
     * Error messages (information disclosure)
     * Cookie security flags
     * HTTPS/TLS configuration
     * CORS configuration
     * Response codes and error handling

5. Vulnerability Detection
   - Compares findings against vulnerability database
   - Categorizes issues:
     * High: Critical security issues
     * Medium: Important security issues
     * Low: Minor security issues
     * Informational: Best practice recommendations

6. Report Generation
   - Creates multiple report formats:
     * HTML report (human-readable)
     * JSON report (machine-readable)
     * Markdown report (documentation)
```

#### **Phase 5: Results Processing**
```
1. Scan Completion
   - ZAP completes analysis
   - All endpoints tested
   - Vulnerabilities cataloged

2. Report Generation
   - report_html.html: Visual report with details
   - report_json.json: Structured data for automation
   - report_md.md: Markdown format for documentation

3. Upload Artifacts
   - Reports saved as GitHub Actions artifacts
   - Available for download (30 days retention)
   - Can be shared with security team
```

#### **Phase 6: Cleanup**
```
1. Stop Flask Application
   - Kills Flask process (using PID)
   - Ensures clean shutdown
   - Runs even if scan fails (if: always)

2. Clean Up Resources
   - Removes temporary files
   - Stops background processes
   - Frees up system resources
```

### Execution Timeline
```
0:00 - Test job completes
0:01 - ZAP job starts
0:02 - Code checkout complete
0:03 - Python environment setup
0:05 - Dependencies installed
0:06 - Flask app starting...
0:16 - Flask app running (health check passed)
0:17 - ZAP container starting...
0:18 - ZAP spider crawling application
0:22 - ZAP active scanning endpoints
0:27 - ZAP analyzing responses
0:28 - Reports generated
0:29 - Artifacts uploaded
0:30 - Flask app stopped
0:31 - Job complete ✅
```

---

## What ZAP Tests

### 1. Application Endpoints

#### **Discovered Endpoints**
ZAP automatically discovers and tests:
- `GET /` - Homepage
- `GET /register` - Registration page
- `POST /register` - Registration endpoint
- `GET /login` - Login page
- `POST /login` - Login endpoint
- `GET /dashboard` - Dashboard (protected)
- `GET /health` - Health check
- `GET /api/passwords` - API endpoint
- `POST /api/passwords` - API endpoint
- All static resources (CSS, JS, images)

#### **Testing Methods**
- **Spider**: Automatically crawls all links
- **Active Scan**: Sends malicious payloads
- **Fuzzing**: Tests with various inputs
- **Authentication**: Tests login/logout flows

### 2. Security Headers

ZAP checks for presence and correctness of:

#### **X-Frame-Options**
- **Purpose**: Prevents clickjacking attacks
- **Expected**: `DENY` or `SAMEORIGIN`
- **Test**: ZAP checks if header is present

#### **X-Content-Type-Options**
- **Purpose**: Prevents MIME type sniffing
- **Expected**: `nosniff`
- **Test**: ZAP verifies header value

#### **Content-Security-Policy (CSP)**
- **Purpose**: Prevents XSS attacks
- **Expected**: Well-configured policy
- **Test**: ZAP analyzes CSP directives

#### **Strict-Transport-Security (HSTS)**
- **Purpose**: Forces HTTPS connections
- **Expected**: `max-age` directive
- **Test**: ZAP checks for HSTS header

#### **X-XSS-Protection**
- **Purpose**: Enables browser XSS filter
- **Expected**: `1; mode=block`
- **Test**: ZAP verifies header

#### **Referrer-Policy**
- **Purpose**: Controls referrer information
- **Expected**: Appropriate policy
- **Test**: ZAP checks policy value

#### **Permissions-Policy**
- **Purpose**: Controls browser features
- **Expected**: Restrictive policy
- **Test**: ZAP analyzes permissions

### 3. Authentication & Session Management

#### **Login Process**
- Tests login endpoint for vulnerabilities
- Checks password handling
- Verifies session creation

#### **Session Security**
- Cookie flags: `HttpOnly`, `Secure`, `SameSite`
- Session ID strength
- Session timeout
- Session fixation

#### **Access Control**
- Tests protected endpoints
- Verifies authentication requirements
- Checks authorization bypass

### 4. Input Validation & Injection

#### **SQL Injection**
- Tests form fields with SQL payloads
- Example: `' OR '1'='1`
- Checks if application is vulnerable

#### **Cross-Site Scripting (XSS)**
- Tests for reflected XSS
- Tests for stored XSS
- Example: `<script>alert('XSS')</script>`

#### **Command Injection**
- Tests for OS command execution
- Example: `; ls -la`

#### **Path Traversal**
- Tests for directory traversal
- Example: `../../../etc/passwd`

#### **XML External Entity (XXE)**
- Tests XML parsing vulnerabilities
- Checks for external entity inclusion

### 5. Error Handling & Information Disclosure

#### **Error Messages**
- Checks for sensitive information in errors
- Tests stack trace exposure
- Verifies error page security

#### **HTTP Status Codes**
- Tests for information leakage
- Checks error handling

#### **Response Headers**
- Checks for server version disclosure
- Verifies no sensitive headers

### 6. HTTPS/TLS Configuration

#### **Certificate Validation**
- Checks SSL/TLS configuration
- Verifies certificate validity

#### **Cipher Suites**
- Tests for weak ciphers
- Checks TLS version

### 7. CORS (Cross-Origin Resource Sharing)

#### **CORS Configuration**
- Tests CORS headers
- Checks for overly permissive CORS
- Verifies origin validation

---

## Types of Vulnerabilities Detected

### 1. High Severity Issues

#### **Missing Security Headers**
```
Issue: Missing X-Frame-Options Header
Severity: High
Impact: Application vulnerable to clickjacking
Location: All endpoints
Recommendation: Add X-Frame-Options: DENY header
```

#### **Cross-Site Scripting (XSS)**
```
Issue: Reflected XSS in search parameter
Severity: High
Impact: Attackers can execute JavaScript in user's browser
Location: GET /search?q=<script>alert('XSS')</script>
Recommendation: Sanitize and escape user input
```

#### **SQL Injection**
```
Issue: SQL Injection in login form
Severity: High
Impact: Unauthorized database access
Location: POST /login (username parameter)
Recommendation: Use parameterized queries
```

### 2. Medium Severity Issues

#### **Missing Content-Security-Policy**
```
Issue: No CSP header present
Severity: Medium
Impact: Increased XSS risk
Location: All endpoints
Recommendation: Implement Content-Security-Policy
```

#### **Session Cookie Not Secure**
```
Issue: Session cookie missing Secure flag
Severity: Medium
Impact: Cookie sent over HTTP (if HTTPS available)
Location: Session cookies
Recommendation: Set Secure flag on cookies
```

#### **Information Disclosure**
```
Issue: Error message reveals database structure
Severity: Medium
Impact: Information useful for attackers
Location: Error pages
Recommendation: Use generic error messages
```

### 3. Low Severity Issues

#### **Missing X-Content-Type-Options**
```
Issue: No X-Content-Type-Options header
Severity: Low
Impact: MIME type sniffing possible
Location: All endpoints
Recommendation: Add X-Content-Type-Options: nosniff
```

#### **Server Header Disclosure**
```
Issue: Server header reveals technology stack
Severity: Low
Impact: Information disclosure
Location: HTTP responses
Recommendation: Remove or mask Server header
```

### 4. Informational Issues

#### **Missing Referrer-Policy**
```
Issue: No Referrer-Policy header
Severity: Informational
Impact: Referrer information leaked
Location: All endpoints
Recommendation: Add Referrer-Policy header
```

#### **Missing Permissions-Policy**
```
Issue: No Permissions-Policy header
Severity: Informational
Impact: Browser features not restricted
Location: All endpoints
Recommendation: Add Permissions-Policy header
```

---

## Configuration Details

### File: `.github/workflows/test.yml`

```yaml
zap-baseline:
  name: OWASP ZAP Baseline Scan
  runs-on: ubuntu-latest
  needs: test                    # Wait for test job
  permissions:
    contents: read               # Read repository
    security-events: write       # Write security alerts
  
  env:
    SECRET_KEY: 'test-secret-key-for-zap-scan'
    AWS_REGION: 'us-east-1'
    AWS_ACCESS_KEY_ID: 'test-access-key'
    AWS_SECRET_ACCESS_KEY: 'test-secret-key'
    DYNAMODB_USERS_TABLE: 'PasswordManagerV2-Users-Test'
    DYNAMODB_PASSWORDS_TABLE: 'PasswordManagerV2-Passwords-Test'
    FLASK_DEBUG: 'false'
    PORT: '5000'
  
  steps:
  - name: Checkout code
    uses: actions/checkout@v4
  
  - name: Set up Python
    uses: actions/setup-python@v4
    with:
      python-version: '3.11'
      cache: 'pip'
  
  - name: Install dependencies
    run: |
      python -m pip install --upgrade pip
      pip install -r requirements.txt
  
  - name: Start Flask application
    run: |
      nohup python app.py > flask.log 2>&1 &
      echo $! > flask.pid
      # Wait and verify app is running
      # Health check retry loop
  
  - name: ZAP Baseline Scan
    uses: zaproxy/action-baseline@v0.11.0
    continue-on-error: true      # Don't fail on warnings
    with:
      target: 'http://localhost:5000'  # Application URL
      cmd_options: '-a'          # Continue even if warnings
  
  - name: Stop Flask application
    if: always()                 # Always cleanup
    run: |
      kill $(cat flask.pid) 2>/dev/null || true
  
  - name: Upload ZAP reports
    uses: actions/upload-artifact@v4
    if: always()
    with:
      name: zap-security-reports
      path: |
        report_html.html
        report_json.json
        report_md.md
      retention-days: 30
```

### Key Configuration Decisions

1. **Baseline Scan**
   - Why: Fast, suitable for CI/CD
   - Impact: 5-10 minute scan time

2. **Continue on Error**
   - Why: Don't block pipeline on warnings
   - Impact: Pipeline continues, reports still generated

3. **Application Startup**
   - Why: ZAP needs running application
   - Impact: 10-15 seconds for Flask to start

4. **Health Check Retry**
   - Why: Ensure app is fully ready
   - Impact: Reliable scan execution

5. **Always Cleanup**
   - Why: Ensure Flask stops even if scan fails
   - Impact: No orphaned processes

---

## Benefits and Impact

### 1. Runtime Security Testing
- **Real Application Testing**: Tests actual running application
- **Runtime Vulnerabilities**: Finds issues static analysis can't
- **Complete Stack**: Tests server, framework, dependencies

### 2. OWASP Top 10 Coverage
- **Industry Standard**: Tests against OWASP Top 10
- **Comprehensive**: Covers major vulnerability categories
- **Up-to-Date**: Based on latest OWASP standards

### 3. Automated Security Testing
- **CI/CD Integration**: Runs automatically on every push
- **No Manual Effort**: Fully automated scanning
- **Consistent**: Same tests every time

### 4. Security Headers Verification
- **Header Compliance**: Checks all security headers
- **Best Practices**: Enforces security best practices
- **Configuration Issues**: Finds misconfigurations

### 5. Vulnerability Prevention
- **Early Detection**: Finds issues before production
- **Cost Savings**: Fixing in development is cheaper
- **Risk Reduction**: Lower security risk

### Real-World Impact
- **Before ZAP**: Manual security testing, missed vulnerabilities
- **After ZAP**: Automated testing, consistent coverage
- **Result**: Better security, fewer production incidents

---

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    TEST JOB COMPLETES                        │
│                                                              │
│  ✓ Unit tests passed                                        │
│  ✓ Linting passed                                           │
│  ✓ Code formatting checked                                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              ZAP BASELINE JOB STARTS                         │
│                                                              │
│  Trigger: After test job completes                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  ENVIRONMENT SETUP                           │
│                                                              │
│  Step 1: Checkout Code                                      │
│    └─ Clone repository                                      │
│                                                              │
│  Step 2: Set up Python                                      │
│    └─ Install Python 3.11                                   │
│                                                              │
│  Step 3: Install Dependencies                               │
│    └─ pip install -r requirements.txt                       │
│    └─ Install Flask, boto3, cryptography, etc.              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              FLASK APPLICATION STARTUP                       │
│                                                              │
│  1. Configure Environment Variables                         │
│     ├─ SECRET_KEY                                           │
│     ├─ AWS credentials (test)                               │
│     ├─ DynamoDB table names                                 │
│     └─ PORT: 5000                                           │
│                                                              │
│  2. Start Flask Application                                 │
│     └─ python app.py (background)                           │
│     └─ Logs: flask.log                                      │
│     └─ PID: flask.pid                                       │
│                                                              │
│  3. Wait for Application                                    │
│     └─ Initial wait: 10 seconds                             │
│     └─ Health check: http://localhost:5000/health           │
│     └─ Retry loop: 15 attempts, 2 seconds apart            │
│                                                              │
│  4. Verify Application Running                              │
│     ✓ Process check                                         │
│     ✓ Health endpoint responds                              │
│     ✓ Application initialized                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              ZAP CONTAINER STARTUP                           │
│                                                              │
│  1. Pull ZAP Docker Image                                   │
│     └─ ghcr.io/zaproxy/zaproxy:stable                      │
│                                                              │
│  2. Start ZAP Proxy Server                                  │
│     └─ HTTP proxy on port 8080                              │
│     └─ Web UI on port 8090                                  │
│                                                              │
│  3. Configure Scan Parameters                               │
│     ├─ Target: http://localhost:5000                        │
│     ├─ Scan type: Baseline                                  │
│     └─ Options: Continue on warnings (-a)                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              APPLICATION DISCOVERY (SPIDER)                  │
│                                                              │
│  ZAP Crawls Application:                                    │
│                                                              │
│  Starting Point: http://localhost:5000                      │
│    ├─ Follows all links                                     │
│    ├─ Discovers endpoints:                                  │
│    │   • GET /                                              │
│    │   • GET /register                                      │
│    │   • GET /login                                         │
│    │   • GET /dashboard                                     │
│    │   • GET /health                                        │
│    │   • GET /api/passwords                                 │
│    │   • POST /register                                     │
│    │   • POST /login                                        │
│    └─ Maps application structure                            │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                ACTIVE SCANNING PHASE                         │
│                                                              │
│  For each discovered endpoint:                              │
│                                                              │
│  1. Security Headers Test                                   │
│     ├─ Check X-Frame-Options                               │
│     ├─ Check X-Content-Type-Options                        │
│     ├─ Check Content-Security-Policy                       │
│     ├─ Check Strict-Transport-Security                     │
│     ├─ Check X-XSS-Protection                              │
│     ├─ Check Referrer-Policy                               │
│     └─ Check Permissions-Policy                            │
│                                                              │
│  2. Input Validation Tests                                  │
│     ├─ SQL Injection attempts                              │
│     │   └─ Payload: ' OR '1'='1                            │
│     ├─ XSS (Cross-Site Scripting)                          │
│     │   └─ Payload: <script>alert('XSS')</script>          │
│     ├─ Command Injection                                    │
│     ├─ Path Traversal                                       │
│     └─ XXE (XML External Entity)                           │
│                                                              │
│  3. Authentication Tests                                    │
│     ├─ Login endpoint security                             │
│     ├─ Session management                                  │
│     ├─ Cookie security flags                               │
│     ├─ Access control                                      │
│     └─ Password handling                                   │
│                                                              │
│  4. Error Handling Tests                                    │
│     ├─ Information disclosure                              │
│     ├─ Error messages                                      │
│     └─ Stack trace exposure                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                RESPONSE ANALYSIS                             │
│                                                              │
│  Analyze HTTP Responses:                                    │
│                                                              │
│  For each response:                                         │
│    ├─ Status codes                                         │
│    ├─ Response headers                                      │
│    ├─ Response body content                                 │
│    ├─ Cookie attributes                                     │
│    ├─ Error messages                                        │
│    └─ Information disclosure                                │
│                                                              │
│  Compare against:                                           │
│    ├─ OWASP Top 10 patterns                                │
│    ├─ CWE vulnerability database                            │
│    └─ Security best practices                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│            VULNERABILITY DETECTION                           │
│                                                              │
│  Issues Categorized:                                        │
│                                                              │
│  🔴 High Severity:                                          │
│     • Missing critical security headers                     │
│     • SQL Injection vulnerabilities                         │
│     • XSS vulnerabilities                                   │
│                                                              │
│  🟡 Medium Severity:                                        │
│     • Missing CSP header                                    │
│     • Session cookie issues                                 │
│     • Information disclosure                                │
│                                                              │
│  🔵 Low Severity:                                           │
│     • Missing optional headers                              │
│     • Server header disclosure                              │
│                                                              │
│  ℹ️  Informational:                                         │
│     • Best practice recommendations                         │
│     • Configuration suggestions                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              REPORT GENERATION                               │
│                                                              │
│  1. HTML Report (report_html.html)                          │
│     └─ Human-readable format                               │
│     └─ Color-coded severity                                │
│     └─ Detailed descriptions                               │
│     └─ Remediation guidance                                │
│                                                              │
│  2. JSON Report (report_json.json)                          │
│     └─ Machine-readable format                             │
│     └─ Structured data                                     │
│     └─ For automation/integration                          │
│                                                              │
│  3. Markdown Report (report_md.md)                          │
│     └─ Documentation format                                │
│     └─ Easy to read                                        │
│     └─ Can be included in docs                             │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              ARTIFACT UPLOAD                                 │
│                                                              │
│  Upload Reports to GitHub Actions:                          │
│    ✓ report_html.html                                       │
│    ✓ report_json.json                                       │
│    ✓ report_md.md                                           │
│    ✓ flask.log (debugging)                                  │
│                                                              │
│  Retention: 30 days                                         │
│  Available for download from GitHub Actions UI              │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              CLEANUP PHASE                                   │
│                                                              │
│  1. Stop Flask Application                                  │
│     └─ Kill process using PID                              │
│     └─ Clean shutdown                                      │
│                                                              │
│  2. Clean Up Resources                                      │
│     └─ Remove temporary files                              │
│     └─ Stop background processes                           │
│                                                              │
│  Runs even if scan fails (if: always)                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    JOB COMPLETE                              │
│                                                              │
│  ✓ ZAP Baseline Scan: COMPLETE                              │
│  ✓ Reports: Generated and uploaded                          │
│  ✓ Flask Application: Stopped                               │
│  ✓ Pipeline: CONTINUES                                      │
│                                                              │
│  Developer can now:                                         │
│    • Download reports from GitHub Actions                   │
│    • Review security findings                               │
│    • Fix identified vulnerabilities                         │
│    • Track security improvements                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

**OWASP ZAP** provides automated dynamic security testing that:
- ✅ Tests the running application (not just source code)
- ✅ Finds runtime vulnerabilities and misconfigurations
- ✅ Checks security headers and authentication
- ✅ Tests against OWASP Top 10 vulnerabilities
- ✅ Generates detailed security reports

**In This Project:**
- Runs automatically after unit tests pass
- Tests Flask application on localhost:5000
- Uses Baseline Scan for fast CI/CD integration
- Generates HTML, JSON, and Markdown reports
- Doesn't block pipeline (continue-on-error enabled)

**Result**: Runtime security testing, early vulnerability detection, and comprehensive security coverage complementing static analysis.

---

*Report Generated: 2025*
*Project: Secured Orbit - Password Manager*
*Tool: OWASP ZAP Dynamic Application Security Testing*

