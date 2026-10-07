# 02_ARCHITECTURE.md
# Phase 1 — Initial Platform Architecture

**Status:** DRAFT — Architect output  
**Repository:** LUXORANOVA9/Luxor9  
**Branch:** phase-1/architecture-scoping-2026-10-07

## 1. Repository Inspection Snapshot

The connected repository was inspected before producing this architecture.

### Observed current architecture

At the inspected main snapshot:

- Backend: Python / FastAPI
- Database access: async SQLAlchemy + asyncpg
- Database: Neon PostgreSQL
- Cache/runtime: Redis
- Frontend: Next.js 14.2 / React 18 / TypeScript
- Styling: Tailwind CSS
- Real-time: WebSockets
- Agent layer: existing LLM router + tool execution
- Containerization: Docker / docker-compose
- Existing database models include tasks, agent_turns, and memories.

The current backend also exposes an existing agent/tool execution surface, so this repository already has an AI control/application layer. It must not automatically inherit financial authority.

### Important target-state delta

Requested target:
- Rust transaction backend
- Next.js/TypeScript frontend
- PostgreSQL
- Redis
- Kafka/Redpanda/NATS
- Solidity/Foundry

Therefore the architecture is a target-state extension/evolution, not a claim that the current codebase already implements these components.

The recommended first implementation path is:

existing Luxor9 AI platform
+
new Rust deterministic transaction plane
+
shared typed contracts/events

rather than rewriting the existing application blindly.

# 2. Architectural Constitution

## 2.1 Authority hierarchy

From highest authority to lowest:

1. Law/regulatory requirements and licensed operating constraints.
2. Human governance/authorization.
3. Deterministic policy engines.
4. Cryptographic verification.
5. Database constraints and transactional state.
6. Automated tests/security gates.
7. Machine-learning/statistical risk models.
8. LLM agent recommendations.

An LLM recommendation can never override a higher layer.

# 3. Global Trust Boundaries

                         INTERNET
                            |
                     WAF / CDN / DDoS
                            |
                     Experience Plane
                            |
                         API/BFF
                            |
            +---------------+----------------+
            |                                |
      Identity/Policy                    Gaming API
            |                                |
            +---------------+----------------+
                            |
                    Transaction Plane
                            |
              +-------------+-------------+
              |                           |
          Risk Pre-check                Ledger
              |                           |
              +-------------+-------------+
                            |
                      Event Backbone
                            |
          +-----------------+------------------+
          |                 |                  |
        Risk AI          Analytics          Notifications
          |
      Human review
          |
     Policy decision
                            |
                    Settlement / Treasury
                            |
                      Blockchain Layer

# 4. Service Boundary Model

## 4.1 API Gateway / BFF

Responsibilities:

- authentication context propagation;
- request validation;
- rate limiting;
- idempotency key extraction;
- API versioning;
- WebSocket/session gateway;
- routing.

It must not contain business logic that changes financial truth.

## 4.2 Identity Service

Owns:

- user identity;
- credentials;
- sessions;
- devices;
- authentication state;
- account lifecycle.

Does not own ledger balances or game outcomes.

## 4.3 Compliance / Eligibility Service

Owns:

- KYC/AML integration state;
- sanctions screening state;
- jurisdiction classification;
- age/eligibility policy;
- responsible-gaming restrictions;
- account restrictions.

Key API concept:

EligibilityDecision = evaluate(user, game, jurisdiction, policy_version)

Response is deterministic and signed/versioned where practical.

An LLM may explain evidence to a reviewer but cannot manufacture an eligibility decision.

## 4.4 Game Catalog Service

Owns:

- supported games;
- game versions;
- configuration;
- limits;
- mathematical metadata;
- availability by jurisdiction.

It does not settle money.

## 4.5 Game Engine

Owns:

- bet validation;
- deterministic random-input derivation;
- game resolution;
- payout calculation;
- game-version execution.

A game engine should expose a pure/deterministic interface as far as possible:

validate_bet()
resolve()
calculate_payout()

It emits a proposed settlement result, which the ledger independently validates before recording the financial mutation.

## 4.6 Betting Service

Owns:

- bet lifecycle;
- bet command acceptance;
- nonce allocation;
- correlation IDs;
- game-session state;
- settlement coordination.

