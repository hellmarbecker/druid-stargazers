-- Final query.
-- Create a canvas out of (month x repo) so we can do an inner join on repo,
-- and do the unbound preceding window in a filtered metric.

WITH 
  cte_calendar AS (
  SELECT 
    TIME_FLOOR(t.dateByWeek, 'P1M') AS date_month,
    starred_repo
  FROM (
    SELECT
      TIMESTAMP_TO_MILLIS(TIME_FLOOR(MIN(__time), 'P1M')) AS minDate, 
      TIMESTAMP_TO_MILLIS(TIME_CEIL(MAX(__time), 'P1M')) AS maxDate
    FROM
      "stargazers-ecosystem"
    ),
    UNNEST(DATE_EXPAND(minDate, maxDate, 'P1W')) AS t(dateByWeek),
    ( SELECT DISTINCT starred_repo FROM "stargazers-ecosystem" )
  GROUP BY 1, 2
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
  SUM(cte_stars.count_monthly) FILTER(WHERE cte_stars.date_month <= cte_calendar.date_month) AS sum_cume
FROM cte_calendar INNER JOIN cte_stars ON cte_calendar.starred_repo = cte_stars.starred_repo
GROUP BY 1, 2
ORDER BY 1, 2
