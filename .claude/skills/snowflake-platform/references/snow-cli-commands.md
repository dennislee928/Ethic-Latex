# Snow CLI Command Reference

Version: 3.14.0+ (Dec 2025)

## Installation

```bash
pip install snowflake-cli
snow --version
```

## Global Options

```bash
snow --help
snow --version
snow --debug <command>        # Enable debug output
snow --format json <command>  # JSON output
```

## Connection Commands

```bash
# Add new connection
snow connection add

# Test connection
snow connection test -c <connection_name>

# List connections
snow connection list

# Set default connection
snow connection set-default <connection_name>
```

## SQL Commands

```bash
# Execute query
snow sql -q "SELECT CURRENT_USER()"

# Execute from file
snow sql -f query.sql

# Specify connection
snow sql -q "SELECT 1" -c my_connection

# Output format
snow sql -q "SELECT 1" --format json
```

## Native App Commands

```bash
# Development
snow app run              # Deploy and create/upgrade app
snow app deploy           # Upload to stage only
snow app teardown         # Remove app completely

# Versioning
snow app version create V1_0
snow app version list
snow app version drop V1_0

# Publishing
snow app publish --version V1_0 --patch 0

# Release Channels
snow app release-channel list
snow app release-channel add-version --channel ALPHA --version V1_0
snow app release-directive set default --version V1_0 --patch 0 --channel DEFAULT
```

## Streamlit Commands

```bash
# Deploy Streamlit app
snow streamlit deploy
snow streamlit deploy --replace
snow streamlit deploy --replace --open  # Open in browser

# List Streamlit apps
snow streamlit list
```

## Stage Commands

```bash
# List files in stage
snow stage list @my_stage

# Copy files
snow stage copy @my_stage/file.txt ./local/
snow stage copy ./local/file.txt @my_stage/

# Remove files
snow stage remove @my_stage/file.txt
```

## Snowpark Commands

```bash
# Deploy procedure
snow snowpark procedure deploy

# Deploy function
snow snowpark function deploy

# Execute procedure
snow snowpark procedure execute <name>
```

## SPCS (Container Services) Commands

```bash
# Compute pools
snow spcs compute-pool list
snow spcs compute-pool create <name>

# Services
snow spcs service list
snow spcs service deploy
snow spcs service status <name>

# Image repositories
snow spcs image-repository list
```

## Object Commands

```bash
# List objects
snow object list warehouse
snow object list database
snow object list schema

# Describe object
snow object describe warehouse <name>
```

## Log Commands (New 2025)

```bash
# View logs
snow logs

# Stream logs
snow logs --follow
```

## Helper Commands

```bash
# Check for SnowSQL env vars to migrate
snow helper check-snowsql-env-vars

# Import connections from SnowSQL
snow helpers import-snowsql-connections
```

## Project Initialization

```bash
# Initialize new project
snow init

# Initialize with template
snow init --template native-app
snow init --template streamlit
```

## Configuration File

Default location: `~/.snowflake/config.toml`

```toml
[connections.default]
account = "orgname-accountname"
user = "USERNAME"
authenticator = "SNOWFLAKE_JWT"
private_key_path = "~/.snowflake/rsa_key.p8"
warehouse = "COMPUTE_WH"
database = "MY_DB"
schema = "PUBLIC"

[connections.dev]
account = "orgname-accountname"
user = "DEV_USER"
password = "..."
```

## Environment Variables

```bash
SNOWFLAKE_DEFAULT_CONNECTION_NAME  # Default connection to use
SNOWFLAKE_HOME                     # Config directory (~/.snowflake)
```
