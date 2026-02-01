# snowflake-platform

Build on Snowflake's AI Data Cloud with snow CLI, Cortex AI functions, Native Apps, and Snowpark.

## Auto-Trigger Keywords

This skill activates when conversations include:

**Platform:**
- snowflake
- snow cli
- snowflake cli
- snowflake connection
- snowflake account

**Cortex AI:**
- cortex ai
- snowflake cortex
- AI_COMPLETE
- AI_SUMMARIZE
- AI_TRANSLATE
- AI_FILTER
- AI_CLASSIFY
- AI_SENTIMENT
- SNOWFLAKE.CORTEX
- cortex llm
- cortex functions

**Native Apps:**
- native app
- snowflake native app
- snowflake marketplace
- provider studio
- application package
- release channels
- snow app run
- snow app deploy
- snow app publish
- setup_script.sql
- manifest.yml

**Authentication:**
- snowflake jwt
- snowflake authentication
- account locator
- rsa key snowflake
- snowflake private key

**Snowpark:**
- snowpark
- snowpark python
- snowflake dataframe
- snowflake udf
- snowflake stored procedure

**REST API:**
- snowflake rest api
- snowflake sql api
- /api/v2/statements
- statementHandle
- statementStatusUrl
- snowflake polling
- snowflake async query

**Errors:**
- jwt validation error snowflake
- account identifier
- REFERENCE_USAGE
- external access integration
- release directive
- security review status
- Unsupported Accept header null
- Too many subrequests
- 090001 snowflake
- statementHandle timeout

## What This Skill Covers

1. **Snow CLI** - Project management, SQL execution, app deployment
2. **REST API** - SQL API v2, async queries, polling, Cloudflare Workers integration
3. **Cortex AI** - LLM functions in SQL (COMPLETE, SUMMARIZE, TRANSLATE, etc.)
4. **Native Apps** - Development, versioning, marketplace publishing
5. **Authentication** - JWT key-pair, account identifiers (critical gotcha)
6. **Snowpark** - Python DataFrame API, UDFs, stored procedures
7. **Marketplace** - Security review, Provider Studio, paid listings

## What This Skill Does NOT Cover

- Streamlit in Snowflake (use `streamlit-snowflake` skill)
- Data engineering/ETL patterns
- BI tool integrations (Tableau, Looker)
- Advanced ML model deployment

## Key Corrections

- Account identifier confusion (org-account vs locator)
- REST API missing Accept header on polling
- Workers fetch timeout (use AbortSignal)
- Subrequest limits during polling
- External access integration reset after deploys
- Release channel syntax (CLI vs legacy SQL)
- Artifact nesting in snowflake.yml
- REFERENCE_USAGE grant syntax for shared data

## Included Agents

This skill includes **1 companion agent** for common workflows:

| Agent | Purpose | Trigger Phrases |
|-------|---------|-----------------|
| **snowflake-deploy** | Deploy native apps, run security scans | "deploy snowflake app", "publish to marketplace" |

**Why use the agent?** Context hygiene. Native app deployment involves security scans, version management, and release directives - the agent handles the multi-step workflow and returns a clean status report.

---

## Related Skills

- `streamlit-snowflake` - Streamlit apps in Snowflake
