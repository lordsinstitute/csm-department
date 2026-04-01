# 🛡️ ThreatForge AI

<div align="center">

![CognitoForge Banner](https://img.shields.io/badge/CognitoForge-AI%20Security-blueviolet?style=for-the-badge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)

**AI-Powered Security Analysis & Attack Simulation Platform**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Integrations](#-integrations)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

---

## 🌟 Overview

**CognitoForge AI** is a cutting-edge security analysis platform that leverages artificial intelligence to simulate adversarial attacks on code repositories. Built with Google's Gemini AI, it provides comprehensive security insights through automated vulnerability detection, attack vector analysis, and intelligent threat modeling.

### Why CognitoForge?

- 🤖 **AI-Driven Analysis**: Powered by Google Gemini 2.0 Flash for intelligent security assessments
- 🎯 **Attack Simulation**: Realistic attack scenario generation based on MITRE ATT&CK framework
- 📊 **Data Warehouse Integration**: Snowflake integration for analytics and historical tracking
- ☁️ **Cloud Compute**: DigitalOcean Gradient support for scalable AI workloads
- 🔐 **Enterprise Auth**: Secure authentication via Auth0
- 📈 **Real-Time Dashboard**: Live analytics and visualization of security metrics

---
---

## 👨‍💻 Team

| Name                          | Roll Number   |
|-------------------------------|---------------|
| Mohammed Murtuzauddin Maaz    | 160922748011  |
| Mohammed Abubaker             | 160922748044  |
| Anas Athar Mohiuddin          | 160922748024  |


**Project Guide:**  
Mr.Srikanth Reddy Madi, Assistant Professor  

**Co-Guide / HoD:**  
Dr. Abdul Rasool MD, Associate Professor & Head of Department, CSE (AIML)  

**Institution:**  
Lords Institute of Engineering and Technology, Hyderabad  

---

## ✨ Features

### Core Capabilities

#### 🔍 **Intelligent Repository Analysis**
- Automated scanning of GitHub repositories
- Smart file prioritization based on risk indicators
- Language-agnostic vulnerability detection
- CI/CD pipeline analysis

#### 🎯 **AI-Powered Attack Planning**
- Contextual attack scenario generation using Gemini AI
- MITRE ATT&CK technique mapping
- Severity-based vulnerability classification
- Deterministic fallback for offline operation

#### 📊 **Advanced Analytics Dashboard**
- Real-time security metrics and KPIs
- Historical trend analysis via Snowflake
- Vulnerability distribution by severity
- AI vs. rule-based scan tracking
- Repository-level risk scoring

#### ☁️ **Cloud Infrastructure**
- **Snowflake Integration**: Data warehousing for simulation runs, affected files, and AI insights
- **Gradient Compute**: Task execution environment with metadata tracking
- **Scalable Architecture**: Horizontal scaling for high-volume analysis

#### 🔐 **Security & Compliance**
- Auth0 authentication and authorization
- Secure credential management
- Input sanitization and validation
- Audit logging for all operations

#### 📝 **Comprehensive Reporting**
- Detailed vulnerability reports with remediation guidance
- PDF export capabilities
- Gemini-generated security intelligence summaries
- Attack vector visualization

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Frontend Layer (Next.js 14)                      │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────────────────┐ │
│  │ Dashboard  │  │  Demo/Report│  │  Auth (Auth0)                │ │
│  │ Component  │  │   Pages     │  │                              │ │
│  └─────┬──────┘  └──────┬──────┘  └──────────────────────────────┘ │
│        │                │                                           │
│        └────────────────┴────────────┐                             │
│                                      │                             │
│                   ┌──────────────────▼──────────────────┐          │
│                   │   API Service (TypeScript)          │          │
│                   │   - Type-safe requests              │          │
│                   │   - Error handling                  │          │
│                   │   - Auth token management           │          │
│                   └──────────────────┬──────────────────┘          │
└──────────────────────────────────────┼──────────────────────────────┘
                                       │
                          HTTP/REST (Port 8000)
                                       │
┌──────────────────────────────────────▼──────────────────────────────┐
│                    Backend Layer (FastAPI)                          │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              Operations Router                                 │ │
│  │  - POST /upload_repo                                          │ │
│  │  - POST /simulate_attack                                      │ │
│  │  - GET  /reports/{repo_id}/latest                            │ │
│  │  - GET  /analytics/summary                                    │ │
│  │  - GET  /api/gradient/status                                  │ │
│  └────────────────────┬───────────────────────────────────────────┘ │
│                       │                                            │
│       ┌───────────────┴───────────────┐                           │
│       │                               │                           │
│  ┌────▼─────────┐            ┌────────▼──────────┐               │
│  │   Gemini AI  │            │  Gradient Service │               │
│  │   Service    │            │  (Task Execution) │               │
│  │              │            └───────────────────┘               │
│  │ - Attack     │                                                │
│  │   Planning   │            ┌───────────────────┐               │
│  │ - Insights   │            │   Snowflake       │               │
│  │ - Analysis   │            │   Integration     │               │
│  └──────────────┘            │                   │               │
│                              │ - store_runs()    │               │
│                              │ - fetch_analytics()│               │
│                              └─────────┬─────────┘               │
└────────────────────────────────────────┼──────────────────────────┘
                                         │
                          ┌──────────────▼───────────────┐
                          │    Snowflake Warehouse       │
                          │  - simulation_runs           │
                          │  - affected_files            │
                          │  - ai_insights               │
                          └──────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Authentication**: Auth0 React SDK

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **AI/ML**: Google Generative AI (Gemini)
- **Data Validation**: Pydantic
- **Async Runtime**: Uvicorn
- **API Documentation**: OpenAPI/Swagger

### Data & Infrastructure
- **Data Warehouse**: Snowflake
- **Cloud Compute**: DigitalOcean Gradient (simulated)
- **Repository Fetcher**: GitHub API
- **Storage**: Local JSON (with Snowflake sync)

### DevOps & Tools
- **Version Control**: Git
- **Package Manager**: npm (frontend), pip (backend)
- **Environment**: dotenv for configuration
- **Testing**: FastAPI TestClient, pytest

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Git**
- **Google Gemini API Key** ([Get one here](https://ai.google.dev/))
- **Auth0 Account** ([Sign up here](https://auth0.com/))
- **(Optional)** Snowflake Account for analytics

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/n4bi10p/CognitoForge-Ai.git
cd CognitoForge-Ai
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your credentials
# Required: COGNITOFORGE_GEMINI_API_KEY
# Optional: Snowflake credentials
```

#### 3. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local

# Edit .env.local with your Auth0 credentials
```

#### 4. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access the Application:**
- Frontend: http://localhost:3000
- Backend API: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs

---

## ⚙️ Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```bash
# Required: Gemini AI
COGNITOFORGE_GEMINI_API_KEY=your_gemini_api_key_here
COGNITOFORGE_USE_GEMINI=true
COGNITOFORGE_GEMINI_MODEL=gemini-2.0-flash-exp

# Optional: GitHub API (for higher rate limits)
COGNITOFORGE_GITHUB_TOKEN=ghp_your_github_token

# Optional: Snowflake Data Warehouse
COGNITOFORGE_SNOWFLAKE_ACCOUNT=your_account.region
COGNITOFORGE_SNOWFLAKE_USER=your_username
COGNITOFORGE_SNOWFLAKE_PASSWORD=your_password
COGNITOFORGE_SNOWFLAKE_WAREHOUSE=COMPUTE_WH
COGNITOFORGE_SNOWFLAKE_DATABASE=COGNITOFORGE_DB
COGNITOFORGE_SNOWFLAKE_SCHEMA=PUBLIC

# Optional: Gradient Compute
USE_GRADIENT_MOCK=true  # Set to false for production
```

### Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```bash
# Backend API
NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000

# Auth0 Configuration
AUTH0_SECRET=use_openssl_rand_hex_32_to_generate
AUTH0_BASE_URL=http://localhost:3000
AUTH0_ISSUER_BASE_URL=https://your-domain.auth0.com
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
AUTH0_SCOPE=openid profile email
```

---

## 📖 Usage

### Running a Security Analysis

1. **Navigate to Demo Page**: http://localhost:3000/demo

2. **Enter Repository URL**:
   ```
   https://github.com/username/repository
   ```

3. **Start Analysis**: Click "Start Analysis"

4. **View Results**:
   - Attack vectors discovered
   - Severity classifications
   - AI-generated insights (Gemini metadata)
   - Gradient execution metrics
   - Affected files list

### Viewing Analytics Dashboard

1. **Navigate to Dashboard**: http://localhost:3000/dashboard

2. **Metrics Available**:
   - Total repositories analyzed
   - Total security scans
   - Vulnerability breakdown by severity
   - AI-powered vs. deterministic scan ratio
   - Recent simulations with timestamps
   - Snowflake analytics (if configured)
   - Gradient cluster status

### Downloading Reports

1. From the demo page after analysis
2. Click "Download Report"
3. PDF generated with full vulnerability details

---

## 📚 API Documentation

### Core Endpoints

#### Upload Repository
```http
POST /upload_repo
Content-Type: application/json

{
  "repo_id": "repository-name",
  "repo_url": "https://github.com/user/repo"
}
```

#### Simulate Attack
```http
POST /simulate_attack
Content-Type: application/json

{
  "repo_id": "repository-name",
  "force": false
}
```

**Response includes**:
- Attack plan with steps
- Gemini metadata (if AI-generated)
- Gradient task execution details
- Sandbox simulation logs

#### Get Latest Report
```http
GET /reports/{repo_id}/latest
```

#### Analytics Summary (Snowflake)
```http
GET /analytics/summary
```

Returns severity distribution:
```json
{
  "critical": 5,
  "high": 12,
  "medium": 8,
  "low": 3
}
```

#### Gradient Status
```http
GET /api/gradient/status
```

### Interactive API Docs

Visit http://127.0.0.1:8000/docs for full Swagger UI documentation.

---

## 🔌 Integrations

### Google Gemini AI

CognitoForge uses Gemini 2.0 Flash for:
- Contextual attack scenario generation
- Repository structure analysis
- Security insight generation
- Vulnerability prioritization

**Setup**: Add `COGNITOFORGE_GEMINI_API_KEY` to backend `.env`

### Snowflake Data Warehouse

Stores and analyzes:
- Simulation run metadata
- Affected files per vulnerability
- AI-generated insights
- Historical trends

**Tables Created**:
- `simulation_runs`
- `affected_files`
- `ai_insights`

### DigitalOcean Gradient

AI task execution environment:
- Configurable compute instances
- Task metadata tracking
- Mock mode for development

### Auth0 Authentication

Secure user management:
- OAuth 2.0 / OpenID Connect
- Social login support
- JWT token validation

---

## 🔒 Security

### Best Practices Implemented

- ✅ Environment variables for secrets (never committed)
- ✅ Input validation and sanitization
- ✅ CORS configuration
- ✅ Auth0 JWT verification
- ✅ Rate limiting ready
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS protection (React auto-escaping)

### Responsible Disclosure

Found a security issue? Please create a private security advisory on GitHub or contact the maintainers directly.

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'feat: add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Code Style

- **Frontend**: ESLint + Prettier (TypeScript)
- **Backend**: Black + isort + flake8 (Python)
- **Commits**: Conventional Commits format

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 📄 License

This project is licensed under the **MIT License**.

### MIT License

```
MIT License

Copyright (c) 2025 CognitoForge AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### License Summary

✅ Commercial use  
✅ Modification  
✅ Distribution  
✅ Private use  
⚠️ No warranty  
⚠️ No liability  

---

## 📞 Support

### Documentation

- **Integration Guide**: [SNOWFLAKE_GRADIENT_INTEGRATION.md](SNOWFLAKE_GRADIENT_INTEGRATION.md)
- **Implementation Details**: [INTEGRATION_IMPLEMENTATION_SUMMARY.md](INTEGRATION_IMPLEMENTATION_SUMMARY.md)
- **Quick Start**: [QUICK_START.md](QUICK_START.md)
- **Setup Guide**: [docs/SETUP.md](docs/SETUP.md)
- **Auth0 Setup**: [docs/AUTH0_SETUP.md](docs/AUTH0_SETUP.md)

### Community

- **Issues**: [GitHub Issues](https://github.com/n4bi10p/CognitoForge-Ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/n4bi10p/CognitoForge-Ai/discussions)

### Roadmap

- [ ] Real-time WebSocket updates
- [ ] Advanced trend visualization
- [ ] Multi-language support
- [ ] CI/CD integration plugins
- [ ] Custom rule engine
- [ ] Collaborative workspaces
- [ ] Integration with popular DevOps tools

---

## 🙏 Acknowledgments

- **Google Gemini AI** - Intelligent security analysis
- **MITRE ATT&CK** - Attack technique framework
- **Auth0** - Authentication infrastructure
- **Snowflake** - Data warehousing platform
- **FastAPI** - High-performance Python web framework
- **Next.js** - React framework for production
- **shadcn/ui** - Beautiful UI components

---

## 📊 Project Status

![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square)
![Maintained](https://img.shields.io/badge/maintained-yes-brightgreen?style=flat-square)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)

**Current Version**: 1.0.0  
**Status**: Active Development  
**Last Updated**: October 2025

---

<div align="center">

### ⭐ Star us on GitHub — it helps!

Made with ❤️ by the CognitoForge Team

[Report Bug](https://github.com/n4bi10p/CognitoForge-Ai/issues) • [Request Feature](https://github.com/n4bi10p/CognitoForge-Ai/issues)

</div>
