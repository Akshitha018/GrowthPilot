# 🚀 GrowthPilot — Autonomous AI Growth Experimentation Agent

GrowthPilot is an **AI-powered growth experimentation platform** that helps businesses discover growth opportunities, generate experiments, analyze experiment performance, recommend winning strategies, and execute approved growth actions.

Instead of requiring a merchant to manually decide what to test, analyze results, and determine what to do next, GrowthPilot creates an end-to-end experimentation workflow:

**Business Goal → AI Experiment → Customer Assignment → Results → Statistical Analysis → Winner → AI Recommendation → Merchant Approval → AI Action → Actual Impact**

---

## 📌 Table of Contents

* [Overview](#-overview)
* [Problem Statement](#-problem-statement)
* [Solution](#-solution)
* [Key Features](#-key-features)
* [How GrowthPilot Works](#-how-growthpilot-works)
* [System Architecture](#-system-architecture)
* [Experiment Lifecycle](#-experiment-lifecycle)
* [AI Recommendation and Action Workflow](#-ai-recommendation-and-action-workflow)
* [Actual Impact Tracking](#-actual-impact-tracking)
* [Technology Stack](#-technology-stack)
* [Project Structure](#-project-structure)
* [Backend API](#-backend-api)
* [Database Design](#-database-design)
* [Frontend](#-frontend)
* [Installation and Setup](#-installation-and-setup)
* [Running the Project](#-running-the-project)
* [API Documentation](#-api-documentation)
* [Example Workflow](#-example-workflow)
* [Validation and Error Handling](#-validation-and-error-handling)
* [Future Scope](#-future-scope)
* [Project Highlights](#-project-highlights)
* [Author](#-author)

---

# 🌟 Overview

GrowthPilot is designed as an **Autonomous AI Growth Experimentation Agent**.

The platform allows a merchant or business user to provide a growth goal such as:

> "Increase customer conversion."

GrowthPilot then generates an experiment containing:

* Experiment name
* Hypothesis
* Objective
* Target customer segment
* Control strategy
* Variant A
* Variant B
* Budget
* Experiment status

Customers are assigned to experiment groups, results are collected, and the platform analyzes the performance of each group.

The winning strategy is then used to generate an **AI-powered growth recommendation**.

The merchant remains in control by approving or rejecting the recommendation before execution.

After approval, GrowthPilot executes the action and records the **actual impact** of the experiment.

---

# ❗ Problem Statement

Businesses frequently struggle to run effective growth experiments because the process involves several manual steps:

1. Identifying growth opportunities
2. Designing experiments
3. Defining hypotheses
4. Selecting customer segments
5. Assigning customers to test groups
6. Collecting experiment results
7. Analyzing conversion performance
8. Selecting the winning strategy
9. Deciding what action to take
10. Measuring the resulting business impact

This fragmented process can be:

* Time-consuming
* Difficult to scale
* Dependent on manual analysis
* Prone to inconsistent decision-making
* Slow to convert insights into actions

GrowthPilot addresses this problem by connecting these stages into a single intelligent experimentation workflow.

---

# 💡 Solution

GrowthPilot combines:

* Artificial Intelligence
* Automated experiment generation
* Customer segmentation
* Controlled experimentation
* Statistical analysis
* AI-powered recommendations
* Human approval
* Automated action execution
* Impact tracking

The result is a closed-loop growth experimentation system.

### Closed-Loop Growth Cycle

```text
Business Goal
      ↓
AI Experiment Generation
      ↓
Experiment Design
      ↓
Customer Assignment
      ↓
Experiment Execution
      ↓
Result Collection
      ↓
Statistical Analysis
      ↓
Winner Selection
      ↓
AI Recommendation
      ↓
Merchant Approval
      ↓
AI Action Execution
      ↓
Actual Impact Measurement
      ↓
Next Growth Experiment
```

---

# ✨ Key Features

## 1. AI Experiment Generation

The user provides:

* Business goal
* Target customer segment

GrowthPilot generates an experiment automatically.

The generated experiment contains:

* Name
* Hypothesis
* Objective
* Target segment
* Control description
* Variant A description
* Variant B description
* Budget
* Initial status

---

## 2. Experiment Lifecycle Management

Experiments follow a structured lifecycle:

```text
DRAFT
  ↓
ACTIVE
  ↓
COMPLETED
  ↓
WINNER_SELECTED
```

The application prevents invalid lifecycle transitions through backend validation.

---

## 3. Customer Assignment

Customers are assigned to experiment groups:

```text
CONTROL
VARIANT_A
VARIANT_B
```

This allows different strategies to be tested against different customer groups.

---

## 4. Experiment Result Collection

The system records customer-level experiment results.

Currently, conversion is used as the primary metric.

Example:

```text
Customer: C001
Group: CONTROL
Conversion: 1
```

A value of:

```text
1 = Converted
0 = Did not convert
```

is used for conversion analysis.

---

## 5. Experiment Analysis

GrowthPilot calculates conversion performance for each experiment group.

Example:

```text
CONTROL      → 50%
VARIANT_A    → 75%
VARIANT_B    → 40%
```

The platform identifies the group with the highest conversion rate as the winner.

---

## 6. Winner Selection

After analysis, the winning group can be selected.

The experiment status becomes:

```text
WINNER_SELECTED
```

This creates a clear connection between experiment results and subsequent AI recommendations.

---

## 7. AI-Powered Recommendations

GrowthPilot generates an AI recommendation based on experiment performance.

The recommendation includes:

* Recommended strategy
* Reason for the recommendation
* Expected impact

Example:

```text
Recommendation:
Apply the winning VARIANT_A strategy.

Reason:
VARIANT_A achieved the highest conversion rate
among the tested groups.

Expected Impact:
Improve conversion by approximately 25%.
```

---

## 8. Human-in-the-Loop Approval

GrowthPilot does not immediately execute an AI recommendation.

The merchant must first approve it.

The action lifecycle is:

```text
PROPOSED
    ↓
APPROVED
    ↓
EXECUTING
    ↓
EXECUTED
```

The merchant can also reject a proposed action:

```text
PROPOSED → REJECTED
```

This provides human oversight over AI-generated growth actions.

---

## 9. AI Action Execution

After approval, GrowthPilot executes the proposed growth action.

The system records:

* Execution status
* Execution timestamp
* Execution result
* Actual impact

---

## 10. Actual Impact Tracking

GrowthPilot goes beyond simply recommending an action.

After execution, the platform records the actual observed impact.

Example:

```text
Execution Result:
Winning group: VARIANT_A
Conversion rate: 75%

Actual Impact:
VARIANT_A achieved a 75% conversion rate
compared with 50% for CONTROL.

Improvement: 50%
```

This allows GrowthPilot to compare:

**Expected Impact vs Actual Impact**

and creates the foundation for continuous optimization.

---

# 🏗️ System Architecture

```text
                         ┌───────────────────────┐
                         │       Merchant        │
                         │    Business Goal      │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │   React Frontend      │
                         │      Dashboard        │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │    FastAPI Backend    │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
     ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
     │ AI Experiment   │   │ Experiment      │   │ AI Action       │
     │ Generator       │   │ Engine          │   │ Engine          │
     └────────┬────────┘   └────────┬────────┘   └────────┬────────┘
              │                     │                     │
              ▼                     ▼                     ▼
     ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
     │ Experiment      │   │ Customer        │   │ Recommendation  │
     │ Design          │   │ Assignment      │   │ & Execution     │
     └─────────────────┘   └────────┬────────┘   └────────┬────────┘
                                    │                     │
                                    ▼                     ▼
                           ┌─────────────────────────────────┐
                           │          PostgreSQL             │
                           │            Database             │
                           └─────────────────────────────────┘
```

---

# 🔄 Experiment Lifecycle

Each experiment moves through a controlled lifecycle.

### 1. Draft

The AI-generated experiment starts in:

```text
DRAFT
```

The merchant can review the experiment.

### 2. Active

The experiment is activated:

```text
ACTIVE
```

Customers can now be assigned to experiment groups.

### 3. Completed

Once sufficient results are collected:

```text
COMPLETED
```

### 4. Winner Selected

After analysis, the winning strategy is selected:

```text
WINNER_SELECTED
```

---

# ⚡ AI Recommendation and Action Workflow

After winner selection:

```text
Experiment Analysis
        ↓
Winning Group
        ↓
AI Recommendation
        ↓
AI Growth Action
        ↓
PROPOSED
        ↓
Merchant Approval
        ↓
APPROVED
        ↓
EXECUTING
        ↓
EXECUTED
        ↓
Actual Impact
```

The workflow combines automation with human oversight.

---

# 📈 Actual Impact Tracking

GrowthPilot records several execution-related fields.

| Field              | Purpose                               |
| ------------------ | ------------------------------------- |
| `status`           | Current action state                  |
| `approved_at`      | Time the merchant approved the action |
| `executed_at`      | Time execution completed              |
| `execution_result` | Result of execution                   |
| `actual_impact`    | Observed business impact              |

This allows the platform to maintain a historical record of growth actions.

---

# 🛠️ Technology Stack

## Frontend

* React
* JavaScript
* Axios
* Recharts
* HTML
* CSS

## Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic/FastAPI validation
* Uvicorn

## Database

* PostgreSQL

## Data and Analytics

* Pandas
* NumPy
* Scikit-learn
* Statistical analysis

## AI

* AI-powered experiment generation
* AI-powered growth recommendations

## Development Tools

* Git
* GitHub
* VS Code
* PostgreSQL tools

---

# 📁 Project Structure

```text
GrowthPilot/
│
├── backend/
│   │
│   ├── app/
│   │   │
│   │   ├── models/
│   │   │   ├── experiment.py
│   │   │   ├── ai_action.py
│   │   │   └── ...
│   │   │
│   │   ├── routes/
│   │   │   ├── experiments.py
│   │   │   ├── generator.py
│   │   │   ├── ai_actions.py
│   │   │   └── ...
│   │   │
│   │   ├── services/
│   │   │   ├── experiment_generator.py
│   │   │   └── ...
│   │   │
│   │   ├── database.py
│   │   └── main.py
│   │
│   ├── requirements.txt
│   └── ...
│
├── frontend/
│   │
│   ├── src/
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── ...
│   │
│   ├── package.json
│   └── ...
│
├── README.md
└── .gitignore
```

---

# 🔌 Backend API

The FastAPI backend provides endpoints for the major stages of the experimentation workflow.

## Experiments

### Get all experiments

```http
GET /experiments/
```

### Get experiment

```http
GET /experiments/{experiment_id}
```

### Create experiment

```http
POST /experiments/
```

### Activate experiment

```http
PATCH /experiments/{experiment_id}/activate
```

### Complete experiment

```http
PATCH /experiments/{experiment_id}/complete
```

### Select winner

```http
PATCH /experiments/{experiment_id}/winner
```

---

# 📊 Experiment Analysis

### Analyze experiment

```http
GET /experiments/{experiment_id}/analysis
```

### Get experiment decision

```http
GET /experiments/{experiment_id}/decision
```

### Get AI recommendation

```http
GET /experiments/{experiment_id}/ai-recommendation
```

---

# 👥 Customer Assignment

### Get experiment assignments

```http
GET /experiments/{experiment_id}/assignments
```

### Assign customer

```http
POST /experiments/{experiment_id}/assign
```

---

# 📈 Experiment Results

### Save result

```http
POST /experiments/{experiment_id}/results
```

### Get results

```http
GET /experiments/{experiment_id}/results
```

---

# ⚡ AI Actions

### Get all AI actions

```http
GET /ai-actions/
```

### Get action

```http
GET /ai-actions/{action_id}
```

### Approve action

```http
PUT /ai-actions/{action_id}/approve
```

### Execute action

```http
PUT /ai-actions/{action_id}/execute
```

### Reject action

```http
PUT /ai-actions/{action_id}/reject
```

---

# 🗄️ Database Design

GrowthPilot uses PostgreSQL for persistent storage.

The core entities include:

### Experiments

Stores experiment definitions.

Important fields include:

```text
experiment_id
name
hypothesis
objective
target_segment
control_description
variant_a_description
variant_b_description
status
budget
```

### Experiment Assignments

Connects customers with experiment groups.

```text
experiment_id
customer_id
group
```

Groups include:

```text
CONTROL
VARIANT_A
VARIANT_B
```

### Experiment Results

Stores customer-level experiment outcomes.

```text
experiment_id
customer_id
metric
value
```

### AI Actions

Stores AI-generated growth actions.

```text
action_id
experiment_id
action_type
description
reason
expected_impact
status
created_at
approved_at
executed_at
execution_result
actual_impact
```

---

# 🎨 Frontend Dashboard

The React dashboard provides a centralized interface for managing the experimentation workflow.

The dashboard includes:

### 🏠 Dashboard

Displays high-level growth experiment information.

### 🧪 Experiments

Allows the merchant to:

* Generate experiments
* Select experiments
* Activate experiments
* Complete experiments
* Select winners

### 📊 Analysis

Displays:

* Conversion rates
* Group performance
* Winning group
* Improvement percentage
* Conversion performance chart

### ⚡ AI Actions

Displays:

* AI recommendation
* Reason
* Expected impact
* Action status
* Approval controls
* Execution controls
* Execution result
* Actual impact
* Execution timestamp

### 📋 History

Provides visibility into previous experiments and their statuses.

---

# 🚀 Installation and Setup

## Prerequisites

Install the following:

* Python 3.x
* Node.js
* npm
* PostgreSQL
* Git

---

# 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Navigate into the project:

```bash
cd GrowthPilot
```

---

# 2. Backend Setup

Navigate to the backend:

```bash
cd backend
```

Create a virtual environment:

### Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 3. Configure PostgreSQL

Create a PostgreSQL database for GrowthPilot.

Configure the database connection in the backend according to your local environment.

For example:

```text
DATABASE_URL=postgresql://username:password@localhost:5432/growthpilot
```

Do not commit real database credentials to GitHub.

---

# 4. Start the Backend

From:

```text
GrowthPilot/backend
```

run:

```bash
uvicorn app.main:app --reload
```

The backend will normally be available at:

```text
http://127.0.0.1:8000
```

---

# 5. Frontend Setup

Open another terminal.

Navigate to:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 🧪 Running the Project

Once both frontend and backend are running:

```text
1. Open GrowthPilot Dashboard
             ↓
2. Enter business goal
             ↓
3. Enter target customer segment
             ↓
4. Generate experiment
             ↓
5. Select experiment
             ↓
6. Activate experiment
             ↓
7. Assign customers
             ↓
8. Add experiment results
             ↓
9. Analyze experiment
             ↓
10. Select winner
             ↓
11. Review AI recommendation
             ↓
12. Approve AI action
             ↓
13. Execute AI action
             ↓
14. View actual impact
```

---

# 📖 API Documentation

FastAPI automatically provides interactive API documentation.

After starting the backend, open:

```text
http://127.0.0.1:8000/docs
```

The Swagger interface allows developers to:

* View available endpoints
* Inspect request parameters
* Test APIs
* View responses
* Debug backend functionality

---

# 🧩 Example Workflow

Suppose a merchant wants to:

```text
Increase customer conversion
```

for:

```text
New customers
```

GrowthPilot can generate an experiment such as:

```text
Experiment:
New Customer Conversion Test

Hypothesis:
Changing the promotional strategy for new customers
will increase conversion.

Control:
Existing promotional strategy

Variant A:
Strategy A

Variant B:
Strategy B
```

Customers are assigned:

```text
CONTROL
C001
C004

VARIANT_A
C002
C005

VARIANT_B
C003
```

After results are collected:

```text
CONTROL      → 50%
VARIANT_A    → 100%
VARIANT_B    → 0%
```

GrowthPilot identifies:

```text
Winner: VARIANT_A
```

The AI then generates a recommendation:

```text
Apply the winning VARIANT_A strategy.
```

The merchant approves the action.

The action is executed.

GrowthPilot records:

```text
Status:
EXECUTED

Execution Result:
Winning group: VARIANT_A
Conversion rate: 100%

Actual Impact:
VARIANT_A achieved a 100% conversion rate
compared with 50% for CONTROL.
Improvement: 100%.
```

This completes the growth experimentation loop.

---

# 🛡️ Validation and Error Handling

GrowthPilot includes backend validation to prevent invalid requests and experiment states.

Examples include:

### Missing goal

```text
Goal is required
```

### Missing target segment

```text
Target segment is required
```

### Invalid experiment transition

The backend validates allowed experiment statuses.

### Invalid AI action approval

An action can only be approved when its status is:

```text
PROPOSED
```

### Invalid execution

An AI action must be:

```text
APPROVED
```

before it can be executed.

### Missing assignments

Execution fails safely if the experiment has no customer assignments.

### Missing results

Execution fails safely if conversion results are unavailable.

### Database failures

Database operations use rollback handling to prevent partially committed changes.

---

# 🔮 Future Scope

GrowthPilot can be extended into a more advanced autonomous growth platform.

## 1. Authentication and Authorization

Add:

* Merchant accounts
* Login/signup
* Role-based access
* Protected dashboards

---

## 2. Real Business Integrations

Connect GrowthPilot with:

* E-commerce platforms
* CRM systems
* Marketing platforms
* Payment systems
* Customer analytics platforms

---

## 3. Real-Time Experiment Execution

Instead of simulated customer assignments and actions, experiments could interact directly with production systems.

---

## 4. Advanced Statistical Testing

Future versions could include:

* A/B testing significance testing
* Confidence intervals
* p-values
* Bayesian experimentation
* Sequential testing
* Multi-armed bandits

---

## 5. Multi-Metric Optimization

Instead of optimizing only conversion, GrowthPilot could optimize:

* Revenue
* Average order value
* Customer lifetime value
* Retention
* Click-through rate
* Engagement
* Profit margin

---

## 6. Autonomous Experiment Loops

A future version could automatically:

```text
Analyze
   ↓
Generate
   ↓
Test
   ↓
Learn
   ↓
Recommend
   ↓
Execute
   ↓
Measure
   ↓
Generate Next Experiment
```

This would move GrowthPilot closer to a truly autonomous growth agent.

---

# 🏆 Project Highlights

GrowthPilot demonstrates the integration of several important software engineering and AI concepts:

* AI-assisted experiment generation
* Automated experimentation
* Customer-level experiment assignment
* Conversion analytics
* Statistical decision-making
* AI recommendations
* Human-in-the-loop AI
* Automated action execution
* Actual impact measurement
* REST API development
* PostgreSQL database management
* React dashboard development
* FastAPI backend development
* End-to-end system integration
* Error handling and validation

---

# 🎓 Academic / Portfolio Value

GrowthPilot can demonstrate practical knowledge in:

```text
Artificial Intelligence
        +
Machine Learning
        +
Data Science
        +
Statistical Analysis
        +
Backend Development
        +
Frontend Development
        +
Database Management
        +
API Development
        +
Automation
        +
AI Agents
```

It is designed as an end-to-end system rather than an isolated machine learning model.

---

# 📌 Current Project Status

### Core platform

* [x] AI experiment generation
* [x] Experiment lifecycle
* [x] Customer assignment
* [x] Experiment result collection
* [x] Conversion analysis
* [x] Winner selection
* [x] AI recommendation
* [x] AI action generation
* [x] Merchant approval
* [x] Action rejection
* [x] Action execution
* [x] Execution result tracking
* [x] Actual impact tracking
* [x] Frontend dashboard
* [x] Experiment analysis visualization
* [x] Backend validation
* [x] Error handling

### Planned improvements

* [ ] Authentication
* [ ] Production deployment
* [ ] Real business integrations
* [ ] Advanced statistical testing
* [ ] Automated continuous experimentation
* [ ] Production-scale monitoring

---

# 👩‍💻 Author

**Akshitha Penakacherla**

B.Tech — Data Science

GrowthPilot was developed as an AI-powered experimentation platform focused on combining **Data Science, Artificial Intelligence, experimentation, and full-stack development** into a single end-to-end application.

---

# ⭐ Project Vision

GrowthPilot aims to evolve from an experimentation dashboard into an **autonomous AI growth agent** capable of continuously learning from business experiments.

The long-term vision is:

```text
Business Goal
      ↓
Discover Opportunity
      ↓
Generate Hypothesis
      ↓
Design Experiment
      ↓
Run Experiment
      ↓
Analyze Results
      ↓
Learn
      ↓
Recommend Action
      ↓
Get Approval
      ↓
Execute
      ↓
Measure Impact
      ↓
Learn Again
      ↓
🚀 Next Experiment
```

**GrowthPilot — Experiment. Learn. Optimize. Grow. 🚀**
