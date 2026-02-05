#!/bin/bash
# Quick setup script for ClaudeCode_GLM4_7 on any machine

echo "🦞 Setting up ClaudeCode_GLM4_7..."

# Clone repo
if [ ! -d ~/moltbook ]; then
    git clone git@github.com:sbstndb/moltbook.git ~/moltbook
    echo "✅ Repo cloned"
else
    echo "⚠️  ~/moltbook already exists"
fi

# Create credentials folder
mkdir -p ~/.config/moltbook

# Prompt for API key
if [ ! -f ~/.config/moltbook/credentials.json ]; then
    echo ""
    echo "Enter your Moltbook API key (moltbook_sk_...):"
    read -r API_KEY
    cat > ~/.config/moltbook/credentials.json << CREDS
{
  "api_key": "$API_KEY",
  "agent_name": "ClaudeCode_GLM4_7"
}
CREDS
    echo "✅ Credentials saved"
else
    echo "⚠️  Credentials already exist"
fi

# Test
echo ""
echo "🧪 Testing API access..."
RESPONSE=$(curl -s "https://www.moltbook.com/api/v1/agents/me" \
  -H "Authorization: Bearer $(jq -r .api_key ~/.config/moltbook/credentials.json)")

if echo "$RESPONSE" | grep -q "success"; then
    echo "✅ Setup successful!"
    echo ""
    echo "📝 When starting Claude, say:"
    echo "   Read ~/moltbook/CLAUDE.md"
else
    echo "❌ API test failed. Check your API key."
fi
