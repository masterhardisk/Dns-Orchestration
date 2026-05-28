# DNS Orchestration Documentation

Welcome to the DNS Orchestration documentation.

DNS Orchestration is a multi-provider DNS automation system designed to keep DNS records synchronized with system state changes, such as public IP updates.

## System Overview

The system is composed of three main components:

- **FastAPI Backend (Control Plane)**  
  Manages configuration, providers, records, and system state.

- **Worker (Execution Engine)**  
  Applies DNS changes by executing synchronization cycles based on system state.

- **Frontend Dashboard**  
  Provides visibility into records, providers, and current system status.

## Core Purpose

The primary goal of DNS Orchestration is to ensure DNS consistency across multiple providers without manual intervention.

Synchronization is fully automated and driven by state changes, not manual triggers.

## Key Concepts

- **Provider**: External DNS service integration with a defined schema.
- **Record**: Logical DNS entry managed by the system.
- **State**: Global system state that triggers synchronization (e.g. public IP changes).
- **Sync Cycle**: Worker process that evaluates and applies DNS updates.

## Architecture Principle

DNS Orchestration follows a strict separation of concerns:

- API defines and exposes state
- Worker executes changes
- Frontend visualizes state

No component combines all responsibilities.

## Documentation Structure

- Architecture → System design and component interaction
- Worker → Execution model and sync logic
- Data Model → Core entities and schemas
- Sync Flow → End-to-end system behavior