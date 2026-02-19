# Makefile — Luxor9 Free Cloud Stack

.PHONY: dev build deploy setup sandbox-image logs clean

# ════════════════════════════
# LOCAL DEVELOPMENT
# ════════════════════════════

# Dev mode — backend hot-reload + frontend dev server
dev:
	@echo "🚀 Starting Luxor9 dev environment..."
	docker compose up -d redis
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
	cd frontend && npm run dev

# Build backend image locally
build:
	docker compose build backend

# ════════════════════════════
# DEPLOYMENT (Render + Vercel)
# ════════════════════════════

# Deploy backend to Render (via webhook)
deploy:
	@echo "🚀 Deploying to Render..."
	@curl -s -X POST "$(RENDER_DEPLOY_HOOK)" && echo " ✅ Backend deploy triggered"
	@echo "🎨 Frontend auto-deploys via Vercel on git push"

# ════════════════════════════
# SETUP
# ════════════════════════════

# First-time setup
setup: sandbox-image
	cd frontend && npm install
	@echo ""
	@echo "✅ Setup complete!"
	@echo "   1. Copy .env.example → .env and fill in API keys"
	@echo "   2. Run neon-schema.sql in your Neon SQL editor"
	@echo "   3. Run 'make dev' to start locally"

# Build sandbox image
sandbox-image:
	docker build -t luxor9-sandbox:latest ./sandbox-image

# ════════════════════════════
# UTILITIES
# ════════════════════════════

# Backend logs (docker)
logs:
	docker compose logs -f backend

# Clean up
clean:
	docker compose down -v
	@echo "🧹 Cleaned"
