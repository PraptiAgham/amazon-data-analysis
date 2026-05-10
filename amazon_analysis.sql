-- ============================================================
--  AMAZON SALES DATA ANALYSIS — SQL QUERIES
--  Author  : Prapti Agham
--  Email   : praptiagham4@gmail.com
--  Tool    : MySQL
--  Dataset : Amazon Sales Dataset (Kaggle)
-- ============================================================


-- ============================================================
-- STEP 1 : CREATE DATABASE & TABLE
-- ============================================================

CREATE DATABASE IF NOT EXISTS amazon_analysis;
USE amazon_analysis;

DROP TABLE IF EXISTS amazon_products;

CREATE TABLE amazon_products (
    product_id          VARCHAR(20)     PRIMARY KEY,
    product_name        VARCHAR(500),
    category            VARCHAR(500),
    main_category       VARCHAR(100),
    actual_price        DECIMAL(10, 2),
    discounted_price    DECIMAL(10, 2),
    discount_percentage DECIMAL(5, 2),
    rating              DECIMAL(3, 1),
    rating_count        INT,
    about_product       TEXT
);

-- NOTE: After creating the table, import the cleaned CSV using:
-- LOAD DATA INFILE 'amazon_cleaned.csv'
-- INTO TABLE amazon_products
-- FIELDS TERMINATED BY ','
-- ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS;


-- ============================================================
-- STEP 2 : DATA EXPLORATION
-- ============================================================

-- Q1: How many total products are in the dataset?
SELECT COUNT(*) AS total_products
FROM amazon_products;

-- Q2: How many unique categories are there?
SELECT COUNT(DISTINCT main_category) AS total_categories
FROM amazon_products;

-- Q3: Overall summary statistics
SELECT
    ROUND(AVG(actual_price), 2)        AS avg_actual_price,
    ROUND(AVG(discounted_price), 2)    AS avg_discounted_price,
    ROUND(AVG(discount_percentage), 2) AS avg_discount_pct,
    ROUND(AVG(rating), 2)              AS avg_rating,
    SUM(rating_count)                  AS total_reviews,
    MAX(actual_price)                  AS max_price,
    MIN(actual_price)                  AS min_price
FROM amazon_products;

-- Q4: Check for null values in key columns
SELECT
    SUM(CASE WHEN actual_price        IS NULL THEN 1 ELSE 0 END) AS null_actual_price,
    SUM(CASE WHEN discounted_price    IS NULL THEN 1 ELSE 0 END) AS null_discounted_price,
    SUM(CASE WHEN discount_percentage IS NULL THEN 1 ELSE 0 END) AS null_discount_pct,
    SUM(CASE WHEN rating              IS NULL THEN 1 ELSE 0 END) AS null_rating,
    SUM(CASE WHEN rating_count        IS NULL THEN 1 ELSE 0 END) AS null_rating_count
FROM amazon_products;


-- ============================================================
-- STEP 3 : CATEGORY ANALYSIS
-- ============================================================

-- Q5: Number of products per category (sorted by count)
SELECT
    main_category,
    COUNT(*)                           AS product_count,
    ROUND(AVG(actual_price), 2)        AS avg_actual_price,
    ROUND(AVG(discounted_price), 2)    AS avg_discounted_price,
    ROUND(AVG(discount_percentage), 2) AS avg_discount_pct,
    ROUND(AVG(rating), 2)              AS avg_rating,
    SUM(rating_count)                  AS total_reviews
FROM amazon_products
GROUP BY main_category
ORDER BY product_count DESC;

-- Q6: Top 3 categories by average rating
SELECT
    main_category,
    ROUND(AVG(rating), 2) AS avg_rating,
    COUNT(*)              AS product_count
FROM amazon_products
GROUP BY main_category
ORDER BY avg_rating DESC
LIMIT 3;

-- Q7: Which category has the highest average discount?
SELECT
    main_category,
    ROUND(AVG(discount_percentage), 2) AS avg_discount_pct
FROM amazon_products
GROUP BY main_category
ORDER BY avg_discount_pct DESC
LIMIT 5;

-- Q8: Category share of total products (%)
SELECT
    main_category,
    COUNT(*) AS product_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM amazon_products), 2) AS pct_share
