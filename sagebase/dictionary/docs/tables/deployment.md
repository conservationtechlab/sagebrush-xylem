# deployment

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `deployment_id` | uuid | **PK**, required |  |
| `site_id` | uuid | required |  |
| `device_id` | string | required |  |
| `start_date` | date | required |  |
| `end_date` | date |  |  |
| `deployed_by` | string |  |  |
| `note` | string |  |  |
| `lat` | number |  |  |
| `long` | number |  |  |
| `geom` | json |  |  |
| `elevation` | number |  |  |

## Relations

- References [`site.site_id`](site.md)
- References [`device.device_id`](device.md)
- Referenced by [`event.deployment_id`](event.md)