Suggested states:

REQUESTED
ELIGIBILITY_CHECKED
FUNDS_RESERVED
ACCEPTED
RESOLVED
SETTLED
FAILED
CANCELLED

Illegal transitions must be unreachable through the service API.

## 4.7 Ledger Service

This is the financial authority.

Owns:

- ledger accounts;
- journal transactions;
- debit/credit entries;
- holds/reservations;
- reversals;
- reconciliation.

Core invariant:

SUM(all debits) = SUM(all credits)

For each account:

opening + credits - debits = closing

The ledger must never accept a settlement without:

- authenticated caller;
- valid authorization context;
- valid transaction reference;
- valid currency/scale;
- sufficient reserved funds where applicable;
- idempotency protection.

## 4.8 Wallet / Payment Service

Owns:

- payment provider adapters;
- blockchain deposit observation;
- withdrawal requests;
- transaction state;
- webhook verification;
- provider reconciliation.

It may request a ledger mutation.

It cannot directly alter balances.

## 4.9 Risk Service

Owns:

- risk events;
- feature calculation;
- risk scores;
- risk cases;
- recommendation generation;
- risk evidence.

Risk should primarily consume events asynchronously, with a bounded pre-bet policy check for hard rules that must execute before a wager is accepted.

AI may investigate:

- velocity anomalies;
- account/device relationships;
- wallet clusters;
- behavioural patterns.

The final enforcement decision belongs to deterministic policy and authorized human workflows.

## 4.10 AI Control Plane

The existing Luxor9 agent framework is the natural starting point for this plane.

Allowed responsibilities:

- architecture analysis;
- code generation;
- refactoring;
- test generation;
- security investigation;
- risk investigation;
- support assistance;
- SRE diagnosis;
- document generation.

Forbidden direct authority:

- changing a ledger balance;
- approving/releasing treasury funds;
- overriding KYC/AML;
- disabling jurisdiction controls;
- changing cryptographic fairness parameters in production;
- deploying production smart contracts;
- changing security policies without human approval.

## 4.11 Blockchain / Treasury Service

Owns:

- chain RPC adapters;
- address/indexing state;
- blockchain transaction records;
- settlement proofs;
- treasury reconciliation;
- Safe multisig workflows.

The application should hold no plaintext treasury private keys.

# 5. Primary Data Model

The following schemas are logical Phase-1 definitions. Exact SQL types and migrations belong to later implementation phases.

## 5.1 Users

users
-----
id UUID
status
created_at
updated_at

## 5.2 Identities

identities
----------
id UUID
user_id UUID
provider
provider_reference
verification_state
created_at
updated_at

PII should be minimized and provider-sensitive payloads kept outside ordinary application logs.

## 5.3 Jurisdiction Policy

jurisdiction_policies
---------------------
policy_id
jurisdiction_code
policy_version
money_gaming_allowed
crypto_allowed
fiat_allowed
minimum_age
kyc_required
responsible_gaming_rules
effective_from
effective_until
status

The policy is versioned so historical decisions can be reconstructed.

## 5.4 Ledger Accounts

ledger_accounts
---------------
id
owner_type
owner_id
currency
account_type
status
created_at

Potential account types:

- user liability
- settlement/escrow
- treasury asset
- fee/revenue
- payment clearing
- suspense

## 5.5 Ledger Transactions

ledger_transactions
-------------------
id
idempotency_key
transaction_type
reference_type
reference_id
currency
status
created_at
committed_at

## 5.6 Ledger Entries

ledger_entries
--------------
id
transaction_id
account_id
direction
amount_minor_units
created_at

Never update a committed entry in place.

Correction occurs through explicit reversal/adjustment transactions.

## 5.7 Holds

balance_holds
-------------
id
account_id
reference_id
amount_minor_units
status
created_at
released_at

Holds provide a concurrency-safe reservation mechanism for wagers and withdrawals.

## 5.8 Games

games
-----
id
slug
status
current_version
jurisdiction_policy_reference
created_at

## 5.9 Game Versions

game_versions
-------------
id
game_id
version
algorithm_identifier
config_hash
payout_model_version
fairness_protocol_version
status
approved_at

