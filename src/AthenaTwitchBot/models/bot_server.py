# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
from dataclasses import dataclass, field
import asyncio

# Custom Library

# Custom Packages
from AthenaTwitchBot.models.twitch_bot_protocol import TwitchBotProtocol
from AthenaTwitchBot.models.message_context import MessageContext
from AthenaTwitchBot.data.output_types import OutputTypes
from AthenaTwitchBot.models.output_system import OutputSystem
import AthenaTwitchBot.functions.global_vars as gbl

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
@dataclass(kw_only=True, eq=False, order=False, slots=True)
class BotServer:
    # optional kwargs
    ssl_enabled:bool=False
    irc_host:str='irc.chat.twitch.tv'
    irc_port:int=6667
    irc_port_ssl:int=6697

    # things that aren't normally customized, but you never know what a user might want
    chat_bot_protocol:type[TwitchBotProtocol]=TwitchBotProtocol
    output_system:OutputSystem=OutputSystem()

    # non init stuff
    bot_transport:asyncio.Transport=field(init=False)

    def launch(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start_chat_bot(loop))
        # login with the chatbot
        loop.create_task(self.login_chat_bot())
        # make sure we run forever?
        loop.run_forever()
        loop.close()

    async def start_chat_bot(self, loop:asyncio.AbstractEventLoop):
        self.bot_transport,_ = await loop.create_connection(
            protocol_factory=self.chat_bot_protocol,
            host=self.irc_host,
            port=self.irc_port_ssl if self.ssl_enabled else self.irc_port,
            ssl=self.ssl_enabled
        )

    async def login_chat_bot(self):
        await gbl.bot_server.output_direct(
            output_type=OutputTypes.twitch,
            context=MessageContext(
                _output=[
                    f"PASS oauth:{gbl.bot.oauth_token}",
                    f"NICK {gbl.bot.nickname}",
                    f"JOIN {','.join(str(c) for c in gbl.bot.channels)}",
                    "CAP REQ :twitch.tv/tags"
                ]
            )
        )

    async def output_all(self, context:MessageContext):
        await asyncio.gather(
            self.output_direct(
                output_type=t,
                context=context
            ) for t in OutputTypes
        )

    async def output_direct(self, output_type: OutputTypes, context:MessageContext):
        try:
            await self.output_system[output_type].output(context, transport=self.bot_transport)
        except KeyError:
            print("here")



