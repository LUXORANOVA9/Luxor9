# Package Templates

This directory contains starter templates for creating new packages in each category of the LUXORANOVA9 monorepo. Copy a template into the appropriate `packages/<category>/` folder and customize the files for your project.

## Usage

```bash
# Replace <template> with one of: ai, saas, tools, frameworks, notebooks, demos, infrastructure
# Replace <category> with the matching packages subfolder
# Replace <package-name> with your new package directory name
cp -r packages/shared/templates/<template> packages/<category>/<package-name>
cd packages/<category>/<package-name>
# Update package.json, README.md, and source files as needed
```

## Templates Available

- `ai/` – Template for AI and machine learning libraries (`packages/ai/`)
- `saas/` – Template for SaaS applications and backend services (`packages/saas/`)
- `tools/` – Template for developer tooling and CLIs (`packages/tools/`)
- `frameworks/` – Template for framework and platform layers (`packages/frameworks/`)
- `notebooks/` – Template for research helpers and notebook companions (`packages/notebooks/`)
- `demos/` – Template for demos and proof-of-concept experiences (`packages/demos/`)
- `infrastructure/` – Template for infrastructure and DevOps tooling (`packages/infrastructure/`)

Each template includes:

- `README.md` with category-specific guidance
- `package.json` configured with shared scripts and placeholder metadata
- `tsconfig.json` extending the shared TypeScript configuration
- `jest.config.js` extending the shared Jest configuration
- `src/` directory with an `index.ts` export placeholder

Refer to the monorepo [CONTRIBUTING.md](../../CONTRIBUTING.md) for additional guidance when creating new packages.