A game result must reference the exact version that produced it.

## 5.10 Bets

bets
----
id
user_id
game_id
game_version_id
client_seed
nonce
stake_minor_units
currency
idempotency_key
status
ledger_reservation_id
outcome_id
created_at
resolved_at

## 5.11 Fairness Commitments

fairness_commitments
--------------------
id
game_id
server_seed_hash
server_seed_reference
client_seed
nonce
algorithm_version
commitment_status
created_at
revealed_at

Do not store raw server seeds in ordinary application tables before their proper lifecycle allows disclosure.

## 5.12 Risk Events

risk_events
-----------
id
event_type
subject_type
subject_id
feature_payload
source
occurred_at
correlation_id

## 5.13 Risk Cases

risk_cases
----------
id
subject_type
subject_id
risk_band
status
policy_version
opened_at
closed_at

## 5.14 Audit Events

audit_events
------------
id
actor_type
actor_id
action
resource_type
resource_id
policy_version
correlation_id
payload_hash
created_at

Audit events should be append-only.

# 6. Core Communication Patterns

## 6.1 Bet Placement — synchronous authority path

Client
  |
  v
API Gateway
  |
  +--> Authentication
  |
  +--> Jurisdiction / Eligibility
  |
  +--> Responsible Gaming Policy
  |
  +--> Hard Risk Rules
  |
  v
Betting Service
  |
  v
Ledger: RESERVE FUNDS
  |
  v
Game Engine
  |
  v
Deterministic Outcome
  |
  v
Settlement Coordinator
  |
  v
Ledger: COMMIT SETTLEMENT
  |
  v
Event Backbone

Important:

Risk AI should not sit directly in the critical path if it can produce a nondeterministic decision.

Use deterministic hard-stop rules in the synchronous path.

AI enrichment can happen immediately afterward or in a separate low-latency recommendation path.

## 6.2 Bet Settlement — deterministic responsibility split

### Game Engine owns

- mathematical outcome;
- payout computation;
- fairness evidence.

### Ledger owns

- whether the money movement is valid;
- whether reserved funds exist;
- whether the transaction is idempotent;
- the authoritative resulting balance.

### Risk owns

- whether the event pattern is suspicious;
- whether further investigation is appropriate.

This separation prevents:

AI risk recommendation -> direct balance mutation

and prevents:

game engine -> direct unrestricted balance mutation

# 7. Event Backbone

Recommended event types:

identity.created
identity.verified
kyc.updated
jurisdiction.evaluated
account.restricted

bet.requested
bet.accepted
bet.rejected
bet.resolved
bet.settled

ledger.hold.created
ledger.hold.released
ledger.transaction.committed
ledger.reversal.created

deposit.detected
deposit.confirmed
withdrawal.requested
withdrawal.queued
withdrawal.completed
withdrawal.failed

risk.event.created
risk.score.updated
risk.case.opened
risk.case.updated

blockchain.tx.detected
blockchain.tx.confirmed
blockchain.tx.reorged

audit.event.created

Event envelope:

{
  "event_id": "uuid",
  "event_type": "bet.settled",
  "event_version": 1,
  "occurred_at": "RFC3339",
  "correlation_id": "uuid",
  "causation_id": "uuid",
  "producer": "betting-service",
  "payload": {}
}

Consumers must be idempotent.

# 8. Consistency Model

## Strong consistency

Use for:

- ledger mutations;
- holds;
- bet acceptance against available funds;
- withdrawal authorization state;
- privileged state transitions.

## Eventual consistency

Suitable for:

- analytics;
- dashboards;
- notifications;
- risk enrichment;
- support knowledge;
- behavioural aggregates.

The UI can be eventually consistent for display, but the ledger cannot.

# 9. Idempotency Model

Every externally repeatable command receives an idempotency key.

Examples:

POST /bets
POST /withdrawals
POST /deposits/webhook
POST /settlements

Logical property:

N identical requests with the same idempotency key = 1 logical mutation

Implementation pattern:

request
  |
  v
Idempotency Store
  |
  +--> existing result -> replay result
  |
  +--> new key
          |
          v
      transaction
          |
          v
      persist result

# 10. Deterministic vs AI Separation

## Deterministic authorities

