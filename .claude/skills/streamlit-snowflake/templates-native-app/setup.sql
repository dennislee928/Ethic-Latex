-- Snowflake Native App Setup Script
-- This runs when the app is installed in a consumer account
-- Documentation: https://docs.snowflake.com/en/developer-guide/native-apps/creating-setup-script

-- =============================================================================
-- APPLICATION ROLES
-- =============================================================================

-- Admin role for app management
CREATE APPLICATION ROLE IF NOT EXISTS app_admin;

-- User role for regular usage
CREATE APPLICATION ROLE IF NOT EXISTS app_user;


-- =============================================================================
-- SCHEMAS
-- =============================================================================

-- Schema for app configuration and data
CREATE SCHEMA IF NOT EXISTS core;
GRANT USAGE ON SCHEMA core TO APPLICATION ROLE app_admin;
GRANT USAGE ON SCHEMA core TO APPLICATION ROLE app_user;

-- Schema for Streamlit app
CREATE SCHEMA IF NOT EXISTS streamlit;
GRANT USAGE ON SCHEMA streamlit TO APPLICATION ROLE app_admin;
GRANT USAGE ON SCHEMA streamlit TO APPLICATION ROLE app_user;


-- =============================================================================
-- STREAMLIT APP
-- =============================================================================

-- Create the Streamlit application
CREATE OR REPLACE STREAMLIT streamlit.main_app
  FROM '/streamlit'
  MAIN_FILE = 'streamlit_app.py';

-- Grant access to Streamlit app
GRANT USAGE ON STREAMLIT streamlit.main_app TO APPLICATION ROLE app_admin;
GRANT USAGE ON STREAMLIT streamlit.main_app TO APPLICATION ROLE app_user;


-- =============================================================================
-- STORED PROCEDURES (Optional)
-- =============================================================================

-- Example: Configuration procedure
-- CREATE OR REPLACE PROCEDURE core.configure_app(config VARIANT)
--   RETURNS STRING
--   LANGUAGE PYTHON
--   RUNTIME_VERSION = '3.11'
--   PACKAGES = ('snowflake-snowpark-python')
--   HANDLER = 'config.configure'
--   AS $$
-- # Python handler code here
-- $$;

-- GRANT USAGE ON PROCEDURE core.configure_app(VARIANT) TO APPLICATION ROLE app_admin;


-- =============================================================================
-- TABLES (Optional)
-- =============================================================================

-- Example: App configuration table
-- CREATE TABLE IF NOT EXISTS core.app_config (
--     key STRING PRIMARY KEY,
--     value VARIANT,
--     updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
-- );

-- GRANT SELECT, INSERT, UPDATE ON TABLE core.app_config TO APPLICATION ROLE app_admin;
-- GRANT SELECT ON TABLE core.app_config TO APPLICATION ROLE app_user;


-- =============================================================================
-- VERSION CALLBACK (Optional)
-- =============================================================================

-- Called when app version changes
-- CREATE OR REPLACE PROCEDURE core.version_init()
--   RETURNS STRING
--   LANGUAGE SQL
--   AS
--   BEGIN
--     -- Migration logic here
--     RETURN 'Version initialized';
--   END;


-- =============================================================================
-- GRANT ROLES TO OWNER
-- =============================================================================

-- The app owner gets admin role by default
GRANT APPLICATION ROLE app_admin TO APPLICATION;
