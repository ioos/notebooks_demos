#!/bin/bash

# Exit with nonzero exit code if anything fails.
set -e

# Save some useful information
REPO=$(git config remote.origin.url)
SSH_REPO=${REPO/https:\/\/github.com\//git@github.com:}

# Get the commit sha since gh-pages has no history.
SHA=$(git rev-parse --verify HEAD)

# Go to the out directory and create a *new* Git repo.
cd $GH_PAGES_DIR
git init

# Config the dummy git user.
git config user.name "Travis-CI"
git config user.email "$COMMIT_AUTHOR_EMAIL"

# The first and only commit to this new Git repo contains all the
# files present with the commit message "Deploy to GitHub Pages".
git add .
git commit -m "Deploy to GitHub Pages: ${SHA}"

# Get the deploy key by using Travis's stored variables to decrypt deploy_key.enc
ENCRYPTED_KEY_VAR="encrypted_${ENCRYPTION_LABEL}_key"
ENCRYPTED_IV_VAR="encrypted_${ENCRYPTION_LABEL}_iv"
ENCRYPTED_KEY=${!ENCRYPTED_KEY_VAR}
ENCRYPTED_IV=${!ENCRYPTED_IV_VAR}
openssl aes-256-cbc -K $ENCRYPTED_KEY -iv $ENCRYPTED_IV -in deploy_key.enc -out deploy_key -d
chmod 600 deploy_key
eval `ssh-agent -s`
ssh-add deploy_key

# Now that we're all set up, we can push.
git push --quiet --force $SSH_REPO gh-pages
