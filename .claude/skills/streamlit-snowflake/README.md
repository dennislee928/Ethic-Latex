# streamlit-snowflake

Build and deploy Streamlit apps natively in Snowflake with production-ready templates.

## Auto-Trigger Keywords

This skill should be suggested when the user mentions:

- streamlit snowflake
- streamlit in snowflake
- SiS (Streamlit in Snowflake)
- snow streamlit deploy
- snowflake native app streamlit
- snowflake marketplace app
- environment.yml snowflake
- snowflake anaconda channel
- snowpark streamlit
- streamlit data app snowflake

## What This Skill Provides

- **Project scaffold**: `snowflake.yml`, `environment.yml`, `streamlit_app.py`
- **Snowpark patterns**: Session connection, caching, DataFrame handling
- **Multi-page structure**: Ready-to-use pages/ directory
- **Marketplace publishing**: Native App templates for Marketplace listings
- **CI/CD**: GitHub Actions deployment workflow
- **Error prevention**: Package channel, version, and auth issue fixes

## Quick Usage

```
User: "Help me set up a Streamlit app in Snowflake"
Claude: [Proposes using streamlit-snowflake skill]
```

## Contents

```
streamlit-snowflake/
├── SKILL.md                    # Full documentation
├── README.md                   # This file
├── templates/                  # Project templates
│   ├── snowflake.yml
│   ├── environment.yml
│   ├── streamlit_app.py
│   ├── pages/
│   └── common/
├── templates-native-app/       # Marketplace publishing
│   ├── manifest.yml
│   ├── setup.sql
│   └── README.md
├── references/                 # Supporting docs
│   ├── available-packages.md
│   ├── authentication.md
│   └── ci-cd.md
└── scripts/
    └── check-packages.sql
```

## Key Errors Prevented

| Error | This Skill Prevents |
|-------|---------------------|
| PackageNotFoundError | Uses correct `channels: - snowflake` |
| Old Streamlit features missing | Explicit `streamlit=1.35.0` version |
| Deployment syntax errors | CLI 3.14.0+ patterns |
| Auth failures (2026) | Documents modern auth methods |

## Requirements

- Snowflake account with Streamlit enabled
- Snowflake CLI 3.14.0+ (`snow` command)
- Python 3.11 (recommended)

## Links

- [Streamlit in Snowflake Docs](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Snowflake CLI](https://docs.snowflake.com/en/developer-guide/snowflake-cli/index)
- [Package Explorer](https://snowpark-python-packages.streamlit.app/)