- ledger
- cryptographic verifier
- game algorithm
- jurisdiction policy
- responsible-gaming limits
- authorization
- CI/CD gates
- database constraints
- smart-contract state

## AI assistance

- architecture generation
- code generation
- refactoring
- test generation
- security reasoning
- fraud investigation
- case summarization
- customer support
- operational diagnosis

### Forbidden pattern

Claude
  |
  v
"approve withdrawal"
  |
  v
Treasury transfer

### Required pattern

Claude recommendation
  |
  v
Policy Engine
  |
  v
Authorization Gate
  |
  v
Human approval where required
  |
  v
Treasury action

# 11. Jurisdiction Engine

All access to money gaming must execute through:

JurisdictionResolver + EligibilityPolicy

Inputs:

- verified identity information;
- declared location;
- network/geographic signal;
- account history;
- product classification;
- jurisdiction policy version;
- game classification.

Outputs:

ALLOWED
RESTRICTED
KYC_REQUIRED
MANUAL_REVIEW
PROHIBITED

### India policy requirement

For an online-money-gaming implementation, India must currently be represented as PROHIBITED by the platform policy model unless a competent legal/compliance process establishes a different classification for a different product model.

The architecture must not contain technical bypass logic.

# 12. Current Repo -> Target Platform Migration

## Stage A — Preserve

Keep existing:

- Next.js frontend;
- Python/FastAPI agent application;
- current memory/task system;
- current Redis integration.

Do not repurpose its existing task/agent database models as financial ledger tables.

## Stage B — Introduce

Add a separate Rust workspace:

services/
  transaction-api/
  identity/
  eligibility/
  betting/
  game-engine/
  ledger/
  wallet/
  risk/

## Stage C — Introduce typed contracts

Create:

packages/contracts/
  API schemas
  event schemas
  error codes
  versioned domain identifiers

## Stage D — Introduce event backbone

Kafka/Redpanda/NATS.

## Stage E — Add blockchain

Only after the off-chain ledger/game core is independently verified.

# 13. Target Repository Structure

/
├── frontend/                  # existing Next.js experience
├── backend/                   # existing AI application plane
│
├── services/                  # new Rust transaction plane
│   ├── api/
│   ├── identity/
│   ├── eligibility/
│   ├── betting/
│   ├── game-engine/
│   ├── ledger/
│   ├── wallet/
│   └── risk/
│
├── contracts/
│   ├── settlement/
│   └── treasury/
│
├── packages/
│   └── contracts/
│
├── infra/
│   ├── docker/
│   ├── terraform/
│   └── k8s/
│
├── tests/
│   ├── integration/
│   ├── property/
│   ├── e2e/
│   ├── load/
│   └── security/
│
└── docs/
    ├── architecture/
    ├── compliance/
    ├── security/
    └── adr/

This is a target-state structure, not an instruction to create all directories in Phase 1.

# 14. Communication Diagram — Game Engine / Ledger / Risk

                         BET COMMAND
                              |
                              v
                       +-------------+
                       | Betting API |
                       +------+------+
                              |
                    eligibility + hard risk
                              |
                              v
                       +-------------+
                       | Ledger Hold |
                       +------+------+
                              |
                              v
                       +-------------+
                       | Game Engine |
                       +------+------+
                              |
                 deterministic outcome
                              |
                              v
                   +-------------------+
                   | Settlement Check  |
                   +---------+---------+
                             |
                             v
                       +-----------+
                       |  Ledger   |
                       +-----+-----+
                             |
                       committed event
                             |
                             v
                      +-------------+
                      | Event Bus   |
                      +------+------+ 
                             |
               +-------------+-------------+
               |                           |
               v                           v
         +-----------+               +-----------+
         | Risk Svc  |               | Analytics |
         +-----+-----+               +-----------+
               |
          features / models
               |
               v
         +-------------+
         | AI Analyst  |
         +------+------+
                |
         recommendation only
                |
                v
         +-------------+
         | Policy Gate |
         +-------------+
                |
          human escalation

# 15. Failure and Recovery Requirements

The architecture must survive:

