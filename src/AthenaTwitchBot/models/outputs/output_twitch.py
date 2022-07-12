# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
import asyncio

# Custom Library

# Custom Packages
from AthenaTwitchBot.models.outputs.output import Output
from AthenaTwitchBot.models.message_context import MessageContext
from AthenaTwitchBot.functions.output_twitch_prep import output_twitch_prep
from AthenaTwitchBot.data.message_flags import MessageFlags

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
OUTPUT_MAPPING = {
    MessageFlags.ping:lambda transport,context:(
        transport.write(
            output_twitch_prep(f"PONG {context.output}")
        )
    ),
    MessageFlags.undefined :lambda transport,context:(
        None
    ),
    MessageFlags.write:lambda transport,context:(
        transport.write(
            output_twitch_prep(
                f"PRIVMSG {context.channel} :{context.output}"
            )
        )
    ),
    MessageFlags.reply:lambda transport,context:(
        transport.write(
            output_twitch_prep(
                f"@reply-parent-msg-id={context.tags.message_id} PRIVMSG {context.channel} :{context.output}"
            )
        )
    ),
    MessageFlags.login:lambda transport,context:(
        transport.write(output_twitch_prep(context.output))
    )
}

class OutputTwitch(Output):
    # noinspection PyMethodOverriding
    async def output(self, context:MessageContext,*,transport:asyncio.Transport):
        # if no output has been defined, just exit here
        if context.output is None:
            return
        # context.output should always be a list of strings, where every string is a line to return to twitch
        try:
            OUTPUT_MAPPING[context.flag](transport, context)
        except KeyError:
            print(f"context.flag<{context.flag.name}> not found in the OUTPUT_MAPPING")