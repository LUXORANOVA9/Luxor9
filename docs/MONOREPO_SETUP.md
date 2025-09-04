# LUXORANOVA9 Monorepo Setup Guide

## Overview

This guide covers the complete setup and migration of repositories to the LUXORANOVA9 monorepo with shared configurations, testing frameworks, CI/CD pipelines, and deployment strategies.

## Package Creation

### Using the Package Creation Script

Create new packages using the provided script:

```bash
# Create an AI package
npm run create:package ai my-ai-package

# Create a SaaS application
npm run create:package saas my-saas-app

# Create a development tool
npm run create:package tools my-tool
```

## Development Workflow

### Initial Setup
```bash
# Clone repository
git clone https://github.com/LUXORANOVA9/Luxor9.git
cd Luxor9

# Install dependencies and bootstrap
npm run bootstrap
```

### Working with Packages
```bash
# Build all packages
npm run build

# Test all packages
npm run test

# Lint all packages
npm run lint
```

## Shared Configurations

- **ESLint Configuration**: `@luxoranova9/eslint-config`
- **Jest Configuration**: `@luxoranova9/jest-config`
- **TypeScript Configuration**: `@luxoranova9/typescript-config`
- **Shared Utilities**: `@luxoranova9/utils`

## CI/CD Pipeline

The monorepo includes package-specific CI/CD that only runs tests for changed packages, optimizing build times.

For complete documentation, see the full setup guide.