- duplicate requests;
- duplicate webhooks;
- event delivery duplication;
- event delay;
- worker crash;
- PostgreSQL restart;
- Redis failure;
- event-bus outage;
- blockchain RPC failure;
- blockchain reorg;
- payment-provider timeout;
- partial settlement;
- AI service outage.

The platform must remain financially correct even if every AI model is offline.

This is a critical acceptance criterion:

**AI outage must degrade intelligence, not accounting.**

# 16. Security Architecture

Mandatory controls:

### Application

- strict authentication;
- server-side authorization;
- rate limiting;
- request validation;
- secure sessions/passkeys where appropriate;
- replay protection;
- signed webhooks;
- audit logging.

### Financial

- double-entry;
- holds;
- idempotency;
- reconciliation;
- append-only history;
- privileged-action audit.

### Blockchain

- Safe multisig;
- least privilege;
- emergency controls;
- no private treasury keys in application memory/config;
- contract tests/fuzzing/invariants;
- external smart-contract review before mainnet.

### AI

- least-privilege tools;
- explicit allow/deny tool matrix;
- prompt-injection defense;
- untrusted-input boundaries;
- complete tool-call audit;
- human approval for high-impact actions.

# 17. Scalability Direction

The first implementation should not begin as dozens of independent production microservices.

Recommended sequence:

Modular monolith
    ->
typed domain modules
    ->
event backbone
    ->
selective service extraction
    ->
horizontal game workers
    ->
regional partitioning if required

Scale independently according to workload:

- game workers by bet throughput;
- WebSocket layer by concurrent connections;
- event consumers by partition lag;
- read models by query volume;
- analytics by event volume.

PostgreSQL remains the source of truth while read-heavy/analytical workloads move to specialized stores later.

# 18. Phase-1 Security Invariants

The following must become automated tests in later phases:

ledger:
  sum(debits) == sum(credits)

idempotency:
  same key -> same logical mutation

authorization:
  unauthorized principal -> no state change

eligibility:
  PROHIBITED -> no wager

fairness:
  same inputs -> same result

fairness commitment:
  hash(revealed seed) == committed hash

game:
  payout <= configured maximum

risk:
  AI output != authoritative policy decision

AI:
  unauthorized tool -> DENY

deployment:
  failed gate -> NO PRODUCTION

# 19. Phase-1 Decision Record

### Accepted as architectural direction

- Rust for transaction-critical services.
- Next.js/TypeScript for the experience plane.
- PostgreSQL for financial truth.
- Redis for ephemeral state.
- Kafka/Redpanda/NATS for event propagation.
- Solidity/Foundry only for narrowly scoped blockchain settlement.
- Existing Luxor9 Python/FastAPI system remains the initial AI/application plane.
- Deterministic policy + ledger + cryptographic verification remain authoritative.

### Explicitly unresolved

- launch jurisdiction;
- licensing entity/operator structure;
- final KYC/AML vendors;
- payment providers;
- exact blockchain network(s);
- exact game catalog;
- final SLA/capacity targets;
- smart-contract custody model;
- production threat model approval.

These become explicit decisions in subsequent phases.

# 20. Phase-1 Exit Criteria

Phase 1 is READY FOR HUMAN REVIEW when:

1. This architecture and feature brief are reviewed.
2. The current-repo/target-stack delta is acknowledged.
3. The jurisdiction model is accepted.
4. The service boundaries are accepted.
5. Ledger/Game/Risk authority boundaries are accepted.
6. The schema ownership model is accepted.
7. The migration strategy is accepted.
8. No implementation agent begins financial code before approval.

**Current status: PENDING HUMAN APPROVAL**

## Evidence / Inspection Basis

The architecture reflects the inspected repository snapshot and specifically accounts for the existing:

- Next.js frontend;
- Python/FastAPI backend;
- async SQLAlchemy/asyncpg;
- Neon PostgreSQL;
- Redis;
- WebSocket task updates;
- LLM router/agent tool layer;
- existing tasks, agent_turns, and memories data models.

External compliance references used during Phase 1 research:

- Ministry of Electronics & Information Technology — Promotion and Regulation of Online Gaming Act, 2025.
- Ministry of Electronics & Information Technology — Promotion and Regulation of Online Gaming Rules, 2026.
- Press Information Bureau — implementation/enforcement summaries for the Act and Rules.
