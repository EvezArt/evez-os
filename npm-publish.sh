#!/bin/bash
# Publish eigenforensics to npm
# Requires: npm login (npm adduser)
# Run: bash npm-publish.sh

cd /tmp/evez-npm
npm publish
echo "Published to npm: https://www.npmjs.com/package/eigenforensics"
