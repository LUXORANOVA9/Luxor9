# 01_FEATURE_BRIEF.md
# Phase 1 — Initial Platform Architecture Scoping

**Status:** DRAFT — Phase 1 Architect output  
**Repository:** LUXORANOVA9/Luxor9  
**Branch:** phase-1/architecture-scoping-2026-10-07  
**Feature:** Initial Platform Architecture Scoping  
**Business purpose:** Define the foundational design requirements, target technology stack, service boundaries, data ownership, communication patterns, and jurisdictional compliance framework for a high-concurrency decentralized gaming platform.

## 1. Executive Summary

This phase establishes the platform constitution before implementation begins.

The connected repository is **not currently a gaming platform**. The inspected main branch contains an existing Luxor9 AI-agent application with:

- a Next.js 14 / React / TypeScript frontend;
- a Python / FastAPI backend;
- async SQLAlchemy + asyncpg against Neon PostgreSQL;
- Redis for cache/runtime coordination;
- WebSocket-based real-time task updates;
- an existing LLM router and agent/tool execution layer.

The requested target platform instead requires a Rust transaction-critical backend, Next.js/TypeScript experience layer, PostgreSQL financial source of truth, Redis for ephemeral state, an event backbone such as Kafka/Redpanda/NATS, and Solidity/Foundry for narrowly scoped blockchain settlement.

Therefore this phase adopts a two-plane evolution strategy:

1. Preserve the existing Luxor9 AI-agent application as the AI Engineering / Intelligence Plane while it remains useful.
2. Introduce a new Rust Transaction Plane for identity authorization, game commands, provably-fair computation, ledger mutations, settlement, and other deterministic financial workflows.
3. Integrate the planes through explicit typed APIs/events rather than allowing LLM-driven code paths to become financial authorities.

This is an architecture-scoping document, not authorization to launch or process real-money activity.

## 2. Scope

### In scope

- Platform-level system boundaries.
- Deterministic transaction architecture.
- Identity/compliance boundary.
- Game Engine boundary.
- Double-entry Ledger boundary.
- Risk/Fraud boundary.
- Wallet/Payments boundary.
- Blockchain/treasury boundary.
- Event-driven communication.
- Core domain schemas and ownership.
- Idempotency and audit requirements.
- Jurisdiction-policy architecture.
- Migration boundary between the existing Luxor9 application and the proposed gaming transaction plane.
- Phase-1 exit criteria.

### Out of scope

- Production gambling operations.
- Mainnet smart-contract deployment.
- Live payment-provider credentials.
- KYC/AML provider procurement.
- Final legal opinions.
- Specific licensed-jurisdiction authorization.
- Game-specific mathematical specifications beyond interface requirements.
- Production treasury keys.
- Autonomous AI control of money, compliance, or deployments.

## 3. Compliance Position

The platform must be jurisdiction-aware from its first executable request path.

India is not a viable default launch jurisdiction for an online-money-gaming product under the current 2025 Act and 2026 Rules. The Promotion and Regulation of Online Gaming Act, 2025 prohibits online money games and also prohibits their offering, facilitation, advertising and related financial processing in the circumstances covered by the Act. The 2026 Rules entered into force on 1 May 2026.

Therefore:

- India must be represented as a prohibited policy state for online-money gaming unless authoritative legal/compliance review establishes otherwise for a specific future product classification.
- The system must not attempt to evade Indian restrictions through offshore hosting, crypto-only payments, VPN handling, domain changes, or similar technical workarounds.
- The product may be architected for a properly licensed jurisdiction or for a non-money/social/e-sports model.
- Jurisdiction policy must be data-driven and versioned, not hard-coded across services.

## 4. Product Constitution

The following invariants are non-negotiable:

1. Deterministic systems are authoritative.
2. LLM responses are never the source of truth for balances, bet outcomes, KYC/AML status, sanctions decisions, jurisdiction eligibility, or production authorization.
3. No monetary calculation uses binary floating-point arithmetic.
4. Every financial mutation is idempotent.
5. The ledger is immutable and double-entry.
6. Every privileged action is attributable and auditable.
7. External callbacks/webhooks must be authenticated, validated, replay-safe and idempotent.
8. Game outcomes must be reproducible from recorded cryptographic inputs.
9. Risk AI may recommend; policy engines and humans determine high-impact actions.
10. No agent may autonomously release/transfer treasury funds or deploy privileged production infrastructure.
11. Blockchain state is a settlement/audit mechanism where appropriate, not a replacement for the authoritative financial ledger.
12. Failure recovery must preserve monetary and audit invariants.

## 5. Target System Shape

### Experience Plane

- Next.js
- React
- TypeScript
- WebSocket/SSE
- typed API client
- wallet integration where permitted

### Transaction Plane

