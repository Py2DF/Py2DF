import collections
import typing
from collections import deque
from abc import abstractmethod

from ..errors import DFSyntaxError
from ..enums import (
    PlayerTarget, EntityTarget, BlockType, IfPlayerType, IfEntityType, IfGameType, IfVariableType,
    SelectionTarget,
    BracketDirection, BracketType, IfType, Material, ItemEqComparisonMode)
from ..classes import JSONData, Arguments, BracketedBlock, Block, Bracket, DFVariable, DFGameValue, Tag, DFText, Item, \
    ItemCollection
from ..utils import remove_u200b_from_doc, flatten
from ..constants import BLOCK_ID, DEFAULT_VAL
from ..reading.reader import DFReader
from ..typings import Locatable, Textable, p_check, ItemParam, Numeric, Listable
from ._block_utils import BlockParam, BlockMetadata, _load_metadata, _load_btypes


class IfBlock(BracketedBlock, JSONData):
    """An ABC representing an If Block. Executes code if a certain condition is met.

    Parameters
    ----------\u200b
    action : :class:`~py2df.enums.actions.IfType`
        The condition to check.

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this If block.

    target : Optional[:class:`~py2df.enums.targets.Target`], optional
        The target of this If, if there exists. If this is None, DiamondFire will default to the current selection
        (if exists) or it will be ignored (if it doesn't, as occurs in 'If Game' and 'If Var')

    append_to_reader : :class:`bool`, optional
        Whether or not this newly-created If should be already appended to the
        :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.

    invert : :class:`bool`, optional
        If ``True`` , then this If's code will only execute when the condition is false (i.e., applies NOT).
        Default: ``False``

    codeblocks : Iterable[:class:`~py2df.classes.abc.Block`], optional
        The blocks, including Brackets, inside this If. Defaults to empty deque (None).

    Attributes
    ----------\u200b
    block : Union[:attr:`~py2df.enums.parameters.IF_PLAYER`, :attr:`~py2df.enums.parameters.IF_ENTITY`, \
:attr:`~py2df.enums.parameters.IF_GAME`, :attr:`~py2df.enums.parameters.IF_VAR`]
        The type of this codeblock.

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this If block.

    action : :class:`~py2df.enums.actions.IfType`
        The condition to check.

    codeblocks : Deque[:class:`~py2df.classes.abc.Block`]
        The blocks, including Brackets, inside this If.

    invert : :class:`bool`
        If ``True`` , then this If's code will only execute when the condition is false (i.e., applies NOT).
        Default: ``False``

    sub_action : ``None``
        ('If' has no sub actions.)

    length : :class:`int`
        The length of each individual If (excluding brackets). This is always equal to 1.

    total_length : :class:`int`
        The sum of all lengths of all codeblocks inside this If, including If itself and brackets (so 3 + inner length).

    data : ``None``
        ('If' has no extra codeblock data.)

    target : Optional[:class:`~py2df.enums.targets.Target`]
        The target of this If, or ``None`` for current selection (if there exists) or in case of there not being
        any target (e.g. 'If Game').
    """
    __slots__ = ()

    block: BlockType = NotImplemented
    args: Arguments
    action: IfType
    codeblocks: typing.Deque[Block]
    invert: bool
    sub_action: None = None
    length: int = 1
    data: None = None
    target: typing.Optional[PlayerTarget]

    def __enter__(self) -> "IfBlock":
        """
        Triggers the creation of an opening bracket and the addition of all codeblocks into this If block.

        Returns
        -------
        :class:`IfBlock`
            self (The current instance)
        """
        self.codeblocks.appendleft(Bracket(BracketDirection.OPEN, BracketType.NORM))
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
        self.codeblocks.append(Bracket(BracketDirection.CLOSE, BracketType.NORM))
        DFReader().close_code_loc()

    def as_json_data(self) -> dict:
        """
        Produces a JSON-serializable dict representing this If.

        Returns
        -------
        :class:`dict`
        """
        return dict(
            id=BLOCK_ID,
            block=self.block.value,
            args=self.args.as_json_data(),
            action=self.action.value,
            **(dict(target=self.target.value) if self.target else dict()),
            **(dict(inverted="NOT") if self.invert else dict())
        )

    @abstractmethod  # abstract because of custom inits. This has to call init.
    def __neg__(self):
        raise NotImplementedError

    def __invert__(self):
        return self.__neg__()


