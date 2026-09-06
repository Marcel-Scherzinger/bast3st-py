import enum


class err(enum.Flag):
    # NETWORK
    network_statusDisallowed = enum.auto()
    network_respInvalid_notJson = enum.auto()
    network = network_respInvalid_notJson | network_statusDisallowed

    missingSelection_input = enum.auto()
    missingSelection_output = enum.auto()

    #: A list was requested and the whole list is missing.
    #: If the list was requested by name, there is no list with this name.
    missingSelection_list_whole = enum.auto()
    #: The list exists but the requested item of the list does not
    missingSelection_list_item = enum.auto()

    missingSelection = (
        missingSelection_list_whole
        | missingSelection_list_item
        | missingSelection_output
        | missingSelection_input
    )
    any = missingSelection | network
