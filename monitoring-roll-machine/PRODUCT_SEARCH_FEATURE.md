# Product Search Feature

## Overview
The product search feature provides automatic product information retrieval from an ERP API when entering product codes. This feature enhances user experience by reducing manual data entry and ensuring data consistency.

## API Integration

### API Endpoint
- **URL**: `http://localhost:8001/api/method/frappe.utils.custom_api.get_product_detail`
- **Method**: GET
- **Parameter**: `item_code` (e.g., `?item_code=BD-RED`)

### Authentication
```json
{
    "Content-Type": "application/json",
    "Authorization": "token 61996278bcc8bbb:8a178a12b28e784"
}
```

### Expected API Response Structure
```json
{
    "message": {
        "success": true,
        "message": "Product detail retrieved successfully",
        "data": {
            "item_code": "BD-RED",
            "item_name": "Baby Doll-RED",
            "description": "Baby Doll-RED",
            "stock_uom": "Nos",
            "disabled": 0,
            "item_group": "Products",
            "has_variants": 0,
            "variant_of": "BD",
            "variants": {
                "attributes": [
                    {
                        "attribute": "Colour",
                        "attribute_value": "Red",
                        "abbreviation": "RED"
                    }
                ],
                "variant_items": [...],
                "template_info": {
                    "template_code": "BD",
                    "template_name": "Baby Doll"
                }
            },
            "creation": "2025-06-26 10:20:09.461704",
            "modified": "2025-06-26 10:20:54.844824"
        }
    }
}
```

## Field Mappings

### Form Fields
| Form Field | API Source | Description |
|------------|------------|-------------|
| Product Code | `data.item_code` | Product identifier from ERP |
| Product Name | `data.item_name` | Full product name (read-only) |
| Color Code | `data.variants.attributes[0].abbreviation` | Color abbreviation from variants |
| Batch Number | Current Date (YYYYMMDD) | Auto-generated in YMD format |
| Target Length | Manual Entry | User-defined target length |
| Unit | Manual Selection | Meter or Yard |

### Print Preview Fields
| Print Field | Source | Example |
|-------------|--------|---------|
| Header | Product Code | "BD-RED" |
| Product Name | Product Name | "Baby Doll-RED" |
| Color | Color Code | "RED" |
| Length | Target Length + Unit | "100.0 Meter" |
| Roll No. | Default | "0" |
| Lot No. | Batch Number | "20250626" |
| QR Code | Product Code + Length | "BD-RED-100.0" |

## Features

### Auto-Search Functionality
- **Trigger**: Typing 3+ characters in Product Code field
- **Delay**: 150ms debounce to prevent excessive API calls
- **Threading**: Non-blocking background API calls
- **Visual Feedback**: Loading indicator and status messages

### Search Status Indicators
- **Searching...**: Orange border, "Searching..." status
- **Found**: Green status with product name
- **Not Found**: Red status with error message
- **Timeout**: Red status for connection issues
- **Connection Error**: Red status for network problems

### Error Handling
- Connection timeouts (3 seconds)
- Network connectivity issues
- Invalid API responses
- Missing product data

### Thread Safety
- Uses `QThread` for background API calls
- Session pooling for connection reuse
- Proper cleanup of worker threads
- Race condition prevention

## Code Structure

### ProductSearchWorker (QThread)
- Handles background API calls
- Manages HTTP session pooling
- Emits signals for success/failure
- Implements proper timeout handling

### ProductForm Updates
- Added Product Name field (read-only)
- Updated field validation
- Enhanced error handling
- Improved user feedback

### PrintPreviewDialog Updates
- Updated field mappings for consistency
- Uses batch_number as lot_number
- Proper QR code generation

## Data Validation

### Required Fields
- Product Code (must not be empty)
- Product Name (auto-filled from API)
- Color Code (auto-filled from API)
- Batch Number (auto-generated)
- Target Length (must be > 0)

### Auto-Generation
- **Batch Number**: Generated using current date in YYYYMMDD format
- **Default Values**: 100.0 meters for target length

## Usage Workflow

1. **User enters product code** (3+ characters)
2. **Auto-search triggers** after 150ms delay
3. **API call executes** in background thread
4. **Form auto-populates** with retrieved data:
   - Product Name (from `item_name`)
   - Color Code (from `variants.attributes[0].abbreviation`)
   - Batch Number (current date in YYYYMMDD)
5. **User reviews/adjusts** target length and unit
6. **Start monitoring** or **Print preview** with complete data

## Configuration

### API Settings (ProductForm class)
```python
API_BASE_URL = "http://localhost:8001/api/method/frappe.utils.custom_api.get_product_detail"
API_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "token 61996278bcc8bbb:8a178a12b28e784"
}
```

### Search Settings
- **Minimum characters**: 3
- **Search delay**: 150ms
- **API timeout**: 3 seconds
- **Connection pooling**: Enabled

## Future Enhancements

1. **Offline support**: Cache frequently used products
2. **Search suggestions**: Dropdown with matching products
3. **Barcode scanning**: Direct product code input
4. **Batch editing**: Multiple products at once
5. **Custom field mapping**: Configurable field relationships 