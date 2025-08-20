## Order Mapping

> **⚠️ MAPPING DESIGN IN PROGRESS**
>
> The detailed field mappings from Central Orders data model to D365 DMF entities are currently being designed and will be updated with specific transformation rules.

### Overview

The order mapping transforms data from the Central Orders database into D365 retail transaction format using DMF CSV structure. This mapping builds upon the existing Shopify to D365 integration patterns but sources data from the unified Central Orders data model instead of directly from individual platforms.

### Mapping Approach

**Source-Agnostic Design**: Transform Central Orders data (which already contains normalized multi-channel data) into D365 format

**Retail Transaction Pattern**: Use proven retail transaction structure from existing Shopify integration

**Business Logic Preservation**: Maintain existing D365 business rules and validation requirements

**Kit Expansion Support**: Handle meal kit expansion logic similar to current Shopify integration

### Entity Mapping Structure

#### 1. Orders → RetailTransactionEntity (Transactions.csv)

```
Central Orders.Orders table → Transaction header CSV
```

**Key Mapping Areas**:

- **Transaction Identification**: SourceOrderId → TransactionNumber with format conversion
- **Customer Information**: Customer fields → D365 customer account lookup/creation
- **Financial Totals**: TotalAmount, TotalTaxAmount → GrossAmount, NetAmount with sign conversion
- **Delivery Information**: Delivery address fields → D365 delivery address structure
- **Channel Attribution**: ChannelId → OperatingUnitNumber with channel prefix logic

#### 2. OrderLines → RetailTransactionSalesLineV2Entity (Sales transactions V2.csv)

```
Central Orders.OrderLines table → Sales line CSV
```

**Key Mapping Areas**:

- **Product Identification**: ProductSku → ItemId with PLU lookup logic
- **Pricing**: UnitPriceInclusive, LineTotalInclusive → Price, NetAmount with currency handling
- **Tax Information**: LineTaxAmount → SalesTaxAmount with tax group mapping
- **Service Charges**: IsServiceCharge flag → appropriate D365 line handling
- **Kit Expansion**: Kit products → multiple D365 lines with component logic

#### 3. OrderPayments → RetailTransactionPaymentLineV2Entity (Payment transactions V2.csv)

```
Central Orders.OrderPayments table → Payment line CSV
```

**Key Mapping Areas**:

- **Payment Methods**: PaymentTypeId → TenderType with payment method mapping
- **Payment Amounts**: PaymentAmount → AmountTendered with currency conversion
- **Payment References**: PaymentReference → payment tracking fields

#### 4. Tax Calculations → RetailTransactionTaxLineEntity (Tax transactions.csv)

```
Central Orders.OrderLines tax data → Tax line CSV
```

**Key Mapping Areas**:

- **Tax Amounts**: LineTaxAmount → TaxAmount with line-level tax distribution
- **Tax Codes**: Product tax groups → TaxCode with D365 tax configuration
- **Tax Rates**: Calculated tax percentages → TaxPercentage

### Business Logic Requirements

#### Kit Expansion Logic

```
IF ProductSku IN KitDefinitions THEN
    Expand kit into component lines
    Apply kit pricing logic ($0.01 components)
    Maintain line number sequencing
END IF
```

#### Channel-Specific Handling

```
CASE ChannelId
    WHEN UBEREATS THEN OperatingUnitNumber = "ONL-" + store_code
    WHEN SHOPIFY THEN OperatingUnitNumber = "ONL-" + picking_store
    WHEN AMAZON THEN OperatingUnitNumber = "ONL-" + fulfillment_center
END CASE
```

#### Service Charge Processing

```
IF IsServiceCharge = 1 THEN
    Map to appropriate D365 service item
    Apply service charge business rules
    Exclude from picking workflows
END IF
```

### Data Transformation Examples

#### Currency and Sign Conversion

```csharp
// D365 uses negative amounts for sales transactions
var d365GrossAmount = centralOrder.TotalAmount * -1;
var d365NetAmount = centralOrder.TotalAmount * -1;
var d365PaymentAmount = centralOrder.TotalAmount; // Positive for payments
```

#### Transaction Number Formatting

```csharp
// Convert Central Orders SourceOrderId to D365 transaction number format
var d365TransactionNumber = TransactionNumberFormat(centralOrder.SourceOrderId, centralOrder.ChannelId);
```

#### Customer Account Mapping

```csharp
// Map customer data to D365 customer account
var d365CustomerAccount = await GetOrCreateD365CustomerAccount(
    centralOrder.CustomerEmail,
    centralOrder.CustomerFirstName,
    centralOrder.CustomerLastName,
    centralOrder.DeliveryAddress);
```

### Configuration Requirements

**Reference Data Mappings**:

- Channel codes to D365 operating unit numbers
- Payment type codes to D365 tender types
- Product SKUs to D365 item IDs via PLU lookup
- Tax configurations for different product categories

**Business Rules Configuration**:

- Kit expansion definitions and component mappings
- Service charge SKU mappings
- Delivery method and type mappings
- Discount handling rules

### Key Design Decisions Pending

**Customer Management**: Approach for creating/updating D365 customer records from Central Orders data

**Kit Expansion**: Detailed logic for expanding kits from Central Orders vs. D365 integration point

**Line Numbering**: Sequencing strategy when kits expand into multiple D365 lines

**Tax Calculation**: Whether to use Central Orders tax amounts or recalculate in D365

**Error Handling**: Strategy for handling mapping failures and data validation issues

### Integration with Existing Shopify Logic

The Central Orders to D365 mapping will leverage proven patterns from the existing Shopify integration:

- Transaction structure and field mappings
- Customer account management logic
- Kit expansion business rules
- Tax handling and calculation methods
- Error handling and retry mechanisms

**Detailed field-by-field mapping specifications will be provided once the Central Orders to D365 transformation requirements are finalized.**
