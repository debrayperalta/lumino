from flask import Blueprint
from flask_restful import Resource
from webargs.flaskparser import use_kwargs

from raiden.api.v1.encoding import (
    BlockchainEventsRequestSchema,
    ChannelPatchSchema,
    ChannelPutSchema,
    ChannelLuminoGetSchema,
    ChannelPutLuminoSchema,
    ConnectionsConnectSchema,
    ConnectionsLeaveSchema,
    PaymentSchema,
    RaidenEventsRequestSchema,
    DashboardLuminoSchema,
    RaidenEventsRequestSchemaV2,
    SearchLuminoRequestSchema,
)
from raiden.utils import typing


def create_blueprint():
    # Take a look at this SO question on hints how to organize versioned
    # API with flask:
    # http://stackoverflow.com/questions/28795561/support-multiple-api-versions-in-flask#28797512
    return Blueprint('v1_resources', __name__)


class BaseResource(Resource):
    def __init__(self, rest_api_object, **kwargs):
        super().__init__(**kwargs)
        self.rest_api = rest_api_object


class AddressResource(BaseResource):

    def get(self):
        return self.rest_api.get_our_address()


class ChannelsResource(BaseResource):

    put_schema = ChannelPutSchema

    def get(self):
        """
        this translates to 'get all channels the node is connected with'
        """
        return self.rest_api.get_channel_list(
            self.rest_api.raiden_api.raiden.default_registry.address
        )

    @use_kwargs(put_schema, locations=('json',))
    def put(self, **kwargs):
        return self.rest_api.open(
            registry_address=self.rest_api.raiden_api.raiden.default_registry.address,
            **kwargs,
        )


class ChannelsResourceLumino(BaseResource):
    get_schema = ChannelLuminoGetSchema
    put_schema = ChannelPutLuminoSchema

    @use_kwargs(get_schema, locations=('query',))
    def get(self,
            token_addresses: typing.ByteString = None):
        """
        this translates to 'get the channels for the tokens and check if they can join'
        """
        return self.rest_api.get_channel_list_for_tokens(
            self.rest_api.raiden_api.raiden.default_registry.address,
            token_addresses=token_addresses
        )

    @use_kwargs(put_schema, locations=('json',))
    def put(self, **kwargs):
        return self.rest_api.open_lumino(
            registry_address=self.rest_api.raiden_api.raiden.default_registry.address,
            **kwargs,
        )


class ChannelsResourceByTokenAddress(BaseResource):

    def get(self, **kwargs):
        """
        this translates to 'get all channels the node is connected to for the given token address'
        """
        return self.rest_api.get_channel_list(
            registry_address=self.rest_api.raiden_api.raiden.default_registry.address,
            **kwargs,
        )


class ChannelsResourceByTokenAndPartnerAddress(BaseResource):

    patch_schema = ChannelPatchSchema

    @use_kwargs(patch_schema, locations=('json',))
    def patch(self, **kwargs):
        return self.rest_api.patch_channel(
            registry_address=self.rest_api.raiden_api.raiden.default_registry.address,
            **kwargs,
        )

    def get(self, **kwargs):
        return self.rest_api.get_channel(
            registry_address=self.rest_api.raiden_api.raiden.default_registry.address,
            **kwargs,
        )


class TokensResource(BaseResource):

    def get(self):
        """
        this translates to 'get all token addresses we have channels open for'
        """
        return self.rest_api.get_tokens_list(
            self.rest_api.raiden_api.raiden.default_registry.address,
        )


class PartnersResourceByTokenAddress(BaseResource):

    def get(self, token_address):
        return self.rest_api.get_partners_by_token(
            self.rest_api.raiden_api.raiden.default_registry.address,
            token_address,
        )


class BlockchainEventsNetworkResource(BaseResource):

    get_schema = BlockchainEventsRequestSchema()

    @use_kwargs(get_schema, locations=('query',))
    def get(self, from_block, to_block):
        from_block = from_block or self.rest_api.raiden_api.raiden.query_start_block
        to_block = to_block or 'latest'

        return self.rest_api.get_blockchain_events_network(
            registry_address=self.rest_api.raiden_api.raiden.default_registry.address,
            from_block=from_block,
            to_block=to_block,
        )


class BlockchainEventsTokenResource(BaseResource):

    get_schema = BlockchainEventsRequestSchema()

    @use_kwargs(get_schema, locations=('query',))
    def get(self, token_address, from_block, to_block):
        from_block = from_block or self.rest_api.raiden_api.raiden.query_start_block
        to_block = to_block or 'latest'

        return self.rest_api.get_blockchain_events_token_network(
            token_address=token_address,
            from_block=from_block,
            to_block=to_block,
        )


