-- Naive approach with a self join
-- Truncate and aggregate by month to limit result sets
-- This does not work when there are months that have no star for a repository

WITH cte AS (
  SELECT DATE_TRUNC('MONTH', "__time") AS date_month, starred_repo, COUNT(*) AS count_monthly
  FROM "stargazers-ecosystem"
  GROUP BY 1, 2
)
SELECT
  cte.date_month,
  cte.starred_repo,
  SUM(t2.count_monthly) AS sum_cume
FROM cte INNER JOIN cte t2 ON cte.starred_repo = t2.starred_repo
WHERE t2.date_month <= cte.date_month
GROUP BY 1, 2
ORDER BY 1, 2
