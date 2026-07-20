# device_type

Device model information of device used in deployment.

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `device_type_id` | uuid | **PK**, required | Unique identifier of device type |
| `brand` | string |  | Manufacturer brand of device |
| `model` | string |  | Model of device published by manufacturer |
| `code` | string |  | Internal code used to characterize device |
| `device_class_id` | uuid | **FK** | Identifier of device class |

**PK** - Primary Key  
**FK** - Foreign Key  

## Relations

- device_class_id => [`device_class.device_class_id`](device_class.md)
- [`device.device_type_id`](device.md) => device_type_id
