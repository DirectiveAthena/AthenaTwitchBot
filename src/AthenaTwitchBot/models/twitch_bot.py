# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations
import asyncio
from dataclasses import dataclass, field, InitVar
from typing import Callable
import inspect

# Custom Library
import AthenaLib
import AthenaColor

# Custom Packages

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
@dataclass(slots=True,eq=False,order=False,kw_only=True)
class TwitchBot:
    nickname:str
    oauth_token:str
    channel:str
    prefix:str

    # Twitch-specific capabilities : https://dev.twitch.tv/docs/irc/capabilities
    twitch_capibility_commands:bool=False
    twitch_capibility_membership:bool=False
    twitch_capibility_tags:bool=True # only one that has the default set to true, as this is required to make reply's work

    predefined_commands:InitVar[dict[str: Callable]]=None # made part of init if someone wants to feel the pain of adding commands manually

    # noinspection PyDataclass
    commands:dict[str: Callable]=field(init=False)
    frequent_outputs:list[tuple[Callable, int]]=field(init=False)

    # non init slots

    # ------------------------------------------------------------------------------------------------------------------
    # - Code -
    # ------------------------------------------------------------------------------------------------------------------
    def __new__(cls, *args, **kwargs):
        # Loop over own functions to see if any is decorated with the command setup
        cls.commands = {}
        cls.frequent_outputs = []

        # create the actual instance
        #   Which is to be used in the commands tuple
        obj = super(TwitchBot, cls).__new__(cls,*args,**kwargs)

        # loop over the bot's metods and parse the different methods
        for k,v in cls.__dict__.items():
            if inspect.isfunction(v):
                if "is_command" in (attributes := [attribute for attribute in dir(v) if not attribute.startswith("__")]):
                    cls.commands[v.command_name] = v
                elif "is_frequent_ouput" in attributes:
                    cls.frequent_outputs.append((v,v.delay))

        return obj

    def __post_init__(self, predefined_commands: dict[str: Callable]=None):
        if predefined_commands is not None:
            # the self instance isn't assigned on the predefined_commands input
            self.commands |= {k:(v,self) for k, v in predefined_commands.items()}