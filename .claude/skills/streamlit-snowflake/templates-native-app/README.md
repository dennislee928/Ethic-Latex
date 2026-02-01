# Publishing Streamlit Apps to Snowflake Marketplace

This guide covers converting your Streamlit app to a Native App and publishing to the Snowflake Marketplace.

## Overview

**Workflow:**
1. Convert Streamlit app to Native App structure
2. Create Application Package
3. Test locally with trial installation
4. Create Provider Profile (one-time)
5. Create Marketplace Listing
6. Submit for approval

## Native App Directory Structure

```
my-native-app/
├── manifest.yml              # App manifest (required)
├── setup.sql                 # Installation script (required)
├── README.md                 # App documentation
├── streamlit/                # Streamlit app files
│   ├── environment.yml
│   ├── streamlit_app.py
│   ├── pages/
│   └── common/
└── scripts/                  # Optional helper scripts
    └── deploy.sql
```

## Step 1: Create Application Package

```sql
-- Create the application package
CREATE APPLICATION PACKAGE IF NOT EXISTS my_app_package;

-- Create a versioned stage for app files
CREATE SCHEMA IF NOT EXISTS my_app_package.versions;
CREATE STAGE IF NOT EXISTS my_app_package.versions.v1
  DIRECTORY = (ENABLE = TRUE);

-- Upload files to stage (via Snowflake CLI or Snowsight)
-- PUT file://manifest.yml @my_app_package.versions.v1/;
-- PUT file://setup.sql @my_app_package.versions.v1/;
-- PUT file://streamlit/* @my_app_package.versions.v1/streamlit/;
```

### Using Snowflake CLI

```bash
# Upload all files
snow stage put manifest.yml @my_app_package.versions.v1/ --overwrite
snow stage put setup.sql @my_app_package.versions.v1/ --overwrite
snow stage put streamlit/ @my_app_package.versions.v1/streamlit/ --overwrite --recursive
```

## Step 2: Add Version to Package

```sql
-- Add version to the application package
ALTER APPLICATION PACKAGE my_app_package
  ADD VERSION v1_0
  USING '@my_app_package.versions.v1';

-- Set as release directive (for distribution)
ALTER APPLICATION PACKAGE my_app_package
  SET DEFAULT RELEASE DIRECTIVE
  VERSION = v1_0
  PATCH = 0;
```

## Step 3: Test Installation

```sql
-- Create test installation in your account
CREATE APPLICATION my_app_test
  FROM APPLICATION PACKAGE my_app_package
  USING VERSION v1_0;

-- Verify Streamlit app works
-- Navigate to Apps > my_app_test in Snowsight

-- Drop test when done
DROP APPLICATION my_app_test;
```

## Step 4: Create Provider Profile (One-Time)

1. Go to **Snowsight** > **Data Products** > **Provider Studio**
2. Click **Profiles** > **+ Profile**
3. Fill in:
   - Company name
   - Contact information
   - Logo (recommended: 200x200px PNG)
   - Description
4. Click **Submit for Approval**

**Note:** Provider profile approval can take 1-3 business days.

## Step 5: Set Distribution to External

```sql
-- Enable external distribution
ALTER APPLICATION PACKAGE my_app_package
  SET DISTRIBUTION = EXTERNAL;
```

**Note:** This triggers Snowflake's security scan (NAAPS). Allow 24-48 hours for scan completion.

## Step 6: Create Marketplace Listing

1. Go to **Provider Studio** > **Listings** > **+ Create Listing**
2. Select **Snowflake Marketplace**
3. Configure listing:

### Basic Info
- **Title**: Your app name (shown in Marketplace)
- **Subtitle**: Brief tagline
- **Description**: Full description (Markdown supported)

### Attachments
- **Icon**: 200x200px PNG (required)
- **Screenshots**: Up to 5 images showing app functionality

### Data Product
- Select your Application Package

### Pricing (for paid apps)
- **Free**: No charge
- **Paid**: Configure Stripe, set pricing

### Categories & Regions
- Select relevant categories
- Choose deployment regions

4. Click **Publish** to submit for review

## Step 7: Approval Process

Snowflake reviews all Marketplace listings:

1. **Automated Security Scan** - NAAPS checks for vulnerabilities
2. **Manual Review** - Snowflake team reviews functionality
3. **Approval/Feedback** - Usually 3-5 business days

**Common rejection reasons:**
- Missing documentation
- Security vulnerabilities
- Non-functional features
- Inappropriate content

## Updating Your App

### Create New Version

```sql
-- Upload updated files to new stage
CREATE STAGE IF NOT EXISTS my_app_package.versions.v2;
-- ... upload files ...

-- Add new version
ALTER APPLICATION PACKAGE my_app_package
  ADD VERSION v2_0
  USING '@my_app_package.versions.v2';

-- Update release directive
ALTER APPLICATION PACKAGE my_app_package
  SET DEFAULT RELEASE DIRECTIVE
  VERSION = v2_0
  PATCH = 0;
```

Existing consumers will see update notification in Snowsight.

## Paid Listings (Stripe Setup)

For paid apps:

1. Create Stripe account at [stripe.com](https://stripe.com)
2. In Provider Studio, go to **Monetization Settings**
3. Connect your Stripe account
4. Configure pricing:
   - Per-seat pricing
   - Flat monthly fee
   - Usage-based pricing

## Best Practices

### Documentation
- Include clear README in your app
- Document required privileges
- Provide example use cases

### Testing
- Test in multiple regions
- Verify with different roles
- Check mobile/tablet rendering

### Security
- Request minimum necessary privileges
- Never hardcode credentials
- Use Snowflake secrets for sensitive data

### User Experience
- Add loading spinners for long operations
- Handle errors gracefully
- Provide helpful error messages

## Resources

- [Native Apps Developer Guide](https://docs.snowflake.com/en/developer-guide/native-apps/native-apps-about)
- [Marketplace Publishing Guidelines](https://docs.snowflake.com/en/developer-guide/native-apps/publish-guidelines)
- [Provider Studio Documentation](https://other-docs.snowflake.com/en/collaboration/provider-listings-gs)
- [Monetization Guide](https://other-docs.snowflake.com/en/collaboration/provider-monetization)