class IfPlayer(IfBlock):
    """An If Player block. Executes code if a certain condition related to a player is met.

    Parameters
    ----------\u200b
    action : :class:`~py2df.enums.actions.IfPlayerType`
        The condition to check on the player.

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this If Player.

    target : Optional[:class:`~py2df.enums.targets.PlayerTarget`], optional
        The target of this If Player. If this is None, DiamondFire will default to the current selection.

    append_to_reader : :class:`bool`, optional
        Whether or not this newly-created :class:`IfPlayer` should be already appended to the
        :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.

    invert : :class:`bool`, optional
        If ``True`` , then this If Player's code will only execute when the condition is false (i.e., applies NOT).
        Default: ``False``

    codeblocks : Iterable[:class:`~py2df.classes.abc.Block`], optional
        The blocks, including Brackets, inside this If Player. Defaults to empty deque (None).

    Attributes
    ----------\u200b
    block : :attr:`~py2df.enums.parameters.BlockType.IF_PLAYER`
        The type of this codeblock (If Player).

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this If Player.

    action : :class:`~py2df.enums.actions.IfPlayerType`
        The condition to check.

    codeblocks : Deque[:class:`~py2df.classes.abc.Block`]
        The blocks, including Brackets, inside this If Player.

    invert : :class:`bool`
        If ``True`` , then this If Player's code will only execute when the condition is false (i.e., applies NOT).
        Default: ``False``

    sub_action : ``None``
        (If Player has no sub actions.)

    length : :class:`int`
        The length of each individual If Player (excluding brackets). This is always equal to 1.

    data : ``None``
        (If Player has no extra codeblock data.)

    target : Optional[:class:`~py2df.enums.targets.PlayerTarget`]
        The target of this If Player, or ``None`` for current selection.
    """
    __slots__ = ("args", "action", "target", "invert", "codeblocks")

    block: BlockType = BlockType.IF_PLAYER
    args: Arguments
    action: IfPlayerType
    codeblocks: typing.Deque[Block]
    invert: bool
    sub_action: None = None
    length: int = 1
    data: None = None
    target: typing.Optional[PlayerTarget]

    def __init__(
        self, action: IfPlayerType, args: Arguments = Arguments(),
        target: typing.Union[PlayerTarget, SelectionTarget] = DEFAULT_VAL,
        *, append_to_reader: bool = False, invert: bool = False, codeblocks: typing.Iterable[Block] = None
    ):
        """
        Initialize this If Player.

        Parameters
        ----------
        action : :class:`~py2df.enums.actions.IfPlayerType`
            The type of If Player this is.

        args : :class:`~py2df.classes.collections.Arguments`
            The arguments of this If Player.

        target : :class:`~py2df.enums.targets.PlayerTarget`, optional
            The target of this If Player. Defaults to :attr:`~py2df.enums.targets.PlayerTarget.DEFAULT` (Default
            Player).

        append_to_reader : :class:`bool`, optional
            Whether or not this newly-created :class:`IfPlayer` should already be appended to the
            :class:`~py2df.reading.reader.DFReader`. Defaults to ``False`` (because it is already appended
            when :meth:`~IfPlayer.__enter__` is called).

        invert : :class:`bool`, optional
            If ``True`` , then this If Player's code will only execute when the condition is false (i.e., applies NOT).
            Default: ``False``

        codeblocks : Iterable[:class:`~py2df.classes.abc.Block`], optional
            The blocks, including Brackets, inside this If Player. Defaults to empty deque (None).
        """
        self.action = IfPlayerType(action)
        self.args = args
        self.target = PlayerTarget(
            target.value if SelectionTarget in (target, type(target)) else target
        ) if target else None

        self.codeblocks = deque(codeblocks) if codeblocks else deque()
        self.invert = invert

        if append_to_reader:
            DFReader().append_codeblock(self)

    def __neg__(self):
        return IfPlayer(
            self.action, self.args, self.target, append_to_reader=False, invert=-self.invert,
            codeblocks=self.codeblocks
        )


