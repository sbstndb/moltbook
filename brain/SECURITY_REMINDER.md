# Security Reminder ⚠️

## API Key Exposure

⚠️ **NEVER commit API keys to public repos!**

If accidentally exposed:
- Check if service allows key regeneration
- Monitor account for suspicious activity
- Revoke old key if possible

## Mitigation

1. Check if Moltbook allows key regeneration
2. Monitor your agent activity on Moltbook
3. If suspicious activity, contact Moltbook support

## Prevention

- NEVER commit API keys, secrets, credentials
- Use .gitignore for sensitive files
- Review `git diff` before committing

## Safe to Commit

- CLAUDE.md (public profile info OK)
- MEMORY.md, TRENDING.md, etc. (no secrets)
- Code, configs (no API keys)

## NOT Safe to Commit

- API keys
- Passwords
- Tokens
- Private credentials
