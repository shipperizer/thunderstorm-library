from marshmallow import Schema, fields, validates_schema, ValidationError, EXCLUDE
from marshmallow.validate import Length


# TODO @shipperizer add descriptions
class POSSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    hash = fields.String(required=True, description='Hash of the whole pos resource')
    scheduled = fields.Boolean(required=True, description='Defines if the POS has been scheduled to play or not')
    auto_mappable = fields.Boolean(required=True)
    short_start_date = fields.String(required=False)
    short_start_time = fields.String(required=True)
    source_start = fields.Integer(required=True)
    title_uuid = fields.UUID(required=True, allow_none=True)
    unmatched_show_attributes = fields.Dict(required=True)
    screen_identifier = fields.String(required=True)
    schedule_id = fields.String(required=True, allow_none=True)
    playlist_id = fields.String(required=True, allow_none=True)
    message = fields.String(required=True, allow_none=True)
    expired = fields.Boolean(required=True)
    id = fields.String(required=True)
    title_name = fields.String(required=True, allow_none=True)
    language = fields.Dict(required=True, allow_none=True)
    print_number = fields.String(required=True, allow_none=True)
    overall_duration = fields.Integer(required=True, allow_none=True)
    end = fields.Float(required=True)
    uuid = fields.UUID(required=True)
    start = fields.Float(required=True)
    seats_available = fields.Integer(allow_none=True, required=True)
    placeholder_type = fields.String(allow_none=True, required=True)
    title = fields.String(required=True)
    show_attributes = fields.Dict(required=True, allow_none=False)
    source = fields.String(allow_none=True, required=True)
    state = fields.String(required=True, allow_none=False)
    complex_identifier = fields.String(allow_none=True, required=True)
    seats_sold = fields.Integer(allow_none=True, required=True)
    week_number = fields.Integer(required=True)
    feature_duration = fields.Integer(allow_none=True, required=True)
    device_uuid = fields.UUID(allow_none=True, required=True)
    screen_uuid = fields.UUID(allow_none=True, required=True)
    deleted = fields.Boolean(required=False)                           # not required in agent service
    sms_device_uuid = fields.UUID(required=False, allow_none=True)     # pos on which device
    ts_show_attributes = fields.Dict(required=False, allow_none=True)  # refact of show_attributes


class PackSchema(Schema):
    """
    Schema for validating pack json, copied from the pack service and extended with last_modified
    """
    class Meta:
        unknown = EXCLUDE

    version_id = fields.UUID(description='Primary identifier of a pack resource', dump_only=True)
    uuid = fields.UUID(required=True, description='Generic identifier of a pack resource')
    name = fields.String(required=True, description='Name of the pack')
    clips = fields.List(fields.Dict(), required=True, description='List of clips present in the pack')
    date_from = fields.Date(allow_none=True, description='Date since the pack is valid')
    date_to = fields.Date(allow_none=True, description='Final date for the pack to be valid')
    time_from = fields.Time(allow_none=True, description='Time since the pack is valid')
    time_to = fields.Time(allow_none=True, description='Final time for the pack to be valid')
    issuer = fields.String(required=True, description='Pack issuer')
    priority = fields.Integer(allow_none=True, description='Pack priority')
    external_show_attribute_maps = fields.List(
        fields.Dict(), allow_none=True, description='List of show attributes'
    )
    placeholder_uuid = fields.UUID(allow_none=True, description='Main identifier of a placeholder resource')
    placeholder_name = fields.String(allow_none=True, description='Name of a placeholder resource')
    title_name = fields.String(allow_none=True, description='Name of the title')
    title_uuid = fields.UUID(allow_none=True, description='Main identifier of a title')
    title_external_ids = fields.List(fields.Dict(), allow_none=True, description='List of external IDs the title is matched to')
    screens = fields.List(fields.UUID(), allow_none=True, description='List of screen uuids')
    ratings = fields.List(fields.Dict(), allow_none=True, description='List of ratings dictionaries.')
    print_no = fields.Integer(allow_none=True, description='Print number of the Pack')
    hash = fields.String(description='Hash of the pack information', dump_only=True)
    created_at = fields.DateTime(allow_none=True, description='Creation datetime of the pack', dump_only=True)
    last_modified = fields.Float(
        allow_none=True,
        description='Last time the pack got modified, only used when syncing packs from site, not on send'
    )

    @validates_schema
    def check_placeholders(self, data, **kwargs):
        ph_uuid = data.get('placeholder_uuid')
        ph_name = data.get('placeholder_name')

        if ph_uuid is None and (ph_name is None or ph_name == ''):
            raise ValidationError(f'Placeholder UUID <{ph_uuid}> and name <{ph_name}> cannot be both None')


