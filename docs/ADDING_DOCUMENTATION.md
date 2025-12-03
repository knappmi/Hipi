# Adding Documentation

## Automatic Detection

**Yes!** New documentation files are automatically detected and added to the UI.

### How It Works

1. **Dynamic Scanning**: The documentation index page (`/docs`) automatically scans the `docs/` directory every time it's accessed
2. **No Restart Required**: New `.md` files appear immediately without restarting the platform
3. **Automatic Listing**: All markdown files (`.md`) in the `docs/` directory are automatically listed

### Adding New Documentation

1. **Create a Markdown File**: Add a new `.md` file to the `docs/` directory
   ```bash
   # Example
   touch docs/MY_NEW_FEATURE.md
   ```

2. **Write Your Documentation**: Use standard Markdown syntax
   ```markdown
   # My New Feature
   
   This is documentation for my new feature.
   
   ## Features
   - Feature 1
   - Feature 2
   ```

3. **Access in UI**: The file will automatically appear in the documentation index at `/docs`

### File Naming

- Use descriptive names: `FEATURE_NAME.md`
- Use underscores for spaces: `MY_NEW_FEATURE.md` (displays as "My New Feature")
- The system automatically formats names for display

### Supported Markdown Features

- Headers (`#`, `##`, `###`)
- Code blocks with syntax highlighting
- Tables
- Lists (ordered and unordered)
- Links
- Images
- Blockquotes
- And all standard Markdown features

### Excluded Files

- `README.md` in the `docs/` directory is excluded from the index (it's the documentation index itself)
- Only `.md` files are included

### Best Practices

1. **Start with a Title**: Use `# Title` at the top
2. **Add Sections**: Use `## Section` for major sections
3. **Include Examples**: Add code examples with syntax highlighting
4. **Link Related Docs**: Link to related documentation files
5. **Keep It Updated**: Update docs when features change

### Example Structure

```markdown
# Feature Name

Brief description of the feature.

## Overview

Detailed overview...

## Usage

How to use the feature...

## API Endpoints

- `GET /api/v1/feature` - Get feature data
- `POST /api/v1/feature` - Create feature

## Examples

\`\`\`bash
curl http://localhost:8000/api/v1/feature
\`\`\`

## Related Documentation

- [Related Feature](RELATED_FEATURE.md)
- [Quick Reference](QUICK_REFERENCE.md)
```

### Accessing Documentation

- **Web UI**: http://localhost:5000/docs
- **Individual Docs**: http://localhost:5000/docs/FILENAME.md
- **Navigation**: Click "Documentation" in the main menu

### Troubleshooting

**Document not appearing?**
- Check the file is in the `docs/` directory
- Verify it has a `.md` extension
- Ensure the file is readable
- Refresh the `/docs` page

**Document not rendering correctly?**
- Check Markdown syntax
- Verify code blocks are properly formatted
- Check for special characters that might break rendering