class IfEntity(IfBlock):
    """An If Entity block. Executes code if a certain condition related to a entity is met.

    Parameters
    ----------\u200b
    action : :class:`~py2df.enums.actions.IfEntityType`
        The condition to check on the entity.

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this If Entity.

    target : Optional[:class:`~py2df.enums.targets.EntityTarget`], optional
        The target of this If Entity. If this is None, DiamondFire will default to the current selection.

    append_to_reader : :class:`bool`, optional
        Whether or not this newly-created :class:`IfEntity` should be already appended to the
        :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.

    invert : :class:`bool`, optional
        If ``True`` , then this If Entity's code will only execute when the condition is false (i.e., applies NOT).
        Default: ``False``

    codeblocks : Iterable[:class:`~py2df.classes.abc.Block`], optional
        The blocks, including Brackets, inside this If Entity. Defaults to empty deque (None).

    Attributes
    ----------\u200b
    block : :attr:`~py2df.enums.parameters.BlockType.IF_ENTITY`
        The type of this codeblock (If Entity).

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this If Entity.

    action : :class:`~py2df.enums.actions.IfEntityType`
        The condition to check.

    codeblocks : Deque[:class:`~py2df.classes.abc.Block`]
        The blocks, including Brackets, inside this If Entity.

    invert : :class:`bool`
        If ``True`` , then this If Entity's code will only execute when the condition is false (i.e., applies NOT).
        Default: ``False``

    sub_action : ``None``
        (If Entity has no sub actions.)

    length : :class:`int`
        The length of each individual If Entity (excluding brackets). This is always equal to 1.

    data : ``None``
        (If Entity has no extra codeblock data.)

    target : Optional[:class:`~py2df.enums.targets.EntityTarget`]
        The target of this If Entity, or ``None`` for current selection.
    """
    __slots__ = ("args", "action", "target", "invert", "codeblocks")

    block: BlockType = BlockType.IF_ENTITY
    args: Arguments
    action: IfEntityType
    codeblocks: typing.Deque[Block]
    invert: bool
    sub_action: None = None
    length: int = 1
    data: None = None
    target: typing.Optional[EntityTarget]

    def __init__(
        self, action: IfEntityType, args: Arguments = Arguments(),
        target: typing.Union[EntityTarget, SelectionTarget] = DEFAULT_VAL,
        *, append_to_reader: bool = False, invert: bool = False, codeblocks: typing.Iterable[Block] = None
    ):
        """
        Initialize this If Entity.

        Parameters
        ----------
        action : :class:`~py2df.enums.actions.IfEntityType`
            The type of If Entity this is.

        args : :class:`~py2df.classes.collections.Arguments`
            The arguments of this If Entity.

        target : :class:`~py2df.enums.targets.EntityTarget`, optional
            The target of this If Entity. Defaults to :attr:`~py2df.enums.targets.EntityTarget.DEFAULT` (Default
            Entity).

        append_to_reader : :class:`bool`, optional
            Whether or not this newly-created :class:`IfEntity` should already be appended to the
            :class:`~py2df.reading.reader.DFReader`. Defaults to ``False`` (because it is already appended
            when :meth:`~IfEntity.__enter__` is called).

        invert : :class:`bool`, optional
            If ``True`` , then this If Entity's code will only execute when the condition is false (i.e., applies NOT).
            Default: ``False``

        codeblocks : Deque[:class:`~py2df.classes.abc.Block`], optional
            The blocks, including Brackets, inside this If Entity. Defaults to empty deque (None).
        """
        self.action = IfEntityType(action)
        self.args = args
        self.target = EntityTarget(
            target.value if SelectionTarget in (target, type(target)) else target
        ) if target else None

        self.codeblocks = deque(codeblocks) if codeblocks else deque()
        self.invert = invert

        if append_to_reader:
            DFReader().append_codeblock(self)

    def __neg__(self):
        return IfEntity(
            self.action, self.args, self.target, append_to_reader=False, invert=-self.invert,
            codeblocks=self.codeblocks
        )


