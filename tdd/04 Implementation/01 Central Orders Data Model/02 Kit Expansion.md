## Kit Expansion

> **⚠️ DESIGN IN PROGRESS**
> 
> This section is currently being designed and will be updated with detailed implementation specifications.

### Overview

Kit expansion handles the business logic where meal kits and food kits are transformed from single line items into multiple component items during order processing. This replicates the existing logic from the Shopify to D365 integration.

### Key Requirements

- **Kit Detection**: Identify when a product SKU represents a kit that needs expansion
- **Component Lookup**: Retrieve individual components that make up each kit
- **Pricing Logic**: Handle complex pricing where components are priced at $0.01 to prevent negative parent kit prices
- **Line Number Management**: Maintain proper line sequencing when kits expand into multiple components
- **Discount Allocation**: Apply discounts to parent kit lines while setting component discounts to $0

### Implementation Areas

- Kit definition storage and retrieval
- Component expansion algorithms
- Pricing calculation adjustments
- Integration with order line processing
- D365 mapping for expanded kit structures

**Detailed specifications will be provided once the kit expansion design is finalized.**