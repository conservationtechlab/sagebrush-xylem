# site

Region or area of data capture for survey.

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `site_id` | uuid | **PK**, required | Unique identifier of the site |
| `site_code` | string | required | Internal code used to distinguish site - e.g. 'SDZWA Biodiversity Reserve'|
| `geom` | json | required | GeoJSON polygon WGS84 |

**PK** - Primary Key  

## Relations

- [`deployment.site_id`](deployment.md) => site_id
