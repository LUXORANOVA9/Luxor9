# Package Templates

This directory contains templates for creating new packages in each category of the LUXORANOVA9 monorepo.

## Usage

To create a new package, copy the appropriate template directory and customize it:

```bash
# For an AI package
cp -r packages/shared/templates/ai packages/ai/my-new-ai-package
cd packages/ai/my-new-ai-package
# Edit package.json to update name, description, etc.
```

## Templates Available

- `ai/` - Template for AI and Machine Learning packages
- `saas/` - Template for SaaS applications
- `tools/` - Template for development tools
- `frameworks/` - Template for frameworks and platforms
- `notebooks/` - Template for Jupyter notebooks and research
- `demos/` - Template for demo applications
- `infrastructure/` - Template for infrastructure and DevOps