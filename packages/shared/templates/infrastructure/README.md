# Infrastructure Package Template

A template for provisioning, automation, and DevOps tooling within the LUXORANOVA9 monorepo.

## Quick Start

```bash
npm install
npm run build
npm test
```

## Scripts

- `npm run build` - Build the package
- `npm run dev` - Start development mode with watch
- `npm test` - Run tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Run tests with coverage
- `npm run lint` - Lint the code
- `npm run lint:fix` - Lint and fix the code
- `npm run clean` - Clean build artifacts

## Directory Structure

```
src/                  # Infrastructure code, IaC definitions, or automation
├── index.ts         # Entry point exporting reusable modules
└── ...              # Add deployment scripts, providers, or helpers

tests/               # Validate automation logic and guardrails

docs/                # Document environments and operational runbooks
```

## Development

This package uses the shared LUXORANOVA9 configurations:
- ESLint configuration from `@luxoranova9/eslint-config`
- Jest configuration from `@luxoranova9/jest-config`
- TypeScript configuration from `@luxoranova9/typescript-config`

## Contributing

Please read the monorepo [CONTRIBUTING.md](../../../CONTRIBUTING.md) for development guidelines.
