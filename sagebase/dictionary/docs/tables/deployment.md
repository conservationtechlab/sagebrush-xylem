# deployment

Deployment record of device deployed during survey.

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `deployment_id` | uuid | **PK**, required | Unique identifier of deployment record |
| `site_id` | uuid | **FK**, required | Linked site record |
| `device_id` | string | **FK**, required | Linked device record |
| `start_date` | date | required | Date when device was deployed |
| `end_date` | date |  | Date when deployment ended |
| `deployed_by` | uuid |  | Who deployed device |
| `note` | string |  | Notes on deployment |
| `lat` | number |  | Point Latitude DD,WGS84 |
| `long` | number |  | Point Longitude DD,WGS84 |
| `geom` | json |  | GeoJSON polygon WGS84 |
| `elevation` | number |  | Point or Avg Elevation in meters |

**PK** - Primary Key  
**FK** - Foreign Key  

## Relations

- site_id => [`site.site_id`](site.md)
- device_id => [`device.device_id`](device.md)
- deployed_by => [`person.person_id`](person.md)
- [`event.deployment_id`](event.md) => deployment_id

