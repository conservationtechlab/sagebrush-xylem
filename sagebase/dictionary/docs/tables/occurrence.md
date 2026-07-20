# occurrence

Contains record of organism occurrences per event record. Linked to species data via class.

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `occurrence_id` | uuid | **PK**, required | Unique identifier of occurrence record |
| `event_id` | uuid | **FK**, required | Linked event record - foreign key |
| `model_id` | uuid | **FK** | Model used to classify organism - foreign key |
| `class_id` | string | **FK**, required | Organism class - foreign key |
| `confidence` | string |  | Model confidence score out of 1.0 |
| `validator_id` | uuid | **FK** | Validator of class |
| `annotation_id` | uuid | **FK** | Classifier annotation - foreign key |
| `occurrence_time` | timestamp | required | Timestamp for presence within event |
| `media_id` | uuid | **FK** | Media record |

**PK** - Primary Key  
**FK** - Foreign Key

## Relations

- event_id => [`event.event_id`](event.md)
- model_id => [`model.model_id`](model.md)
- class_id => [`class.class_id`](class.md)
- validator_id => [`person.person_id`](person.md)
- annotation_id => [`annotation.annotation_id`](annotation.md)
- media_id => [`media.media_id`](media.md)
