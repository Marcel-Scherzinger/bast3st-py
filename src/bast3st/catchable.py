import enum


class err(enum.Flag):
    """
    Collection of all :ref:`catchable-errors` that can occur in any situation.

    As described in :class:`enum.Flag`, you can use bitwise operations to combine
    the error names from this type. Thisway, you can filter out arbitrary combinations
    of different error causes.

    Never rely on the exact numeric values of the following constants.
    They are not stable and not considered part of the api.
    """

    # network
    #: the status that was reported isn't among the ones in the allowed list
    network_statusDisallowed = enum.auto()
    #: a selector tried to extract json from the response,
    #: but the response is not json
    network_respInvalid_notJson = enum.auto()
    network = network_respInvalid_notJson | network_statusDisallowed
    """
    - :data:`network_respInvalid_notJson`
    - :data:`network_statusDisallowed`
    """

    # missingSelection
    missingSelection_input = enum.auto()
    missingSelection_output = enum.auto()
    #: a variable was requested that is missing, e.g. no variable with the specified name exists
    missingSelection_variable = enum.auto()
    #: a list was requested and the whole list is missing.
    #: If the list was requested by name, there is no list with this name.
    missingSelection_list_whole = enum.auto()
    #: the list exists but the requested item of the list does not
    missingSelection_list_item = enum.auto()
    missingSelection_list = missingSelection_list_whole | missingSelection_list_item
    """
    - :data:`missingSelection_list_item`
    - :data:`missingSelection_list_whole`
    """
    missingSelection = (
        missingSelection_list
        | missingSelection_output
        | missingSelection_input
        | missingSelection_variable
    )
    """
    - :data:`missingSelection_list`
    - :data:`missingSelection_output`
    - :data:`missingSelection_input`
    - :data:`missingSelection_variable`
    """

    regex_syntax = enum.auto()
    regex_noMatch = enum.auto()
    regex = regex_syntax | regex_noMatch
    """
    - :data:`regex_syntax`
    - :data:`regex_noMatch`
    """

    # any
    any = missingSelection | network | regex
    """
    - :data:`missingSelection`
    - :data:`network`
    - :data:`regex`
    """
