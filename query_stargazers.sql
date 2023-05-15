SELECT
  "__time",
  "user.login",
  "user.avatar_url",
  "user.bio",
  "user.blog",
  "user.company",
  "user.created_at",
  "user.email",
  "user.events_url",
  "user.followers",
  "user.followers_url",
  "user.following",
  "user.following_url",
  "user.gists_url",
  "user.gravatar_id",
  "user.hireable",
  "user.html_url",
  "user.id",
  "user.location",
  "user.name",
  "user.node_id",
  "user.organizations_url",
  "user.public_gists",
  "user.public_repos",
  "user.received_events_url",
  "user.repos_url",
  "user.site_admin",
  "user.starred_url",
  "user.subscriptions_url",
  "user.twitter_username",
  "user.type",
  "user.updated_at",
  "user.url",
  "user",
  "starred_repo",
  "other_repo"
FROM "stargazers_enriched", UNNEST(MV_TO_ARRAY(other_starred_repos)) AS t(other_repo)