FROM amazon_products
GROUP BY main_category
ORDER BY pct_share DESC;


-- ============================================================
-- STEP 4 : DISCOUNT ANALYSIS
-- ============================================================

-- Q9: Count of products in each discount bucket
SELECT
    CASE
        WHEN discount_percentage BETWEEN 0  AND 10  THEN '0-10%'
        WHEN discount_percentage BETWEEN 11 AND 20  THEN '11-20%'
        WHEN discount_percentage BETWEEN 21 AND 30  THEN '21-30%'
        WHEN discount_percentage BETWEEN 31 AND 40  THEN '31-40%'
        WHEN discount_percentage BETWEEN 41 AND 50  THEN '41-50%'
        WHEN discount_percentage BETWEEN 51 AND 60  THEN '51-60%'
        WHEN discount_percentage BETWEEN 61 AND 70  THEN '61-70%'
        WHEN discount_percentage BETWEEN 71 AND 80  THEN '71-80%'
        ELSE '81%+'
    END AS discount_bucket,
    COUNT(*) AS product_count
FROM amazon_products
WHERE discount_percentage IS NOT NULL
GROUP BY discount_bucket
ORDER BY MIN(discount_percentage);

-- Q10: Average savings (actual - discounted price) by category
SELECT
    main_category,
    ROUND(AVG(actual_price - discounted_price), 2) AS avg_savings_inr,
    ROUND(AVG(discount_percentage), 2)             AS avg_discount_pct
FROM amazon_products
GROUP BY main_category
ORDER BY avg_savings_inr DESC;

-- Q11: Products with discount greater than 70% (heavy discounts)
SELECT
    product_name,
    main_category,
    actual_price,
    discounted_price,
    discount_percentage,
    rating,
    rating_count
FROM amazon_products
WHERE discount_percentage > 70
ORDER BY discount_percentage DESC
LIMIT 15;


-- ============================================================
-- STEP 5 : RATING & REVIEW ANALYSIS
-- ============================================================

-- Q12: Rating distribution — count of products per rating bracket
SELECT
    CASE
        WHEN rating < 3.0              THEN 'Below 3.0'
        WHEN rating BETWEEN 3.0 AND 3.9 THEN '3.0 - 3.9'
        WHEN rating BETWEEN 4.0 AND 4.4 THEN '4.0 - 4.4'
        WHEN rating BETWEEN 4.5 AND 4.9 THEN '4.5 - 4.9'
        WHEN rating = 5.0              THEN '5.0'
    END AS rating_bracket,
    COUNT(*) AS product_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM amazon_products), 1) AS pct
FROM amazon_products
GROUP BY rating_bracket
ORDER BY MIN(rating);

-- Q13: Avg rating per discount bucket (do deep discounts hurt ratings?)
SELECT
    CASE
        WHEN discount_percentage BETWEEN 0  AND 10  THEN '0-10%'
        WHEN discount_percentage BETWEEN 11 AND 20  THEN '11-20%'
        WHEN discount_percentage BETWEEN 21 AND 30  THEN '21-30%'
        WHEN discount_percentage BETWEEN 31 AND 40  THEN '31-40%'
        WHEN discount_percentage BETWEEN 41 AND 50  THEN '41-50%'
        WHEN discount_percentage BETWEEN 51 AND 60  THEN '51-60%'
        WHEN discount_percentage BETWEEN 61 AND 70  THEN '61-70%'
        WHEN discount_percentage BETWEEN 71 AND 80  THEN '71-80%'
        ELSE '81%+'
    END AS discount_bucket,
    ROUND(AVG(rating), 2)  AS avg_rating,
    COUNT(*)               AS product_count
FROM amazon_products
WHERE discount_percentage IS NOT NULL
GROUP BY discount_bucket
ORDER BY MIN(discount_percentage);

-- Q14: Top 10 most reviewed products
SELECT
    product_name,
    main_category,
    actual_price,
    discounted_price,
    discount_percentage,
    rating,
    rating_count
FROM amazon_products
ORDER BY rating_count DESC
LIMIT 10;

