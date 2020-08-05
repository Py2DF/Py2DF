import collections
import typing
from .. import enums
from ..enums import (
    PlayerTarget, EntityTarget, BlockType, PlayerActionType, EntityActionType, GameActionType, ControlType,
    SelectionTarget,
    Material)
from ..classes import JSONData, Arguments, ActionBlock, Tag, DFNumber, DFVariable, DFText, Item, ItemCollection
from ..utils import remove_u200b_from_doc, flatten
from ..typings import p_check, Numeric, Locatable, Textable, ParticleParam, ItemParam, SpawnEggable, Potionable, \
    Listable, p_bool_check
from ..constants import BLOCK_ID, DEFAULT_VAL
from ..reading.reader import DFReader
from ._block_utils import BlockParam, BlockMetadata, _load_metadata


class PlayerAction(ActionBlock, JSONData):
    """A Player Action.

    Parameters
    ----------\u200b
    action : :class:`~py2df.enums.actions.PlayerActionType`
        The type of player action this is.

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this Player Action.

    target : Optional[:class:`~.PlayerTarget`], optional
        The target of this Player Action, or ``None`` for empty (current selection/default player). Defaults to
        ``None``.

    append_to_reader : :class:`bool`, optional
        Whether or not this newly-created :class:`PlayerAction` should be already appended to the
        :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.

    Attributes
    ----------\u200b
    block : :attr:`~py2df.enums.parameters.BlockType.PLAYER_ACTION`
        The type of this codeblock (Player Action).

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this Player Action.

    action : :class:`~py2df.enums.actions.PlayerActionType`
        The type of player action this is.

    sub_action : ``None``
        (Player actions have no sub actions.)

    length : :class:`int`
        The length of each individual player action. This is always equal to 2.

    data : ``None``
        (Player actions have no extra codeblock data.)

    target : Optional[:class:`~.PlayerTarget`]
        The target of this Player Action, or ``None`` for empty (current selection/default player).
    """
    __slots__ = ("args", "action", "target")

    block: BlockType = BlockType.PLAYER_ACTION
    args: Arguments
    action: PlayerActionType
    sub_action: None = None
    length: int = 2
    data: None = None
    target: typing.Optional[PlayerTarget]
    
    def __init__(
        self, action: PlayerActionType, args: Arguments = Arguments(),
        target: typing.Optional[typing.Union[PlayerTarget, SelectionTarget]] = None,
        *, append_to_reader: bool = True
    ):
        """
        Initialize this Player Action.
        
        Parameters
        ----------
        action : :class:`~py2df.enums.actions.PlayerActionType`
            The type of player action this is.
            
        args : :class:`~py2df.classes.collections.Arguments`
            The arguments of this Player Action.
        
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this Player Action, or ``None`` for empty (current selection/default player). Defaults to
            ``None``.
        
        append_to_reader : :class:`bool`, optional
            Whether or not this newly-created :class:`PlayerAction` should be already appended to the
            :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.
        """
        self.action = PlayerActionType(action)
        self.args = args
        self.target = PlayerTarget(
            target.value if SelectionTarget in (target, type(target)) else target
        ) if target is not None else None
        
        if append_to_reader:
            DFReader().append_codeblock(self)

    def as_json_data(self) -> dict:
        """
        Produces a JSON-serializable dict representing this player action.

        Returns
        -------
        :class:`dict`
        """
        return dict(
            id=BLOCK_ID,
            block=PlayerAction.block.value,
            args=self.args.as_json_data(),
            action=self.action.value,
            **(dict(target=self.target.value) if self.target else dict())
        )


class EntityAction(ActionBlock, JSONData):
    """An Entity Action.

    Parameters
    ----------\u200b
    action : :class:`~py2df.enums.actions.EntityActionType`
        The type of entity action this is.

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this Entity Action.

    target : Optional[:class:`~.EntityTarget`], optional
        The target of this Entity Action, or ``None`` for empty (current selection/default entity). Defaults to
        ``None``.

    append_to_reader : :class:`bool`, optional
        Whether or not this newly-created :class:`EntityAction` should be already appended to the
        :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.

    Attributes
    ----------\u200b
    block : :attr:`~py2df.enums.parameters.BlockType.ENTITY_ACTION`
        The type of this codeblock (Entity Action).

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this Entity Action.

    action : :class:`~py2df.enums.actions.EntityActionType`
        The type of entity action this is.

    sub_action : ``None``
        (Entity actions have no sub actions.)

    length : :class:`int`
        The length of each individual entity action. This is always equal to 2.

    data : ``None``
        (Entity actions have no extra codeblock data.)

    target : Optional[:class:`~.EntityTarget`]
        The target of this Entity Action, or ``None`` for empty (current selection/default entity).
    """
    __slots__ = ("args", "action", "target")

    block: BlockType = BlockType.ENTITY_ACTION
    args: Arguments
    action: EntityActionType
    sub_action: None = None
    length: int = 2
    data: None = None
    target: typing.Optional[EntityTarget]

    def __init__(
        self, action: EntityActionType, args: Arguments = Arguments(),
        target: typing.Optional[typing.Union[EntityTarget, SelectionTarget]] = None,
        *, append_to_reader: bool = True
    ):
        """
        Initialize this Entity Action.

        Parameters
        ----------
        action : :class:`~py2df.enums.actions.EntityActionType`
            The type of entity action this is.

        args : :class:`~py2df.classes.collections.Arguments`
            The arguments of this Entity Action.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this Entity Action, or ``None`` for empty (current selection/default entity). Defaults to
            ``None``.

        append_to_reader : :class:`bool`, optional
            Whether or not this newly-created :class:`EntityAction` should be already appended to the
            :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.
        """
        self.action = EntityActionType(action)
        self.args = args
        self.target = EntityTarget(
            target.value if SelectionTarget in (target, type(target)) else target
        ) if target is not None else None

        if append_to_reader:
            DFReader().append_codeblock(self)

    def as_json_data(self) -> dict:
        """
        Produces a JSON-serializable dict representing this entity action.

        Returns
        -------
        :class:`dict`
        """
        return dict(
            id=BLOCK_ID,
            block=EntityAction.block.value,
            args=self.args.as_json_data(),
            action=self.action.value,
            **(dict(target=self.target.value) if self.target else dict())
        )