class IfGame(IfBlock):
    """An If Game block. Executes code if a certain condition related to the game (state of the plot, a block etc.)
    is met.

    Parameters
    ----------\u200b
    action : :class:`~py2df.enums.actions.IfGameType`
        The condition to check.

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this If Game.

    append_to_reader : :class:`bool`, optional
        Whether or not this newly-created :class:`IfGame` should be already appended to the
        :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.

    invert : :class:`bool`, optional
        If ``True`` , then this If Game's code will only execute when the condition is false (i.e., applies NOT).
        Default: ``False``

    codeblocks : Iterable[:class:`~py2df.classes.abc.Block`], optional
        The blocks, including Brackets, inside this If Game. Defaults to empty deque (None).

    Attributes
    ----------\u200b
    block : :attr:`~py2df.enums.parameters.BlockType.IF_GAME`
        The type of this codeblock (If Game).

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this If Game.

    action : :class:`~py2df.enums.actions.IfGameType`
        The condition to check.

    codeblocks : Deque[:class:`~py2df.classes.abc.Block`]
        The blocks, including Brackets, inside this If Game.

    invert : :class:`bool`
        If ``True`` , then this If Game's code will only execute when the condition is false (i.e., applies NOT).
        Default: ``False``

    sub_action : ``None``
        (If Game has no sub actions.)

    length : :class:`int`
        The length of each individual If Game (excluding brackets). This is always equal to 1.

    data : ``None``
        (If Game has no extra codeblock data.)

    target : ``None``
        (If Game has no target.)
    """
    __slots__ = ("args", "action", "invert", "codeblocks")

    block: BlockType = BlockType.IF_GAME
    args: Arguments
    action: IfGameType
    codeblocks: typing.Deque[Block]
    invert: bool
    sub_action: None = None
    length: int = 1
    data: None = None
    target: None = None

    def __init__(
        self, action: IfGameType, args: Arguments = Arguments(),
        *, append_to_reader: bool = False, invert: bool = False, codeblocks: typing.Iterable[Block] = None
    ):
        """
        Initialize this If Game.

        Parameters
        ----------
        action : :class:`~py2df.enums.actions.IfGameType`
            The condition to check.

        args : :class:`~py2df.classes.collections.Arguments`
            The arguments of this If Game.

        append_to_reader : :class:`bool`, optional
            Whether or not this newly-created :class:`IfGame` should already be appended to the
            :class:`~py2df.reading.reader.DFReader`. Defaults to ``False`` (because it is already appended
            when :meth:`~IfGame.__enter__` is called).

        invert : :class:`bool`, optional
            If ``True`` , then this If Game's code will only execute when the condition is false (i.e., applies NOT).
            Default: ``False``

        codeblocks : Deque[:class:`~py2df.classes.abc.Block`], optional
            The blocks, including Brackets, inside this If Game. Defaults to empty deque (None).
        """
        self.action = IfGameType(action)
        self.args = args

        self.codeblocks = deque(codeblocks) if codeblocks else deque()
        self.invert = invert

        if append_to_reader:
            DFReader().append_codeblock(self)

    def __neg__(self):
        return cls(
            self.action, self.args, append_to_reader=False, invert=-self.invert,
            codeblocks=self.codeblocks
        )

    # region:humanized-ifgame
    @classmethod
    def sign_has_text(
        cls, loc: Locatable, text: Textable,
        *, line_to_check: typing.Optional[int] = None, equals: bool = False
    ) -> "IfGame":
        """Checks if the text on a sign at a certain location contains the text given.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            The location of the sign.

        text : :attr:`~.Textable`
            The text to look for.

        line_to_check : Optional[:class:`int`], optional
            The line where to check for containing the text (1-4), or ``None`` for all lines. Defaults to ``None``.

        equals : :class:`bool`, optional
            If the whole line(s) should be checked for being equal to the text, instead of just checking if the text
            is contained within it/each. Defaults to ``False``.

        Returns
        -------
        :class:`IfGame`
            The generated IfGame instance.

        Raises
        ------
        :exc:`ValueError`
            If the line to be checked is not within the distance 1 <= line <= 4.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # location of sign
            with IfGame.sign_has_text(loc, "Some Text", line_to_check=3, equals=False):
                # ... code to be executed if 3rd line contains "Some Text" ...
        """
        if line_to_check is not None:
            line_to_check = int(line_to_check)
            if not 1 <= line_to_check <= 4:
                raise ValueError("Sign line must be between 1 and 4.")

        args = Arguments([
            p_check(loc, Locatable, "loc"),
            p_check(text, Textable, "text"),
        ], tags=[
            Tag(
                "Sign Line", option=line_to_check if line_to_check is not None else "All Lines",
                action=IfGameType.SIGN_HAS_TXT, block=BlockType.IF_GAME
            ),
            Tag(
                "Check Mode", option="Sign Line Equals" if equals else "Sign Line Contains",
                action=IfGameType.SIGN_HAS_TXT, block=BlockType.IF_GAME
            )
        ])

        return cls(
            action=IfGameType.SIGN_HAS_TXT,
            args=args,
            append_to_reader=False,
            invert=False
        )

    @classmethod
    def block_equals(
        cls, loc: Locatable, *block_types: typing.Optional[typing.Union[BlockParam, Listable]],
        metadata: typing.Optional[BlockMetadata]
    ):
        """Checks if a block at the desired location is a certain block.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Location of the block to be checked.

        block_types : Optional[Union[:class:`Material`, :attr:`~.ItemParam`, :attr:`~.Textable`, :attr:`~.Listable`]], optional
            The type of Block(s) to check for.

            The type can be specified either as:

            - an instance of :class:`~.Material` (the material of the block to set);
            - an item (:attr:`~.ItemParam` - the item representing the block to set);
            - text (:attr:`~.Textable` - the material of the block to set as text);
            - a :attr:`~.Listable` (A List - in DF - variable containing either Item or Text parameters).

        metadata : Optional[Union[:class:`dict`, List[:attr:`~.Textable`]], :attr:`~.Listable`], optional
            Optionally, the metadata of the desired block (``None`` for none). If not ``None``, can be in two forms:

            1. **As a dictionary:** If this is specified, then:
                - The keys must be strings;
                - The values can be one of:
                    - :class:`str` (the written out option);
                    - :class:`int` (is converted into a string accordingly);
                    - :class:`bool` (is turned into "true"/"false" accordingly);
                    - ``None`` (is turned into "none");
                    - :class:`~.DFVariable` (is turned into "%var(name)" accordingly).
                    - Any other types not mentioned will simply be ``str()``\ ed.
                - Example::

                    {
                        "facing": "east",
                        "drag": True,
                        "west": None,
                        "rotation": 8,
                        "powered": DFVariable("my_var")
                    }

            2. **As a list/iterable:** If this is specified, then it must be a list of valid Textable parameters,         whose values DF expects to be formatted in one of the following ways:
                - ``"tag=value"``
                - ``"tag:value"``
                - ``"tag,value"``


        Returns
        -------
        :class:`IfGame`
            The generated IfGame instance.

        Raises
        ------
        :exc:`ValueError`
            If no block types are specified.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # where it is
            block_1 = Material.STONE       # must either be a stone block...
            block_2 = Material.GOLD_BLOCK  # ...or be a gold block.
            meta = { "facing": "east" }  # must be facing east, for example

            with IfGame.block_equals(loc, block_1, block_2, meta):
                # ... code to be executed if the block at the given location is of the given type(s)...
        """
        if len(block_types) < 1:
            raise ValueError("At least one block type must be specified.")

        true_btypes: typing.List[typing.Union[ItemParam, Textable]] = _load_btypes(block_types)

        true_metadata: typing.List[Textable] = _load_metadata(typing.cast(metadata, BlockMetadata), allow_none=True)

        args = Arguments([
            p_check(loc, Locatable, "loc"),
            *[p_check(
                block_type, typing.Union[ItemParam, Textable, Listable], f"block_types[{i}]") for i, block_type in
                enumerate(true_btypes)
            ],
            *[p_check(meta, typing.Union[Textable, Listable], f"metadata[{i}]") for i, meta in enumerate(true_metadata)]
        ])
        return cls(
            action=IfGameType.BLOCK_EQUALS,
            args=args,
            append_to_reader=False,
            invert=False
        )

    @classmethod
    def event_block_equals(
        cls, *block_types: typing.Union[BlockParam, Listable]
    ):
        """Checks if the block in a block-related event is a certain block.

        .. rank:: Emperor

        .. workswith:: Place Block Event, Break Block Event

        Parameters
        ----------
        block_types : Union[:class:`Material`, :attr:`~.ItemParam`, :attr:`~.Textable`, :attr:`~.Listable`]
            The type of Block(s) to check for.

            The type can be specified either as:

            - an instance of :class:`~.Material` (the material of the block to set);
            - an item (:attr:`~.ItemParam` - the item representing the block to set);
            - text (:attr:`~.Textable` - the material of the block to set as text);
            - a :attr:`~.Listable` (A List - in DF - variable containing either Item or Text parameters).


        Returns
        -------
        :class:`IfGame`
            The generated IfGame instance.

        Examples
        --------
        ::

            block_1 = Material.STONE       # must either be a stone block...
            block_2 = Material.GOLD_BLOCK  # ...or be a gold block.
            with IfGame.event_block_equals(block_1, block_2):
                # ... code to be executed if the Event Block is either a Stone block or a Gold Block.
        """
        if len(block_types) < 1:
            raise ValueError("At least one block type must be specified.")

        true_btypes: typing.List[typing.Union[ItemParam, Textable]] = _load_btypes(block_types)

        args = Arguments([
            *[p_check(block_type, typing.Union[ItemParam, Textable, Listable], f"block_types[{i}]") for i, block_type in
              enumerate(true_btypes)]
        ])
        return cls(
            action=IfGameType.EVENT_BLOCK_EQUALS,
            args=args,
            append_to_reader=False,
            invert=False
        )

    @classmethod
    def command_equals(
        cls, *texts: typing.Union[Textable, Listable],
        only_first_word: bool = False, ignore_case: bool = True
    ):
        """Checks if the command entered in this Command Event is equal to the given text.

        .. rank:: Emperor

        .. workswith:: Command Event

        Parameters
        ----------
        texts : Union[:attr:`~.Textable`, :attr:`~.Listable`]
            Text(s) to check for.

        only_first_word : :class:`bool`, optional
            If ``True``, only the first word the command is compared against the text(s). If ``False``, the whole
            command line must be equal. Defaults to ``False``.

        ignore_case : :class:`bool`, optional
            If the check should be case insensitive. Defaults to ``True``.

        Returns
        -------
        :class:`IfGame`
            The generated IfGame instance.

        Examples
        --------
        ::

            my_cmd_name = "kill"
            with IfGame.command_equals("kill", only_first_word=True):
                # ... code to be executed if user sent '@kill <anything after, or nothing>' ...
        """
        args = Arguments([
            p_check(text, typing.Union[Textable, Listable], f"texts[{i}]") for i, text in enumerate(texts)
        ], tags=[
            Tag(
                "Check Mode", option="Check First Word" if only_first_word else "Check Entire Command",
                action=IfGameType.COMMAND_EQUALS, block=BlockType.IF_GAME
            ),
            Tag(
                "Ignore Case", option=bool(ignore_case),  # default is True
                action=IfGameType.COMMAND_EQUALS, block=BlockType.IF_GAME
            )
        ])
        return cls(
            action=IfGameType.COMMAND_EQUALS,
            args=args,
            append_to_reader=False,
            invert=False
        )

    @classmethod
    def event_item_equals(
        cls, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable],
        comparison_mode=ItemEqComparisonMode.IGNORE_DURABILITY_AND_STACK_SIZE
    ):
        """Checks if the item in an item-related event is a certain item.

        .. workswith:: Click Item Events, Pickup Item Event, Drop Item Event, Consume Item Event

        Parameters
        ----------
        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`]], :attr:`~.Listable`]
            Item(s) to check for. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a list of items.

        comparison_mode : :class:`~.ItemEqComparisonMode`, optional
            The mode of comparison that will determine if the items are equal (Exactly equals, \
Ignore stack size/durability or Material only). Defaults to Ignore stack size/durability \
(:attr:`~.IGNORE_DURABILITY_AND_STACK_SIZE`).

        Returns
        -------
        :class:`IfGame`
            The generated IfGame instance.

        Examples
        --------
        ::

            item_1 = Item(Material.STONE, name="aaa")          # must either be a stone named "aaa"...
            item_2 = Item(Material.DIAMOND_SWORD, name="bbb")  # ...or a diamond sword named "bbb".
            with IfGame.event_item_equals(item_1, item_2, comparison_mode=ItemEqComparisonMode.EXACTLY_EQUALS):
                # ... code to be executed if the event item is EXACTLY EQUAL to one of the given items.
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        c_mode = ItemEqComparisonMode(comparison_mode)
        if c_mode == ItemEqComparisonMode.IGNORE_STACK_SIZE:
            c_mode = ItemEqComparisonMode.IGNORE_DURABILITY_AND_STACK_SIZE

        args = Arguments([
            p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list
        ], tags=[
            Tag(
                "Comparison Mode", option=c_mode,  # default is Ignore stack size/durability
                action=IfGameType.EVENT_ITEM_EQUALS, block=BlockType.IF_GAME
            )
        ])
        return cls(
            action=IfGameType.EVENT_ITEM_EQUALS,
            args=args,
            append_to_reader=False,
            invert=False
        )

    @classmethod
    def block_powered(
        cls, *locs: typing.Union[Locatable, Listable],
        indirect_power: bool = False
    ):
        """Checks if a block/multiple blocks at a certain location is/some locations are powered by redstone.

        Parameters
        ----------
        locs : Union[:attr:`~.Locatable`, :attr:`~.Listable`]
            The location(s) of the block(s) to have their redstone power checked.

        indirect_power : :class:`bool`, False
            If ``True``, accepts blocks being indirectly redstone powered. If ``False``, only directly. Defaults to
            ``False``.

        Returns
        -------
        :class:`IfGame`
            The generated IfGame instance.

        Examples
        --------
        ::

            with IfGame.block_powered(locs):  # TODO: Example
                # ... code to be executed if
        """
        args = Arguments([
            p_check(loc, typing.Union[Locatable, Listable], f"locs[{i}]") for i, loc in enumerate(locs)
        ], tags=[
            Tag(
                "Redstone Power Mode", option="Indirect Power" if indirect_power else "Direct Power",
                action=IfGameType.BLOCK_POWERED, block=BlockType.IF_GAME
            )
        ])
        return cls(
            action=IfGameType.BLOCK_POWERED,
            args=args,
            append_to_reader=False,
            invert=False
        )

    @classmethod
    def container_has_any(
        cls, loc: Locatable, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]
    ):
        """Checks if a container has some item in its inventory.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Container location.

        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`]], :attr:`~.Listable`]
            Item(s) to check for. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a list of items.

            .. note::

                If multiple items are given, the container only needs to have one of them.


        Returns
        -------
        :class:`IfGame`
            The generated IfGame instance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # location of the container
            item_1 = Item(Material.STONE, name="stone")      # must either have a stone named "stone"...
            item_2 = Item(Material.SLIMEBALL, name="slime")  # ...or a slimeball named "slime" in it.
            with IfGame.container_has_any(loc, item_1, item_2):
                # ... code to be executed if the container at the given location has one of the given items ...
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(loc, Locatable, "loc"),
            *[p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list]
        ])
        return cls(
            action=IfGameType.CONTAINER_HAS,
            args=args,
            append_to_reader=False,
            invert=False
        )

    @classmethod
    def container_has_all(
        cls, loc: Locatable, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]
    ):
        """Checks if a container has all of the given items.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Container location.

        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`]], :attr:`~.Listable`]
            Item(s) to check for. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a list of items.


        Returns
        -------
        :class:`IfGame`
            The generated IfGame instance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # location of the container
            item_1 = Item(Material.STONE, name="stone")      # must have a stone named "stone"...
            item_2 = Item(Material.SLIMEBALL, name="slime")  # ...and a slimeball named "slime" in it.
            with IfGame.container_has_all(loc, items):
                # ... code to be executed if the container at the given location has all of the given items ...
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(loc, Locatable, "loc"),
            *[p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list]
        ])
        return cls(
            action=IfGameType.CONTAINER_HAS_ALL,
            args=args,
            append_to_reader=False,
            invert=False
        )

    @classmethod
    def cmd_arg_equals(
        cls, *texts: typing.Union[Textable, Listable], arg_num: Numeric,
        ignore_case: bool = True
    ):
        """Checks if part of the command entered in this Command Event is equal to a certain text.

        .. rank:: Emperor

        .. workswith:: Command Event

        Parameters
        ----------
        texts : Union[:attr:`~.Textable`, :attr:`~.Listable`]
            Text(s) to check for. (Must be equal to one of them.)

        arg_num : :attr:`~.Numeric`
            Number of the argument to be compared.

            .. note:: Argument number **1** is the command. **2, 3, ...** are the ones that follow.

        ignore_case : :class:`bool`, optional
            If the equality check should be done case insensitively. Defaults to ``True``.

        Returns
        -------
        :class:`IfGame`
            The generated IfGame instance.

        Examples
        --------
        ::

            with IfGame.cmd_arg_equals("test", "input", arg_num=2):
                # ... code to be executed if the second argument of a user-sent command is equal to one of the given \
texts ...
                # for example: '@somecmd test' or '@cmd input' would match.
        """
        args = Arguments([
            *[p_check(text, typing.Union[Textable, Listable], f"texts[{i}]") for i, text in enumerate(texts)],
            p_check(arg_num, Numeric, "distance")
        ], tags=[
            Tag(
                "Ignore Case", option=bool(ignore_case),  # default is True
                action=IfGameType.CMD_ARG_EQUALS, block=BlockType.IF_GAME
            )
        ])
        return cls(
            action=IfGameType.CMD_ARG_EQUALS,
            args=args,
            append_to_reader=False,
            invert=False
        )

    @classmethod
    def event_cancelled(cls):
        """Checks if the current event is cancelled.

        Returns
        -------
        :class:`IfGame`
            The generated IfGame instance.

        Examples
        --------
        ::

            with IfGame.event_cancelled():
                # ... code to be executed if the event is cancelled ...
        """
        return cls(
            action=IfGameType.EVENT_CANCELLED,
            args=Arguments(),
            append_to_reader=False,
            invert=False
        )

    # endregion:humanized-ifgame