class PlaceholderSchema(Schema):
    """
    For use within sync_placeholders from the agent
    """
    class Meta:
        unknown = EXCLUDE

    uuid = fields.UUID(required=True)
    name = fields.String(required=True)
    created = fields.Float(required=True)
    last_modified = fields.Float(required=True)
    type = fields.String(allow_none=True)
    content_type = fields.String(allow_none=True)
    is_trimmable = fields.Boolean(required=False)
    can_delete = fields.Boolean(required=True)
    warn = fields.Boolean(required=False)


class ShowAttributeSchema(Schema):
    """
    For use within sync_show_attributes from the agent
    """
    class Meta:
        # exlcude icon field as NOT returned in 2.4 response and meaningless to cloud services
        unknown = EXCLUDE

    uuid = fields.UUID(required=True)
    custom = fields.Boolean(required=True)
    cpl_attribute = fields.Boolean(required=True)
    screen_attribute = fields.Boolean(required=True)
    name = fields.String(required=True)
    # at list one external_show_attribute is always present
    external_show_attribute_maps = fields.Dict(
        keys=fields.UUID(), values=fields.Dict(), required=True
    )


class ShowAttributesRawSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    show_attributes = fields.List(fields.Nested(ShowAttributeSchema), description='List of show attribute resources')
    complex_uuid = fields.UUID(required=True)


class PlaylistSchema(Schema):
    """
    Schema for validating playlist data
    """
    class Meta:
        unknown = EXCLUDE

    uuid = fields.UUID(required=True, description='Primary identifier of a Playlist.')
    clean = fields.Boolean(description='True if the playlist is empty.')
    content_ids = fields.List(fields.UUID(), description='Primary identifiers of playlist contents.')
    duration_in_seconds = fields.Float(description="Duration of all events in the playlist that are 'non-recursive'.")
    is_3d = fields.Boolean(allow_none=True, description='True if Playlist contains 3D contents.')
    is_4k = fields.Boolean(allow_none=True, description='True if Playlist contains 4K contents.')
    is_hfr = fields.Boolean(allow_none=True, description='True if Playlist contains High Frame Rate contents.')
    is_template = fields.Boolean(description='True if the Playlist contains any placeholder items (Pack, Macro).')
    playlist = fields.Dict(description='SPL json data')
    playlist_ids = fields.List(fields.UUID(), description='List of playlists inside a playlist (recursion). Primarly for internal handling of intermissions.')
    preshow_duration = fields.Float(description='Preshow duration in seconds.')
    title = fields.String(description='Playlist Title.')
    total_duration_in_seconds = fields.Float(description='Duration of all events in the playlist including recursive ones.')
    # added by the ts-agent
    device_uuid = fields.UUID(required=True, description='Primary identifier of a Device.')


class PackSendResponseSchema(Schema):
    """
    CLone of PackSendRequestSchema, with delivery status as addition
    needs to be in line with the pack service
    """
    class Meta:
        unknown = EXCLUDE

    receipt_uuid = fields.UUID(required=True)
    complex_uuid = fields.UUID(required=True)
    pack_uuid = fields.UUID(required=True)
    delivery_status = fields.String(required=True)


