# Overview

## Purpose

This TDD defines the implementation of a Central Online Order System that integrates already-fulfilled Uber Eats orders into Harris Farms' D365 Finance & Operations system.

**Current Problem**: Harris Farms manually processes Uber Eats orders by scanning items through POS systems and writing off charges monthly. This creates operational inefficiencies and prevents unified reporting.

**Solution**: Establish a Central Order Management database that automatically captures fulfilled Uber Eats orders and feeds them into D365 using existing retail transaction patterns.

## Approach

**Integration Flow**:

1. **Webhook Capture**: Uber Eats sends delivery.state_changed webhook when orders are handed off to couriers
2. **Order Processing**: Azure Functions retrieve order details and store in Central Orders database
3. **D365 Integration**: Orders are sent to D365 using Data Management Framework (DMF) based on the current retail transaction integration

**Key Components**:

- **Central Orders Database**: Multi-channel order data model with APIs and order viewer interface
- **Uber Eats Integration**: Webhook-based capture with safety net mechanisms
- **D365 Integration**: Direct publishing using established retail transaction patterns

**Technology Stack**: Azure Functions, Service Bus, SQL Database

**Integration Pattern**: Webhook-first with configuration-driven channel expansion.