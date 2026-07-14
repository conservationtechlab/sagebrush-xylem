# occurrence

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `occurrence_id` | uuid | **PK**, required |  |
| `event_id` | uuid | required |  |
| `model_id` | uuid |  |  |
| `class_id` | string | required |  |
| `confidence` | string |  |  |
| `validator_id` | uuid |  |  |
| `annotation_id` | uuid |  |  |
| `occurrence_time` | timestamp | required |  |
| `media_id` | uuid |  |  |

## Relations

- References [`person.person_id`](person.md)
- References [`event.event_id`](event.md)
- References [`model.model_id`](model.md)
- References [`class.class_id`](class.md)
- References [`annotation.annotation_id`](annotation.md)
- References [`media.media_id`](media.md)
