---
globs:
  - "**/PROVIDER_STUDIO.md"
  - "**/manifest.yml"
  - "**/setup.sql"
---

# Snowflake Marketplace Listing

Generate copy-paste content for Snowflake Provider Studio listings.

## When to Use

- After completing a Native App ready for marketplace submission
- When user says "prepare marketplace listing"
- When user says "provider studio content"

## Output Format

Create `docs/PROVIDER_STUDIO.md` with all fields formatted for copy-paste into Provider Studio.

## Provider Studio Fields

| Field | Max Length | Notes |
|-------|------------|-------|
| Title | 72 chars | App name |
| Subtitle | 128 chars | One-liner value prop |
| Description | 10,000 chars | HTML editor (H1, H2, bold, italic, lists, links) |
| Business Needs | 6 max | Select from dropdown |
| Quick Start Examples | 10 max | Title + Description + SQL |
| Video | URL | YouTube/Vimeo embed |
| Documentation | URL | External link |
| **Data Dictionary** | Required | **MANDATORY for data listings** (2025) |
| Data Attributes | Structured | Column descriptions, types, sample values |

## Data Dictionary Requirement (2025)

**MANDATORY** for all data listings. Provider Studio now requires structured data documentation:

| Component | What to Include |
|-----------|-----------------|
| Table descriptions | Purpose, row count, update frequency |
| Column metadata | Name, type, description, sample values |
| Data attributes | Geographic coverage, time range, refresh rate |

**Tip**: Generate data dictionary from your schema using:
```sql
DESCRIBE TABLE my_schema.my_table;
SELECT * FROM my_schema.my_table LIMIT 5;
```

## Business Needs Dropdown (Complete List)

**Healthcare/Insurance:**
- Real World Data (RWD)
- Population Health Management
- Patient 360
- Life Sciences Commercialization

**Location/Geographic:**
- Location Data Enrichment
- Location Geocoding
- Location Planning
- Foot Traffic Analytics

**Business/Company:**
- Contact Data Enrichment
- Market Analysis
- Fundamental Analysis
- 360-Degree Customer View
- Customer Acquisition

**Financial:**
- Risk Analysis
- Pricing Analysis
- Asset Valuation
- Quantitative Analysis
- Fraud Remediation
- Blockchain Analysis

**Customer/Marketing:**
- Audience Segmentation
- Audience Activation
- Personalize Customer Experiences
- Identity Resolution
- Attribution Analysis
- Subscriber Acquisition and Retention

**Operations:**
- Data Quality and Cleansing
- Demand Forecasting
- Inventory Management
- Supply Chain
- Machine Learning

**Compliance/Government:**
- Regulatory Reporting
- Economic Impact Analysis
- ESG Investment Analysis
- Customer Onboarding (KYC)

## Description Template

```html
<h2>Overview</h2>
<p>{{OVERVIEW_PARAGRAPH}}</p>

<h2>What's Included</h2>

<p><strong>{{TABLE_1_NAME}} ({{COUNT}} records)</strong></p>
<ul>
  <li>{{BULLET_1}}</li>
  <li>{{BULLET_2}}</li>
  <li>{{BULLET_3}}</li>
</ul>

<h2>Key Features</h2>
<ul>
  <li><strong>{{FEATURE_1}}</strong> - {{DESC}}</li>
  <li><strong>{{FEATURE_2}}</strong> - {{DESC}}</li>
  <li><strong>{{FEATURE_3}}</strong> - {{DESC}}</li>
</ul>

<h2>Use Cases</h2>
<ol>
  <li><strong>{{USE_CASE_1}}</strong> - {{DESC}}</li>
  <li><strong>{{USE_CASE_2}}</strong> - {{DESC}}</li>
  <li><strong>{{USE_CASE_3}}</strong> - {{DESC}}</li>
</ol>

<h2>Data Source</h2>
<p>{{DATA_SOURCE_PARAGRAPH}}</p>
```

## Quick Start Example Format

Each example needs 3 separate fields in Provider Studio:

**Usage example title:** (short name)
```
{{EXAMPLE_TITLE}}
```

**Description:** (what it demonstrates)
```
{{EXAMPLE_DESCRIPTION}}
```

**Query:** (working SQL)
```sql
{{EXAMPLE_SQL}}
```

## Region Availability (Required)

**Important:** The "All regions" option with "Automatic" fulfillment may not be available for all accounts. You must configure:

| Setting | Value | Notes |
|---------|-------|-------|
| Region availability | **Custom regions** | "All regions" option may be restricted |
| Regions | Asia Pacific (14) | Or select specific regions for your data |
| Fulfillment method | **Manual** | "Automatic" may not be allowed |

**Manual fulfillment** means you must create remote accounts and manage replication manually. This gives more control but requires more setup.

## Submission Checklist

- [ ] Title under 72 characters
- [ ] Subtitle under 128 characters
- [ ] 6 business needs selected
- [ ] Description formatted correctly in HTML editor
- [ ] All SQL examples tested and return results
- [ ] Video URL works (if provided)
- [ ] Documentation URL works (if provided)
- [ ] **Region availability configured** (Custom regions + Manual fulfillment)
- [ ] App version created and security scan APPROVED
- [ ] Release directive set on DEFAULT channel

## Paid Listing Prerequisites

Before enabling monetization (paid listings), complete these steps in order:

| # | Requirement | How to Check/Complete |
|---|-------------|----------------------|
| 1 | Full Snowflake account (not trial) | Admin → Billing (check account type) |
| 2 | ACCOUNTADMIN role | `SELECT CURRENT_ROLE();` |
| 3 | Provider Profile approved | Provider Studio → Profiles → Must show "Approved" |
| 4 | Stripe account configured | Admin → Billing → Marketplace billing → Provider billing → Activate account |
| 5 | Provider & Consumer Terms accepted | ORGADMIN must accept (may be same as ACCOUNTADMIN for single-org accounts) |
| 6 | Contact Marketplace Ops | Submit support case with: account locator, role, profile status, terms status |

**Important**: Cannot convert existing free listing to paid. Must create new paid listing.

📚 **Source**: Snowflake Support (Jan 2026)
