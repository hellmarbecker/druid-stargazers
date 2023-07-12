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