class ChannelBlockchainEventsResource(BaseResource):

    get_schema = BlockchainEventsRequestSchema()

    @use_kwargs(get_schema, locations=('query',))
    def get(self, token_address, partner_address=None, from_block=None, to_block=None):
        from_block = from_block or self.rest_api.raiden_api.raiden.query_start_block
        to_block = to_block or 'latest'

        return self.rest_api.get_blockchain_events_channel(
            token_address=token_address,
            partner_address=partner_address,
            from_block=from_block,
            to_block=to_block,
        )


class RaidenInternalEventsResource(BaseResource):

    get_schema = RaidenEventsRequestSchema()

    @use_kwargs(get_schema, locations=('query',))
    def get(self, limit=None, offset=None):
        return self.rest_api.get_raiden_internal_events_with_timestamps(
            limit=limit,
            offset=offset,
        )


class RegisterTokenResource(BaseResource):

    def put(self, token_address):
        return self.rest_api.register_token(
            self.rest_api.raiden_api.raiden.default_registry.address,
            token_address,
        )


class ConnectionsResource(BaseResource):

    put_schema = ConnectionsConnectSchema()
    delete_schema = ConnectionsLeaveSchema()

    @use_kwargs(put_schema)
    def put(
            self,
            token_address,
            funds,
            initial_channel_target,
            joinable_funds_target,
    ):
        return self.rest_api.connect(
            registry_address=self.rest_api.raiden_api.raiden.default_registry.address,
            token_address=token_address,
            funds=funds,
            initial_channel_target=initial_channel_target,
            joinable_funds_target=joinable_funds_target,
        )

    @use_kwargs(delete_schema, locations=('json',))
    def delete(self, token_address):
        return self.rest_api.leave(
            registry_address=self.rest_api.raiden_api.raiden.default_registry.address,
            token_address=token_address,
        )


class ConnectionsInfoResource(BaseResource):

    def get(self):
        return self.rest_api.get_connection_managers_info(
            self.rest_api.raiden_api.raiden.default_registry.address,
        )


class PaymentResource(BaseResource):

    post_schema = PaymentSchema(
        only=('amount', 'identifier'),
    )
    get_schema = RaidenEventsRequestSchema()

    @use_kwargs(get_schema, locations=('query',))
    def get(
            self,
            token_address: typing.TokenAddress = None,
            target_address: typing.Address = None,
            limit: int = None,
            offset: int = None,
    ):
        return self.rest_api.get_raiden_events_payment_history_with_timestamps(
            token_address=token_address,
            target_address=target_address,
            limit=limit,
            offset=offset,
        )

    @use_kwargs(post_schema, locations=('json',))
    def post(
            self,
            token_address: typing.TokenAddress,
            target_address: typing.TargetAddress,
            amount: typing.PaymentAmount,
            identifier: typing.PaymentID,
    ):
        return self.rest_api.initiate_payment(
            registry_address=self.rest_api.raiden_api.raiden.default_registry.address,
            token_address=token_address,
            target_address=target_address,
            amount=amount,
            identifier=identifier,
        )
      
      
class DashboardResource(BaseResource):
    get_schema = DashboardLuminoSchema()
    @use_kwargs(get_schema, locations=('query',))
    def get(
            self,
            graph_from_date: typing.LogTime = None,
            graph_to_date: typing.LogTime = None,
            table_limit: int = None

    ):
        return self.rest_api.get_dashboard_data(
            self.rest_api.raiden_api.raiden.default_registry.address,
            graph_from_date=graph_from_date,
            graph_to_date=graph_to_date,
            table_limit=table_limit
        )

    
class PaymentResourceLumino(BaseResource):

    get_schema = RaidenEventsRequestSchemaV2()

    @use_kwargs(get_schema, locations=('query',))
    def get(
            self,
            token_network_identifier: typing.Address = None,
            initiator_address: typing.Address = None,
            target_address: typing.Address = None,
            from_date: typing.LogTime = None,
            to_date: typing.LogTime = None,
            event_type: int = None,
            limit: int = None,
            offset: int = None,
    ):
        return self.rest_api.get_raiden_events_payment_history_with_timestamps_v2(
            token_network_identifier=token_network_identifier,
            initiator_address=initiator_address,
            target_address=target_address,
            from_date=from_date,
            to_date=to_date,
            event_type=event_type,
            limit=limit,
            offset=offset,
        )


class PendingTransfersResourceByTokenAndPartnerAddress(BaseResource):

    def get(self, token_address, partner_address):
        return self.rest_api.get_pending_transfers(token_address, partner_address)


class NetworkResource(BaseResource):

    def get(self, token_network_address):
        return self.rest_api.get_network_graph(token_network_address)


class SearchLuminoResource(BaseResource):

    get_schema = SearchLuminoRequestSchema()

    @use_kwargs(get_schema, locations=('query',))
    def get(
            self,
            query: typing.ByteString = None,
            only_receivers: bool = None
    ):
        return self.rest_api.search_lumino(
            self.rest_api.raiden_api.raiden.default_registry.address,
            query=query,
            only_receivers=only_receivers
        )

