import typing
from collections import deque

from ..classes import UtilityBlock, JSONData, Arguments, Block, Bracket, BracketedBlock, DFLocation, Tag, DFNumber, \
    ItemCollection, DFVariable
from ..enums import BlockType, IfPlayerType, IfType, BracketDirection, BracketType, IfEntityType, \
    RepeatType, SetVarType, SelectObjectType, RAdjacentPattern
from ..reading.reader import DFReader
from ..constants import BLOCK_ID
from ..typings import Numeric, Textable, Listable, Locatable, p_check
from ..utils import remove_u200b_from_doc
from .ifs import IfPlayer, IfEntity, IfGame, IfVariable, IfBlock

AnyIf = typing.Union[IfPlayer, IfEntity, IfGame, IfVariable]


class Repeat(BracketedBlock, UtilityBlock, JSONData):
    """A Codeblock that repeats code inside it. Look for the humanized classmethods in the documentation.
    Example usage::

        @PlayerEvent.join
        def on_join():
            # ... code ...
            with Repeat.n_times(5):
                # ... code to repeat 5 times ...

            # ... more code, outside the Repeat ...

    Parameters
    ----------\u200b
    action : :class:`~py2df.enums.utilityblock.RepeatType`
        The type of Repeat.

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this Repeat block.

    sub_action : Optional[:class:`~py2df.enums.enum_util.IfType`]
        If ``action`` is :attr:`~py2df.enums.utilityblock.RepeatType.WHILE_COND`, then this is the If condition
        that determines if the Repeat will keep going. Defaults to ``None``.

    append_to_reader : :class:`bool`, optional
        Whether or not this newly-created :class:`Repeat` should be already appended to the
        :class:`~py2df.reading.reader.DFReader`. Defaults to ``False`` (is already done on __enter__).

    codeblocks : Iterable[:class:`~py2df.classes.abc.Block`], optional
        The blocks, including Brackets, inside this Repeat. Defaults to empty deque (None).

    invert : :class:`bool`, optional
            If this is a :attr:`~py2df.enums.utilityblock.RepeatType.WHILE_COND`, then this determines whether or not
            the Repeat should only occur while the condition is False (i.e., NOT). Defaults to ``False``.

    Attributes
    ----------\u200b
    block : :attr:`~py2df.enums.parameters.BlockType.REPEAT`
        The type of this codeblock (Repeat).

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this Repeat block.

    action : :class:`~py2df.enums.utilityblock.RepeatType`
        The type of Repeat.

    codeblocks : Deque[:class:`~py2df.classes.abc.Block`]
        The blocks, including Brackets, inside this Repeat.

    sub_action : Optional[:class:`~py2df.enums.enum_util.IfType`]
        If ``action`` is :attr:`~py2df.enums.utilityblock.RepeatType.WHILE_COND`, then this is the If condition
        that determines if the Repeat will keep going.

    invert : :class:`bool`
            If this is a :attr:`~py2df.enums.utilityblock.RepeatType.WHILE_COND`, then this determines whether or not
            the Repeat should only occur while the condition is False (i.e., NOT). Defaults to ``False``.

    length : :class:`int`
        The length of each individual Repeat (excluding brackets). This is always equal to 1.

    total_length : :class:`int`
        The sum of all lengths of all codeblocks inside this Repeat, including Repeat itself and brackets
        (so 3 + inner length).

    data : ``None``
        ('Repeat' has no extra codeblock data.)

    target : ``None``
        ('Repeat' has no target.)
    """
    __slots__ = ("action", "args", "codeblocks", "invert", "sub_action")

    block: BlockType = BlockType.REPEAT
    args: Arguments
    action: RepeatType
    codeblocks: typing.Deque[Block]
    invert: bool
    sub_action: typing.Optional[IfType]
    length: int = 1
    data: None = None
    target: None = None

    def __init__(
        self, action: RepeatType, args: Arguments, sub_action: typing.Optional[IfType] = None,
        *, append_to_reader: bool = False, codeblocks: typing.Iterable[Block] = None, invert: bool = False
    ):
        """
        Parameters
        ----------
        action : :class:`~py2df.enums.utilityblock.RepeatType`
            The condition to check.

        args : :class:`~py2df.classes.collections.Arguments`
            The arguments of this Repeat block.

        append_to_reader : :class:`bool`, optional
            Whether or not this newly-created :class:`RepeatPlayer` should be already appended to the
            :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.

        codeblocks : Iterable[:class:`~py2df.classes.abc.Block`], optional
            The blocks, including Brackets, inside this Repeat Player. Defaults to empty deque (None).

        invert : :class:`bool`, optional
            If this is a :attr:`~py2df.enums.utilityblock.RepeatType.WHILE_COND`, then this determines whether or not
            the Repeat should only occur while the condition is False (i.e., NOT). Defaults to ``False``.
        """
        self.action = RepeatType(action)
        self.args = Arguments(args)

        if append_to_reader:
            DFReader().append_codeblock(self)

        self.codeblocks = deque(codeblocks or [])

        self.sub_action = sub_action if self.action == RepeatType.WHILE_COND else None

        self.invert = invert and self.action == RepeatType.WHILE_COND

    def __enter__(self) -> "Repeat":
        """
        Triggers the creation of an opening bracket and the addition of all codeblocks into this Repeat.

        Returns
        -------
        :class:`Repeat`
            self (The current instance)
        """
        self.codeblocks.appendleft(Bracket(BracketDirection.OPEN, BracketType.REPEAT))
        reader = DFReader()

        if reader.curr_code_loc is not None and self not in reader.curr_code_loc:
            reader.append_codeblock(self)

        reader.curr_code_loc = self
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb) -> None:
        """
        Closes the Bracket, and resets the location of codeblocks (i.e., they now go outside the brackets).

        Returns
        -------
        ``None``
            ``None``
        """
        self.codeblocks.append(Bracket(BracketDirection.CLOSE, BracketType.REPEAT))
        DFReader().close_code_loc()

    def as_json_data(self) -> dict:
        """
        Produces a JSON-serializable dict representing this Repeat.

        Returns
        -------
        :class:`dict`
        """
        return dict(
            id=BLOCK_ID,
            block=self.block.value,
            args=self.args.as_json_data(),
            action=self.action.value,
            **(dict(
                sub_action=(
                    "E" if self.sub_action in (
                        IfEntityType.NAME_EQUALS, IfEntityType.IS_NEAR, IfEntityType.STANDING_ON
                    ) else ""  # ENameEquals; EIsNear; EStandingOn => separate from IfPlayer's.
                ) + str(self.sub_action.value)
            ) if self.sub_action else dict()),
            **(dict(inverted="NOT") if self.invert else dict())
        )

    def __neg__(self):
        return Repeat(
            self.action, self.args, append_to_reader=False, invert=-self.invert,
            codeblocks=self.codeblocks
        )

    def __invert__(self):
        return self.__neg__()

    # region:humanized_repeat

    @classmethod
    def adjacent(
        cls, var: DFVariable, center: Locatable,
        *, change_rotation: bool = False, include_origin: bool = False,
        pattern: RAdjacentPattern = RAdjacentPattern.ADJACENT
    ) -> "Repeat":
        """Repeats code once for each block adjacent to a location. Each iteration, the var is set to the current block.

        Parameters
        ----------
        var : :class:`~.DFVariable`
            The variable that represents the location of the current block on each iteration. Location.

        center : :attr:`~.Locatable`
            The center block around which to obtain the adjacent locations from.

        change_rotation : :class:`bool`, optional
            Whether or not the locations' respective pitches and yaws should be modified. Defaults to ``False``

        include_origin : :class:`bool`, optional
            Whether or not to include the origin/center block in the iteration. Defaults to ``False``

        pattern : :class:`~.RAdjacentPattern`
            The pattern to follow (Cardinal, Square, Adjacent or Cube). Defaults to
            :attr:`~py2df.enums.utilityblock.RAdjacentPattern.ADJACENT`

        Returns
        -------
        :class:`Repeat`
            The generated Repeat instance.

        Examples
        --------
        ::

            curr_loc = DFVariable("%default curr_loc", local=True)
            center = DFLocation(1, 2, 3)  # center that will determine the adjacent locations.
            with Repeat.adjacent(curr_loc, center, include_origin=False, pattern=RAdjacentPattern.CUBE):
                # code that will repeat for every location adjacent to 'center' in a cube format (curr_loc will be set\
to the current location on every iteration).
        """

        return cls(
            action=RepeatType.ADJACENT,
            args=Arguments(
                [var, p_check(center, Locatable, "center")],
                tags=[
                    Tag(
                        "Change Location Rotation", option=bool(change_rotation), action=RepeatType.ADJACENT,
                        block=BlockType.REPEAT
                    ),
                    Tag(
                        "Include Origin Block", option=bool(include_origin), action=RepeatType.ADJACENT,
                        block=BlockType.REPEAT
                    ),
                    Tag(
                        "Pattern", option=pattern, action=RepeatType.ADJACENT,
                        block=BlockType.REPEAT
                    )
                ]
            ),
            append_to_reader=False
        )

    @classmethod
    def for_each(cls, var: DFVariable, list_to_iterate: Listable, *, allow_list_changes: bool = True) -> "Repeat":
        """Repeats once for every element in a list. Every iteration the var is set to the value at
        the current index.

        Parameters
        ----------
        var : :class:`~.DFVariable`
            The variable that is set to the current list element on each iteration.

        list_to_iterate : :attr:`~.Listable`
            The list to iterate over.

        allow_list_changes : :class:`bool`, optional
            If the list should be able to be changed while the loop is running. Defaults to ``True`` (if ``False``, a
            copy of the list is used).

        Returns
        -------
        :class:`Repeat`
            The generated Repeat instance.

        Examples
        --------
        ::

            curr_el = DFVariable("%default curr_el", local=True)  # the current armor piece in the iteration
            armor_items = DFVariable("%default armor_items", DFGameValue(GameValueType.ARMOR_ITEMS))  # list of armor
            with Repeat.for_each(curr_el, armor_items, allow_list_changes=False):
                # code that iterates over all 4 of the Default Player's armor items. On every iteration, 'curr_el' is \
set to the current armor item being analyzed.
        """

        return cls(
            action=RepeatType.FOR_EACH,
            args=Arguments(
                [var, p_check(list_to_iterate, Listable)],
                tags=[Tag(
                    "Allow List Changes", option=True if allow_list_changes else "False (Use Copy of List)",
                    action=RepeatType.FOR_EACH, block=BlockType.REPEAT
                )]
            ),
            append_to_reader=False
        )

    @classmethod
    def forever(cls) -> "Repeat":
        """Repeats code forever (or until lagslayer or a control block stops it)

        Returns
        -------
        :class:`Repeat`
            The generated Repeat instance.

        Examples
        --------
        ::

            with Repeat.forever():
                # Repeat code forever
                Control.wait(20)  # wait 1 second every iteration (20 ticks)
        """

        return cls(
            action=RepeatType.FOREVER,
            args=Arguments(),
            append_to_reader=False
        )

    @classmethod
    def grid(cls, var: DFVariable, start_pos: Locatable, end_pos: Locatable) -> "Repeat":
        """Repeats code once for every block in a region. Each iteration, the var is set to the curr. block's location.

        Parameters
        ----------
        var : :class:`~.DFVariable`
            The variable that is set to the location of the current block on each iteration.

        start_pos : :attr:`~.Locatable`
            The start position of the region to repeat over.

        end_pos : :attr:`~.Locatable`
            The end position of the region to repeat over.

        Returns
        -------
        :class:`Repeat`
            The generated Repeat instance.

        Examples
        --------
        ::

            current_loc = DFVariable("current_loc", local=True)
            with Repeat.grid(current_loc, DFLocation(1, 2, 3), DFLocation(4, 5, 6)):
                # code to repeat for every block between x,y,z = {1, 2, 3} and {4, 5, 6} ('current_loc' gets set to \
the location of the current block).
        """

        return cls(
            action=RepeatType.GRID,
            args=Arguments([var, p_check(start_pos, Locatable, "start_pos"), p_check(end_pos, Locatable, "end_pos")]),
            append_to_reader=False
        )

    @classmethod
    def n_times(cls, amount: Numeric) -> "Repeat":
        """Repeats code multiple times.

        Parameters
        ----------
        amount : :attr:`~.Numeric`
            The amount of times to repeat.

        Returns
        -------
        :class:`Repeat`
            The generated Repeat instance.

        Examples
        --------
        ::

            with Repeat.n_times(5):
                # code to repeat 5 times in DiamondFire

            with Repeat.n_times(var):
                # code to repeat a variable amount of times in DiamondFire
        """

        return cls(
            action=RepeatType.N_TIMES,
            args=Arguments([p_check(amount, Numeric, "amount")]),
            append_to_reader=False
        )

    @classmethod
    def sphere(
        cls, var: DFVariable, center: Locatable, radius: Numeric, points: Numeric, *, point_locs_inwards: bool = False
    ) -> "Repeat":
        """Repeats code once for every evenly distributed sphere point.

        Parameters
        ----------
        var : :class:`~.DFVariable`
            The variable that is set to the location on each iteration.

        center : :attr:`~.Locatable`
            The center of the sphere.

        radius : :attr:`~.Numeric`
            The radius of the sphere, in blocks.

        points : :attr:`~.Numeric`
            The amount of points in the sphere ("resolution").

        point_locs_inwards : :class:`bool`, optional
            Whether or not the locations should have their pitches and yaws changed to always point to the center.
            Defaults to ``False``

        Returns
        -------
        :class:`Repeat`
            The generated Repeat instance.

        Examples
        --------
        ::

            curr_loc = DFVariable("%default curr_loc", local=True)
            center = DFLocation(1, 2, 3)  # could be a variable as well, game value etc.
            with Repeat.sphere(curr_loc, center, 5, 200, point_locs_inwards=True):
                # code that will repeat for every point of 200 points forming a sphere of radius 5 blocks. ('curr_loc' \
is set to the current iterated location.)
        """

        return cls(
            action=RepeatType.SPHERE,
            args=Arguments(
                [var, p_check(center, Locatable, "center"),
                 p_check(radius, Numeric, "radius"), p_check(points, Numeric, "points")],
                tags=[Tag(
                    "Point Locations Inwards",
                    option=bool(point_locs_inwards),
                    action=RepeatType.SPHERE,
                    block=BlockType.REPEAT
                )]
            ),
            append_to_reader=False
        )

    @classmethod
    def while_cond(cls, cond: AnyIf) -> "Repeat":
        """Repeats code while a certain condition is true.

        Parameters
        ----------
        cond : :class:`~.IfBlock`
            The condition that will determine if this loop will continue to run. Note that this must be a
            pre-made If block.

        Returns
        -------
        :class:`Repeat`
            The generated Repeat instance.

        Raises
        ------
        :exc:`TypeError`
            If the condition given was not an If Block (:class:`~.IfPlayer`, :class:`~.IfEntity`, :class:`~.IfGame` or
            :class:`~.IfVariable`).

        Examples
        --------
        ::

            with Repeat.while_cond(var_a == var_b):
                # code that will execute in DF while 'var_a' is equal to 'var_b'
        """
        if not isinstance(cond, IfBlock) or type(cond) == IfBlock:  # must not be a raw 'IfBlock'
            raise TypeError("Condition must be a valid If block (IfPlayer, IfEntity, IfGame, IfVariable).")

        args = cond.args
        sub_action = cond.action
        invert = cond.invert

        return cls(
            action=RepeatType.WHILE_COND,
            args=Arguments(args),
            sub_action=sub_action,
            append_to_reader=False,
            invert=bool(invert)
        )

    # endregion:humanized_repeat


