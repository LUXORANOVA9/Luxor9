#!/bin/bash

# Package Creation Script for LUXORANOVA9 Monorepo
# Usage: ./create-package.sh <category> <package-name>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check arguments
if [ $# -ne 2 ]; then
    print_error "Usage: $0 <category> <package-name>"
    print_info "Categories: ai, saas, tools, frameworks, notebooks, demos, infrastructure, shared"
    exit 1
fi

CATEGORY=$1
PACKAGE_NAME=$2
PACKAGE_PATH="packages/${CATEGORY}/${PACKAGE_NAME}"

# Validate category
case $CATEGORY in
    ai|saas|tools|frameworks|notebooks|demos|infrastructure|shared)
        print_info "Creating ${CATEGORY} package: ${PACKAGE_NAME}"
        ;;
    *)
        print_error "Invalid category: ${CATEGORY}"
        print_info "Valid categories: ai, saas, tools, frameworks, notebooks, demos, infrastructure, shared"
        exit 1
        ;;
esac

# Check if package already exists
if [ -d "$PACKAGE_PATH" ]; then
    print_error "Package already exists: ${PACKAGE_PATH}"
    exit 1
fi

# Create package directory
mkdir -p "$PACKAGE_PATH"

# Create basic directory structure
mkdir -p "${PACKAGE_PATH}/src"
mkdir -p "${PACKAGE_PATH}/tests/unit"
mkdir -p "${PACKAGE_PATH}/tests/integration"
mkdir -p "${PACKAGE_PATH}/tests/__fixtures__"
mkdir -p "${PACKAGE_PATH}/docs"

# Create category-specific directories
case $CATEGORY in
    ai)
        mkdir -p "${PACKAGE_PATH}/src/lib"
        mkdir -p "${PACKAGE_PATH}/src/utils"
        mkdir -p "${PACKAGE_PATH}/src/types"
        ;;
    saas)
        mkdir -p "${PACKAGE_PATH}/src/api"
        mkdir -p "${PACKAGE_PATH}/src/services"
        mkdir -p "${PACKAGE_PATH}/src/models"
        mkdir -p "${PACKAGE_PATH}/src/middleware"
        mkdir -p "${PACKAGE_PATH}/src/config"
        mkdir -p "${PACKAGE_PATH}/src/utils"
        mkdir -p "${PACKAGE_PATH}/src/types"
        mkdir -p "${PACKAGE_PATH}/tests/e2e"
        mkdir -p "${PACKAGE_PATH}/public"
        ;;
    tools)
        mkdir -p "${PACKAGE_PATH}/src/cli"
        mkdir -p "${PACKAGE_PATH}/src/lib"
        mkdir -p "${PACKAGE_PATH}/src/utils"
        mkdir -p "${PACKAGE_PATH}/src/types"
        mkdir -p "${PACKAGE_PATH}/bin"
        ;;
    frameworks)
        mkdir -p "${PACKAGE_PATH}/src/core"
        mkdir -p "${PACKAGE_PATH}/src/plugins"
        mkdir -p "${PACKAGE_PATH}/src/utils"
        mkdir -p "${PACKAGE_PATH}/src/types"
        mkdir -p "${PACKAGE_PATH}/examples"
        ;;
    notebooks)
        mkdir -p "${PACKAGE_PATH}/notebooks"
        ;;
    *)
        mkdir -p "${PACKAGE_PATH}/src/lib"
        mkdir -p "${PACKAGE_PATH}/src/utils"
        ;;
esac

# Generate package.json
cat > "${PACKAGE_PATH}/package.json" << EOF
{
  "name": "@luxoranova9/${PACKAGE_NAME}",
  "version": "1.0.0",
  "description": "Generated ${CATEGORY} package",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "dev": "tsc --watch",
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "lint": "eslint src/**/*.ts",
    "lint:fix": "eslint src/**/*.ts --fix",
    "clean": "rm -rf dist coverage"
  },
  "keywords": [
    "${CATEGORY}",
    "luxoranova9"
  ],
  "author": "LUXORANOVA9",
  "license": "Apache-2.0",
  "repository": {
    "type": "git",
    "url": "https://github.com/LUXORANOVA9/Luxor9.git",
    "directory": "packages/${CATEGORY}/${PACKAGE_NAME}"
  },
  "devDependencies": {
    "@luxoranova9/eslint-config": "^1.0.0",
    "@luxoranova9/jest-config": "^1.0.0",
    "@luxoranova9/typescript-config": "^1.0.0",
    "@types/jest": "^29.0.0",
    "@types/node": "^18.0.0",
    "eslint": "^8.0.0",
    "jest": "^29.0.0",
    "prettier": "^3.0.0",
    "typescript": "^5.0.0"
  },
  "dependencies": {},
  "files": [
    "dist/",
    "README.md"
  ]
}
EOF

