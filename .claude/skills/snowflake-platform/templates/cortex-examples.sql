-- Snowflake Cortex AI Function Examples
-- Run these in Snowflake worksheet or via snow sql

-- ============================================
-- COMPLETE - Text Generation
-- ============================================

-- Simple prompt
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3.1-70b',
    'Explain data warehousing in one sentence'
) AS response;

-- With conversation history
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'llama3.1-70b',
    [
        {'role': 'system', 'content': 'You are a data analyst assistant'},
        {'role': 'user', 'content': 'What is a fact table?'}
    ]
) AS response;

-- With options (lower temperature = more deterministic)
SELECT SNOWFLAKE.CORTEX.COMPLETE(
    'mistral-large2',
    'Generate a product description for: wireless earbuds',
    {'temperature': 0.3, 'max_tokens': 200}
) AS response;

-- ============================================
-- SUMMARIZE - Text Summarization
-- ============================================

-- Summarize single text
SELECT SNOWFLAKE.CORTEX.SUMMARIZE(
    'Snowflake is a cloud-based data warehousing platform that enables
    organizations to store, process, and analyze large volumes of data.
    It separates compute from storage, allowing independent scaling of
    each resource. The platform supports structured and semi-structured
    data, including JSON, Avro, and Parquet formats.'
) AS summary;

-- Summarize column from table
SELECT
    product_id,
    SNOWFLAKE.CORTEX.SUMMARIZE(review_text) AS review_summary
FROM product_reviews
LIMIT 10;

-- Aggregate summaries across rows (no context window limit!)
SELECT AI_SUMMARIZE_AGG(feedback_text) AS all_feedback_summary
FROM customer_feedback
WHERE created_date > DATEADD(day, -30, CURRENT_DATE());

-- ============================================
-- TRANSLATE - Language Translation
-- ============================================

-- Auto-detect source language
SELECT SNOWFLAKE.CORTEX.TRANSLATE(
    'Bonjour, comment allez-vous?',
    '',     -- Empty = auto-detect
    'en'    -- Target: English
) AS translated;

-- Explicit source language
SELECT AI_TRANSLATE(
    'Hola, buenos días',
    'es',   -- Source: Spanish
    'en'    -- Target: English
) AS translated;

-- Translate column
SELECT
    original_text,
    SNOWFLAKE.CORTEX.TRANSLATE(original_text, '', 'en') AS english_text
FROM international_reviews
LIMIT 10;

-- ============================================
-- SENTIMENT - Sentiment Analysis
-- ============================================

-- Single text (returns -1 to 1)
SELECT SNOWFLAKE.CORTEX.SENTIMENT(
    'This product is amazing! Best purchase ever.'
) AS sentiment_score;

-- Categorize by sentiment
SELECT
    review_text,
    SNOWFLAKE.CORTEX.SENTIMENT(review_text) AS score,
    CASE
        WHEN SNOWFLAKE.CORTEX.SENTIMENT(review_text) > 0.3 THEN 'Positive'
        WHEN SNOWFLAKE.CORTEX.SENTIMENT(review_text) < -0.3 THEN 'Negative'
        ELSE 'Neutral'
    END AS sentiment_category
FROM product_reviews
LIMIT 20;

-- ============================================
-- AI_FILTER - Natural Language Filtering
-- ============================================

-- Filter with plain English
SELECT * FROM support_tickets
WHERE AI_FILTER(description, 'mentions billing or payment issues');

-- Combine with SQL predicates
SELECT * FROM customer_feedback
WHERE created_date > '2025-01-01'
  AND AI_FILTER(feedback_text, 'customer is frustrated or angry');

-- Find specific topics
SELECT * FROM news_articles
WHERE AI_FILTER(content, 'discusses artificial intelligence or machine learning');

-- ============================================
-- AI_CLASSIFY - Text Classification
-- ============================================

-- Categorize support tickets
SELECT
    ticket_id,
    description,
    AI_CLASSIFY(
        description,
        ['billing', 'technical', 'shipping', 'account', 'other']
    ) AS category
FROM support_tickets
LIMIT 20;

-- Priority classification
SELECT
    ticket_id,
    AI_CLASSIFY(
        description,
        ['urgent', 'high', 'medium', 'low']
    ) AS priority
FROM support_tickets
WHERE status = 'open';

-- ============================================
-- Practical Example: Customer Support Analysis
-- ============================================

-- Comprehensive ticket analysis
SELECT
    ticket_id,
    created_date,
    description,
    SNOWFLAKE.CORTEX.SENTIMENT(description) AS sentiment,
    AI_CLASSIFY(description, ['billing', 'technical', 'shipping', 'account']) AS category,
    SNOWFLAKE.CORTEX.SUMMARIZE(description) AS summary
FROM support_tickets
WHERE created_date > DATEADD(day, -7, CURRENT_DATE())
ORDER BY sentiment ASC  -- Show most negative first
LIMIT 50;
