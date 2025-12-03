# Terminal Security Configuration

The web terminal runs with restricted permissions for enhanced security.

## Security Features

### User Isolation
- **Non-root execution**: Terminal runs as `hapuser` (UID 1001) instead of root
- **Isolated home directory**: User has access only to `/app/home`
- **No sudo access**: Cannot escalate privileges
- **Restricted groups**: No access to privileged groups

### Environment Restrictions
- **Limited PATH**: Only `/usr/local/bin:/usr/bin:/bin`
- **Removed dangerous variables**: No `SUDO_*`, `DOCKER_HOST`, `KUBECONFIG`, etc.
- **Restricted shell**: Can use restricted bash (`/bin/rbash`) if configured

### File System Restrictions
- **Limited write access**: Only to home directory
- **Restricted permissions**: Umask set to `027` (group and others have limited access)
- **No system file access**: Cannot modify system files

## Configuration

### Environment Variables

Set these in `docker-compose.yml` or `.env`:

```yaml
environment:
  - TERMINAL_USER=hapuser      # Terminal username
  - TERMINAL_UID=1001          # User ID
  - TERMINAL_GID=1001          # Group ID
  - TERMINAL_HOME=/app/home    # Home directory
  - RESTRICTED_SHELL=/bin/bash # Shell to use (/bin/rbash for restricted)
```

### User Setup

The terminal user is automatically created on container startup via `docker/setup_terminal_user.sh`.

Manual setup:
```bash
docker compose exec platform bash /app/docker/setup_terminal_user.sh
```

## Using Restricted Bash

For even more restrictions, use restricted bash:

1. Set `RESTRICTED_SHELL=/bin/rbash` in environment
2. Restricted bash prevents:
   - Changing directories (`cd` disabled)
   - Modifying PATH
   - Redirecting output (`>`, `>>`)
   - Using `/` in command names

## Customizing Restrictions

### Modify .bashrc

Edit `/app/home/.bashrc` in the container to add custom restrictions:

```bash
# Prevent dangerous commands
alias sudo='echo "sudo disabled"'
alias su='echo "su disabled"'
alias chmod='echo "chmod disabled"'
alias chown='echo "chown disabled"'
```

### Add Custom Commands

Place safe commands in `/app/home/bin/`:

```bash
# These will be in PATH
/app/home/bin/mycommand
```

## Security Best Practices

1. **Regular audits**: Review terminal logs regularly
2. **Monitor usage**: Track what commands are being run
3. **Update restrictions**: Adjust restrictions based on needs
4. **Limit access**: Use authentication/authorization (future feature)
5. **Log everything**: All terminal activity should be logged

## Troubleshooting

### Permission Denied Errors

If commands fail with permission errors:
- Check if command is in restricted PATH
- Verify user has access to required files
- Review umask settings

### User Creation Fails

If user creation fails:
- Ensure running as root in container
- Check UID/GID don't conflict
- Verify useradd is available

### Commands Not Found

If commands aren't found:
- Check PATH environment variable
- Verify command exists in allowed directories
- Add to `/app/home/bin/` if needed

## Future Enhancements

- [ ] Command whitelist/blacklist
- [ ] Session recording and audit logs
- [ ] Time-based access restrictions
- [ ] IP-based access control
- [ ] Command rate limiting
- [ ] Integration with platform authentication

