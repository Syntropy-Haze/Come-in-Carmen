#!/bin/bash

# LES AFR TRANSMISSION SCRIPT
# Add a new transmission to the void

# Colors for terminal output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
JSON_FILE="$SCRIPT_DIR/transmissions.json"

# Check if message is provided
if [ -z "$1" ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          LES AFR TRANSMISSION PROTOCOL v1.0                ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Usage: ./add-transmission.sh \"YOUR MESSAGE\" [SOURCE]"
    echo ""
    echo "Examples:"
    echo "  ./add-transmission.sh \"PROTOCOL ACTIVE\""
    echo "  ./add-transmission.sh \"SYNTROPY DETECTED\" \"QUEBEC-NODE\""
    echo ""
    exit 1
fi

MESSAGE="$1"
SOURCE="${2:-null}"

# Generate timestamp in ISO format
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Create the new transmission JSON
if [ "$SOURCE" == "null" ]; then
    NEW_TRANSMISSION=$(cat <<EOF
    {
      "timestamp": "$TIMESTAMP",
      "source": null,
      "message": "$MESSAGE"
    }
EOF
)
else
    NEW_TRANSMISSION=$(cat <<EOF
    {
      "timestamp": "$TIMESTAMP",
      "source": "$SOURCE",
      "message": "$MESSAGE"
    }
EOF
)
fi

# Check if jq is available for proper JSON manipulation
if command -v jq &> /dev/null; then
    # Use jq for proper JSON handling
    TEMP_FILE=$(mktemp)
    jq --argjson new "$NEW_TRANSMISSION" '.transmissions += [$new]' "$JSON_FILE" > "$TEMP_FILE"
    mv "$TEMP_FILE" "$JSON_FILE"
else
    # Fallback: manual JSON manipulation (less safe but works)
    # Remove the last ] and closing brace, add new transmission, close again
    TEMP_FILE=$(mktemp)
    head -n -2 "$JSON_FILE" > "$TEMP_FILE"
    echo "    ," >> "$TEMP_FILE"
    echo "$NEW_TRANSMISSION" >> "$TEMP_FILE"
    echo "  ]" >> "$TEMP_FILE"
    echo "}" >> "$TEMP_FILE"
    mv "$TEMP_FILE" "$JSON_FILE"
fi

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ⚡ TRANSMISSION RECEIVED ⚡                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "Timestamp: $TIMESTAMP"
echo "Source:    ${SOURCE}"
echo "Message:   $MESSAGE"
echo ""
echo -e "${GREEN}+++ ADDED TO THE VOID +++${NC}"
echo ""
echo "Next steps:"
echo "  1. Review: cat transmissions.json"
echo "  2. Commit: git add transmissions.json && git commit -m \"New transmission\""
echo "  3. Push:   git push"
echo ""
