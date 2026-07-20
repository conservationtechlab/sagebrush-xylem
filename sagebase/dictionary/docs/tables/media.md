# media

Media information recorded during event.

## Columns

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `media_id` | uuid | **PK**, required | Unique identifier of media record |
| `media_type` | string | required | Class of media recorded, e.g. "Image" |
| `bitrate` | string |  | Bitrate of media, e.g. '30fps' or '192kbps'  |
| `sample_rate` | strign |  | Sample rate of media, e.g. '96kHz' |
| `uri` | string |  | Uniform Resource Identifier - file storage path |

**PK** - Primary Key  

## Relations

- [`event.media_id`](event.md) => media_id
- [`occurrence.media_id`](occurrence.md) => media_id
