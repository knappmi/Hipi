#!/bin/bash
# Script to connect local Hipi repository to GitHub
# 
# Instructions:
# 1. Go to https://github.com and create a new repository named "Hipi"
# 2. Do NOT initialize it with README, .gitignore, or license
# 3. Run this script: bash setup_github.sh

echo "Setting up GitHub remote for Hipi repository..."

# Replace 'YOUR_USERNAME' with your actual GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

# Add the remote (adjust URL format if using SSH)
git remote add origin https://github.com/${GITHUB_USERNAME}/Hipi.git

# Verify the remote was added
echo ""
echo "Remote added. Current remotes:"
git remote -v

echo ""
echo "Ready to push! Run the following commands:"
echo "  git push -u origin main"
echo ""
echo "Or if you prefer SSH (if you have SSH keys set up):"
echo "  git remote set-url origin git@github.com:${GITHUB_USERNAME}/Hipi.git"
echo "  git push -u origin main"