class IfVariable(IfBlock):
    """An If Variable block. Executes code if a certain condition related to a variable is met.

    Parameters
    ----------\u200b
    action : :class:`~py2df.enums.actions.IfVariableType`
        The condition to check.

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this If Variable.

    append_to_reader : :class:`bool`, optional
        Whether or not this newly-created :class:`IfVariable` should be already appended to the
        :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.

    invert : :class:`bool`, optional
        If ``True`` , then this If Variable's code will only execute when the condition is false (i.e., applies NOT).
        Default: ``False``

    codeblocks : Iterable[:class:`~py2df.classes.abc.Block`], optional
        The blocks, including Brackets, inside this If Variable. Defaults to empty deque (None).

    Attributes
    ----------\u200b
    block : :attr:`~py2df.enums.parameters.BlockType.IF_VAR`
        The type of this codeblock (If Variable).

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this If Variable.

    action : :class:`~py2df.enums.actions.IfVariableType`
        The condition to check.

    codeblocks : Deque[:class:`~py2df.classes.abc.Block`]
        The blocks, including Brackets, inside this If Variable.

    invert : :class:`bool`
        If ``True`` , then this If Variable's code will only execute when the condition is false (i.e., applies NOT).
        Default: ``False``

    sub_action : ``None``
        (If Variable has no sub actions.)

    length : :class:`int`
        The length of each individual If Variable (excluding brackets). This is always equal to 1.

    data : ``None``
        (If Variable has no extra codeblock data.)

    target : ``None``
        (If Variable has no target.)
    """
    __slots__ = ("args", "action", "invert", "codeblocks", "_called_by_var")

    block: BlockType = BlockType.IF_VAR
    args: Arguments
    action: IfVariableType
    codeblocks: typing.Deque[Block]
    invert: bool
    sub_action: None = None
    length: int = 1
    data: None = None
    target: None = None

    def __init__(
        self, action: IfVariableType, args: Arguments = Arguments(),
        *, append_to_reader: bool = False, invert: bool = False, codeblocks: typing.Iterable[Block] = None
    ):
        """
        Initialize this If Variable.

        Parameters
        ----------
        action : :class:`~py2df.enums.actions.IfVariableType`
            The condition to check.

        args : :class:`~py2df.classes.collections.Arguments`
            The arguments of this If Variable.

        append_to_reader : :class:`bool`, optional
            Whether or not this newly-created :class:`IfVariable` should already be appended to the
            :class:`~py2df.reading.reader.DFReader`. Defaults to ``False`` (because it is already appended
            when :meth:`~IfVariable.__enter__` is called).

        invert : :class:`bool`, optional
            If ``True`` , then this If Variable's code will only execute when the condition is false (i.e., applies NOT).
            Default: ``False``

        codeblocks : Deque[:class:`~py2df.classes.abc.Block`], optional
            The blocks, including Brackets, inside this If Variable. Defaults to empty deque (None).
        """
        self.action = IfVariableType(action)
        self.args = args

        self.codeblocks = deque(codeblocks) if codeblocks else deque()
        self.invert = invert

        if append_to_reader:
            DFReader().append_codeblock(self)

        self._called_by_var: bool = False

    def __neg__(self):
        return IfVariable(
            self.action, self.args, append_to_reader=False, invert=-self.invert,
            codeblocks=self.codeblocks
        )

    def __bool__(self):
        """Allows for bool() calls on IfVariableType.EQUALS and IfVariableType.NOT_EQUALS, making the use of `If`s
        possible.

        Otherwise, returns True.
        """
        if self._called_by_var:
            if self.action in (IfVariableType.EQUALS, IfVariableType.NOT_EQUALS):
                arg_1 = self.args.items[0]
                arg_2 = self.args.items[1]
                res = False
                if isinstance(arg_1, DFVariable) or isinstance(arg_2, DFVariable):
                    res = arg_1.name == arg_2.name and arg_1.scope == arg_2.scope if isinstance(arg_1, DFVariable) \
                        and isinstance(arg_2, DFVariable) else False
                elif isinstance(arg_1, DFGameValue) or isinstance(arg_2, DFGameValue):
                    res = arg_1.gval_type == arg_2.gval_type if isinstance(arg_1, DFGameValue) \
                        and isinstance(arg_2, DFGameValue) else False
                else:
                    res = arg_1 == arg_2

                return not res if self.action == IfVariableType.NOT_EQUALS else res

        return True


