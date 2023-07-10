-- This fails with an error:
-- Error: Unsupported operation
-- Cannot convert to Duration as this period contains months and months vary in length

SELECT t.dateByWeek 
FROM (
  SELECT
    TIMESTAMP_TO_MILLIS(TIME_FLOOR(MIN(__time), 'P1M')) AS minDate, 
    TIMESTAMP_TO_MILLIS(TIME_CEIL(MAX(__time), 'P1M')) AS maxDate
  FROM
    "stargazers-ecosystem"
  ),
  UNNEST(DATE_EXPAND(minDate, maxDate, 'P1M')) AS t(dateByWeek)
