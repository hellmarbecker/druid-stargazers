-- Attempt to use a canvas by spreading out the months from min to max timestamp.
-- This fails because the equals join has been removed.
-- We get an error:
-- SQL requires a join with 'LESS_THAN_OR_EQUAL' condition that is not supported.

WITH 
  cte_calendar AS (
  SELECT DISTINCT TIME_FLOOR(t.dateByWeek, 'P1M') AS date_month
  FROM (
    SELECT
      TIMESTAMP_TO_MILLIS(TIME_FLOOR(MIN(__time), 'P1M')) AS minDate, 
      TIMESTAMP_TO_MILLIS(TIME_CEIL(MAX(__time), 'P1M')) AS maxDate
    FROM
      "stargazers-ecosystem"
    ),
    UNNEST(DATE_EXPAND(minDate, maxDate, 'P1W')) AS t(dateByWeek)
  ),
  cte_stars AS (
  SELECT 
    DATE_TRUNC('MONTH', "__time") AS date_month, 
    starred_repo, 
    COUNT(*) AS count_monthly
  FROM "stargazers-ecosystem"
  GROUP BY 1, 2
)
SELECT
  cte_calendar.date_month,
  cte_stars.starred_repo,
  SUM(cte_stars.count_monthly) AS sum_cume
FROM cte_calendar, cte_stars
WHERE cte_stars.date_month <= cte_calendar.date_month
GROUP BY 1, 2
ORDER BY 1, 2