class KDMSendRequestSchema(Schema):
    """
    For sending kdm.data on the message bus
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(
        required=True, description='Primary identifier of the complex resource you want to target'
    )
    kdm_data = fields.String(required=True, description='KDM payload in XML format')
    kdm_id = fields.UUID(required=True, description='UUID of the KDM you want to send')


class UserCreateRequestSchema(Schema):
    """
    For sending user creation requests on the message bus
    """
    class Meta:
        unknown = EXCLUDE

    username = fields.UUID(required=True, description="Username of the user to be created (Should be the agent's uuid)")
    password = fields.String(required=True, description='Password of the user to be created')
    # https://artsalliancemedia.atlassian.net/browse/TSA-572: Agent role should have all necessary permissions for agents
    roles = fields.List(fields.String(required=True), required=True, validate=Length(max=1), description='List of roles to assign to the user')


class UserActivateRequestSchema(Schema):
    """
    For sending user creation requests on the message bus
    """
    class Meta:
        unknown = EXCLUDE

    username = fields.UUID(
        required=True,
        description="Username of the user to be activated (Should be the agent's uuid)"
    )
    complex_uuid = fields.UUID(
        required=True,
        description="Complex uuid to be used in creating a complex group for the agent's user"
    )


# TODO: import from User Service when exposed
class UserActivateResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    agent_uuid = fields.UUID(required=True, allow_none=False)
    complex_uuid = fields.UUID(required=True, allow_none=False)


class PlaceholderUpdateSchema(PlaceholderSchema):
    """
    For use within placeholders.raw on the message bus
    """
    class Meta:
        unknown = EXCLUDE

    created = fields.DateTime(required=True)
    last_modified = fields.DateTime(required=True)


class PlaceholderUpdateRequestSchema(Schema):
    """
    For sending placeholders.raw on the message bus
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)
    placeholders = fields.List(fields.Nested(PlaceholderUpdateSchema))


class SyncAllPacksResponseSchema(Schema):
    """
    For sending pack.sync-all.response messages on the message bus
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)
    packs = fields.Dict(keys=fields.UUID(required=True), values=fields.Float(required=True), required=True)


class SyncPackResponseSchema(Schema):
    """
    For sending pack.sync.response messages on the message bus
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)
    pack = fields.Nested(PackSchema)


class SyncPlaylistHashResponseSchema(Schema):
    """
    For sending playlist.sync-hash.response messages on the message bus
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)
    playlists = fields.Dict(
        keys=fields.UUID(required=False),
        values=fields.Dict(
            keys=fields.UUID(required=True, description='Primary identifier of a playlist.'),
            values=fields.String(required=True, validate=Length(equal=40)),
            required=False
        ),
        required=True
    )
    # The fields below is added afterwards, make it un-required for adapt old ts-agent
    success = fields.Boolean(required=False)
    message = fields.String(required=False, allow_none=True, description='Request failed with error message')
    executed_at = fields.Float(required=False, description='Time the delete was requested to Screenwriter')


class SyncPlaylistResponseSchema(Schema):
    """
    For sending playlist.sync.response messages on the message bus
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)
    playlist = fields.Nested(PlaylistSchema, required=True)
    # The fields below is added afterwards, make it un-required for adapt old ts-agent
    device_uuid = fields.UUID(required=False)
    playlist_uuid = fields.UUID(required=False)
    success = fields.Boolean(required=False)
    message = fields.String(required=False, allow_none=True, description='Request failed with error message')
    executed_at = fields.Float(required=False, description='Time the delete was requested to Screenwriter')


class CPLLocationsHashNotifySchema(Schema):
    """
    For sending cpl.locations-hash.notify
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)
    cpl_location_hash = fields.String(required=True)


class CPLLocationsRequestSchema(Schema):
    """
    For receiving cpl.locations.request
    From cpl-service
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)


