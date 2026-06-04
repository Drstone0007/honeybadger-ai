#!/bin/bash
# LinkedIn AI News: Fetch + Post via Interceptor
# Usage:
#   ./linkedin-post.sh              # Fetch news and post to LinkedIn
#   ./linkedin-post.sh --dry-run    # Fetch news and save to file (no post)
#
# Requirements:
#   - Interceptor Chrome extension installed and active
#   - LinkedIn account logged in

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data"

# Step 1: Fetch news
echo "Fetching AI news..."
python3 "$SCRIPT_DIR/linkedin_ai_news.py" --dry-run

if [ $? -ne 0 ]; then
    echo "Failed to fetch news"
    exit 1
fi

# Check if dry-run mode
if [ "$1" = "--dry-run" ]; then
    echo "Dry run complete. Post saved to $DATA_DIR/linkedin_post.txt"
    exit 0
fi

# Step 2: Check if interceptor is available
if ! command -v interceptor &> /dev/null; then
    echo "ERROR: interceptor not found"
    echo ""
    echo "To post to LinkedIn, install the Interceptor Chrome extension:"
    echo "  1. Open Chrome browser"
    echo "  2. Install Interceptor extension from Chrome Web Store"
    echo "  3. Log into LinkedIn in Chrome"
    echo "  4. Run this script again"
    echo ""
    echo "Post content saved to: $DATA_DIR/linkedin_post.txt"
    echo "You can copy/paste it manually to LinkedIn."
    exit 1
fi

# Step 3: Read the post content
POST_CONTENT=$(cat "$DATA_DIR/linkedin_post.txt")

if [ -z "$POST_CONTENT" ]; then
    echo "No post content found"
    exit 1
fi

echo "Opening LinkedIn..."
interceptor open "https://www.linkedin.com/feed/"

echo "Waiting for page to load..."
sleep 3

# Click "Start a post" button
echo "Clicking 'Start a post'..."
interceptor find "Start a post" --role button
sleep 2

# Find the text editor and type content
echo "Typing post content..."
interceptor scene insert "$POST_CONTENT"
sleep 2

# Click Post button
echo "Publishing post..."
interceptor find "Post" --role button
sleep 3

echo "Done! Post published to LinkedIn."
