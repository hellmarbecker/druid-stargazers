SELECT
  THETA_SKETCH_ESTIMATE(
    THETA_SKETCH_INTERSECT(
      DS_THETA(login) FILTER(WHERE starred_repo = 'apache/druid'),
      DS_THETA(login) FILTER(WHERE starred_repo = 'allegro/turnilo')))
FROM
  "stargazers-ecosystem"