class CPLLocationsResponseSchema(CPLLocationsRequestSchema):
    """
    For sending cpl.locations.response
    """
    class Meta:
        unknown = EXCLUDE

    from_push = fields.Boolean(required=False)
    cpl_location_hash = fields.String(required=True)
    cpl_location_map = fields.Dict(required=True)


class CPLXMLRequestSchema(Schema):
    """
    For receiving cpl.xml.request
    From cpl-service
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)
    cpl_uuid = fields.UUID(required=True)


class CPLXMLResponseSchema(CPLXMLRequestSchema):
    """
    For sending cpl.xml.response
    """
    class Meta:
        unknown = EXCLUDE

    cpl_xml = fields.String(required=True)


class CPLMetaRequestSchema(Schema):
    """
    For receiving cpl.meta.request
    From cpl-service
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)
    cpl_uuid = fields.UUID(required=True)


class CPLMetaResponseSchema(CPLMetaRequestSchema):
    """
    For sending cpl.meta.response
    """
    class Meta:
        unknown = EXCLUDE

    cpl_meta = fields.Dict(
        required=True,
        description='CPL metadata for a single CPL from SCWR'
    )


class CPLDeleteSendRequestSchema(Schema):
    """
    For cpl-delete.send.request
    """
    class Meta:
        unknown = EXCLUDE
    complex_uuid = fields.UUID(required=True)
    device_uuid = fields.UUID(required=True)
    cpl_uuids = fields.List(fields.UUID(), required=True)


class CPLDeleteSendResponseSchema(Schema):
    """
    For cpl-delete.send.response
    """
    class Meta:
        unknown = EXCLUDE
    complex_uuid = fields.UUID(required=True)
    device_uuid = fields.UUID(required=True)
    cpl_uuids = fields.List(fields.UUID(), required=True)
    action_id = fields.UUID(required=True, allow_none=True)
    error = fields.String(required=True, allow_none=True, description='Request failed with error message')
    executed_at = fields.Float(required=True, description='Time the delete was requested to Screenwriter')


class SyncAllSmpteRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True, allow_none=False)
    days = fields.Integer(required=True, allow_none=False)


class SyncAllSmpteResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    since = fields.Integer(required=True, allow_none=False)
    uuids = fields.List(fields.String())


class SMPTESyncRequestSchema(Schema):
    """
    For receiving smpte.sync.request from playback-service
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)
    smpte_log_uuid = fields.UUID(required=True)


class SMPTESyncResponseSchema(SMPTESyncRequestSchema):
    """
    For sending smpte.sync.response
    """
    class Meta:
        unknown = EXCLUDE

    smpte_log_data = fields.Dict(required=True)


# TODO @shipperizer import it from pos-service once lib is ready
class POSWeekFetchSchema(Schema):
    """
    For receiving pos-week.fetch from pos-service
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True, description='Primary identifier of a Complex')


class POSWeekRawSchema(Schema):
    """
    For sending pos-week.raw to pos-service
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True, description='Primary identifier of a Complex')
    current_week_number = fields.Integer(required=True, description='Current POS week, defined by a site config')


# TODO @shipperizer import it from pos-service once lib is ready
class POSHashFetchSchema(Schema):
    """
    For receiving pos-hash.fetch from pos-service
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True, description='Primary identifier of a Complex')
    week = fields.Integer(required=True, description='Week for which we want to collect POS')