- Rust
- Tokio
- Axum/gRPC
- PostgreSQL
- exact integer/fixed-point monetary types
- deterministic game engine
- double-entry ledger
- idempotency service

### Intelligence Plane

- Existing Luxor9 agent framework
- Claude-powered development/operations agents
- risk analysis
- fraud investigation
- support
- SRE analysis
- documentation

AI remains a bounded advisory/control-assistance layer.

### Settlement Plane

- Solidity
- Foundry
- OpenZeppelin
- Safe multisig
- chain indexer
- narrowly scoped settlement contracts

### Data Plane

- PostgreSQL: transactional source of truth
- Redis: ephemeral/cache/coordination
- Kafka/Redpanda/NATS: durable event propagation
- ClickHouse or equivalent analytics store later
- object storage for evidence/artifacts later

## 6. Primary Business Domains

| Domain | Owner | Authoritative store |
|---|---|---|
| Identity | Identity Service | PostgreSQL |
| KYC/AML state | Compliance Service + external providers | PostgreSQL + provider evidence |
| Jurisdiction | Policy Service | Versioned policy configuration |
| Game definition | Game Catalog | PostgreSQL |
| Game execution | Game Engine | Deterministic computation + execution records |
| Bet lifecycle | Betting Service | PostgreSQL |
| Financial accounting | Ledger Service | PostgreSQL journal |
| Payments | Payment Service | PostgreSQL + provider/chain evidence |
| Risk | Risk Service | PostgreSQL/event stream + analytics |
| Treasury | Treasury Service + multisig | Multisig/on-chain + reconciliation ledger |
| AI decisions | AI Control Plane | Audit/event store |
| User-visible state | Frontend | Never authoritative |

## 7. Initial Core Schemas

Phase 1 does not implement migrations yet, but these are the canonical logical entities.

### Identity

- users
- credentials
- sessions
- devices
- identities
- kyc_cases
- aml_cases
- jurisdiction_assignments
- responsible_gaming_profiles
- account_restrictions

### Financial

- ledger_accounts
- ledger_transactions
- ledger_entries
- balance_holds
- idempotency_keys
- reconciliation_runs

### Gaming

- games
- game_versions
- game_configs
- betting_sessions
- bets
- bet_outcomes
- fairness_commitments

### Payments

- payment_accounts
- deposit_intents
- deposits
- withdrawal_requests
- blockchain_transactions
- payment_webhook_events

### Risk

- risk_events
- risk_features
- risk_scores
- risk_cases
- risk_decisions
- risk_evidence

### Audit

- audit_events
- privileged_actions
- agent_actions
- policy_decisions

All financial/compliance records must carry stable identifiers and correlation references where applicable.

## 8. Core Communication Principle

The hot path must be deterministic and narrow.

### Bet command concept

Client -> API Gateway -> Eligibility/Policy -> Risk Pre-check -> Ledger Reservation -> Game Engine -> Settlement -> Ledger Commit -> Event Bus

AI is not inserted between a user click and a financial truth decision.

### Risk concept

Domain Event -> Feature Extraction -> Rules/Models -> Risk Recommendation -> Deterministic Policy -> Human escalation when required

### AI concept

Evidence -> Agent -> Recommendation -> Policy/Validation -> Authorized action

## 9. Phase-1 Architecture Decisions

### ADR-001 — Separate Transaction Plane from AI Plane

The current Python/FastAPI application remains outside the financial trust boundary until explicitly re-engineered and reviewed.

The new Rust services become the transaction-critical boundary.

### ADR-002 — PostgreSQL is Financial Truth

Balances are derived from an immutable double-entry journal. Redis, event-stream offsets, browser state and LLM output are not authoritative.

### ADR-003 — Event-Driven Side Effects

Financial commands commit transactionally first; downstream analytics, notifications and risk enrichment consume events.

### ADR-004 — Policy Engine Owns Eligibility

Jurisdiction, responsible gaming and compliance decisions are versioned deterministic policies.

### ADR-005 — Blockchain is Settlement/Proof Infrastructure

Use blockchain where it adds custody, settlement or independently verifiable evidence. Do not put the entire high-concurrency game loop on-chain.

## 10. Phase-1 Deliverables

This phase delivers:

- 01_FEATURE_BRIEF.md
- 02_ARCHITECTURE.md

No production code is authorized by these documents.

## 11. Exit Condition

Phase 1 is complete only when a human reviewer confirms:

- architecture boundaries are accepted;
- jurisdiction strategy is accepted;
- deterministic-vs-AI separation is accepted;
- schema ownership is accepted;
- communication pattern is accepted;
- current repository vs target-stack migration boundary is accepted;
- no production deployment or financial integration is implied by the phase.

**Approval status: PENDING HUMAN REVIEW**
