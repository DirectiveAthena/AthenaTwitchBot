# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
from dataclasses import dataclass, field, InitVar
from typing import Callable
import inspect

# Custom Library

# Custom Packages
from AthenaTwitchBot.models.decorator_helpers.command import Command
from AthenaTwitchBot.models.decorator_helpers.scheduled_task import ScheduledTask
from AthenaTwitchBot.models.twitch_channel import TwitchChannel
from AthenaTwitchBot.models.twitch_bot_method import TwitchBotMethod

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
@dataclass(slots=True,eq=False,order=False,kw_only=True)
class TwitchBot:
    nickname:str
    oauth_token:str
    channels:list[TwitchChannel|str]
    prefix:str

    # Twitch-specific capabilities : https://dev.twitch.tv/docs/irc/capabilities
    twitch_capability_commands:bool=False
    twitch_capability_membership:bool=False
    twitch_capability_tags:bool=True # only one that has the default set to true, as this is required to make reply's work

    predefined_commands:InitVar[dict[str: Callable]]=None # made part of init if someone wants to feel the pain of adding commands manually

    # noinspection PyDataclass
    commands:dict=field(init=False)
    scheduled_tasks:list[ScheduledTask]=field(init=False)

    # non init slots

    # ------------------------------------------------------------------------------------------------------------------
    # - Code -
    # ------------------------------------------------------------------------------------------------------------------
    def __new__(cls, *args, **kwargs):
        # Loop over own functions to see if any is decorated with the command setup
        cls.commands = {}
        cls.scheduled_tasks = []

        # loop over the bots methods and parse the different methods
        for k,v in cls.__dict__.items():
            if isinstance(v,TwitchBotMethod):
                print("FOUND A METHOD")

            if inspect.isfunction(v):
                if "is_command" in (attributes := [attribute for attribute in dir(v) if not attribute.startswith("__")]):
                    for cmd in v.cmd:
                        cls.commands[cmd.name.lower()] = cmd

                elif "is_task" in attributes:
                    cls.scheduled_tasks.append(v.tsk)

        return super(TwitchBot, cls).__new__(cls,*args,**kwargs)

    def __post_init__(self, predefined_commands: dict[str: Callable]=None):
        # format every channel into the correct model
        self.channels = [
            TwitchChannel(c) if not isinstance(c, TwitchChannel) else c
            for c in self.channels
        ]

        if predefined_commands is not None:
            # the self instance isn't assigned on the predefined_commands input
            self.commands |= {
                k.lower():Command(
                    name=k,
                    case_sensitive=False,
                    callback=v,
                    args_enabled=False
                )
                for k, v in predefined_commands.items()
            }
