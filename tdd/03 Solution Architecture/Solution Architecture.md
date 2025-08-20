# Solution Architecture

## System Overview

```mermaid
graph TB
    UE[Uber Eats API] --> WH[Webhook Function]
    WH --> SB[Service Bus Queue]
    SB --> OP[Order Processing Function]
    OP --> CDB[(Central Orders Database)]
    OP --> UE
    
    CDB --> D365F[D365 Integration Function]
    D365F --> DMF[D365 DMF Import]
    
    CDB --> API[Order API Functions]
    API --> UI[Order Viewer Interface]
    
    TF[Timer Function] --> UE
    TF --> SB
    
    subgraph "Azure Functions"
        WH
        OP
        D365F
        API
        TF
    end
    
    subgraph "External Systems"
        UE
        DMF
    end
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant UE as Uber Eats
    participant WH as Webhook Function
    participant SB as Service Bus
    participant OP as Order Processing
    participant CDB as Central DB
    participant D365F as D365 Function
    participant DMF as D365 DMF

    UE->>WH: delivery.state_changed webhook
    WH->>SB: Queue order message
    WH->>UE: HTTP 200 OK
    
    SB->>OP: Trigger order processing
    OP->>UE: Get order details API
    UE->>OP: Order data + line items
    OP->>OP: Transform & expand kits
    OP->>CDB: Store order data
    
    CDB->>D365F: Trigger D365 integration
    D365F->>CDB: Read order data
    D365F->>D365F: Generate DMF package
    D365F->>DMF: Submit retail transaction
```

## Component Architecture

```mermaid
graph LR
    subgraph "Uber Integration"
        WH[Webhook Handler]
        OP[Order Processor]
        SN[Safety Net Timer]
    end
    
    subgraph "Central Data Model"
        CDB[(SQL Database)]
        API[Order APIs]
        UI[Order Viewer]
    end
    
    subgraph "D365 Integration"
        D365F[D365 Publisher]
        DMF[DMF Package Generator]
    end
    
    WH --> OP
    OP --> CDB
    SN --> OP
    CDB --> API
    API --> UI
    CDB --> D365F
    D365F --> DMF
```

## Database Schema Overview

```mermaid
erDiagram
    Orders ||--o{ OrderLines : contains
    Orders ||--o{ OrderPayments : has
    Orders ||--o{ OrderAttributes : has
    Orders ||--o{ OrderStatus : tracks
    OrderLines ||--o{ FulfillmentLines : fulfilled_by
    
    Orders {
        bigint OrderId PK
        string SourceOrderId
        int ChannelId FK
        string CustomerEmail
        string DeliveryAddress
        decimal TotalAmount
        datetime CreatedDate
    }
    
    OrderLines {
        bigint OrderLineId PK
        bigint OrderId FK
        string ProductSku
        decimal Quantity
        decimal UnitPrice
        decimal LineTotal
        bit IsServiceCharge
    }
    
    Channels {
        int ChannelId PK
        string ChannelCode
        string ChannelName
    }
    
    Orders }o--|| Channels : from_channel
```

## Technology Stack

**Compute**: Azure Functions (HTTP, Queue, Timer triggers)

**Messaging**: Azure Service Bus (duplicate detection enabled)

**Storage**: Azure SQL Database

**Monitoring**: Application Insights

**Security**: Azure Key Vault for secrets

## Integration Patterns

**Webhook Processing**: Immediate acknowledgment with asynchronous processing

**Safety Net**: Periodic polling for missed orders with Service Bus deduplication

**Error Handling**: Exponential backoff retry with dead letter queues

**Kit Expansion**: Business logic transformation before D365 publishing
