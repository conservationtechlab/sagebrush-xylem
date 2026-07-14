# device_type

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `device_type_id` | uuid | **PK**, required |  |
| `brand` | string |  |  |
| `model` | string |  |  |
| `code` | string |  |  |
| `device_class_id` | uuid |  |  |

## Relations

- References [`device_class.device_class_id`](device_class.md)
- Referenced by [`device.device_type_id`](device.md)
