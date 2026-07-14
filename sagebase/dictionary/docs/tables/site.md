# site

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `site_id` | uuid | **PK**, required |  |
| `site_code` | string | required |  |
| `geom` | json | required |  |

## Relations

- Referenced by [`deployment.site_id`](deployment.md)
