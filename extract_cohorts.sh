#!/bin/bash

jq '[ ., inputs | { starred_at, login: .user.login, starred_repo } ] | group_by(.login) | [ .[] | { login: .[0].login, repos: [ .[] | .starred_repo ] | sort } ]' multi_repo_20230710-01.json
