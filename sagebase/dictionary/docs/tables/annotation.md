# annotation

Classifier annotation records.

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `annotation_id` | uuid | **PK**, required | Unique identifier of annotation |
| `timestamp` | timestamp | required | Timestamp of parent record annotation refers to |
| `annotator_id` | string | **FK**, required | Annotator of record |

**PK** - Primary Key  
**FK** - Foreign Key 

## Relations

- [`occurrence.annotation_id`](occurrence.md) => annotation_id
- annotator_id => [`person.person_id`](person.md)
