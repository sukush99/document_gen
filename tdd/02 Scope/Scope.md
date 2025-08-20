# Scope

## Inclusions

### Central Orders Data Model

- **Database Schema**: Complete multi-channel order data model with core tables (Orders, OrderLines, OrderPayments, etc.) and reference tables for business expansion
- **Channel Expansion Framework**: Configuration tables for Channels, PaymentTypes, DeliveryTypes, DeliveryMethods, and Systems to support future platform additions
- **Order Viewer Interface**: Read-only web interface for customer service staff to search and view orders across all channels

### Uber Eats Integration

- **Webhook Processing**: HTTP-triggered Azure Function to receive delivery.state_changed webhooks from Uber Eats
- **Order Retrieval**: Queue-triggered Azure Function to fetch complete order details from Uber Eats API using resource_href
- **Data Transformation**: Mapping Uber Eats order format to Central Orders data model
- **Safety Net Mechanism**: Timer-triggered Azure Function to periodically query Uber Eats API for missed orders
- **Error Handling**: Comprehensive retry logic, exponential backoff, and Service Bus duplicate detection

### D365 Integration for Uber Orders

- **DMF Package Generation**: Transform Central Orders data into D365 Data Management Framework format
- **Retail Transaction Structure**: Use existing RetailTransactionEntity, RetailTransactionSalesLineV2Entity, RetailTransactionPaymentLineV2Entity, and RetailTransactionTaxLineEntity
- **Batch Processing**: Automated D365 import using established retail transaction patterns
- **Integration Monitoring**: Status tracking and error reporting for D365 publishing

## Exclusions

### Phase 2 - Shopify Orders Routed to Central Order Data Model

- Modification of existing Shopify integration to route unfulfilled orders through Central Orders system
- Shopify webhook processing and API integration
- Shopify-specific order transformation logic

### Phase 3 - Shopify Orders Picked via Central Order Data Model  

- HFM Picking App backend migration from D365 to Central Orders system
- Picking workflow management and order assignment logic
- Order fulfillment state management and completion processing
- Integration with existing picking hardware and devices

### Additional Exclusions

- **Amazon Integration**: Amazon Seller Central/SP-API integration for order processing
- **Order Fulfillment**: No picking, packing, or shipping capabilities - Uber orders are already fulfilled
- **Payment Processing**: No payment capture or refund processing - orders include payment details for reporting only
- **Customer Management**: No customer profiles or communication - customer data embedded in orders as provided by channels