# Add SaaS-specific dependencies
if [ "$CATEGORY" == "saas" ]; then
    # Add ts-node for development
    sed -i 's/"typescript": "^5.0.0"/"typescript": "^5.0.0",\n    "ts-node": "^10.0.0"/' "${PACKAGE_PATH}/package.json"
    # Add start scripts
    sed -i 's/"dev": "tsc --watch",/"dev": "tsc --watch",\n    "start": "node dist\/index.js",\n    "start:dev": "ts-node src\/index.ts",/' "${PACKAGE_PATH}/package.json"
fi

# Add tools-specific dependencies
if [ "$CATEGORY" == "tools" ]; then
    # Add bin field
    sed -i 's/"main": "dist\/index.js",/"main": "dist\/index.js",\n  "bin": {\n    "'${PACKAGE_NAME}'": "bin\/'${PACKAGE_NAME}'"\n  },/' "${PACKAGE_PATH}/package.json"
fi

# Generate TypeScript config
cat > "${PACKAGE_PATH}/tsconfig.json" << EOF
{
  "extends": "@luxoranova9/typescript-config/base.json",
  "compilerOptions": {
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": [
    "src/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "**/*.test.ts",
    "**/*.spec.ts"
  ]
}
EOF

# Generate ESLint config
cat > "${PACKAGE_PATH}/.eslintrc.js" << EOF
module.exports = {
  extends: '@luxoranova9/eslint-config'
};
EOF

# Generate Jest config
cat > "${PACKAGE_PATH}/jest.config.js" << EOF
const baseConfig = require('@luxoranova9/jest-config');

module.exports = {
  ...baseConfig
};
EOF

# Generate main index file
cat > "${PACKAGE_PATH}/src/index.ts" << EOF
/**
 * Main entry point for ${PACKAGE_NAME}
 */

// Export your main functionality here
export const name = '${PACKAGE_NAME}';
export const version = '1.0.0';
EOF

# Generate README
cat > "${PACKAGE_PATH}/README.md" << EOF
# ${PACKAGE_NAME}

A ${CATEGORY} package in the LUXORANOVA9 monorepo.

## Installation

\`\`\`bash
npm install @luxoranova9/${PACKAGE_NAME}
\`\`\`

## Usage

\`\`\`typescript
import { name } from '@luxoranova9/${PACKAGE_NAME}';

console.log(name); // '${PACKAGE_NAME}'
\`\`\`

## Development

\`\`\`bash
# Install dependencies
npm install

# Build the package
npm run build

# Run tests
npm test

# Run in development mode
npm run dev
\`\`\`

## Scripts

- \`npm run build\` - Build the package
- \`npm run dev\` - Start development mode with watch
- \`npm test\` - Run tests
- \`npm run test:watch\` - Run tests in watch mode
- \`npm run test:coverage\` - Run tests with coverage
- \`npm run lint\` - Lint the code
- \`npm run lint:fix\` - Lint and fix the code
- \`npm run clean\` - Clean build artifacts

## Contributing

Please read the monorepo [CONTRIBUTING.md](../../CONTRIBUTING.md) for development guidelines.
EOF

# Create a basic test
cat > "${PACKAGE_PATH}/tests/unit/index.test.ts" << EOF
import { name, version } from '../../src';

describe('${PACKAGE_NAME}', () => {
  it('should export package name', () => {
    expect(name).toBe('${PACKAGE_NAME}');
  });

  it('should export version', () => {
    expect(version).toBe('1.0.0');
  });
});
EOF

print_info "Package created successfully at: ${PACKAGE_PATH}"
print_info "Next steps:"
echo "  1. cd ${PACKAGE_PATH}"
echo "  2. npm install"
echo "  3. npm run build"
echo "  4. npm test"

# Add to workspace if not already included
if ! grep -q "packages/${CATEGORY}/\*" package.json; then
    print_warning "Don't forget to add 'packages/${CATEGORY}/*' to the workspaces in package.json"
fi