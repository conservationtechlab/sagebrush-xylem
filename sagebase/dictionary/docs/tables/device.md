# device

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `device_id` | string | **PK**, required |  |
| `serial_number` | string |  |  |
| `device_type_id` | string |  |  |

## Relations

- References [`device_type.device_type_id`](device_type.md)
- Referenced by [`deployment.device_id`](deployment.md)
