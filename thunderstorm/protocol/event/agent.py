from thunderstorm.kafka_messaging import Event
from thunderstorm.protocol.schema import (
    # POS
    POSFetchSchema, POSHashFetchSchema, POSWeekFetchSchema, POSMappingRequestSchema,
    POSRawSchema, POSWeekRawSchema, POSHashRawSchema, POSMappingResponseSchema,

    # CPL
    CPLLocationsRequestSchema, CPLXMLRequestSchema, CPLDeleteSendRequestSchema,
    CPLMetaRequestSchema, CPLXMLResponseSchema, CPLLocationsHashNotifySchema,
    CPLLocationsResponseSchema, SendActionResponseSchema, CPLDeleteSendResponseSchema,
    CPLMetaResponseSchema,

    # Playlist
    SyncPlaylistHashResponseSchema, SyncPlaylistResponseSchema,
    SyncPlaylistRequestSchema, SyncAllPlaylistsRequestSchema,
    SyncPlaylistHashRequestSchema, PlaylistSendRequestSchema,
    PlaylistSendResponseSchema,

    # Title
    TitleSendRequestSchema,

    # Complex
    ComplexCheckExistsRequestSchema, ComplexConfigSendResponseSchema, ComplexFLMHashRawSchema,
    ComplexFLMRawSchema, ShowAttributesRawSchema,

    # Pack
    SyncAllPacksResponseSchema, SyncPackResponseSchema, PackSendResponseSchema,
    PlaceholderUpdateRequestSchema,

    # Task
    ScheduleValidationSchema
)

# POS
POS_FETCH = Event(topic='pos.fetch', schema=POSFetchSchema)
POS_HASH_FETCH = Event(topic='pos-hash.fetch', schema=POSHashFetchSchema)
POS_WEEK_FETCH = Event(topic='pos-week.fetch', schema=POSWeekFetchSchema)
POS_MAPPING_REQUEST = Event(topic='pos.mapping.request', schema=POSMappingRequestSchema)

# CPL
CPL_LOCATIONS_REQUEST_EVENT = Event(
    topic='cpl.locations.request',
    schema=CPLLocationsRequestSchema
)
CPL_XML_REQUEST_EVENT = Event(
    topic='cpl.xml.request',
    schema=CPLXMLRequestSchema
)
CPL_DEL_SEND_REQUEST_EVENT = Event(
    topic='cpl-delete.send.request',
    schema=CPLDeleteSendRequestSchema
)
CPL_META_REQUEST_EVENT = Event(
    topic='cpl.meta.request',
    schema=CPLMetaRequestSchema
)

# PLAYLIST
PLAYLIST_SYNC_REQUEST_EVENT = Event(
    topic='playlist.sync.request',
    schema=SyncPlaylistRequestSchema
)

PLAYLIST_SYNC_ALL_REQUEST_EVENT = Event(
    topic='playlist.sync-all.request',
    schema=SyncAllPlaylistsRequestSchema
)

PLAYLIST_SYNC_HASH_REQUEST_EVENT = Event(
    topic='playlist.sync-hash.request',
    schema=SyncPlaylistHashRequestSchema
)

PLAYLIST_SEND_REQUEST = Event(
    topic='playlist.send.request',
    schema=PlaylistSendRequestSchema
)

# TITLE
TITLE_SEND_REQUEST = Event(
    topic='title.send.request',
    schema=TitleSendRequestSchema
)

# COMPLEX
COMPLEX_CHECK_EXISTS_REQUEST = Event(topic='complex.check_exists.request', schema=ComplexCheckExistsRequestSchema)
COMPLEX_CONFIG_SEND_RESPONSE = Event(topic='complex-config.send.response', schema=ComplexConfigSendResponseSchema)
COMPLEX_FLM_HASH_RAW = Event(topic='complex-flm-hash.raw', schema=ComplexFLMHashRawSchema)
COMPLEX_FLM_RAW = Event(topic='complex-flm.raw', schema=ComplexFLMRawSchema)
SHOW_ATTRIBUTES_RAW = Event(topic='show-attributes.raw', schema=ShowAttributesRawSchema)

# POS
POS_RAW = Event(topic='pos.raw', schema=POSRawSchema)
POS_WEEK_RAW = Event(topic='pos-week.raw', schema=POSWeekRawSchema)
POS_HASH_RAW = Event(topic='pos-hash.raw', schema=POSHashRawSchema)
POS_MAPPING_RESPONSE = Event(topic='pos.mapping.response', schema=POSMappingResponseSchema)

# PACK
PACKS_LAST_MODIFIED_RAW = Event(topic='packs-last-modified.raw', schema=SyncAllPacksResponseSchema)
PACK_RAW = Event(topic='pack.raw', schema=SyncPackResponseSchema)
PACK_SEND_RESPONSE = Event(topic='pack.send.response', schema=PackSendResponseSchema)
PLACEHOLDERS_RAW = Event(topic='placeholders.raw', schema=PlaceholderUpdateRequestSchema)

# CPL
CPL_XML_RESPONSE_EVENT = Event(
    topic='cpl.xml.response',
    schema=CPLXMLResponseSchema
)

CPL_LOCS_HASH_NOTIFY_EVENT = Event(
    topic='cpl.locations-hash.notify',
    schema=CPLLocationsHashNotifySchema
)

CPL_LOCS_RESPONSE_EVENT = Event(
    topic='cpl.locations.response',
    schema=CPLLocationsResponseSchema
)

CPL_DEL_ACTION_RESPONSE_EVENT = Event(
    topic='cpl-delete.action.response',
    schema=SendActionResponseSchema
)

CPL_DEL_SEND_RESPONSE_EVENT = Event(
    topic='cpl-delete.send.response',
    schema=CPLDeleteSendResponseSchema
)

CPL_META_RESPONSE_EVENT = Event(
    topic='cpl.meta.response',
    schema=CPLMetaResponseSchema
)

# PLAYLIST
PLAYLIST_SYNC_HASH_RESPONSE_EVENT = Event(
    topic='playlist.sync-hash.response',
    schema=SyncPlaylistHashResponseSchema
)

PLAYLIST_SYNC_RESPONSE_EVENT = Event(
    topic='playlist.sync.response',
    schema=SyncPlaylistResponseSchema
)

PLAYLIST_SEND_RESPONSE_EVENT = Event(
    topic='playlist.send.response',
    schema=PlaylistSendResponseSchema
)

PLAYLIST_ACTION_RESPONSE_EVENT = Event(
    topic='playlist.action.response',
    schema=SendActionResponseSchema
)

# TASK
SCHEDULE_VALIDATION_EVENT = Event(
    topic='task-report.data',
    schema=ScheduleValidationSchema
)
