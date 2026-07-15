# media

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `media_id` | uuid | **PK**, required |  |
| `media_type` | string | required |  |
| `bitrate` | integer |  |  |
| `samplerate` | integer |  |  |
| `uri` | string |  |  |

## Relations

- Referenced by [`event.media_id`](event.md)
- Referenced by [`occurrence.media_id`](occurrence.md)