class SetVar(UtilityBlock, JSONData):
    """Used to set the value of a dynamic variable.

    Parameters
    ----------\u200b
    action : :class:`~py2df.enums.utilityblock.SetVarType`
        The type of SetVar block this is.

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this SetVar block.

    append_to_reader : :class:`bool`, optional
        Whether or not this newly-created :class:`SetVar` should be already appended to the
        :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.

    Attributes
    ----------\u200b
    block : :attr:`~py2df.enums.parameters.BlockType.ENTITY_ACTION`
        The type of this codeblock (SetVar).

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this SetVar block.

    action : :class:`~py2df.enums.utilityblock.SetVarType`
        The type of SetVar block this is.

    sub_action : ``None``
        (SetVar blocks have no sub actions.)

    length : :class:`int`
        The length, in blocks, of each individual control blocks. This is always equal to 2.

    data : ``None``
        (SetVar blocks have no extra codeblock data.)

    target : ``None``
        (SetVar blocks have no target.)
    """
    __slots__ = ("args", "action")

    block: BlockType = BlockType.SET_VAR
    args: Arguments
    action: SetVarType
    sub_action: None = None
    length: int = 2
    data: None = None
    target: None = None

    def __init__(
        self, action: SetVarType, args: Arguments = Arguments(),
        *, append_to_reader: bool = True
    ):
        """
        Initialize this SetVar block.

        Parameters
        ----------
        action : :class:`~py2df.enums.utilityblock.SetVarType`
            The type of SetVar block this is.

        args : :class:`~py2df.classes.collections.Arguments`
            The arguments of this SetVar block.

        append_to_reader : :class:`bool`, optional
            Whether or not this newly-created :class:`SetVar` should be already appended to the
            :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``. (All classmethods will set this to ``True``)
        """
        self.action = SetVarType(action)
        self.args = args

        if append_to_reader:
            DFReader().append_codeblock(self)

    def as_json_data(self) -> dict:
        """Produces a JSON-serializable dict representing this SetVar block.

        Returns
        -------
        :class:`dict`
        """
        return dict(
            id=BLOCK_ID,
            block=self.block.value,
            args=self.args.as_json_data(),
            action=self.action.value
        )