-- Q15: Products with 100,000+ reviews and their avg rating
SELECT
    ROUND(AVG(rating), 2)    AS avg_rating_high_volume,
    COUNT(*)                 AS product_count,
    SUM(rating_count)        AS total_reviews
FROM amazon_products
WHERE rating_count >= 100000;

-- Q16: Low rated but highly reviewed products (potential quality issues)
SELECT
    product_name,
    main_category,
    rating,
    rating_count,
    discount_percentage
FROM amazon_products
WHERE rating < 3.5
  AND rating_count > 10000
ORDER BY rating_count DESC
LIMIT 10;


-- ============================================================
-- STEP 6 : PRICE ANALYSIS
-- ============================================================

-- Q17: Products in each price band (post-discount)
SELECT
    CASE
        WHEN discounted_price < 500          THEN 'Under ₹500'
        WHEN discounted_price BETWEEN 500  AND 999   THEN '₹500–₹999'
        WHEN discounted_price BETWEEN 1000 AND 1999  THEN '₹1000–₹1999'
        WHEN discounted_price BETWEEN 2000 AND 4999  THEN '₹2000–₹4999'
        WHEN discounted_price BETWEEN 5000 AND 9999  THEN '₹5000–₹9999'
        ELSE '₹10,000+'
    END AS price_band,
    COUNT(*)                  AS product_count,
    SUM(rating_count)         AS total_reviews,
    ROUND(AVG(rating), 2)     AS avg_rating
FROM amazon_products
WHERE discounted_price IS NOT NULL
GROUP BY price_band
ORDER BY MIN(discounted_price);

-- Q18: Most expensive products (before discount)
SELECT
    product_name,
    main_category,
    actual_price,
    discounted_price,
    discount_percentage,
    rating
FROM amazon_products
ORDER BY actual_price DESC
LIMIT 10;

-- Q19: Best value products — high rating, high discount, good reviews
SELECT
    product_name,
    main_category,
    actual_price,
    discounted_price,
    discount_percentage,
    rating,
    rating_count
FROM amazon_products
WHERE discount_percentage >= 50
  AND rating >= 4.3
  AND rating_count >= 10000
ORDER BY rating DESC, rating_count DESC
LIMIT 10;


-- ============================================================
-- STEP 7 : ADVANCED / BUSINESS QUERIES
-- ============================================================

-- Q20: Rank categories by total review volume (market engagement)
SELECT
    main_category,
    SUM(rating_count)                                                     AS total_reviews,
    RANK() OVER (ORDER BY SUM(rating_count) DESC)                        AS review_rank,
    ROUND(SUM(rating_count) * 100.0 / SUM(SUM(rating_count)) OVER (), 1) AS pct_of_total
FROM amazon_products
GROUP BY main_category;

-- Q21: Find the best performing product in each category
--      (highest rating_count within each category)
SELECT
    main_category,
    product_name,
    rating,
    rating_count,
    discounted_price,
    discount_percentage
FROM (
    SELECT *,
           RANK() OVER (PARTITION BY main_category ORDER BY rating_count DESC) AS rnk
    FROM amazon_products
) ranked
WHERE rnk = 1
ORDER BY rating_count DESC;

-- Q22: Monthly revenue estimate — price × estimated orders (rating_count proxy)
--      (Using rating_count as a sales volume proxy)
SELECT
    main_category,
    ROUND(SUM(discounted_price * rating_count) / 1000000, 2) AS estimated_revenue_crore,
    COUNT(*)                                                  AS product_count
FROM amazon_products
GROUP BY main_category
ORDER BY estimated_revenue_crore DESC;

-- Q23: Products where actual price and discounted price are the same (no real discount)
SELECT COUNT(*) AS no_discount_products
FROM amazon_products
WHERE actual_price = discounted_price
   OR discount_percentage = 0;

-- Q24: Average price and discount for products rated 4.5 and above
SELECT
    ROUND(AVG(actual_price), 2)        AS avg_price_high_rated,
    ROUND(AVG(discounted_price), 2)    AS avg_disc_price_high_rated,
    ROUND(AVG(discount_percentage), 2) AS avg_discount_high_rated,
    COUNT(*)                           AS product_count
FROM amazon_products
WHERE rating >= 4.5;

-- ============================================================
-- END OF ANALYSIS
-- ============================================================
