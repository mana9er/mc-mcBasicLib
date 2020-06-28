from .basic import McBasicLib


def load(logger, core):
    # Function "load" is required by mana9er-core.
    return BasicLib(logger, core)
