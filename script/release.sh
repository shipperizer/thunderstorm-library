#!/bin/bash

GITHUB_ORG=$1
GITHUB_REPO=$2

PR_NUMBER=$(git log --merges -1 | grep -Eo '#[0-9]+' | sed 's/#//g')
GITHUB_URL="https://api.github.com/repos/$GITHUB_ORG/${GITHUB_REPO}/pulls/${PR_NUMBER}"


VERSION="v$(python setup.py --version)"
TAG="v${VERSION}"

git remote set-url origin git@github.com:${GITHUB_ORG}/${GITHUB_REPO}.git
git tag -f $TAG
git push --tags


# Create release
curl -s -H "Authorization: token ${GITHUB_TOKEN}" ${GITHUB_URL} \
  | jq -r '.body' \
  | github-release release \
    -u $GITHUB_ORG -r $GITHUB_REPO -t $TAG -d -

# Upload package
github-release upload \
  -u $GITHUB_ORG -r $GITHUB_REPO -t $TAG \
  -n "thunderstorm-library-${VERSION}.tar.gz" \
  -f "dist/thunderstorm-library-${VERSION}.tar.gz"