class SelectObj(UtilityBlock, JSONData):
    """Used to change the selection on the current line of code, which will affect the targets of most code blocks.

    Example usage::

        @PlayerEvent.join
        def on_join():
            # ... code ...
            SelectObj.all_players()  # selects all players
            SelectObj.none()  # selects nothing
            # ...

    Parameters
    ----------\u200b
    action : :class:`~py2df.enums.utilityblock.SelectObjectType`
        The new selection, which will be the type of Select Object block.

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this SelectObj block.

    sub_action : Optional[:class:`~py2df.enums.enum_util.IfType`], optional
        If the SelectObj type is one of :attr:`~py2df.enums.utilityblock.SelectObjectType.ENTITIES_COND`,
        :attr:`~py2df.enums.utilityblock.SelectObjectType.MOBS_COND` or
        :attr:`~py2df.enums.utilityblock.SelectObjectType.PLAYERS_COND`, then this attribute represents the specific
        condition that determines whether an entity/mob/player is selected or not. Otherwise, this is ``None``.
        Defaults to ``None``.

    append_to_reader : :class:`bool`, optional
        Whether or not this newly-created :class:`SelectObj` should be already appended to the
        :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.

    invert : :class:`bool`, optional
        If this is a SelectObj with a condition (see :attr:`sub_action`), then this determines whether or not
        the Select Obj should only select entities/mob/player for whom the condition is False (i.e., NOT).
        Defaults to ``False``.

    Attributes
    ----------\u200b
    block : :attr:`~py2df.enums.parameters.BlockType.SELECT_OBJ`
         The new selection, which will be the type of Select Object block.

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this SelectObj block.

    action : :class:`~py2df.enums.utilityblock.SelectObjectType`
        The type of SelectObj block this is.

    sub_action : Optional[:class:`~py2df.enums.enum_util.IfType`]
        If the SelectObj type is one of :attr:`~py2df.enums.utilityblock.SelectObjectType.ENTITIES_COND`,
        :attr:`~py2df.enums.utilityblock.SelectObjectType.MOBS_COND` or
        :attr:`~py2df.enums.utilityblock.SelectObjectType.PLAYERS_COND`, then this attribute represents the specific
        condition that determines whether an entity/mob/player is selected or not. Otherwise, this is ``None``.

    invert : :class:`bool`
        If this is a SelectObj with a condition (see :attr:`sub_action`), then this determines whether or not
        the Select Obj should only select entities/mob/player for whom the condition is False (i.e., NOT).
        Defaults to ``False``.

    length : :class:`int`
        The length, in blocks, of each individual control blocks. This is always equal to 2.

    data : ``None``
        (SelectObj blocks have no extra codeblock data.)

    target : ``None``
        (SelectObj blocks have no target.)
    """
    __slots__ = ("args", "action", "sub_action", "invert")

    block: BlockType = BlockType.SELECT_OBJ
    args: Arguments
    action: SelectObjectType
    invert: bool
    sub_action: typing.Optional[IfType]
    length: int = 2
    data: None = None
    target: None = None

    def __init__(
        self, action: SelectObjectType, args: Arguments = Arguments(), sub_action: typing.Optional[IfType] = None,
        *, append_to_reader: bool = True, invert: bool = False
    ):
        """
        Initialize this SelectObj block.

        Parameters
        ----------
        action : :class:`~py2df.enums.utilityblock.SelectObjectType`
            The type of SelectObj block this is.

        args : :class:`~py2df.classes.collections.Arguments`
            The arguments of this SelectObj block.

        sub_action : Optional[:class:`~py2df.enums.enum_util.IfType`], optional
            If the SelectObj type is one of :attr:`~py2df.enums.utilityblock.SelectObjectType.ENTITIES_COND`,
            :attr:`~py2df.enums.utilityblock.SelectObjectType.MOBS_COND` or
            :attr:`~py2df.enums.utilityblock.SelectObjectType.PLAYERS_COND`, then this attribute represents the specific
            condition that determines whether an entity/mob/player is selected or not. Otherwise, this is ``None``.
            Defaults to ``None``.

        append_to_reader : :class:`bool`, optional
            Whether or not this newly-created :class:`SelectObj` should be already appended to the
            :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.

        invert : :class:`bool`, optional
            If this is a SelectObj with a condition (see :attr:`sub_action`), then this determines whether or not
            the Select Obj should only select entities/mob/player for whom the condition is False (i.e., NOT).
            Defaults to ``False``.
        """
        self.action = SelectObjectType(action)
        self.args = args

        if append_to_reader:
            DFReader().append_codeblock(self)

        if self.action in (SelectObjectType.ENTITIES_COND, SelectObjectType.MOBS_COND, SelectObjectType.PLAYERS_COND):
            self.sub_action = sub_action
        else:
            self.sub_action = None

        self.invert = invert and self.action in (
            SelectObjectType.ENTITIES_COND, SelectObjectType.MOBS_COND, SelectObjectType.PLAYERS_COND
        )

    def as_json_data(self) -> dict:
        """Produces a JSON-serializable dict representing this SelectObj block.

        Returns
        -------
        :class:`dict`
        """
        return dict(
            id=BLOCK_ID,
            block=self.block.value,
            args=self.args.as_json_data(),
            action=self.action.value,
            **(dict(
                subAction=(
                    "E" if self.sub_action in (
                        IfEntityType.NAME_EQUALS, IfEntityType.IS_NEAR, IfEntityType.STANDING_ON
                    ) else ""  # ENameEquals; EIsNear; EStandingOn => separate from IfPlayer's.
                ) + str(self.sub_action.value)
            ) if self.sub_action else dict())
        )

    def __neg__(self):
        return SelectObj(
            self.action, self.args, self.sub_action, append_to_reader=False, invert=-self.invert
        )

    def __invert__(self):
        return self.__neg__()

    # region:humanized_selobj

    @classmethod
    def all_entities(cls) -> "SelectObj":
        """Selects all entities on the plot.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.all_entites()
        """
        return cls(
            SelectObjectType.ALL_ENTITIES,
            append_to_reader=True
        )

    @classmethod
    def all_mobs(cls) -> "SelectObj":
        """Selects all mobs on the plot.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.all_mobs()
        """
        return cls(
            SelectObjectType.ALL_MOBS,
            append_to_reader=True
        )

    @classmethod
    def all_players(cls) -> "SelectObj":
        """Selects all players that are on the plot.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.all_players()
        """
        return cls(
            SelectObjectType.ALL_PLAYERS,
            append_to_reader=True
        )

    @classmethod
    def damager(cls) -> "SelectObj":
        """Selects the damager in a damage-related event. The damager can be a player or an entity.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.damager()
        """
        return cls(
            SelectObjectType.DAMAGER,
            append_to_reader=True
        )

    @classmethod
    def default_entity(cls) -> "SelectObj":
        """Selects the main entity involved in the current Player/Entity Event, or the last spawned entity if none.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.default_entity()
        """
        return cls(
            SelectObjectType.DEFAULT_ENTITY,
            append_to_reader=True
        )

    @classmethod
    def default_player(cls) -> "SelectObj":
        """Selects the main player involved in the current Player Event or Loop.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.default_player()
        """
        return cls(
            SelectObjectType.DEFAULT_PLAYER,
            append_to_reader=True
        )

    @classmethod
    def entities_by_cond(cls, cond: AnyIf) -> "SelectObj":
        """Selects all entities that meet a certain condition.

        Parameters
        ----------
        cond : :class:`~py2df.codeblocks.ifs.IfBlock`
            The condition with which to match entities.
        
        Warnings
        --------
        This does not select players.

        Raises
        ------
        :exc:`TypeError`
            If the condition given was not an If Block (:class:`~.IfPlayer`, :class:`~.IfEntity`, :class:`~.IfGame` or
            :class:`~.IfVariable`).

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.entities_by_cond(entity.is_projectile())  # selects projectiles
            SelectObj.entities_by_cond(entity.exists())  # selects existing entities
        """
        if not isinstance(cond, IfBlock) or type(cond) == IfBlock:  # must not be a raw 'IfBlock'
            raise TypeError("Condition must be a valid If block (IfPlayer, IfEntity, IfGame, IfVariable).")

        return cls(
            SelectObjectType.ENTITIES_COND,
            args=cond.args,
            sub_action=cond.action,
            append_to_reader=True,
            invert=bool(cond.invert)
        )

    @classmethod
    def entity_name(cls, name: Textable) -> "SelectObj":
        """Selects all entities whose names are equal to the text specified.

        Parameters
        ----------
        name : :attr:`~.Textable`
            The name of the entity or entities to select.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.entity_name("my entity")  # selects all entities named "my entity"
        """
        return cls(
            SelectObjectType.ENTITY_NAME,
            args=Arguments([p_check(name, Textable, "name")]),
            append_to_reader=True
        )

    @classmethod
    def filter_selection(cls, cond: AnyIf) -> "SelectObj":
        """Filters the current selection by selecting all objects that meet a certain condition.
        
        Parameters
        ----------
        cond : :class:`~py2df.codeblocks.ifs.IfBlock`
            The condition with which to filter the current selection.

        Raises
        ------
        :exc:`TypeError`
            If the condition given was not an If Block (:class:`~.IfPlayer`, :class:`~.IfEntity`, :class:`~.IfGame` or
            :class:`~.IfVariable`).

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.filter_selection(entity.is_projectile())  # filters selection to consist only of projectiles
            # if no projectiles were selected, the selection will, then, become empty
        """
        if not isinstance(cond, IfBlock) or type(cond) == IfBlock:  # must not be a raw 'IfBlock'
            raise TypeError("Condition must be a valid If block (IfPlayer, IfEntity, IfGame, IfVariable).")
        
        return cls(
            SelectObjectType.FILTER_SELECT,
            args=cond.args,
            sub_action=cond.action,
            append_to_reader=True,
            invert=bool(cond.invert)
        )

    @classmethod
    def killer(cls) -> "SelectObj":
        """Selects the killer in a kill-related event. The killer can be a player or an entity.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.killer()  # selects the killer entity/player
        """
        return cls(
            SelectObjectType.KILLER,
            append_to_reader=True
        )

    @classmethod
    def last_entity(cls) -> "SelectObj":
        """Selects the most recently spawned entity.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.last_entity()  # selects the last spawned entity
        """
        return cls(
            SelectObjectType.LAST_ENTITY,
            append_to_reader=True
        )

    @classmethod
    def last_mob(cls) -> "SelectObj":
        """Selects the most recently spawned mob.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.last_mob()  # selects the last spawned mob
        """
        return cls(
            SelectObjectType.LAST_MOB,
            append_to_reader=True
        )

    @classmethod
    def mob_name(cls, name: Textable) -> "SelectObj":
        """Selects all mobs whose names are equal to the text specified.

        Parameters
        ----------
        name : :attr:`~.Textable`
            The name of the mob(s) to select.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.entity_name("my mob")  # selects all mobs named "my mob"
        """
        return cls(
            SelectObjectType.MOB_NAME,
            args=Arguments([p_check(name, Textable, "name")]),
            append_to_reader=True
        )

    @classmethod
    def mobs_by_cond(cls, cond: AnyIf) -> "SelectObj":
        """Selects all mobs that meet a certain condition.

        Parameters
        ----------
        cond : :class:`~py2df.codeblocks.ifs.IfBlock`
            The condition with which to match mobs.

        Raises
        ------
        :exc:`TypeError`
            If the condition given was not an If Block (:class:`IfPlayer`, :class:`IfEntity`, :class:`IfGame` or
            :class:`IfVariable`).

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            gold_block = Material.GOLD_BLOCK
            SelectObj.filter_selection(entity.standing_on(gold_block))  # select all mobs standing on a gold block
        """
        if not isinstance(cond, IfBlock) or type(cond) == IfBlock:  # must not be a raw 'IfBlock'
            raise TypeError("Condition must be a valid If block (IfPlayer, IfEntity, IfGame, IfVariable).")

        return cls(
            SelectObjectType.MOBS_COND,
            args=cond.args,
            sub_action=cond.action,
            append_to_reader=True,
            invert=bool(cond.invert)
        )

    @classmethod
    def none(cls) -> "SelectObj":
        """Selects nothing. All code blocks will act like they normally would if nothing was selected.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.none()  # selection is now empty
        """
        return cls(
            SelectObjectType.NONE,
            append_to_reader=True
        )

    @classmethod
    def player_name(cls, name: Textable) -> "SelectObj":
        """Selects the player whose name is equal to the text specified.

        Parameters
        ----------
        name : :attr:`~.Textable`
            The username(s)/UUID(s) of the player(s) to select.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.player_name("Rob")  # selects player "Rob"
        """
        return cls(
            SelectObjectType.PLAYER_NAME,
            args=Arguments([p_check(name, Textable, "name")]),
            append_to_reader=True
        )

    @classmethod
    def players_by_cond(cls, cond: AnyIf) -> "SelectObj":
        """Selects all players that meet a certain condition.

        Parameters
        ----------
        cond : :class:`~py2df.codeblocks.ifs.IfBlock`
            The condition with which to match players.

        Raises
        ------
        :exc:`TypeError`
            If the condition given was not an If Block (:class:`IfPlayer`, :class:`IfEntity`, :class:`IfGame` or
            :class:`IfVariable`).

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            diamond_block = Material.DIAMOND_BLOCK
            SelectObj.filter_selection(player.standing_on(diamond_block))  # selects players standing on a diamond block
        """
        if not isinstance(cond, IfBlock) or type(cond) == IfBlock:  # must not be a raw 'IfBlock'
            raise TypeError("Condition must be a valid If block (IfPlayer, IfEntity, IfGame, IfVariable).")

        return cls(
            SelectObjectType.PLAYERS_COND,
            args=cond.args,
            sub_action=cond.action,
            append_to_reader=True,
            invert=bool(cond.invert)
        )

    @classmethod
    def projectile(cls) -> "SelectObj":
        """Selects the projectile in a projectile-related event.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.projectile()  # selects the projectile in question
        """
        return cls(
            SelectObjectType.PROJECTILE,
            append_to_reader=True
        )

    @classmethod
    def random_entity(cls) -> "SelectObj":
        """Selects a random entity.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.random_entity()  # selects a random entity
        """
        return cls(
            SelectObjectType.RANDOM_ENTITY,
            append_to_reader=True
        )

    @classmethod
    def random_mob(cls) -> "SelectObj":
        """Selects a random mob.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.random_mob()  # selects a random mob
        """
        return cls(
            SelectObjectType.RANDOM_MOB,
            append_to_reader=True
        )

    @classmethod
    def random_player(cls) -> "SelectObj":
        """Selects a random player.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.random_player()  # selects a random player
        """
        return cls(
            SelectObjectType.RANDOM_PLAYER,
            append_to_reader=True
        )

    @classmethod
    def select_randomly(cls, amount: Numeric) -> "SelectObj":
        """Filters the current selection by selecting one or more random objects from it.

        Parameters
        ----------
        amount : :attr:`~.Numeric`
            Number of objects to randomly select from the previous selection.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.select_randomly(5)  # randomly picks 5 previously selected objects to become the new selection
        """
        return cls(
            SelectObjectType.RANDOM_SELECTED,
            args=Arguments([p_check(amount, Numeric, "amount")]),
            append_to_reader=True
        )

    @classmethod
    def shooter(cls) -> "SelectObj":
        """Selects the shooter in a projectile-related event.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.shooter()  # selects the shooter
        """
        return cls(
            SelectObjectType.SHOOTER,
            append_to_reader=True
        )

    @classmethod
    def victim(cls) -> "SelectObj":
        """Selects the victim in a kill-related or damage-related event. The victim can be a player or an entity.

        Returns
        -------
        :class:`SelectObj`
            The generated SelectObj instance.

        Examples
        --------
        ::

            SelectObj.victim()  # selects the victim entity/player
        """
        return cls(
            SelectObjectType.VICTIM,
            append_to_reader=True
        )

    # endregion:humanized_selobj


remove_u200b_from_doc(Repeat, SetVar, SelectObj)
