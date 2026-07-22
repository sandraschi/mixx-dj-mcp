"""mixx-dj-mcp tool registration - portmanteau imports."""


def register_all_tools(mcp):
    from .deck_control import register_deck_tools
    from .effects import register_effects_tools
    from .library import register_library_tools
    from .mixer import register_mixer_tools
    from .prefab_cards import register_prefab_tools
    from .set_sequencer import register_sequencer_tools
    from .skin_manager import register_skin_tools
    from .smart_crate import register_crate_tools

    register_deck_tools(mcp)
    register_library_tools(mcp)
    register_effects_tools(mcp)
    register_mixer_tools(mcp)
    register_prefab_tools(mcp)
    register_sequencer_tools(mcp)
    register_skin_tools(mcp)
    register_crate_tools(mcp)
