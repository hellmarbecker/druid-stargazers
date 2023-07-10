-- Create a canvas / calendar dimension with month granularity.
-- Need to use date_expand with weekly and then truncate

SELECT DISTINCT TIME_FLOOR(t.dateByWeek, 'P1M') 
FROM (
  SELECT
    TIMESTAMP_TO_MILLIS(TIME_FLOOR(MIN(__time), 'P1M')) AS minDate, 
    TIMESTAMP_TO_MILLIS(TIME_CEIL(MAX(__time), 'P1M')) AS maxDate
  FROM
    "stargazers-ecosystem"
  ),
  UNNEST(DATE_EXPAND(minDate, maxDate, 'P1W')) AS t(dateByWeek)