class Else(BracketedBlock):
    """An Else block. Executes code when a condition checked by an If block is not met. **Has to be preceded by
    an If Block.

    Parameters
    ----------\u200b
    append_to_reader : :class:`bool`, optional
        Whether or not this newly-created :class:`IfVariable` should be already appended to the
        :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.

    codeblocks : Iterable[:class:`~py2df.classes.abc.Block`], optional
        The blocks, including Brackets, inside this Else. Defaults to empty deque (None).

    Attributes
    ----------\u200b
    block : :attr:`~py2df.enums.parameters.BlockType.IF_VAR`
        The type of this codeblock (Else).

    args : ``None``
        (Else has no arguments.)

    action : ``None``
        (Else has no actions.)

    codeblocks : Deque[:class:`~py2df.classes.abc.Block`]
        The blocks, including Brackets, inside this Else.

    sub_action : ``None``
        (Else has no sub actions.)

    length : :class:`int`
        The length of each individual Else (excluding brackets). This is always equal to 1.

    data : ``None``
        (Else has no extra codeblock data.)

    target : ``None``
        (Else has no target.)
        """
    __slots__ = ("codeblocks",)

    block: BlockType = BlockType.ELSE
    args: None = None
    action: None = None
    codeblocks: typing.Deque[Block]
    sub_action: None = None
    length: int = 1
    data: None = None
    target: None = None

    def __init__(
        self, *, append_to_reader: bool = False,
        codeblocks: typing.Optional[typing.Iterable[Block]] = None
    ):
        if append_to_reader:
            self._append_codeblock()

        self.codeblocks: typing.Deque[Block] = deque(codeblocks or [])

    def __enter__(self) -> "Else":
        """
        Triggers the creation of an opening bracket and the addition of all codeblocks into this If Player.

        Returns
        -------
        :class:`IfPlayer`
            self (The current instance)
        """
        self.codeblocks.appendleft(Bracket(BracketDirection.OPEN, BracketType.NORM))
        reader = DFReader()

        if reader.curr_code_loc and self not in reader.curr_code_loc:
            self._append_codeblock()

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
        self.codeblocks.append(Bracket(BracketDirection.CLOSE, BracketType.NORM))

    def _append_codeblock(self):
        """Checks if there is an If before this Else in order to allow its placement."""
        reader = DFReader()
        curr_loc = reader.curr_code_loc
        if curr_loc and not isinstance(curr_loc[-1], IfBlock):
            raise DFSyntaxError("'Else' block must come directly after an If block at the same bracket level.")

        reader.append_codeblock(self)


remove_u200b_from_doc(IfBlock, IfPlayer, IfEntity, IfGame, IfVariable, Else)
