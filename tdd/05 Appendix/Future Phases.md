# Appendix

## Future Phases

### Why Central Data Model vs. Peer-to-Peer Integration

The Central Online Order System uses a hub-and-spoke architecture rather than connecting each platform directly to D365. This approach provides a single source of truth for all order data, enables unified customer service across channels, and simplifies adding new sales channels without complex D365 customizations.

### Phase 2: Shopify Orders Routed to Central Order Data Model

**Objective**: Modify existing Shopify integration to route unfulfilled orders through Central Orders system instead of directly to D365.

**Key Changes**:

- Redirect Shopify polling integration to Central Orders database
- Migrate existing Shopify-to-D365 business logic to Central Orders
- Extend order viewer interface for multi-channel search

**Result**: Shopify orders flow through unified Central Orders system before D365.

### Phase 3: Shopify Orders Picked via Central Order Data Model

**Objective**: Migrate HFM Picking App from D365 backend to Central Orders system backend while maintaining current frontend functionality.

**Key Changes**:

- Replace D365 OData calls with Central Orders API calls
- Implement picking workflows and order assignment in Central Orders
- Maintain existing picking app UI without changes
- Handle fulfillment state management through Central Orders

**Result**: Unified order source for picking operations across all channels with improved visibility and tracking.

Both phases require detailed design and implementation planning before development can begin.
