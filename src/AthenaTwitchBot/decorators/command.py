# ----------------------------------------------------------------------------------------------------------------------
# - Package Imports -
# ----------------------------------------------------------------------------------------------------------------------
# General Packages
from __future__ import annotations

# Custom Library

# Custom Packages
from AthenaTwitchBot.models.wrapper_helpers.command import Command

# ----------------------------------------------------------------------------------------------------------------------
# - Code -
# ----------------------------------------------------------------------------------------------------------------------
def command_method(name:str, force_capitalization:bool=False):
    def decorator(fnc):
        def wrapper(*args_, **kwargs_):
            return fnc(*args_, **kwargs_)

        # store attributes for later use by the bot
        wrapper.is_command = True
        # store some information
        wrapper.cmd = Command(
            name=name,
            force_capitalization=force_capitalization,
            callback=wrapper,
        )

        return wrapper
    return decorator