class GameAction(ActionBlock, JSONData):
    """A Game Action.

    Parameters
    ----------\u200b
    action : :class:`~py2df.enums.actions.GameActionType`
        The type of game action this is.

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this Game Action.

    append_to_reader : :class:`bool`, optional
        Whether or not this newly-created :class:`GameAction` should be already appended to the
        :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.

    Attributes
    ----------\u200b
    block : :attr:`~py2df.enums.parameters.BlockType.GAME_ACTION`
        The type of this codeblock (Game Action).

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this Game Action.

    action : :class:`~py2df.enums.actions.GameActionType`
        The type of game action this is.

    sub_action : ``None``
        (Game actions have no sub actions.)

    length : :class:`int`
        The length, in blocks, of each individual game action. This is always equal to 2.

    data : ``None``
        (Game actions have no extra codeblock data.)

    target : ``None``
        (Game actions have no target.)
    """
    __slots__ = ("args", "action")

    block: BlockType = BlockType.GAME_ACTION
    args: Arguments
    action: GameActionType
    sub_action: None = None
    length: int = 2
    data: None = None
    target: None = None

    def __init__(
        self, action: GameActionType, args: Arguments = Arguments(),
        *, append_to_reader: bool = True
    ):
        """
        Initialize this Game Action.

        Parameters
        ----------
        action : :class:`~py2df.enums.actions.GameActionType`
            The type of game action this is.

        args : :class:`~py2df.classes.collections.Arguments`
            The arguments of this Game Action.

        append_to_reader : :class:`bool`, optional
            Whether or not this newly-created :class:`GameAction` should be already appended to the
            :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``.
        """
        self.action = GameActionType(action)
        self.args = args
        
        if append_to_reader:
            DFReader().append_codeblock(self)

    def as_json_data(self) -> dict:
        """
        Produces a JSON-serializable dict representing this game action.

        Returns
        -------
        :class:`dict`
        """
        return dict(
            id=BLOCK_ID,
            block=GameAction.block.value,
            args=self.args.as_json_data(),
            action=self.action.value
        )

    # region:humanized-gameaction

    @classmethod
    def block_drops_off(cls) -> "GameAction":
        """Disables blocks dropping as items when broken.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            GameAction.block_drops_off()
        """
        return cls(
            action=GameActionType.BLOCK_DROPS_OFF,
            args=Arguments(),
            append_to_reader=True
        )

    @classmethod
    def block_drops_on(cls) -> "GameAction":
        """Enables blocks dropping as items when broken.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            GameAction.block_drops_on()
        """
        return cls(
            action=GameActionType.BLOCK_DROPS_ON,
            args=Arguments(),
            append_to_reader=True
        )

    @classmethod
    def bone_meal(
        cls, *locs: typing.Union[Locatable, Listable], amount: Numeric, show_particles: bool = True
    ) -> "GameAction":
        """Applies bone meal to a block.

        .. rank:: Noble

        Parameters
        ----------
        locs : Union[:attr:`~.Locatable`, :attr:`~.Listable`]
            The location(s) of the block(s) that will receive the Bone Meal.

        amount : :attr:`~.Numeric`
            The amount of bone meals to apply at once to the blocks.

        show_particles : :class:`bool`, optional
            Whether or not Bone Meal particles should be shown when applied. Defaults to ``True``

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            loc_1 = DFLocation(1, 2, 3)
            loc_2 = DFVariable("my_loc")
            GameAction.bone_meal(loc_1, loc_2, amount=5, show_particles=True)  # 5 bone meals, with particles.
        """
        args = Arguments(
            [
                *[p_check(loc, typing.Union[Locatable, Listable], f"locs[{i}]") for i, loc in enumerate(locs)],
                p_check(amount, Numeric, "amount")
            ],
            tags=[Tag(
                "Show Particles", option=bool(show_particles),
                action=GameActionType.BONE_MEAL, block=BlockType.GAME_ACTION
            )]
        )
        return cls(
            action=GameActionType.BONE_MEAL,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def break_block(cls, *locs: typing.Union[Locatable, Listable]) -> "GameAction":
        """Breaks a block at a certain location as if it was broken by a player.

        Parameters
        ----------
        locs : Union[:attr:`~.Locatable`, :attr:`~.Listable`]
            The location(s) of the block(s) that will be broken.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            loc_1 = DFLocation(1, 2, 3)
            loc_2 = LocationVar("my var")
            loc_3 = DFVariable("other var")  # some locations
            GameAction.break_block(loc_1, loc_2, loc_3)  # breaks those blocks
        """
        return cls(
            action=GameActionType.BREAK_BLOCK,
            args=Arguments(
                [p_check(loc, typing.Union[Locatable, Listable], f"locs[{i}]") for i, loc in enumerate(locs)]
            ),
            append_to_reader=True
        )

    @classmethod
    def cancel_event(cls) -> "GameAction":
        """Cancels the initial event that triggered this line of code.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            GameAction.cancel_event()
        """
        return cls(
            action=GameActionType.CANCEL_EVENT,
            args=Arguments(),
            append_to_reader=True
        )

    @classmethod
    def change_sign(cls, loc: Locatable, line: Numeric, new_text: typing.Optional[Textable] = None) -> "GameAction":
        """Changes a line of text on a sign.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            The location of the sign to have its text changed.

        line : :attr:`~.Numeric`
            The number of the line to be changed.

        new_text : Optional[:attr:`~.Textable`], optional
            The new text that this line should have, or ``None`` to make it empty. Defaults to ``None``.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # location of the sign, or variable
            GameAction.change_sign(loc, 3, "haha")  # change line 3 to "haha"
            GameAction.change_sign(loc, 4)          # change line 4 to nothing (empty)
        """
        if isinstance(line, (int, float, DFNumber)):
            if not (1 <= int(line) <= 4):
                raise ValueError("Sign line number must be between 1 and 4.")

            line = DFNumber(int(line))  # floor; line numbers can only be ints

        return cls(
            action=GameActionType.CHANGE_SIGN,
            args=Arguments([
                p_check(loc, Locatable, "loc"),
                p_check(line, Numeric, "line"),
        *([p_check(new_text, Textable, "new_text")] if new_text is not None else [])  # empty line if None
            ]),
            append_to_reader=True
        )

    @classmethod
    def clear_scoreboard(cls) -> "GameAction":
        """Removes all scores from the scoreboard.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            GameAction.clear_scoreboard()
        """
        return cls(
            action=GameActionType.CLEAR_SC_BOARD,
            args=Arguments(),
            append_to_reader=True
        )

    @classmethod
    def copy_blocks(cls, loc_1: Locatable, loc_2: Locatable, copy_pos: Locatable, paste_pos: Locatable) -> "GameAction":
        """Copies a region of blocks to another region, including air blocks.

        .. rank:: Overlord

        Parameters
        ----------
        loc_1 : :attr:`~.Locatable`
            The first corner of the region to be copied.

        loc_2 : :attr:`~.Locatable`
            The second corner of the region to be copied.

        copy_pos : :attr:`~.Locatable`
            The position from which the region is copied.

        paste_pos : :attr:`~.Locatable`
            The position from which the region is pasted.

            .. note::

                For optimal results, this position should be the same as copy_pos **in relation to the region**
                (i.e., have same distance or angle from center, for example).

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Warnings
        --------
        - 'Copy Blocks' has a limit of 50 000 blocks per operation.
        - 'Copy Blocks' has a cooldown of 5 000 blocks per second. For example, copying 15k blocks would have a 3 \
second cooldown."

        Examples
        --------
        ::

            loc_1 = DFLocation(1, 2, 3)  # some location
            loc_2 = DFVariable("%default other_loc")  # some variable containing a location
            copy_pos = DFGameValue(GameValueType.LOCATION, target=PlayerTarget.DEFAULT)  # default player's pos
            paste_pos = DFVariable("%default paste_pos")  # some variable containing a location
            GameAction.copy_blocks(loc_1, loc_2, copy_pos, paste_pos)
        """
        return cls(
            action=GameActionType.COPY_BLOCKS,
            args=Arguments([
                p_check(loc_1, Locatable, "loc_1"),
                p_check(loc_2, Locatable, "loc_2"),
                p_check(copy_pos, Locatable, "copy_pos"),
                p_check(paste_pos, Locatable, "paste_pos")
            ]),
            append_to_reader=True
        )

    @classmethod
    def create_animated_particle_circle(
        cls, particle: ParticleParam, center: Locatable,
        diameter: typing.Optional[Numeric] = None, duration: typing.Optional[Numeric] = None
    ) -> "GameAction":
        """Creates an animated circle of particles at a certain location.

        .. rank:: Mythic

        Parameters
        ----------
        particle : :attr:`~.ParticleParam`
            The particle to spawn.

        center : :attr:`~.Locatable`
            The center of the circle.

            .. note::

                The rotation of the circle is determined by this location's pitch and yaw.

        diameter : Optional[:attr:`~.Numeric`], optional
            The diameter of the circle, in blocks, or ``None`` for the default value (2 blocks).

        duration : Optional[:attr:`~.Numeric`], optional
            The duration of the animation, **in ticks**\\ , or ``None`` for the default value.


        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            particle = DFParticle(ParticleType.CLOUD)
            center = DFLocation(1, 2, 3, 45, 60)  # 45, 60 are pitch and yaw, to determine the rotation of the circle
            GameAction.create_animated_particle_circle(particle, center, 5, 40)  # diameter: 5 blocks; duration: 2 s \
(40 ticks)
        """
        if duration is not None and diameter is None:
            diameter = 2  # default: 2 blocks

        return cls(
            action=GameActionType.CREATE_ANIMATED_PARTICLE_CIRCLE,
            args=Arguments([
                p_check(particle, ParticleParam, "particle"),
                p_check(center, Locatable, "center"),
                p_check(diameter, Numeric, "diameter") if diameter is not None else None,
                p_check(duration, Numeric, "duration") if duration is not None else None
            ]),
            append_to_reader=True
        )

    @classmethod
    def create_animated_particle_line(
        cls, particle: ParticleParam, loc_1: Locatable, loc_2: Locatable,
        duration: typing.Optional[Numeric] = None
    ) -> "GameAction":
        """Creates a line of particles between two locations.

        .. rank:: Mythic

        Parameters
        ----------
        particle : :attr:`~.ParticleParam`
            The particle to spawn.

        loc_1 : :attr:`~.Locatable`
            The first location (first point of the particle line).

        loc_2 : :attr:`~.Locatable`
            The second location (second point of the particle line).

        duration : Optional[:attr:`~.Numeric`], optional
            The duration of the animation, **in ticks**\\ , or ``None`` for the default value.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            particle = DFParticle(ParticleType.CLOUD)
            loc_1 = DFLocation(1, 2, 3)
            loc_2 = DFLocation(4, 2, 3)  # 4-block-long line
            GameAction.create_animated_particle_line(particle, loc_1, loc_2, 40)  # duration: 2 s (40 ticks)
        """
        return cls(
            action=GameActionType.CREATE_ANIMATED_PARTICLE_LINE,
            args=Arguments([
                p_check(particle, ParticleParam, "particle"),
                p_check(loc_1, Locatable, "loc_1"),
                p_check(loc_2, Locatable, "loc_2"),
                p_check(duration, Numeric, "duration") if duration is not None else None
            ]),
            append_to_reader=True
        )

    @classmethod
    def create_animated_particle_spiral(
        cls, particle: ParticleParam, base: Locatable,
        length: typing.Optional[Numeric] = None, diameter: typing.Optional[Numeric] = None,
        duration: typing.Optional[Numeric] = None
    ) -> "GameAction":
        """Creates an animated spiral of particles at a certain location.

        .. rank:: Mythic

        Parameters
        ----------
        particle : :attr:`~.ParticleParam`
            The particle to spawn.

        base : :attr:`~.Locatable`
            The base location of the spiral.

            .. note::

                The rotation of the spiral is determined by this location's pitch and yaw.

        length : Optional[:attr:`~.Numeric`], optional
            The length of the spiral, in blocks, or ``None`` for the default value (10 blocks).

        diameter : Optional[:attr:`~.Numeric`], optional
            The diameter of the spiral, in blocks, or ``None`` for the default value (2 blocks).

        duration : Optional[:attr:`~.Numeric`], optional
            The duration of the animation, **in ticks**\\ , or ``None`` for the default value.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            particle = DFParticle(ParticleType.BARRIER)  # Type of particle.
            base = DFLocation(1, 2, 3, 45, 60)  # 45, 60 are pitch and yaw, to determine the rotation of the spiral
            GameAction.create_animated_particle_spiral(particle, base, 15, 3, 40)
            # length: 15 blocks; diameter: 3 blocks; duration: 2 s (40 ticks)
        """
        if diameter is not None and length is None:
            length = 10  # default: 10 blocks

        if duration is not None:
            length = length if length is not None else 10       # default: 10 blocks
            diameter = diameter if diameter is not None else 2  # default: 2 blocks

        return cls(
            action=GameActionType.CREATE_ANIMATED_PARTICLE_SPIRAL,
            args=Arguments([
                p_check(particle, ParticleParam, "particle"),
                p_check(base, Locatable, "base"),
                p_check(length, Numeric, "length") if length is not None else None,
                p_check(diameter, Numeric, "diameter") if diameter is not None else None,
                p_check(duration, Numeric, "duration") if duration is not None else None
            ]),
            append_to_reader=True
        )

    @classmethod
    def create_hologram(cls, loc: Locatable, text: Textable) -> "GameAction":
        """Creates a hologram (floating text) at a certain location.

        .. rank:: Mythic


        Parameters
        ----------
        loc : :attr:`~.Locatable`
            The location at which to place the hologram.

        text : :attr`~.Textable`
            The text that this hologram will display.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            loc = DFVariable("some location")
            GameAction.create_hologram(loc, "Hey guys!")  # displays "Hey guys!" at the specified location
        """
        return cls(
            action=GameActionType.CREATE_HOLOGRAM,
            args=Arguments([
                p_check(loc, Locatable, "loc"),
                p_check(text, Textable, "text"),
            ]),
            append_to_reader=True
        )

    @classmethod
    def create_particle_circle(
        cls, particle: ParticleParam, center: Locatable,
        diameter: typing.Optional[Numeric] = None
    ) -> "GameAction":
        """Creates a circle of particles at a certain location.

        .. rank:: Noble

        Parameters
        ----------
        particle : :attr:`~.ParticleParam`
            The particle to spawn.

        center : :attr:`~.Locatable`
            The center of the circle.

            .. note::

                The rotation of the circle is determined by this location's pitch and yaw.

        diameter : Optional[:attr:`~.Numeric`], optional
            The diameter of the circle, in blocks, or ``None`` for the default value (2 blocks).

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            particle = DFParticle(ParticleType.CLOUD)
            center = DFLocation(1, 2, 3, 45, 60)  # 45, 60 are pitch and yaw, to determine the rotation of the circle
            GameAction.create_particle_circle(particle, center, 5)  # diameter: 5 blocks
        """
        return cls(
            action=GameActionType.CREATE_PARTICLE_CIRCLE,
            args=Arguments([
                p_check(particle, ParticleParam, "particle"),
                p_check(center, Locatable, "center"),
                p_check(diameter, Numeric, "diameter") if diameter is not None else None
            ]),
            append_to_reader=True
        )

    @classmethod
    def create_particle_cluster(
        cls, particle: ParticleParam, center: Locatable,
        size: typing.Optional[Numeric] = None, density: typing.Optional[Numeric] = None
    ) -> "GameAction":
        """Randomly spawns particles around a certain location.

        .. rank:: Noble

        Parameters
        ----------
        particle : :attr:`~.ParticleParam`
            The type of particle to spawn.

        center : :attr:`~.Locatable`
            The location around which the particles should be spawned.

        size : Optional[:attr:`~.Numeric`], optional
            The cluster size, or ``None`` to pick the default (2 blocks). Defaults to ``None``.

        density : Optional[:attr:`~.Numeric`], optional
            The cluster density (i.e., particles per block), or ``None`` to pick the default (10). Defaults to ``None``.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.
        """
        if density is not None and size is None:
            size = 2  # default: 2 blocks (size)

        return cls(
            action=GameActionType.CREATE_PARTICLE_CLUSTER,
            args=Arguments([
                p_check(particle, ParticleParam, "particle"),
                p_check(center, Locatable, "center"),
                p_check(size, Numeric, "size") if size is not None else None,
                p_check(density, Numeric, "density") if density is not None else None,
            ]),
            append_to_reader=True
        )

    @classmethod
    def create_particle_line(cls, particle: ParticleParam, loc_1: Locatable, loc_2: Locatable) -> "GameAction":
        """Creates a line of particles between two locations.

        .. rank:: Noble

        Parameters
        ----------
        particle : :attr:`~.ParticleParam`
            The particle to spawn.

        loc_1 : :attr:`~.Locatable`
            The first location (first point of the particle line).

        loc_2 : :attr:`~.Locatable`
            The second location (second point of the particle line).

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            particle = DFParticle(ParticleType.CLOUD)
            loc_1 = DFLocation(1, 2, 3)
            loc_2 = DFLocation(4, 2, 3)  # 4-block-long line
            GameAction.create_animated_particle_line(particle, loc_1, loc_2)
        """
        return cls(
            action=GameActionType.CREATE_PARTICLE_LINE,
            args=Arguments([
                p_check(particle, ParticleParam, "particle"),
                p_check(loc_1, Locatable, "loc_1"),
                p_check(loc_2, Locatable, "loc_2")
            ]),
            append_to_reader=True
        )

    @classmethod
    def create_particle_path(
        cls, particle: ParticleParam, *locs: typing.Union[Locatable, Listable]
    ) -> "GameAction":
        """Creates a path of particles that goes through each location given from first to last.

        Parameters
        ----------
        particle : :attr:`~.ParticleParam`
            Particle to spawn.

        locs : Union[:attr:`~.Locatable`, :attr:`~.Listable`]
            Path locations to go through.


        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Examples
        --------
        ::

            particle = DFParticle(ParticleType.SWEEP_ATTACK)  # particle
            loc_1 = DFLocation(1, 2, 3)
            loc_2 = LocationVar("my var")
            loc_3 = DFVariable("other var")
            GameAction.create_particle_path(particle, loc_1, loc_2, loc_3)  # particle goes through loc_1, _2 and _3
        """
        args = Arguments([
            p_check(particle, ParticleParam, "particle"),
            *[p_check(loc, typing.Union[Locatable, Listable], f"locs[{i}]") for i, loc in enumerate(locs)]
        ])
        return cls(
            action=GameActionType.CREATE_PARTICLE_PATH,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def create_particle_ray(
        cls, particle: ParticleParam, origin: Locatable, length: typing.Optional[Numeric] = None
    ) -> "GameAction":
        """Creates a ray of particles starting at a certain location.

        Parameters
        ----------
        particle : :attr:`~.ParticleParam`
            Particle to spawn.

        origin : :attr:`~.Locatable`
            Ray origin.

            .. note:

                The rotation of the ray is determined by the pitch and yaw of this location.

        length : Optional[:attr:`~.Numeric`], optional
            Ray length, or ``None`` for the default (10 blocks). Defaults to ``None``.


        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Examples
        --------
        ::

            particle = DFParticle(ParticleType.ANGRY_VILLAGER)  # particle type
            origin = DFLocation(1, 2, 3, 40, 60)  # origin of ray; pitch=40 yaw=60 for the rotation
            GameAction.create_particle_ray(particle, origin, 5)  # length of 5 blocks
        """
        args = Arguments([
            p_check(particle, ParticleParam, "particle"),
            p_check(origin, Locatable, "origin"),
            p_check(length, Numeric, "length") if length is not None else None
        ])
        return cls(
            action=GameActionType.CREATE_PARTICLE_RAY,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def create_particle_sphere(
        cls, particle: ParticleParam, center: Locatable, diameter: typing.Optional[Numeric] = None
    ) -> "GameAction":
        """Creates a sphere of particles at a certain location.
    
        .. rank:: Noble
    
        
        Parameters
        ----------
        particle : :attr:`~.ParticleParam`
            Particle type to spawn.
            
        center : :attr:`~.Locatable`
            Sphere center location.
            
        diameter : Optional[:attr:`~.Numeric`], optional
            Sphere diameter, or ``None`` for the default (2 blocks). Default is ``None``.
            
        
        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.
        
        Examples
        --------
        ::

            particle = DFParticle(ParticleType.BARRIER)  # particle type
            center = DFLocation(1, 2, 3)  # center of the sphere
            GameAction.create_particle_sphere(particle, center, 6)  # diameter of 6 blocks
        """
        args = Arguments([
            p_check(particle, ParticleParam, "particle"),
            p_check(center, Locatable, "center"),
            p_check(diameter, Numeric, "diameter") if diameter is not None else None
        ])
        return cls(
            action=GameActionType.CREATE_PARTICLE_SPHERE,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def create_particle_spiral(
        cls, particle: ParticleParam, base: Locatable,
        length: typing.Optional[Numeric] = None, diameter: typing.Optional[Numeric] = None,
        duration: typing.Optional[Numeric] = None
    ) -> "GameAction":
        """Creates a spiral of particles at a certain location.

        .. rank:: Noble

        Parameters
        ----------
        particle : :attr:`~.ParticleParam`
            The particle to spawn.

        base : :attr:`~.Locatable`
            The base location of the spiral.

            .. note::

                The rotation of the spiral is determined by this location's pitch and yaw.

        length : Optional[:attr:`~.Numeric`], optional
            The length of the spiral, in blocks, or ``None`` for the default value (10 blocks).

        diameter : Optional[:attr:`~.Numeric`], optional
            The diameter of the spiral, in blocks, or ``None`` for the default value (2 blocks).

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            particle = DFParticle(ParticleType.BARRIER)  # Type of particle.
            base = DFLocation(1, 2, 3, 45, 60)  # 45, 60 are pitch and yaw, to determine the rotation of the spiral
            GameAction.create_particle_spiral(particle, base, 15, 3)
            # length: 15 blocks; diameter: 3 blocks
        """
        if diameter is not None and length is None:
            length = 10  # default: 10 blocks

        return cls(
            action=GameActionType.CREATE_PARTICLE_SPIRAL,
            args=Arguments([
                p_check(particle, ParticleParam, "particle"),
                p_check(base, Locatable, "base"),
                p_check(length, Numeric, "length") if length is not None else None,
                p_check(diameter, Numeric, "diameter") if diameter is not None else None
            ]),
            append_to_reader=True
        )

    @classmethod
    def drop_block(
        cls, loc: Locatable,
        block_type: typing.Optional[BlockParam] = None,
        metadata: typing.Optional[BlockMetadata] = None,
        *, reform_on_impact: bool = True, hurt_hit_entities: bool = False
    ) -> "GameAction":
        """Spawns a falling block at the specified location.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            The location where to drop a block.

        block_type : Optional[Union[:class:`~.Material`, :attr:`~.ItemParam`, :attr:`~.Textable`]]
            The type of block to drop, or ``None`` (see the Note below). Defaults to ``None``.

            The type can be specified either as:
            - an instance of :class:`~.Material` (the material of the block to drop);
            - an item (:attr:`~.ItemParam` - the item representing the block to drop);
            - text (:attr:`~.Textable` - the material of the block to drop as text).

            .. note::

                If this is ``None``, then the block at the given location is turned into a falling block.

        metadata : Optional[Union[:class:`dict`, List[:attr:`~.Textable`]]]
            Optionally, the metadata of the falling block (``None`` for none). If not ``None``, can be in two forms:

            1. **As a dictionary:** If this is specified, then:
                - The keys must be strings;
                - The values can be one of:
                    - :class:`str` (the written out option);
                    - :class:`int` (is converted into a string accordingly);
                    - :class:`bool` (is turned into "true"/"false" accordingly);
                    - ``None`` (is turned into "none");
                    - :class:`~.DFVariable` (is turned into "%var(name)" accordingly).
                    - Any other types not mentioned will simply be ``str()``\\ ed.
                - Example::

                    {
                        "facing": "east",
                        "drag": True,
                        "west": None,
                        "rotation": 8,
                        "powered": DFVariable("my_var")

                    }

            2. **As a list/iterable:** If this is specified, then it must be a list of valid Textable parameters, \
whose values DF expects to be formatted in one of the following ways:
                - ``"tag=value"``
                - ``"tag:value"``
                - ``"tag,value"``

            .. warning::

                For this to be specified, `block_type` also has to be, otherwise a ValueError is raised.

        reform_on_impact : :class:`bool`, optional
            Whether or not the block should be placed when it hits the ground. Defaults to ``True``.

        hurt_hit_entities ::class:`bool`, optional
            Whether or not entities hit by the falling block should receive damage. Defaults to ``False``.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Raises
        ------
        :exc:`TypeError`
            If `metadata` is not a dict, an Iterable or ``None``.

        :exc:`ValueError`
            If `metadata` was specified, but `block_type` wasn't.

        Warnings
        --------
        Falling blocks automatically disappear after 30 seconds.

        Examples
        --------
        ::

            loc = DFLocation(1, 10, 3)   # where to spawn the falling block
            block_type = Material.BIRCH_STAIRS  # spawn Birch Stairs, for example
            metadata = { "facing": "east" }  # facing east; block metadata
            # OR
            metadata = ["facing=east"]  # also possible, as long as you follow the format

            GameAction.drop_block(loc, block_type, metadata, reform_on_impact=True, hurt_hit_entities=False)
            # Drops a falling Birch Stairs block, facing east, while not hurting any hit entities, and placing when it \
lands.
        """
        if isinstance(block_type, (Material, str, DFText, collections.UserString)):  # check for material validity
            block_type = Material(str(block_type) if isinstance(block_type, DFText) else block_type).value

        if metadata is not None and block_type is None:
            raise ValueError("'block_type' has to be specified in order to specify 'metadata'.")

        true_metadata: typing.List[Textable] = _load_metadata(typing.cast(metadata, BlockMetadata), allow_none=True)

        return cls(
            action=GameActionType.DROP_BLOCK,
            args=Arguments(
                [
                    p_check(loc, Locatable, "loc"),
                    p_check(
                        block_type, typing.Union[Textable, ItemParam], "block_type"
                    ) if block_type is not None else None,
                    *([
                        p_check(text, typing.Union[Textable, Listable], f"metadata[{i}]")
                        for i, text in enumerate(true_metadata)
                    ])
                ], tags=[
                    Tag(
                        "Reform on Impact", option=bool(reform_on_impact),
                        action=GameActionType.DROP_BLOCK, block=BlockType.GAME_ACTION
                    ),
                    Tag(
                        "Hurt Hit Entities", option=bool(hurt_hit_entities),
                        action=GameActionType.DROP_BLOCK, block=BlockType.GAME_ACTION
                    )
                ]
            ),
            append_to_reader=True
        )

    spawn_falling_block = drop_block  # alias
    """Alias of :meth:`drop_block`"""

    @classmethod
    def empty_container(cls, loc: Locatable) -> "GameAction":
        """Empties a container.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            The location of the container to turn empty.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # loc of the container
            GameAction.empty_container(loc)  # empties it
        """
        return cls(
            action=GameActionType.EMPTY_CONTAINER,
            args=Arguments([p_check(loc, Locatable, "loc")]),
            append_to_reader=True
        )

    @classmethod
    def explosion(cls, loc: Locatable, power: typing.Optional[Numeric] = None) -> "GameAction":
        """Creates an explosion at a certain location.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            The location of the explosion.

        power : Optional[:attr:`~.Numeric`], optional
            The power of the explosion (0-4), or ``None`` for the default value (4).

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Raises
        ------
        :exc:`ValueError`
            If the power was given as a literal and is not between 0 and 4.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # where to spawn the explosion
            GameAction.explosion(loc, 4)  # power 4
            GameAction.explosion(loc, DFVariable("%default some power"))  # variable power
        """
        if isinstance(power, (int, float, DFNumber)) and not 0 <= float(power) <= 4:
            raise ValueError("'power' argument must be between 0 and 4.")

        return cls(
            action=GameActionType.EXPLOSION,
            args=Arguments([
                p_check(loc, Locatable, "loc"),
                p_check(power, Numeric, "power")
            ]),
            append_to_reader=True
        )

    @classmethod
    def fill_container(
        cls, loc: Locatable, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]
    ) -> "GameAction":
        """Fills a container with items.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Location of the container to be filled.

        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], \
:attr:`Listable`]]
            The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a predetermined list of items.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Raises
        ------
        :exc:`ValueError`
            If no item was specified.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # loc of the container
            item_1 = Item(Material.STONE, name="some item")
            item_2 = Item(Material.STONE, name="some other item")
            some_items = ItemCollection([Item(Material.GRASS_BLOCK), Item(Material.GRANITE_SLAB)])  # more items
            GameAction.fill_container(loc, item_1, item_2, some_items)  # fill the container at 'loc' with those 4 items
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)
        if not item_list or not any(item_list):
            raise ValueError("No item was specified.")

        return cls(
            action=GameActionType.FILL_CONTAINER,
            args=Arguments([
                p_check(loc, Locatable, "loc"),
                *([p_check(it, typing.Union[ItemParam, Listable], "items") for it in item_list])
            ]),
            append_to_reader=True
        )

    @classmethod
    def firework(cls, firework: ItemParam, loc: Locatable, name: typing.Optional[Textable] = None) -> "GameAction":
        """Launches a firework at a certain location.

        Parameters
        ----------
        firework : :attr:`~.ItemParam`
            The :class:`~.Item` (or a variable/game value of item) representing the firework to be launched.

        loc : :attr:`~.Locatable`
            The location where to spawn the firework.

        name : Optional[:attr:`~.Textable`], optional
            The name of the firework, or ``None`` for none. Defaults to ``None``

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.
        """
        return cls(
            action=GameActionType.FIREWORK,
            args=Arguments([
                p_check(firework, ItemParam, "firework"),
                p_check(loc, Locatable, "loc"),
                p_check(name, Textable, "name") if name is not None else None
            ]),
            append_to_reader=True
        )

    @classmethod
    def firework_effect(cls, firework: ItemParam, loc: Locatable) -> "GameAction":
        """Creates a firework explosion at a certain location.

        Parameters
        ----------
        firework : :attr:`~.ItemParam`
            The :class:`~.Item` (or a variable/game value of item) representing the firework (effect) to be launched.

        loc : :attr:`~.Locatable`
            The location where to spawn the firework.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            firework = Item(Material.FIREWORK_ROCKET, extra_tags=...)  # ... would be the firework NBT tags
            # OR
            firework = DFVariable("my_firework")  # variable representing the firework item
            loc = DFLocation(1, 2, 3)
            GameAction.firework_effect(firework, loc)
        """
        return cls(
            action=GameActionType.FIREWORK_EFFECT,
            args=Arguments(),
            append_to_reader=True
        )

    firework_explosion = firework_effect  # alias
    """Alias of :meth:`firework_effect`"""

    @classmethod
    def hide_scoreboard(cls) -> "GameAction":
        """Disables the scoreboard sidebar on the plot.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            GameAction.hide_scoreboard()
        """
        return cls(
            action=GameActionType.HIDE_SIDEBAR,
            args=Arguments(),
            append_to_reader=True
        )

    @typing.overload
    def launch_projectile(
        cls, projectile: typing.Union[Material, ItemParam, Textable], loc: Locatable,
        *, name: Textable, speed: Numeric,
        inaccuracy: typing.Optional[Numeric] = None, particle: ParticleParam
    ) -> "GameAction": ...

    @typing.overload
    def launch_projectile(
        cls, projectile: typing.Union[Material, ItemParam, Textable], loc: Locatable,
        *, name: Textable, speed: Numeric,
        inaccuracy: Numeric, particle: None = None
    ) -> "GameAction": ...

    @typing.overload
    def launch_projectile(
        cls, projectile: typing.Union[Material, ItemParam, Textable], loc: Locatable,
        *, name: Textable, speed: Numeric,
        inaccuracy: None = None, particle: None = None
    ) -> "GameAction": ...

    @typing.overload
    def launch_projectile(
        cls, projectile: typing.Union[Material, ItemParam, Textable], loc: Locatable,
        *, name: Textable, speed: None = None,
        inaccuracy: None = None, particle: None = None
    ) -> "GameAction": ...

    @typing.overload
    def launch_projectile(
        cls, projectile: typing.Union[Material, ItemParam, Textable], loc: Locatable,
        *, name: None = None, speed: None = None,
        inaccuracy: None = None, particle: None = None
    ) -> "GameAction": ...

    @classmethod
    def launch_projectile(
        cls, projectile: typing.Union[Material, ItemParam, Textable], loc: Locatable,
        *, name: typing.Optional[Textable] = None, speed: typing.Optional[Numeric] = None,
        inaccuracy: typing.Optional[Numeric] = None, particle: typing.Optional[ParticleParam] = None
    ) -> "GameAction":
        """Launches a projectile.

        Parameters
        ----------
        projectile : Union[:class:`~.Material`, :attr:`~.ItemParam`, :attr:`~.Textable`]
            The type of projectile to launch.

            The type can be specified either as:
            - an instance of :class:`~.Material` (the material of the projectile to launch);
            - an item (:attr:`~.ItemParam` - the item representing the projectile to launch);
            - text (:attr:`~.Textable` - the material of the projectile to launch as text).

            (Do note that any of those can be a variable/game value containing it.)

        loc : :attr:`~.Locatable`
            The location from which the projectile should be launched.

        name : Optional[:attr:`~.Textable`], optional
            The name of the projectile, or ``None`` to keep it empty. Defaults to ``None``.

        speed : Optional[:attr:`~.Numeric`], optional
            The speed of the projectile, or ``None`` to let DF decide the default value. Defaults to ``None``.

            .. warning::

                This has to be specified if inaccuracy is specified, otherwise a ValueError is raised.

        inaccuracy : Optional[:attr:`~.Numeric`], optional
            The inaccuracy of the launch, i.e., how much random momentum is applied to the projectile, or ``None``
            for the default (1). Defaults to ``None``.

        particle : Optional[:attr:`~.ParticleParam`], optional
            An optional particle to form a particle trail behind the projectile. Defaults to ``None``.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Raises
        ------
        :exc:`ValueError`
            If `speed` are not specified when `inaccuracy` is also specified.

        Examples
        --------
        ::

            proj = Material.ARROW
            # OR
            proj = Item(Material.ARROW)
            # OR
            proj = "arrow"
            # OR
            proj = DFVariable("my var")  # can contain the Item or material name
            loc = DFLocation(1, 2, 3)  # where to launch, can be var too (Locatable)
            partic = DFParticle(ParticleType.ANGRY_VILLAGER)  # this will be the arrow trail
            GameAction.launch_projectile(proj, loc, name="my projectile", speed=5, inaccuracy=2, particle=partic)
        """
        if isinstance(projectile, (Material, str, collections.UserString, DFText)):  # check for material validity
            projectile = Material(
                str(projectile) if isinstance(projectile, collections.UserString) else projectile
            ).value

        if speed is None and inaccuracy is not None:
            raise ValueError("'speed' must be specified in order to specify 'inaccuracy'.")

        return cls(
            action=GameActionType.LAUNCH_PROJ,
            args=Arguments([
                p_check(projectile, typing.Union[Textable, ItemParam], "projectile"),
                p_check(loc, Locatable, "loc"),
                p_check(name, Textable, "name") if name is not None else None,
                p_check(speed, Numeric, "speed") if speed is not None else None,
                p_check(inaccuracy, Numeric, "inaccuracy") if inaccuracy is not None else None,
                p_check(particle, ParticleParam, "particle") if particle is not None else None
            ]),
            append_to_reader=True
        )

    @classmethod
    def lock_container(cls, loc: Locatable, key: typing.Optional[Textable] = None) -> "GameAction":
        """Sets a container's lock key.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            The location of the container.

        key : Optional[:attr:`~.Textable`], optional
            The new lock key of the container, or ``None`` to unlock it. Defaults to ``None``.

            .. note::

                A lock key determines the item name the container must be opened with.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # or some var
            GameAction.lock_container(loc, "Key Item")  # will only be able to open with items named "Key Item"
            # OR
            GameAction.lock_container(loc)  # unlocks it; i.e., any item/bare hands can open it (the default behavior)
        """
        return cls(
            action=GameActionType.LOCK_CONTAINER,
            args=Arguments([
                p_check(loc, Locatable, "loc"),
                p_check(key, Textable, "key") if key is not None else None
            ]),
            append_to_reader=True
        )

    @classmethod
    def play_particle_effect(cls, particle: ParticleParam, loc: Locatable) -> "GameAction":
        """Plays a particle effect at a certain location.

        Parameters
        ----------
        particle : :attr:`~.ParticleParam`
            The particle to spawn.

        loc : :attr:`~.Locatable`
            The location where to spawn the particle.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.
        """
        return cls(
            action=GameActionType.PLAY_PARTICLE_EFFECT,
            args=Arguments([
                p_check(particle, ParticleParam, "particle"),
                p_check(loc, Locatable, "loc")
            ]),
            append_to_reader=True
        )

    @classmethod
    def remove_hologram(cls, loc_or_text: typing.Union[Locatable, Textable]) -> "GameAction":
        """Removes a hologram.

        .. rank:: Mythic

        Parameters
        ----------
        loc_or_text : Union[:attr:`~.Locatable`, :attr:`~.Textable`]
            The location or the text of the hologram to remove.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            GameAction.remove_hologram(DFLocation(1, 2, 3))  # removes hologram with location x=1, y=2, z=3
            # OR
            GameAction.remove_hologram("hello there")  # removes hologram with text "hello there"
        """
        return cls(
            action=GameActionType.REMOVE_HOLOGRAM,
            args=Arguments([
                p_check(loc_or_text, typing.Union[Locatable, Textable], "loc_or_text")
            ]),
            append_to_reader=True
        )

    @classmethod
    def remove_score(cls, score: Textable) -> "GameAction":
        """Removes a score from the scoreboard.

        Parameters
        ----------
        score : :attr:`~.Textable`
            The text of the score to be removed.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            GameAction.remove_score("User")  # or some var or something
        """
        return cls(
            action=GameActionType.REMOVE_SCORE,
            args=Arguments([
                p_check(score, Textable, "score")
            ]),
            append_to_reader=True
        )

    @classmethod
    def set_block(
        cls, block_type: BlockParam, loc_1: Locatable,
        loc_2: typing.Optional[Locatable] = None, metadata: typing.Optional[BlockMetadata] = None
    ) -> "GameAction":
        """Sets the block at a certain location or region.
        
        Parameters
        ----------
        block_type : Union[:class:`~.Material`, :attr:`~.ItemParam`, :attr:`~.Textable`]]
            The type of block to set.

            The type can be specified either as:

            - an instance of :class:`~.Material` (the material of the block to set);
            - an item (:attr:`~.ItemParam` - the item representing the block to set);
            - text (:attr:`~.Textable` - the material of the block to set as text).

        loc_1 : :attr:`~.Locatable`
            The location of the block to set, if just one, or the first corner of a region, if multiple.

        loc_2 : Optional[:attr:`~.Locatable`], optional
            If setting more than one block, then this is the second corner of a region in which the blocks will be set
            to the specified block type. Otherwise, ``None`` (defaults to loc_1, i.e., region of just one block).
            Default: ``None``.

        metadata : Optional[Union[:class:`dict`, List[:attr:`~.Textable`]]]
            Optionally, the metadata of the block to be set (``None`` for none). If not ``None``, can be in two forms:

            1. **As a dictionary:** If this is specified, then:
                - The keys must be strings;
                - The values can be one of:
                    - :class:`str` (the written out option);
                    - :class:`int` (is converted into a string accordingly);
                    - :class:`bool` (is turned into "true"/"false" accordingly);
                    - ``None`` (is turned into "none");
                    - :class:`~.DFVariable` (is turned into "%var(name)" accordingly).
                    - Any other types not mentioned will simply be ``str()``\\ ed.
                - Example::

                    {
                        "facing": "east",
                        "drag": True,
                        "west": None,
                        "rotation": 8,
                        "powered": DFVariable("my_var")
                    }

            2. **As a list/iterable:** If this is specified, then it must be a list of valid Textable parameters, \
whose values DF expects to be formatted in one of the following ways:
                - ``"tag=value"``
                - ``"tag:value"``
                - ``"tag,value"``

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Raises
        ------
        :exc:`TypeError`
            If `metadata` is not a dict, an Iterable or ``None``; also if an invalid `block_type` was passed (e.g.
            text was given but no such material exists).

        :exc:`ValueError`
            If `metadata` was specified, but `block_type` wasn't.

        Warnings
        --------
        This can set up to 100,000 blocks per action.

        Examples
        --------
        ::

            loc = DFLocation(1, 10, 3)   # where to set the block
            block_type = Material.BIRCH_STAIRS  # set as Birch Stairs, for example
            meta = { "facing": "east" }  # facing east; block metadata
            # OR
            meta = ["facing=east"]  # also possible, as long as you follow the format

            GameAction.set_block(block_type, loc, metadata=meta)  # set 1 block
            # OR
            loc_2 = DFLocation(1, 20, 3)  # other corner of the region, to set multiple blocks
            GameAction.set_block(block_type, loc, loc_2, meta)  # set multiple blocks
            # Sets the block(s) to Birch Stairs, facing east.
        """
        if isinstance(block_type, (Material, str, DFText, collections.UserString)):  # check for material validity
            block_type = Material(str(block_type) if isinstance(block_type, DFText) else block_type).value

        if metadata is not None and loc_2 is None:
            loc_2 = loc_1  # just that block

        true_metadata = _load_metadata(metadata, allow_none=True)

        return cls(
            action=GameActionType.SET_BLOCK,
            args=Arguments([
                p_check(
                    block_type, typing.Union[Textable, ItemParam], "block_type"
                ) if block_type is not None else None,
                p_check(loc_1, Locatable, "loc_1"),
                p_check(loc_2, Locatable, "loc_2"),
                *([
                    p_check(text, typing.Union[Textable, Listable], f"metadata[{i}]")
                    for i, text in enumerate(true_metadata)
                ])
            ]),
            append_to_reader=True
        )

    @classmethod
    def set_block_metadata(cls, loc: Locatable, metadata: BlockMetadata) -> "GameAction":
        """Sets a metadata tag for a certain block.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            The location of the block that will have its metadata set.

        metadata : Optional[Union[:class:`dict`, List[:attr:`~.Textable`]]]
            The new metadata of the block. Can be in two forms:

            1. **As a dictionary:** If this is specified, then:
                - The keys must be strings;
                - The values can be one of:
                    - :class:`str` (the written out option);
                    - :class:`int` (is converted into a string accordingly);
                    - :class:`bool` (is turned into "true"/"false" accordingly);
                    - ``None`` (is turned into "none");
                    - :class:`~.DFVariable` (is turned into "%var(name)" accordingly).
                    - Any other types not mentioned will simply be ``str()``\\ ed.
                - Example::

                    {
                        "facing": "east",
                        "drag": True,
                        "west": None,
                        "rotation": 8,
                        "powered": DFVariable("my_var")
                    }

            2. **As a list/iterable:** If this is specified, then it must be a list of valid Textable parameters, \
whose values DF expects to be formatted in one of the following ways:
                - ``"tag=value"``
                - ``"tag:value"``
                - ``"tag,value"``

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Examples
        --------
        ::

            loc = DFLocation(1, 10, 3)   # where the block is
            meta = { "facing": "east" }  # facing east; block metadata
            # OR
            meta = ["facing=east"]  # also possible, as long as you follow the format

            GameAction.set_block(loc, meta)  # now the block will face east.
        """
        true_metadata = _load_metadata(metadata, allow_none=False)

        if len(true_metadata) < 1:
            raise ValueError("Metadata must be specified (length > 0).")

        return cls(
            action=GameActionType.SET_BLOCK_DATA,
            args=Arguments([
                p_check(loc, Locatable, "loc"),
                *([
                    p_check(text, typing.Union[Textable, Listable], f"metadata[{i}]")
                    for i, text in enumerate(true_metadata)
                ])
            ]),
            append_to_reader=True
        )

    @classmethod
    def set_container(
        cls, loc: Locatable, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]
    ) -> "GameAction":
        """Sets a container's contents.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Location of the container to have its contents set.

        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], \
:attr:`Listable`]]
            The new contents of the container. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a predetermined list of items.

        Returns
        -------
        :class:`GameAction`
            The generated Game Action codeblock.

        Raises
        ------
        :exc:`ValueError`
            If no item was specified.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # loc of the container
            item_1 = Item(Material.STONE, name="some item")
            item_2 = Item(Material.STONE, name="some other item")
            some_items = ItemCollection([Item(Material.GRASS_BLOCK), Item(Material.GRANITE_SLAB)])  # more items
            GameAction.set_container(loc, item_1, item_2, some_items)  # set the container at 'loc' to those 4 items
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)
        if not item_list or not any(item_list):
            raise ValueError("No item was specified.")

        return cls(
            action=GameActionType.SET_CONTAINER,
            args=Arguments([
                p_check(loc, Locatable, "loc"),
                *([p_check(it, typing.Union[ItemParam, Listable], "items") for it in item_list])
            ]),
            append_to_reader=True
        )

    @classmethod
    def set_container_name(
       cls, loc: Locatable, name: Textable
    ) -> "GameAction":
        """Sets the custom name of a container (e.g. chests).

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            The container's location.

        name : :attr:`~.Textable`
            The new container name.


        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # where the container is
            GameAction.set_container_name(loc, "Cool Container")  # set its name to "Cool Container"
        """
        args = Arguments([
            p_check(loc, Locatable, "loc"),
            p_check(name, Textable, "name")
        ])
        return cls(
            action=GameActionType.SET_CONTAINER_NAME,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def set_furnace_speed(
       cls, loc: Locatable, speed: typing.Optional[Numeric] = None
    ) -> "GameAction":
        """Sets the cook time multiplier of a furnace.

        .. workswith:: Furnace, Blast Furnace, Smoker

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Furnace location.


        speed : Optional[:attr:`~.Numeric`], optional
            Cook speed multiplier, or ``None`` to let DF pick a default value. Default is ``None``.


        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Notes
        -----
        - Cook speed = 200 ticks
        - Fuel duration is unaffected by cook speed.


        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # location of furnace
            GameAction.set_furnace_speed(loc, 2)  # furnace is now 2 times faster
        """
        args = Arguments([
            p_check(loc, Locatable, "loc"),
            p_check(speed, Numeric, "speed") if speed is not None else None
        ])
        return cls(
            action=GameActionType.SET_FURNACE_SPEED,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def set_scoreboard_objective(
       cls, objective: Textable
    ) -> "GameAction":
        """Sets the objective name of the scoreboard on your plot.

        Parameters
        ----------
        objective : :attr:`~.Textable`
            New objective name (32 characters or less).


        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Examples
        --------
        ::

            GameAction.set_scoreboard_objective("New objective")
        """
        args = Arguments([
            p_check(objective, Textable, "objective")
        ])
        return cls(
            action=GameActionType.SET_SC_OBJ,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def set_score(
       cls, score: Textable, new_value: typing.Optional[Numeric] = None
    ) -> "GameAction":
        """Sets a score on the scoreboard.

        Parameters
        ----------
        score : :attr:`~.Textable`
            Score name (32 characters or less).

        new_value : Optional[:attr:`~.Numeric`], optional
            New score value, or ``None`` for the default (0). Default is ``None``.


        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Examples
        --------
        ::

            GameAction.set_score("User", 5)  # score "User" is now 5
        """
        args = Arguments([
            p_check(score, Textable, "score"),
            p_check(new_value, Numeric, "new_value") if new_value is not None else None
        ])
        return cls(
            action=GameActionType.SET_SCORE,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def show_scoreboard(cls):
        """Enables the scoreboard sidebar on the plot.

        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Examples
        --------
        ::

            GameAction.show_scoreboard()
        """
        return cls(
            action=GameActionType.SHOW_SIDEBAR,
            args=Arguments(),
            append_to_reader=True
        )

    @classmethod
    def spawn_armor_stand(
       cls, loc: Locatable, name: typing.Optional[Textable] = None,
       *equipment: typing.Optional[typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]],
       visible: bool = True, has_hitbox: bool = True
    ) -> "GameAction":
        """Creates an armor stand at a certain location.

        .. rank:: Mythic


        Parameters
        ----------
        loc : :attr:`~.Locatable`
            The new armor stand's location.

        name : Optional[:attr:`~.Textable`], optional
            The new armor stand's name. Default is ``None``.

        equipment : Optional[:attr:`~.ItemParam`], optional
            Equipment. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a list of items.

            .. note::

                Equipment goes, from left to right: Helmet, Chestplate, Leggings, Boots, Right Hand, Left Hand.

        visible : :class:`bool`, optional
            If ``False``, the armor stand will be invisible. Defaults to ``True`` (visible).

        has_hitbox : :class:`bool`, optional
            If ``False``, the armor stand won't have a hitbox. Defaults to ``True`` (has hitbox).

        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Notes
        -----
        - Options to set the pose and tags are in Entity Action - Appearance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # location of the armor stand
            helmet = Item(Material.DIAMOND_HELMET, unbreakable=True)  # example helmet
            chestp = Item(Material.IRON_CHESTPLATE, name="My Chestplate")  # example chestplate
            # ... etc ...
            GameAction.spawn_armor_stand(loc, "My Armor Stand", helmet, chestp, visible=True, has_hitbox=False)
            # armor stand named "My Armor Stand" with some helmet and chestplate; visible without hitbox
        """
        item_list = flatten(*equipment, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(loc, Locatable, "loc"),
            p_check(name, Textable, "name") if name is not None else None,
            *([p_check(it, typing.Union[ItemParam, Listable], "equipment") for it in item_list])
        ], tags=[
            Tag(
                "Visibility", option=f"{'Visible' if visible else 'Invisible'}{'' if has_hitbox else ' (No hitbox)'}",
                action=GameActionType.SPAWN_ARMOR_STAND, block=BlockType.GAME_ACTION
            )
        ])
        return cls(
            action=GameActionType.SPAWN_ARMOR_STAND,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def spawn_crystal(
       cls, loc: Locatable, name: typing.Optional[Textable] = None,
       *, show_bottom: bool = True
    ) -> "GameAction":
        """Spawns an End Crystal at a certain location.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Location to spawn at.

        name : Optional[:attr:`~.Textable`], optional
            Custom name for the crystal. Default is ``None``.

        show_bottom : :class:`bool`, optional
            Whether or not the Crystal bottom should be shown. Defaults to ``True``.

        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # location of the crystal
            GameAction.spawn_crystal(loc, "My Crystal", show_bottom=False)  # spawns at loc, with name "My Crystal",
                                                                            # without showing its bottom.
        """
        args = Arguments([
            p_check(loc, Locatable, "loc"),
            p_check(name, Textable, "name") if name is not None else None
        ], tags=[
            Tag(
                "Show Bottom", option=bool(show_bottom),
                action=GameActionType.SPAWN_CRYSTAL, block=BlockType.GAME_ACTION
            )
        ])
        return cls(
            action=GameActionType.SPAWN_CRYSTAL,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def spawn_exp_orb(
       cls, loc: Locatable, exp_amount: typing.Optional[Numeric] = None, name: typing.Optional[Textable] = None
    ) -> "GameAction":
        """Spawns an experience orb at a certain location.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Orb location.

        exp_amount : Optional[:attr:`~.Numeric`], optional
            Experience amount, or ``None`` for a default value set by DF. Default is ``None``.

            .. warning::

                This parameter has to be specified in order to specify `name`, or a :exc:`ValueError` is raised.

        name : Optional[:attr:`~.Textable`], optional
            Orb name, or ``None`` for none.. Default is ``None``.


        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Raises
        ------
        :exc:`ValueError`
            If `name` is specified but `exp_amount` isn't.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # where to spawn the orb

            GameAction.spawn_exp_orb(loc, 5, "My Orb")  # 5 experience given by the new orb named "My Orb".
        """
        args = Arguments([
            p_check(loc, Locatable, "loc"),
            p_check(exp_amount, Numeric, "exp_amount") if exp_amount is not None else None,
            p_check(name, Textable, "name") if name is not None else None
        ])
        return cls(
            action=GameActionType.SPAWN_EXP_ORB,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def spawn_evoker_fangs(
       cls, loc: Locatable, name: typing.Optional[Textable] = None
    ) -> "GameAction":
        """Spawns Evoker Fangs at a certain location.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Location to spawn the fangs at.

        name : Optional[:attr:`~.Textable`], optional
            Custom name for the fangs, or ``None`` for none. Default is ``None``.


        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Notes
        -----
        Evoker Fangs deal damage and disappear a second later.


        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # where they spawn
            GameAction.spawn_evoker_fangs(loc, "My Fangs")
        """
        args = Arguments([
            p_check(loc, Locatable, "loc"),
            p_check(name, Textable, "name") if name is not None else None
        ])
        return cls(
            action=GameActionType.SPAWN_FANGS,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def spawn_item(
       cls, loc: Locatable, name: typing.Optional[Textable] = None,
       *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable],
       apply_item_motion: bool = True
    ) -> "GameAction":
        """Spawns an item at a certain location.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Location to spawn the item at.

        name : Optional[:attr:`~.Textable`], optional
            Item stack name to show above. Default is ``None``.

        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`]]
            The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a list of items.

        apply_item_motion : :class:`bool`, optional
            If motion should be applied to the item. Defaults to ``True``.

        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Raises
        ------
        :exc:`ValueError`
            If no item was specified.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # location to spawn the item stack
            my_item = 64 * Item(Material.STONE)  # 64 stones
            GameAction.spawn_item(loc, "Some items", my_item)  # Spawns 64 stones at the location, named "Some items"
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)
        if not item_list or not any(item_list):
            raise ValueError("No item was specified.")

        args = Arguments([
            *[p_check(it, typing.Union[ItemParam, Listable], "items") for it in item_list],
            p_check(loc, Locatable, "loc"),
            p_check(name, Textable, "name") if name is not None else None
        ], tags=[
            Tag(
                "Apply Item Motion", option=bool(apply_item_motion),
                action=GameActionType.SPAWN_ITEM, block=BlockType.GAME_ACTION
            )
        ])
        return cls(
            action=GameActionType.SPAWN_ITEM,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def spawn_mob(
       cls, spawn_egg: SpawnEggable, loc: Locatable, health: typing.Optional[Numeric] = None,
       name: typing.Optional[Textable] = None, potions: typing.Optional[typing.Iterable[Potionable]] = None,
       *equipment: typing.Optional[typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]]
    ) -> "GameAction":
        """Spawns a mob at a certain location.

        Parameters
        ----------
        spawn_egg : :attr:`~.SpawnEggable`
            Mob type.

        loc : :attr:`~.Locatable`
            Location to spawn at.

        health : Optional[:attr:`~.Numeric`], optional
            Mob health. Default is ``None`` (full health).

        name : Optional[:attr:`~.Textable`], optional
            Mob name. Default is ``None`` (no name).

        potions : Optional[Union[Iterable[:attr:`~.Potionable`], Listable]], optional
            Potion effect(s), or a list var of them. Default is ``None`` (no potion effect).

        equipment : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`]], optional
            Mob equipment. Default is ``None`` (no equipment). The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a list of items.

            .. note::

                Equipment goes from left to right: Main Hand, Helmet, Chestplate, Leggings, Boots, Off Hand.

        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.


        Examples
        --------
        ::

            spawn_egg = Item(Material.ZOMBIE_SPAWN_EGG)  # zombie
            loc = DFLocation(1, 2, 3)  # where to spawn
            potions = [DFPotion(PotionType.ABSORPTION, 255, (999, 99))]  # Absorption 255; inf duration (999:99)
            hand_item = Item(Material.DIAMOND_SWORD, name="Epic Sword", unbreakable=True)  # some item
            GameAction.spawn_mob(spawn_egg, loc, 10, "My mob", potions, hand_item, ...)  # ... for other items
            # Spawns a zombie at the given location, named "My mob" and with 10 health (5 hearts) plus the absorption
            # hearts, while holding an unbreakable diamond sword named "Epic Sword".
        """
        if p_bool_check(potions, Listable):
            potions = [potions]

        args = Arguments([
            p_check(spawn_egg, SpawnEggable, "spawn_egg"),
            p_check(loc, Locatable, "loc"),
            p_check(health, Numeric, "health") if health is not None else None,
            p_check(name, Textable, "name") if name is not None else None,
            *[p_check(obj, typing.Union[Potionable, Listable], f"potions[{i}]") for i, obj in enumerate(potions)],
            *[
                p_check(obj, typing.Union[ItemParam, Listable], "items")
                for obj in flatten(equipment, except_iterables=[str], max_depth=1)
            ]
        ])
        return cls(
            action=GameActionType.SPAWN_MOB,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def spawn_rng_item(
        cls, loc: Locatable, name: typing.Optional[Textable] = None,
        *items: typing.Optional[typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]],
        apply_item_motion: bool = True
    ) -> "GameAction":
        """Randomly spawns an item at a certain location.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Location to spawn the item at.

        name : Optional[:attr:`~.Textable`], optional
            Item stack name to show above. Default is ``None``.

        items : typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]
            Items to pick from. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a list of items.

        apply_item_motion : :class:`bool`, optional
            If motion should be applied to the item. Defaults to ``True``.

        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Raises
        ------
        :exc:`ValueError`
            If no item was specified.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # location to spawn the item stack
            my_item = 64 * Item(Material.STONE)  # 64 stones
            other_item = 32 * Item(Material.GOLD_BLOCK)  # or 32 gold blocks
            GameAction.spawn_item(loc, "Some items", my_item, other_item)
            # Spawns either 64 stones or 32 gold blocks at the location, with the stack named "Some items"
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)
        if not item_list or not any(item_list):
            raise ValueError("No item was specified.")

        args = Arguments([
            *[p_check(it, typing.Union[ItemParam, Listable], "items") for it in item_list],
            p_check(loc, Locatable, "loc"),
            p_check(name, Textable, "name") if name is not None else None
        ], tags=[
            Tag(
                "Apply Item Motion", option=bool(apply_item_motion),
                action=GameActionType.SPAWN_RNG_ITEM, block=BlockType.GAME_ACTION
            )
        ])
        return cls(
            action=GameActionType.SPAWN_RNG_ITEM,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def spawn_tnt(
        cls, loc: Locatable, *, power: typing.Optional[Numeric] = None, duration: typing.Optional[Numeric] = None,
        name: typing.Optional[Textable] = None
    ) -> "GameAction":
        """Spawns primed TNT at a certain location.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            TNT location.

        power : Optional[:attr:`~.Numeric`], optional
            TNT power (0-4), or ``None`` for the default (4). Defaults to ``None``.

        duration : Optional[:attr:`~.Numeric`], optional
            Fuse duration (ticks), or ``None`` for the default (0). Defaults to ``None`` (0).

        name : Optional[:attr:`~.Textable`], optional
            Custom name for the TNT. Default is ``None`` (no name).


        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # location of the TNT
            GameAction.spawn_tnt(loc, power=3, duration=40, name="My TNT")
        """
        if isinstance(power, (int, float, DFNumber)) and not 0 <= float(power) <= 4:
            raise ValueError("'power' argument must be between 0 and 4.")

        if duration is not None and power is None:
            power = 4  # default

        args = Arguments([
            p_check(loc, Locatable, "loc"),
            p_check(power, Numeric, "power") if power is not None else None,
            p_check(duration, Numeric, "duration") if duration is not None else None,
            p_check(name, Textable, "name") if name is not None else None
        ])
        return cls(
            action=GameActionType.SPAWN_TNT,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def spawn_vehicle(
        cls, vehicle: BlockParam, loc: Locatable, name: typing.Optional[Textable] = None
    ) -> "GameAction":
        """Spawns a vehicle at a certain location.

        Parameters
        ----------
        vehicle : Union[:class:`Material`, :attr:`~.ItemParam`, :attr:`~.Textable`]
            The type of vehicle.

            The type can be specified either as:
            - an instance of :class:`~.Material` (the material of the vehicle);
            - an item (:attr:`~.ItemParam` - the item representing the vehicle to spawn);
            - text (:attr:`~.Textable` - the material of the vehicle to spawn as text).

        loc : :attr:`~.Locatable`
            Vehicle location.

        name : Optional[:attr:`~.Textable`], optional
            Vehicle name. Default is ``None``.


        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Examples
        --------
        ::

            vehicle = Material.MINECART  # vehicle to spawn
            loc = DFLocation(1, 2, 3)  # where to spawn
            GameAction.spawn_vehicle(vehicle, loc, "My Vehicle")
        """
        if isinstance(vehicle, (Material, str, DFText, collections.UserString)):
            vehicle = Material(vehicle).value

        args = Arguments([
            p_check(vehicle, typing.Union[ItemParam, Textable], "vehicle"),
            p_check(loc, Locatable, "loc"),
            p_check(name, Textable, "name") if name is not None else None
        ])
        return cls(
            action=GameActionType.SPAWN_VEHICLE,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def summon_lightning(
        cls, loc: Locatable, radius: typing.Optional[Numeric] = None
    ) -> "GameAction":
        """Strikes lightning at a certain location, damaging players in a radius.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Strike location.

        radius : Optional[:attr:`~.Numeric`], optional
            Damage radius in blocks, or ``None`` for the default (3). Default is ``None``.


        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # where to strike a lightning
            GameAction.summon_lightning(loc, 5)  # radius: 5 blocks
        """
        args = Arguments([
            p_check(loc, Locatable, "loc"),
            p_check(radius, Numeric, "radius") if radius is not None else None
        ])
        return cls(
            action=GameActionType.SUMMON_LIGHTNING,
            args=args,
            append_to_reader=True
        )

    @classmethod
    def tick_block(
        cls, *locs: typing.Union[Locatable, Listable], ticks: typing.Optional[Numeric] = None
    ) -> "GameAction":
        """Causes a block/multiple blocks to get random ticked.

        Parameters
        ----------
        locs : Union[:attr:`~.Locatable`, :attr:`~.Listable`]
            Location(s) of the block(s) to be ticked.

        ticks : Optional[:attr:`~.Numeric`], optional
            Number of ticks. Default is ``None``.


        Returns
        -------
        :class:`GameAction`
            The generated GameAction instance.

        Examples
        --------
        ::

            loc_1 = DFLocation(1, 2, 3)  # one location
            loc_2 = LocationVar("my var")  # another location
            loc_3 = DFVariable("my var")  # yet another!
            GameAction.tick_block(loc_1, loc_2, loc_3, ticks=20)  # tick those 3 blocks with 20 ticks
        """
        args = Arguments([
            *[p_check(loc, typing.Union[Locatable, Listable], f"locs[{i}]") for i, loc in enumerate(locs)],
            p_check(ticks, Numeric, "ticks") if ticks is not None else None
        ])
        return cls(
            action=GameActionType.TICK_BLOCK,
            args=args,
            append_to_reader=True
        )

    # endregion:humanized-gameaction


class Control(ActionBlock, JSONData):
    """The Control block. Manages the code. See class methods for humanized methods. Example usage::

        @PlayerEvent.join
        def on_join():
            # ... do actions ...
            Control.wait(5, time_unit=CWaitTag.SECONDS)  # waits 5 seconds
            Control.line_return()  # returns

    Parameters
    ----------\u200b
    action : :class:`~py2df.enums.actions.ControlType`
        The type of Control block this is.

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this Control block.

    append_to_reader : :class:`bool`, optional
        Whether or not this newly-created :class:`Control` should be already appended to the
        :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``. (All classmethods will set this to ``True``)

    Attributes
    ----------\u200b
    block : :attr:`~py2df.enums.parameters.BlockType.CONTROL`
        The type of this codeblock (Control).

    args : :class:`~py2df.classes.collections.Arguments`
        The arguments of this Control block.

    action : :class:`~py2df.enums.actions.ControlType`
        The type of Control block this is.

    sub_action : ``None``
        (Control blocks have no sub actions.)

    length : :class:`int`
        The length, in blocks, of each individual control blocks. This is always equal to 2.

    data : ``None``
        (Control blocks have no extra codeblock data.)

    target : ``None``
        (Control blocks have no target.)
    """
    __slots__ = ("args", "action")

    block: BlockType = BlockType.CONTROL
    args: Arguments
    action: ControlType
    sub_action: None = None
    length: int = 2
    data: None = None
    target: None = None

    def __init__(
        self, action: ControlType, args: Arguments = Arguments(),
        *, append_to_reader: bool = True
    ):
        """
        Initialize this Control block.

        Parameters
        ----------
        action : :class:`~py2df.enums.actions.ControlType`
            The type of Control block this is.

        args : :class:`~py2df.classes.collections.Arguments`
            The arguments of this Control block.

        append_to_reader : :class:`bool`, optional
            Whether or not this newly-created :class:`Control` should be already appended to the
            :class:`~py2df.reading.reader.DFReader`. Defaults to ``True``. (All classmethods will set this to ``True``)
        """
        self.action = ControlType(action)
        self.args = args

        if append_to_reader:
            DFReader().append_codeblock(self)

    def as_json_data(self) -> dict:
        """Produces a JSON-serializable dict representing this Control block.

        Returns
        -------
        :class:`dict`
        """
        return dict(
            id=BLOCK_ID,
            block=Control.block.value,
            args=self.args.as_json_data(),
            action=self.action.value
        )

    @classmethod
    def end(cls) -> "Control":
        """Stops reading all code after the control block.

        Returns
        -------
        :class:`Control`
            The generated :class:`Control` block.
        """
        return Control(ControlType.END, append_to_reader=True)

    @classmethod
    def line_return(cls) -> "Control":
        """Returns to the Call Function block the current Function was called from, and continues code from there.

        Returns
        -------
        :class:`Control`
            The generated :class:`Control` block.
        """
        return Control(ControlType.RETURN, append_to_reader=True)

    @classmethod
    def skip(cls) -> "Control":
        """Skips the rest of this repeat statement's code and continues to the next repetition.

        Returns
        -------
        :class:`Control`
            The generated :class:`Control` block.
        """
        return Control(ControlType.SKIP, append_to_reader=True)

    @classmethod
    def stop_repeat(cls) -> "Control":
        """Stops a repeating sequence and continues to the next code block.

        Returns
        -------
        :class:`Control`
            The generated :class:`Control` block.
        """
        return Control(ControlType.STOP_REPEAT, append_to_reader=True)

    @classmethod
    def wait(
        cls, duration: typing.Union[int, float, DFNumber] = DEFAULT_VAL,
        *, time_unit: enums.CWaitTag = DEFAULT_VAL,
            ticks: bool = True, seconds: bool = False, minutes: bool = False
    ) -> "Control":
        """Pauses the current line of code for a certain amount of ticks. seconds, or minutes.

        Examples of usage::

            @PlayerEvent.join
            def on_join():
                # ... actions ...
                Control.wait(40)  # TICKS by default; = 2 seconds
                Control.wait(40, ticks=True)  # same as above
                Control.wait(10, seconds=True)  # 10 seconds
                Control.wait(2, minutes=True)  # 2 minutes
                Control.wait(10, time_unit=CWaitTag.SECONDS)  # 10 seconds
                Control.wait(20, time_unit=TimeUnit.SECONDS)  # 20 seconds

        Parameters
        ----------
        duration : :attr:`~.Numeric`, optional
            The duration of time to wait for, according to the time unit specified in the ``time_unit`` param.
            Defaults to ``1``

        time_unit : :class:`~.CWaitTag`, optional
            The time unit that the duration was specified in. Defaults to :attr:`~py2df.enums.actions.CWaitTag.TICKS`.

        ticks : :class:`bool`, optional
            Alternatively, setting this to True sets time_unit to :attr:`~py2df.enums.actions.CWaitTag.TICKS`.
            Defaults to ``True`` .

        seconds : :class:`bool`, optional
            Alternatively, setting this to True sets time_unit to :attr:`~py2df.enums.actions.CWaitTag.SECONDS`.
            Defaults to ``False`` .

        minutes : :class:`bool`, optional
            Alternatively, setting this to True sets time_unit to :attr:`~py2df.enums.actions.CWaitTag.MINUTES`.
            Defaults to ``False`` .

        Returns
        -------
        :class:`Control`
            The generated :class:`Control` block.

        Warnings
        --------
        Setting ``time_unit`` to anything will override the ``ticks`` , ``seconds`` and ``minutes`` params. Also,
        note that **you cannot set more than one of them** to ``True``. If that happens, the first of the following line
        ``[seconds, minutes, ticks]`` that is ``True`` is chosen as the unit.
        """
        if time_unit == DEFAULT_VAL:
            if seconds:
                time_unit = enums.CWaitTag.SECONDS
            elif minutes:
                time_unit = enums.CWaitTag.MINUTES
            else:
                time_unit = enums.CWaitTag.TICKS

        return Control(
            ControlType.WAIT,
            Arguments(
                items=[p_check(duration, Numeric, "duration")] if duration != DEFAULT_VAL else None,
                tags=[Tag(
                    "Time Unit",
                    option=enums.CWaitTag(time_unit),
                    action=ControlType.WAIT, block=cls.block
                )]
            ),
            append_to_reader=True
        )


remove_u200b_from_doc((PlayerAction, EntityAction, GameAction, Control))