# TODO @shipperizer the schema below is a duplicate of the POSMapSyncSchema in api.v1.schema
# would be nice to find a better way to handle this instead of copying it, although a simple
# import would not be great, most likely restructuring the schema modules is needed
class POSHashRawSchema(Schema):
    """
    For sending pos-hash.raw to pos-service
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True, description='Primary identifier of a Complex')
    pos_map = fields.Dict(
        description='Map pos uuid and pos hash, wrapped into week and device info',
        required=True,
        keys=fields.Integer(required=True),
        values=fields.Dict(
            description='Device map, keys are device uuids and values are maps of <pos uuid>:<pos hash>',
            required=True,
            keys=fields.UUID(required=True),
            values=fields.Dict(
                description='Map of <pos uuid>:<pos hash>',
                required=True,
                keys=fields.UUID(required=True),
                values=fields.String(required=True)
            )
        )
    )


# TODO @shipperizer import it from pos-service once lib is ready
class POSFetchSchema(Schema):
    """
    For receiving pos.fetch from pos-service
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True, description='Primary identifier of a Complex')
    week = fields.Integer(required=True, description='Week for which we want to collect POS')
    uuids = fields.List(fields.UUID(required=True), description='List of POS uuids to collect')


# TODO @shipperizer the schema below is a duplicate of the POSSessionSyncSchema in api.v1.schema
# would be nice to find a better way to handle this instead of copying it, although a simple
# import would not be great, most likely restructuring the schema modules is needed
class POSRawSchema(Schema):
    """
    For sending pos.raw to pos-service
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True, description='Primary identifier of a Complex')
    pos = fields.Dict(
        description='POS sessions, keys are pos uuids and values are actual POS resources',
        required=True,
        keys=fields.UUID(required=True),
        values=fields.Nested(POSSchema, required=True)
    )


class ComplexConfigSendResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    screenwriter_host = fields.String(required=True, validate=Length(min=15, max=100), description='Host and port on which Screenwriter listens to')
    screenwriter_username = fields.String(required=True, validate=Length(min=5, max=100), description='Screenwriter login username')
    screenwriter_password = fields.String(required=True, validate=Length(min=5, max=100), description='Screenwriter login password')
    validation_status = fields.String(required=True, description="'valid' if credentials worked, 'invalid' otherwise")
    error_message = fields.String(allow_none=True, description='Error message in case of validation failure')
    complex_uuid = fields.UUID(required=True, description='Primary identifier of a Complex')


class ComplexCheckExistsRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)
    agent_uuid = fields.UUID(required=True)


class ComplexFLMHashRawSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)
    flm_hash = fields.String(required=True)


class ComplexFLMRawSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)
    flm_data = fields.Dict(required=True)
    flm_hash = fields.String(required=True)


class SyncPlaylistRequestSchema(Schema):
    """
    For sending playlist.sync.request messages on the message bus
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)
    playlist_uuid = fields.UUID(required=True)
    device_uuid = fields.UUID(required=True)


class SyncAllPlaylistsRequestSchema(Schema):
    """
    For sending playlist.sync-all.request messages on the message bus
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)


class SyncPlaylistHashRequestSchema(Schema):
    """
    For sending playlist.sync-hash.request messages on the message bus
    """
    class Meta:
        unknown = EXCLUDE

    complex_uuid = fields.UUID(required=True)
    device_uuids = fields.List(fields.UUID(required=False), allow_none=True, default=[], required=False)
    playlist_uuids = fields.List(fields.UUID(required=False), allow_none=True, default=[], required=False)


class PlaylistSendSchema(Schema):
    """
    For playlist.send.request messages
    """
    class Meta:
        unknown = EXCLUDE

    uuid = fields.UUID(required=True, description="playlist uuid")
    title = fields.String(required=True, description="playlist title")
    events = fields.List(fields.Dict(required=False), required=True, default=[])
    content_ids = fields.List(fields.UUID(required=False), required=False, allow_none=True, default=[])
    is_3d = fields.Boolean(required=False, allow_none=True)
    is_hfr = fields.Boolean(required=False, allow_none=True)
    is_4k = fields.Boolean(required=False, allow_none=True)


class PlaylistSendRequestSchema(Schema):
    """
    For playlist.send.request messages
    """
    class Meta:
        unknown = EXCLUDE

    receipt_uuid = fields.UUID(required=True)
    complex_uuid = fields.UUID(required=True)
    device_uuid = fields.UUID(required=True)
    playlist = fields.Nested(PlaylistSendSchema, required=True)


class PlaylistSendResponseSchema(Schema):
    """
    For playlist.send.response, cause saving playlist in SW is async,
    a playlist.action.response is needed to indicate whether the action
    of saving playlist executed successful or not in screenwriter.
    """
    class Meta:
        unknown = EXCLUDE

    receipt_uuid = fields.UUID(required=True)
    complex_uuid = fields.UUID(required=True)
    device_uuid = fields.UUID(required=True)
    playlist_uuid = fields.UUID(required=True)
    delivery_status = fields.Boolean(required=True, description='true or false')
    action_id = fields.String(required=True, allow_none=True, description='screenwriter async action id')
    message = fields.String(required=True, description='message')


class SendActionResponseSchema(Schema):
    """
    For playlist.action.response、cpl-delete.action.response
    """
    class Meta:
        unknown = EXCLUDE

    action_id = fields.UUID(required=True, allow_none=True, description='screenwriter async action id')
    message = fields.String(required=True)
    success = fields.Boolean(required=True)


class TitleSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    uuid = fields.UUID(required=True, description='Primary identifier of a Title.')
    name = fields.String(required=True, description='Name of the Title.')
    cpls = fields.List(fields.UUID(), default=[], description='UUIDs of CPL matched to the Title.')
    external_titles = fields.List(fields.Dict(keys=fields.String(), values=fields.String()), default=[], description='List of External Title dictionaries matched to the Title.')
    last_modified = fields.Float(description='Last_modified timestamp of the Title')
    year = fields.String(validate=Length(equal=4), description='Title release year.')
    credits_offset = fields.Integer(description='Seconds from start.')
    ratings = fields.List(fields.Dict(keys=fields.String(), values=fields.String()), default=[], description='List of Rating dictionaries associated to the Title.')


class TitleSendRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    title = fields.Nested(TitleSchema(), required=True)
    complex_uuid = fields.UUID(required=True, description='Primary Identifier of a Complex.')
    request_id = fields.UUID(
        required=True, description='Request identifier.'
    )


class TitleSendResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE
    title_uuid = fields.UUID(required=True, description='Primary identifier of a title.')
    complex_uuid = fields.UUID(required=True, description='Primary identifier of a complex.')
    request_id = fields.UUID(required=True, description='Unique request identifier.')
    delivery_attempted_at = fields.Float(required=True, description='Point in time at which delivery on site was attempted')
    delivery_status = fields.String(required=True, description='String denoting whether or not the title send was successful')


class POSMappingRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    pos_uuid = fields.UUID(required=True, description='Primary identifier of a pos session.')
    playlist_uuid = fields.UUID(
        required=True, allow_none=True, description='Primary identifier of a playlist.'
    )
    complex_uuid = fields.UUID(required=True, description='Primary identifier of a complex.')
    placeholder_type = fields.String(allow_none=True, required=True)
    mapping_state = fields.String(required=True, description='pos mapping state, assigned or unassigned')


class POSMappingResponseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    resp_message = fields.String(required=True, description='execution response of agent')
    mapping_status = fields.String(required=True, description='String denoting whether or not the pos mapping was successful')
    complex_uuid = fields.UUID(required=True, description='Primary identifier of a complex.')
    pos_uuid = fields.UUID(required=True, description='Primary identifier of a pos session.')
    playlist_uuid = fields.UUID(
        required=True, allow_none=True, description='Primary identifier of a playlist.'
    )
    attempted_at = fields.Float(required=True, description='Point in time at which mapping on site was attempted')


# Task
class TaskReportDataBaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    organization_id = fields.String(required=True)
    complex_uuid = fields.UUID(required=True)
    task_type = fields.String(required=True)
    payload_hash = fields.String(required=False)
    reported_at = fields.Integer(required=True)


# Schedule validation for Task report data
class ScheduleValidationSchema(TaskReportDataBaseSchema):
    payload = fields.Dict(required=True)
