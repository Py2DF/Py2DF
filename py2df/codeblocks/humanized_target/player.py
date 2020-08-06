import collections
import itertools
import typing

from .._block_utils import _load_btype, BlockParam, _load_btypes, BlockMetadata, _load_metadata
from ..actions import PlayerAction
from ..ifs import IfPlayer, IfEntity
from ...classes import Arguments, ItemCollection, Tag, DFNumber
from ...enums import PlayerTarget, PlayerActionType, IfPlayerType, BlockType, Hand, IfPOpenInvType, PARowPos, \
    PAClearInvMode, EffectParticleMode, AdvancementType, PlayerAnimation, BossBarStyle, BossBarColor
from ...typings import Textable, Numeric, Locatable, ItemParam, Potionable, ParticleParam, p_check, SpawnEggable, \
    p_bool_check, Listable, SoundParam
from ...utils import remove_u200b_from_doc, flatten
from ...constants import DEFAULT_VAL


__all__ = ("Player",)


class Player:
    """Represents a DiamondFire Player. Used for Player Action and If Player humanized methods.

    Parameters
    ----------\u200b
    target : Optional[:class:`~.PlayerTarget`], optional
        The target that this instance represents (Default Player, Killer, Victim etc.) or ``None`` for empty target
        (equivalent to leaving the target line empty on DF - becomes the current selection, or the Default
        Player). Defaults to ``None``.

    Attributes
    ----------\u200b
    target : Optional[:class:`~.PlayerTarget`]
        The target that this instance represents (Default Player, Killer, Victim etc.) or ``None`` for empty target
        (equivalent to leaving the target line empty on DF - becomes the current selection, or the Default
        Player).
    """
    __slots__ = ("target",)
    target: typing.Optional[PlayerTarget]

    def __init__(self, target: typing.Optional[PlayerTarget]):
        self.target: typing.Optional[PlayerTarget] = PlayerTarget(target) if target else None

    def _digest_target(self, target: typing.Optional[PlayerTarget]) -> typing.Optional[PlayerTarget]:
        """Checks a given player target for validity.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`]
            The target to check.

        Returns
        -------
        Optional[:class:`~.PlayerTarget`]
            Returns the given target as a valid PlayerTarget, or None.
        """
        return PlayerTarget(target) if target else None

    # region:playeractions

    def action_bar(
        self, *texts: typing.Optional[typing.Union[Textable, Listable]],
        add_spaces: bool = False,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Sends a message on the action bar for the selected player.

        .. rank:: Mythic


        Parameters
        ----------
        texts : Union[:attr:`~.Textable`, :attr:`~.Listable`], optional
            Action bar message to send (each text given is part of the total message, separated either by spaces,
            if add_spaces is ``True``, or simply added together, if it is ``False``), or a list var with all the text
            bits. Specify nothing to send an empty action bar message.

            .. note::

                - Multiple text parts will be merged into one message.
                - Numbers and locations given will be converted to text.

        add_spaces : :class:`bool`, optional
            If ``True``, the different text bits will be joined by a space between each. If ``False``, they will be
            simply added together. Defaults to ``False``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.action_bar(Color.YELLOW + "• Points: " + Color.GREEN, TextVar("%default points"))
            # OR
            Player(PlayerTarget.DEFAULT).action_bar(Color.YELLOW + "• Points: " + Color.GREEN, TextVar("%default points"))
            # sends "• Points: %var(%default points)" to the default player's action bar.
        """
        args = Arguments([
            p_check(text, typing.Union[Textable, Listable], f"texts[{i}]") for i, text in
            enumerate(texts)
        ], tags=[
            Tag(
                "Text Value Merging", option="Add Spaces" if add_spaces else "No Spaces",  # default is No Spaces
                action=PlayerActionType.ACTION_BAR, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.ACTION_BAR,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def add_inv_row(
        self,
        *items: typing.Optional[typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]],
        new_row_position: PARowPos = PARowPos.BOTTOM,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Adds a row to the bottom or top of the currently open inventory.

        .. rank:: Emperor


        Parameters
        ----------
        items : Optional[Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]], optional
            Items to display. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.Item` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.Item`] for a predetermined list of items.

        new_row_position : :class:`~.PARowPos`, optional
            The position of the new row (either :attr:`~.PARowPos.TOP` or :attr:`~.PARowPos.BOTTOM`). Defaults
            to :attr:`~.PARowPos.BOTTOM`.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::
            
            item_1 = Item(Material.STONE, name="My Item")
            item_2 = ItemVar("my item var")
            p_default.add_inv_row(item_1, item_2, new_row_position=PANewRosPos.TOP)
            # OR
            Player(PlayerTarget.DEFAULT).add_inv_row(item_1, item_2, new_row_position=PANewRosPos.TOP)
            # adds a new row to the top of the default player's currently open inventory with the specified items.
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list
        ], tags=[
            Tag(
                "New Row Position", option=PARowPos(new_row_position),  # default is Bottom Row
                action=PlayerActionType.ADD_INV_ROW, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.ADD_INV_ROW,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def allow_drops(self, *, target: typing.Optional[PlayerTarget] = None):
        """Allows the player to drop items from their inventory.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.allow_drops()
            # OR
            Player(PlayerTarget.DEFAULT).allow_drops()
        """
        return PlayerAction(
            action=PlayerActionType.ALLOW_DROPS,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disguise_as_block(
        self, block_type: BlockParam, name: typing.Optional[Textable] = None,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Disguises the player as a block.

        .. rank:: Overlord


        Parameters
        ----------
        block_type : Union[:class:`Material`, :attr:`~.ItemParam`, :attr:`~.Textable`]
            The type of Block disguise.

            The type can be specified either as:

            - an instance of :class:`~.Material` (the material of the block to set);
            - an item (:attr:`~.ItemParam` - the item representing the block to set);
            - text (:attr:`~.Textable` - the material of the block to set as text).

        name : Optional[:attr:`~.Textable`], optional
            Name of disguise. Default is ``None`` (no name).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.block_disguise(Material.STONE, "Stone")
            # OR
            Player(PlayerTarget.DEFAULT).block_disguise(Material.STONE, "Stone")
            # disguises the default player as a stone block named "Stone"
        """
        args = Arguments([
            p_check(block_type, typing.Union[ItemParam, Textable], "block_type"),
            p_check(name, Textable, "name") if name is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.BLOCK_DISGUISE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def send_break_animation(
        self, *locs: typing.Union[Locatable, Listable], level: typing.Optional[Numeric] = None,
        overwrite_previous_fracture: bool = True,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Makes the player see block fractures on the given blocks.

        Parameters
        ----------
        locs : Union[:attr:`~.Locatable`, :attr:`~.Listable`]
            Location(s) of the block(s) to fracture.

        level : Optional[:attr:`~.Numeric`], optional
            Fracture level (1 to 10), or ``None`` to clear the fracture effect. Default is ``None``.

        overwrite_previous_fracture : :class:`bool`, optional
            If ``True``, any previous block fractures displayed on that/those block(s) will be replaced with this one.
            Defaults to ``True``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Raises
        ------
        :exc:`~.ValueError`
            If the given fracture level (`level` arg) is not within the range 1-10.

        Notes
        -----
        - Fracture animations automatically disappear after 20 seconds.

        Examples
        --------
        ::
            
            loc_1 = DFLocation(1, 2, 3)  # location of block
            loc_2 = LocationVar("my var")  # as a variable
            p_default.send_break_animation(loc_1, loc_2, level=5)
            # OR
            Player(PlayerTarget.DEFAULT).send_break_animation(loc_1, loc_2, level=5)
            # sends a level 5 block fracture on the two given locations to the default player.
        """
        if isinstance(level, (int, float, DFNumber)) and not 1 <= float(level) <= 10:
            raise ValueError("'level' arg must be between 1 and 10.")

        args = Arguments([
            *[p_check(loc, typing.Union[Locatable, Listable], f"locs[{i}]") for i, loc in enumerate(locs)],
            p_check(level, Numeric, "level") if level is not None else None
        ], tags=[
            Tag(
                "Overwrite Previous Fracture", option=bool(overwrite_previous_fracture),  # default is True
                action=PlayerActionType.BREAK_ANIMATION, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.BREAK_ANIMATION,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_chat_color(
        self, text: Textable,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the color of the player's chat messages.

        .. rank:: Overlord


        Parameters
        ----------
        text : :attr:`~.Textable`
            The player's new chat color (usage of :class:`~.Color` is recommended). Note that this can contain a color
            and a formatting modifier (e.g. bold, italics...) simultaneously.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.set_chat_color(Color.RED)
            # OR
            Player(PlayerTarget.DEFAULT).set_chat_color(Color.RED)  # the default player's messages will now be red
        """
        args = Arguments([
            p_check(text, Textable, "text")
        ])
        return PlayerAction(
            action=PlayerActionType.CHAT_COLOR,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def clear_chat(self, *, target: typing.Optional[PlayerTarget] = None):
        """Clears all messages on the player's chat window.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.clear_chat()
            # OR
            Player(PlayerTarget.DEFAULT).clear_chat()
        """
        return PlayerAction(
            action=PlayerActionType.CLEAR_CHAT,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def clear_effects(self, *, target: typing.Optional[PlayerTarget] = None):
        """Removes all of the player's potion effects.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.clear_effects()
            # OR
            Player(PlayerTarget.DEFAULT).clear_effects()
        """
        return PlayerAction(
            action=PlayerActionType.CLEAR_EFFECTS,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def clear_inventory(
        self,
        *, clear_mode: PAClearInvMode = PAClearInvMode.ENTIRE_INVENTORY, clear_crafting_and_cursor: bool = True,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Empties the player's inventory.

        Parameters
        ----------
        clear_mode : :class:`~.PAClearInvMode`, optional
            How much of the inventory should be cleared (either :attr:`~.PAClearInvMode.ENTIRE_INVENTORY`,
            :attr:`~.PAClearInvMode.UPPER_INVENTORY`, :attr:`~.PAClearInvMode.HOTBAR` or
            :attr:`~.PAClearInvMode.ARMOR`). Defaults to :attr:`~.PAClearInvMode.ENTIRE_INVENTORY`.

        clear_crafting_and_cursor : :class:`bool`, optional
            If the crafting area and the cursor should be cleared as well. Defaults to ``True``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.clear_inventory()
            # OR
            Player(PlayerTarget.DEFAULT).clear_inventory()  # clears the whole inventory, including crafting area/cursor
        
        ::
            
            p_default.clear_inventory(clear_mode=PAClearInvMode.HOTBAR, clear_crafting_and_cursor=False)
            # OR
            Player(PlayerTarget.DEFAULT).clear_inventory(clear_mode=PAClearInvMode.HOTBAR, clear_crafting_and_cursor=False)
            # clears just the player's hotbar, while keeping the player's cursor and crafting area, along with the rest of the inv, intact.
        """
        args = Arguments([], tags=[
            Tag(
                "Clear Mode", option=PAClearInvMode(clear_mode),  # default is Entire Inventory
                action=PlayerActionType.CLEAR_INV, block=BlockType.PLAYER_ACTION
            ),
            Tag(
                "Clear Crafting and Cursor", option=bool(clear_crafting_and_cursor),  # default is True
                action=PlayerActionType.CLEAR_INV, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.CLEAR_INV,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def clear_item(
        self, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Removes certain item's from the player's inventory.

        Parameters
        ----------
        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]
            Item(s) to clear. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.Item` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.Item`] for a predetermined list of items.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::
            
            item_1 = Item(Material.STONE, name="Stone")
            item_2 = ItemVar("my var")
            p_default.clear_item(item_1, item_2)
            # OR
            Player(PlayerTarget.DEFAULT).clear_item(item_1, item_2)
            # clears all instances of the given items from the default player's inventory.
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list
        ])
        return PlayerAction(
            action=PlayerActionType.CLEAR_ITEM,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def close_inventory(self, *, target: typing.Optional[PlayerTarget] = None):
        """Closes the player's currently open inventory menu.

        .. rank:: Emperor


        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.close_inventory()
            # OR
            Player(PlayerTarget.DEFAULT).close_inventory()
        """
        return PlayerAction(
            action=PlayerActionType.CLOSE_INV,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def damage(
        self, damage: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Damages the player.

        Parameters
        ----------
        damage : :attr:`~.Numeric`
            Damage to inflict.

            .. note::

                1 damage = 0.5 hearts

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.damage(2)
            # OR
            Player(PlayerTarget.DEFAULT).damage(2)  # deals 1 heart of damage to the default player
        """
        args = Arguments([
            p_check(damage, Numeric, "damage")
        ])
        return PlayerAction(
            action=PlayerActionType.DAMAGE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def enable_death_drops(self, *, target: typing.Optional[PlayerTarget] = None):
        """When this code block is executed, the player will drop the contents of their inventory when they die.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.enable_death_drops()
            # OR
            Player(PlayerTarget.DEFAULT).enable_death_drops()
        """
        return PlayerAction(
            action=PlayerActionType.DEATH_DROPS,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disable_blocks(
        self, *block_types: typing.Optional[typing.Union[BlockParam, Listable]],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Prevents the player from placing and breaking certain blocks. If no blocks are given as parameters, all blocks will be disallowed.

        .. rank:: Noble


        Parameters
        ----------
        block_types : Optional[Union[:class:`Material`, :attr:`~.ItemParam`, :attr:`~.Textable`, :attr:`~.Listable`]], optional
            The type of Blocks to disallow.

            The type can be specified either as:

            - an instance of :class:`~.Material` (the material of the block to set);
            - an item (:attr:`~.ItemParam` - the item representing the block to set);
            - text (:attr:`~.Textable` - the material of the block to set as text);
            - a :attr:`~.Listable` (A List - in DF - variable containing either Item or Text parameters).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.disable_blocks(Material.STONE, Material.GRASS_BLOCK)
            # OR
            Player(PlayerTarget.DEFAULT).disable_blocks(Material.STONE, Material.GRASS_BLOCK)
            # disallows the player from interacting with stone blocks and grass blocks.
        """
        true_btypes = _load_btypes(block_types)

        args = Arguments([
            p_check(block_type, typing.Union[ItemParam, Textable], f"block_types[{i}]") for i, block_type in
            enumerate(true_btypes)
        ])
        return PlayerAction(
            action=PlayerActionType.DISABLE_BLOCKS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disable_flight(self, *, target: typing.Optional[PlayerTarget] = None):
        """Prevents the player from flying.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.disable_flight()
            # OR
            Player(PlayerTarget.DEFAULT).disable_flight()
        """
        return PlayerAction(
            action=PlayerActionType.DISABLE_FLIGHT,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disable_pvp(self, *, target: typing.Optional[PlayerTarget] = None):
        """Prevents the player from damaging other players.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.disable_pvp()
            # OR
            Player(PlayerTarget.DEFAULT).disable_pvp()
        """
        return PlayerAction(
            action=PlayerActionType.DISABLE_PVP,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disallow_drops(self, *, target: typing.Optional[PlayerTarget] = None):
        """Prevents the player from dropping items from their inventory.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.disallow_drops()
            # OR
            Player(PlayerTarget.DEFAULT).disallow_drops()
        """
        return PlayerAction(
            action=PlayerActionType.DISALLOW_DROPS,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def enable_blocks(
        self, *block_types: typing.Optional[typing.Union[BlockParam, Listable]],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Allows the player to place and break certain blocks. If no blocks are given as parameters, all blocks will be enabled.

        .. rank:: Noble


        Parameters
        ----------
        block_types : Optional[Union[:class:`Material`, :attr:`~.ItemParam`, :attr:`~.Textable`, :attr:`~.Listable`]], optional
            The type of Blocks to allow.

            The type can be specified either as:

            - an instance of :class:`~.Material` (the material of the block to set);
            - an item (:attr:`~.ItemParam` - the item representing the block to set);
            - text (:attr:`~.Textable` - the material of the block to set as text);
            - a :attr:`~.Listable` (A List - in DF - variable containing either Item or Text parameters).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.enable_blocks(Material.STONE, Material.SAND)
            # OR
            Player(PlayerTarget.DEFAULT).enable_blocks(Material.STONE, Material.SAND)
            # allows the default player to interact with stone and sand blocks.
        """
        true_btypes = _load_btypes(block_types)

        args = Arguments([
            p_check(block_type, typing.Union[ItemParam, Textable], f"block_types[{i}]") for i, block_type in
            enumerate(true_btypes)
        ])
        return PlayerAction(
            action=PlayerActionType.ENABLE_BLOCKS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def enable_flight(self, *, target: typing.Optional[PlayerTarget] = None):
        """Allows the player to fly.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.enable_flight()
            # OR
            Player(PlayerTarget.DEFAULT).enable_flight()
        """
        return PlayerAction(
            action=PlayerActionType.ENABLE_FLIGHT,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def enable_pvp(self, *, target: typing.Optional[PlayerTarget] = None):
        """Allows the player to damage other players.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.enable_pvp()
            # OR
            Player(PlayerTarget.DEFAULT).enable_pvp()
        """
        return PlayerAction(
            action=PlayerActionType.ENABLE_PVP,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def expand_inventory(
        self,
        *items: typing.Optional[typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]],
        target: typing.Optional[PlayerTarget] = None
    ):
        """If an inventory menu is open for the player, 'Expand Inventory Menu' adds 3 more rows using the items given.

        .. rank:: Emperor


        Parameters
        ----------
        items : Optional[Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]], optional
            Items to display. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.Item` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.Item`] for a predetermined list of items.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            item_1 = Item(Material.DIAMOND_SWORD, name="My Item")
            item_2 = ItemVar("my var")
            item_3 = Item(Material.STONE, lore=["a", "b"])
            p_default.expand_inventory(item_1, item_2, item_3)
            # OR
            Player(PlayerTarget.DEFAULT).expand_inventory(item_1, item_2, item_3)
            # Expands the default player's currently open inventory by adding 3 rows, while having the first one contain the given items.
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list
        ])
        return PlayerAction(
            action=PlayerActionType.EXPAND_INV,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_flight_speed(
            self, speed: Numeric,
            *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the player's flight speed.

        .. rank:: Noble


        Parameters
        ----------
        speed : :attr:`~.Numeric`
            % of normal flight speed (-1000 to 1000).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Raises
        ------
        :exc:`ValueError`
            If the given speed is not between -1000 and 1000.

        Examples
        --------
        ::

            p_default.set_flight_speed(500)
            # OR
            Player(PlayerTarget.DEFAULT).set_flight_speed(500)  # the default player's flight speed is now 5x faster.
        """
        if isinstance(speed, (int, float, DFNumber)) and not -1000 <= float(speed) <= 1000:
            raise ValueError("'speed' arg must be between -1000 and 1000.")

        args = Arguments([
            p_check(speed, Numeric, "speed")
        ])
        return PlayerAction(
            action=PlayerActionType.FLIGHT_SPEED,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def force_flight(
        self,
        *, start: bool = DEFAULT_VAL, stop: bool = False,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Forces the player to start or stop flying.

        Parameters
        ----------
        start : :class:`bool`, optional
            If ``True``, the player will be forced to start flying. Defaults to ``True`` (note that setting
            `stop` to ``True`` and not specifying this will set it to stop flying).

        stop : :class:`bool`, optional
            If ``True``, the player will be forced to stop flying. Defaults to ``False``).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Raises
        ------
        :exc:`ValueError`
            If both `start` and `stop` are given as the same boolean value (if both are truthy or both falsy).

        Examples
        --------
        Start flying::

            p_default.force_flight()
            # OR
            Player(PlayerTarget.DEFAULT).force_flight()  # or specify start=True. Forces the default player to fly

        Stop flying::

            p_default.force_flight(stop=True)
            # OR
            Player(PlayerTarget.DEFAULT).force_flight(stop=True)  # Forces the default player to stop flying.
        """
        if start != DEFAULT_VAL and bool(start) == bool(stop):
            raise ValueError("Please specify either 'start' or 'stop' args as True, not both False or both True.")

        args = Arguments([], tags=[
            Tag(
                "Flight Mode", option="Start Flight" if start or not stop else "Stop Flight",  # default is Start Flight
                action=PlayerActionType.FORCE_FLIGHT, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.FORCE_FLIGHT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def force_glide(
        self,
        *, start: bool = DEFAULT_VAL, stop: bool = False,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Forces the player to start or stop gliding.

        Parameters
        ----------
        start : :class:`bool`, optional
            If ``True``, the player will be forced to start gliding. Defaults to ``True`` (note that setting
            `stop` to ``True`` and not specifying this will set it to stop gliding).

        stop : :class:`bool`, optional
            If ``True``, the player will be forced to stop gliding. Defaults to ``False``).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Raises
        ------
        :exc:`ValueError`
            If both `start` and `stop` are given as the same boolean value (if both are truthy or both falsy).

        Examples
        --------
        Start gliding::

            p_default.force_glide()
            # OR
            Player(PlayerTarget.DEFAULT).force_glide()  # or specify start=True. Forces the default player to glide

        Stop gliding::

            p_default.force_glide(stop=True)
            # OR
            Player(PlayerTarget.DEFAULT).force_glide(stop=True)  # Forces the default player to stop gliding.
        """
        if start != DEFAULT_VAL and bool(start) == bool(stop):
            raise ValueError("Please specify either 'start' or 'stop' args as True, not both False or both True.")

        args = Arguments([], tags=[
            Tag(
                "Glide Mode",
                option="Start Gliding" if start or not stop else "Stop Gliding",  # default is Start Gliding
                action=PlayerActionType.FORCE_GLIDE, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.FORCE_GLIDE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def give_effect(
        self, *potions: typing.Union[Potionable, Listable],
        effect_particle_mode: EffectParticleMode = EffectParticleMode.SHOWN,
        overwrite_existing_effect: bool = False,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Gives the player one or more potion effects.

        Parameters
        ----------
        potions : Union[:attr:`~.Potionable`, :attr:`~.Listable`]
            Potion effect(s) to give, or a List variable with all the potion effects.

        effect_particle_mode : :class:`~.EffectParticleMode`, optional
            The mode applied to the effect particles (either :attr:`~.EffectParticleMode.SHOWN`,
            :attr:`~.EffectParticleMode.BEACON` or :attr:`~.EffectParticleMode.HIDDEN`). Defaults to
            :attr:`~.EffectParticleMode.SHOWN`.

        overwrite_existing_effect : :class:`bool`, optional
            If existing effects should be overridden by the given ones. Defaults to ``False`` (no).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            potion_1 = DFPotion(PotionEffect.ABSORPTION, amplifier=255, duration=(5, 0))  # Absorption 255, 5 min dur.
            potion_2 = PotionVar("my var")  # potion variable
            p_default.give_effect(potion_1, potion_2, effect_particle_mode=EffectParticleMode.BEACON)
            # OR
            Player(PlayerTarget.DEFAULT).give_effect(potion_1, potion_2, effect_particle_mode=EffectParticleMode.BEACON)
            # gives two potion effects with beacon-mode particles to the default player.
        """
        args = Arguments([
            p_check(potion, typing.Union[Potionable, Listable], f"potions[{i}]") for i, potion in enumerate(potions)
        ], tags=[
            Tag(
                "Effect Particle Mode", option=EffectParticleMode(effect_particle_mode),  # default is Shown
                action=PlayerActionType.GIVE_EFFECT, block=BlockType.PLAYER_ACTION
            ),
            Tag(
                "Overwrite Existing Effect", option=bool(overwrite_existing_effect),  # default is False
                action=PlayerActionType.GIVE_EFFECT, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.GIVE_EFFECT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def give_items(
        self, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable],
        amount: typing.Optional[Numeric] = None,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Gives the player all of the specified items.

        Parameters
        ----------
        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]
            Item(s) to give. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.Item` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.Item`] for a predetermined list of items.

        amount : Optional[:attr:`~.Numeric`], optional
            Amount of times to give those items, or ``None`` for the default (1 time). Default is ``None``.

            .. note::

                If an amount is specified, the items will be repeatedly given that many times.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Examples
        --------
        Give once::

            item_1 = Item(Material.STONE)
            item_2 = ItemVar("some item")
            p_default.give_items(item_1, item_2)
            # OR
            Player(PlayerTarget.DEFAULT).give_items(item_1, item_2)  # gives the player the specified items.

        Give twice or more::

            item_1 = Item(Material.STONE)
            item_2 = ItemVar("some item")
            p_default.give_items(item_1, item_2, amount=2)
            # OR
            Player(PlayerTarget.DEFAULT).give_items(item_1, item_2, amount=2)  # gives the player the specified items twice.
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            *[p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list],
            p_check(amount, Numeric, "amount") if amount is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.GIVE_ITEMS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def give_random_item(
        self, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Gives the player a random item or stack of items from the list of items.

        Parameters
        ----------
        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]
            Items to pick from. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.Item` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.Item`] for a predetermined list of items.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        Will give a different item to each targeted player.


        Examples
        --------
        ::

            item_1 = Item(Material.STONE)
            item_2 = ItemVar("some item var")
            p_default.give_random_item(item_1, item_2)
            # OR
            Player(PlayerTarget.DEFAULT).give_random_item(item_1, item_2)
            # randomly picks one of the given items to give to the default player.
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list
        ])
        return PlayerAction(
            action=PlayerActionType.GIVE_RNG_ITEM,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_gm_adventure(self, *, target: typing.Optional[PlayerTarget] = None):
        """Sets the player's gamemode to adventure.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.set_gm_adventure()
            # OR
            Player(PlayerTarget.DEFAULT).set_gm_adventure()
        """
        return PlayerAction(
            action=PlayerActionType.GM_ADVENTURE,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_gm_creative(self, *, target: typing.Optional[PlayerTarget] = None):
        """Sets the player's gamemode to creative.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        - BE WARNED, the player can spawn in any item they wish through the use of toolbars!
        - Click own inventory events may not work as expected.


        Examples
        --------
        ::

            p_default.set_gm_creative()
            # OR
            Player(PlayerTarget.DEFAULT).set_gm_creative()
        """
        return PlayerAction(
            action=PlayerActionType.GM_CREATIVE,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_gm_survival(self, *, target: typing.Optional[PlayerTarget] = None):
        """Sets the player's gamemode to survival.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.set_gm_survival()
            # OR
            Player(PlayerTarget.DEFAULT).set_gm_survival()
        """
        return PlayerAction(
            action=PlayerActionType.GM_SURVIVAL,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def heal(
        self, amount: typing.Optional[Numeric] = None,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Restores the player's health fully or by an amount.

        Parameters
        ----------
        amount : Optional[:attr:`~.Numeric`], optional
            Amount to heal. Default is ``None`` (Heal fully).

            .. note::

                1 health = 0.5 hearts

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.heal(4)
            # OR
            Player(PlayerTarget.DEFAULT).heal(4)  # heals the default player by 2 hearts
        """
        args = Arguments([
            p_check(amount, Numeric, "amount") if amount is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.HEAL,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def hide_disguise(self, *, target: typing.Optional[PlayerTarget] = None):
        """Hides the player's disguise on their screen.

        .. rank:: Overlord


        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.hide_disguise()
            # OR
            Player(PlayerTarget.DEFAULT).hide_disguise()
        """
        return PlayerAction(
            action=PlayerActionType.HIDE_DISGUISE,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def enable_keep_inv(self, *, target: typing.Optional[PlayerTarget] = None):
        """Allows players to keep their inventory's contents when they die.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        This is different from :meth:`enable_death_drops`: While that method guarantees that the player's items will
        be dropped to the ground on death (which is the default behavior), this method simply guarantees that the
        player's items will remain in their inventory even when they respawn (independently of whether or not they were
        dropped to the ground).

        Examples
        --------
        ::

            p_default.enable_keep_inv()
            # OR
            Player(PlayerTarget.DEFAULT).enable_keep_inv()
        """
        return PlayerAction(
            action=PlayerActionType.KEEP_INV,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def kick(self, *, target: typing.Optional[PlayerTarget] = None):
        """Kicks the player from the plot.

        .. rank:: Noble


        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.kick()
            # OR
            Player(PlayerTarget.DEFAULT).kick()
        """
        return PlayerAction(
            action=PlayerActionType.KICK,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def launch_forward(
        self, power: Numeric,
        *, yaw_only: bool = False,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Launches the player a certain amount forward or backward.

        Parameters
        ----------
        power : :attr:`~.Numeric`
            Launch power.

            .. note::

                A negative power will the launch the player backwards.

        yaw_only : :class:`bool`, optional
            If ``True``, only yaw is considered on launch axis. If ``False``, pitch is also considered. Defaults
            to ``False``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        A positive launch power will the launch the player forward, and a negative one, backward.


        Examples
        --------
        ::

            p_default.launch_forward(5)
            # OR
            Player(PlayerTarget.DEFAULT).launch_forward(5)  # launches last spawned mob forward with a power of 5
            # -5 for backwards with same power
        """
        args = Arguments([
            p_check(power, Numeric, "power")
        ], tags=[
            Tag(
                "Launch Axis", option="Yaw Only" if yaw_only else "Pitch and Yaw",  # default is Pitch and Yaw
                action=PlayerActionType.LAUNCH_FWD, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.LAUNCH_FWD,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def launch_projectile(
        self, projectile: BlockParam, *, loc: typing.Optional[Locatable] = None,
        name: typing.Optional[Textable] = None, speed: typing.Optional[Numeric] = None,
        inaccuracy: typing.Optional[Numeric] = None, particle: typing.Optional[ParticleParam] = None,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Launches a projectile from the player.

        Parameters
        ----------
        projectile : Union[:class:`Material`, :attr:`~.ItemParam`, :attr:`~.Textable`]
            The type of Projectile to launch.

            The type can be specified either as:

            - an instance of :class:`~.Material` (the material of the block to set);
            - an item (:attr:`~.ItemParam` - the item representing the block to set);
            - text (:attr:`~.Textable` - the material of the block to set as text).

        loc : Optional[:attr:`~.Locatable`], optional
            Launch point (where the projectile is launched from). Default is ``None`` (from the player in a predetermined
            spot).

        name : Optional[:attr:`~.Textable`], optional
            Projectile name. Default is ``None`` (no name).

        speed : Optional[:attr:`~.Numeric`], optional
            The projectile's speed. Default is ``None`` (default speed).

            .. note::

                This has to be specified in order for `inaccuracy` to be given, or a :exc:`ValueError` is raised.

        inaccuracy : Optional[:attr:`~.Numeric`], optional
            Inaccuracy (how much random momentum is applied on launch), or ``None`` for the default (1).
            Default is ``None`` (1).

        particle : Optional[:attr:`~.ParticleParam`], optional
            A particle to be the projectile's launch trail. Default is ``None`` (no launch trail).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Examples
        --------
        ::

            proj = Material.ARROW  # launch an arrow from the player
            partc = ParticleType.BUBBLE  # bubble trail
            p_default.launch_projectile(proj, name="My Arrow", speed=5, inaccuracy=2, particle=partc)
            # OR
            Player(PlayerTarget.DEFAULT).launch_projectile(proj, name="My Arrow", speed=5, inaccuracy=2, particle=partc)
        """
        if inaccuracy is not None and speed is None:
            raise ValueError("Cannot specify 'inaccuracy' argument without specifying 'speed'.")

        args = Arguments([
            p_check(projectile, typing.Union[ItemParam, Textable], "projectile"),
            p_check(loc, Locatable, "loc") if loc is not None else None,
            p_check(name, Textable, "name") if name is not None else None,
            p_check(speed, Numeric, "speed") if speed is not None else None,
            p_check(inaccuracy, Numeric, "inaccuracy") if inaccuracy is not None else None,
            p_check(particle, ParticleParam, "particle") if particle is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.LAUNCH_PROJ,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def launch_toward(
        self, loc: Locatable, power: typing.Optional[Numeric] = None,
        *, ignore_distance: bool = False,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Launches the player toward a certain location.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            The location to launch the player towards.

        power : Optional[:attr:`~.Numeric`], optional
            Launch power. Default is ``None`` (a default value is assigned for power).

            .. note:;

                A negative launch power will launch the entity away from the location.

        ignore_distance : :class:`bool`, optional
            If the distance between the player and the location should be ignored when calculating the strength of the
            pull. Defaults to ``False``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # the location where to launch towards
            p_default.launch_toward(loc, 10)
            # OR
            Player(PlayerTarget.DEFAULT).launch_toward(loc, 10)  # launch the default player towards location
                                                                 # with a power of 10
        """
        args = Arguments([
            p_check(loc, Locatable, "loc"),
            p_check(power, Numeric, "power") if power is not None else None
        ], tags=[
            Tag(
                "Ignore Distance", option=bool(ignore_distance),  # default is False
                action=PlayerActionType.LAUNCH_TOWARD, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.LAUNCH_TOWARD,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def launch_up(
        self, power: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Launches the player a certain amount up or down. A positive amount is up, and a negative amount is down.

        Parameters
        ----------
        power : :attr:`~.Numeric`
            Launch power.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.launch_up(10)
            # OR
            Player(PlayerTarget.DEFAULT).launch_up(10)  # Launches the player up with power 10 (use -10 for down).
        """
        args = Arguments([
            p_check(power, Numeric, "power")
        ])
        return PlayerAction(
            action=PlayerActionType.LAUNCH_UP,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def play_lightning_effect(
        self, loc: Locatable,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Plays a thunderbolt effect to the player that is silent and deals no damage.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Strike location.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # location of the thunderbolt effect
            p_default.play_lightning_effect(loc)
            # OR
            Player(PlayerTarget.DEFAULT).play_lightning_effect(loc)
            # plays a client-side thunderbolt effect for the default player.
        """
        args = Arguments([
            p_check(loc, Locatable, "loc")
        ])
        return PlayerAction(
            action=PlayerActionType.LIGHTNING_EFFECT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def load_saved_inv(self, *, target: typing.Optional[PlayerTarget] = None):
        """Loads the selected saved inventory.

        .. rank:: Noble


        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        - If no saved inventory exists, the player's inventory will be cleared.
        - Inventories loaded with 'Load Saved Inventory' take several ticks to load. Use 'Control: Wait' if you need to check the inventory's contents after it is loaded.


        Examples
        --------
        ::

            p_default.load_saved_inv()
            # OR
            Player(PlayerTarget.DEFAULT).load_saved_inv()
        """
        return PlayerAction(
            action=PlayerActionType.LOAD_INV,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disguise_as_mob(
        self, spawn_egg: SpawnEggable, name: typing.Optional[Textable] = None,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Disguises the player as a mob.

        .. rank:: Overlord


        Parameters
        ----------
        spawn_egg : :attr:`~.SpawnEggable`
            Mob to disguise as (a spawn egg).

        name : Optional[:attr:`~.Textable`], optional
            Disguise name (of the mob). Default is ``None`` (no name).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            mob = Material.ZOMBIE_SPAWN_EGG  # disguise as zombie
            p_default.disguise_as_mob(mob, "Zomb")
            # OR
            Player(PlayerTarget.DEFAULT).disguise_as_mob(mob, "Zomb")  # disguise the default player as a zombie
                                                                       # named "Zomb"
        """
        args = Arguments([
            p_check(spawn_egg, SpawnEggable, "spawn_egg"),
            p_check(name, Textable, "name") if name is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.MOB_DISGUISE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def enable_nat_regen(self, *, target: typing.Optional[PlayerTarget] = None):
        """Allows the player's health to regenerate naturally.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.enable_nat_regen()
            # OR
            Player(PlayerTarget.DEFAULT).enable_nat_regen()
        """
        return PlayerAction(
            action=PlayerActionType.NAT_REGEN,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disable_death_drops(self, *, target: typing.Optional[PlayerTarget] = None):
        """When this code block is executed, the player will no longer drop the contents of their inventory when they die.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.disable_death_drops()
            # OR
            Player(PlayerTarget.DEFAULT).disable_death_drops()
        """
        return PlayerAction(
            action=PlayerActionType.NO_DEATH_DROPS,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disable_keep_inv(self, *, target: typing.Optional[PlayerTarget] = None):
        """When this code block is executed, the player will no longer keep the contents of their inventory when they die.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.disable_keep_inv()
            # OR
            Player(PlayerTarget.DEFAULT).disable_keep_inv()
        """
        return PlayerAction(
            action=PlayerActionType.NO_KEEP_INV,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disable_nat_regen(self, *, target: typing.Optional[PlayerTarget] = None):
        """Prevents the player's health from regenerating naturally.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.disable_nat_regen()
            # OR
            Player(PlayerTarget.DEFAULT).disable_nat_regen()
        """
        return PlayerAction(
            action=PlayerActionType.NO_NAT_REGEN,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disable_proj_coll(self, *, target: typing.Optional[PlayerTarget] = None):
        """Prevents projectiles from hitting the player.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.disable_proj_coll()
            # OR
            Player(PlayerTarget.DEFAULT).disable_proj_coll()
        """
        return PlayerAction(
            action=PlayerActionType.NO_PROJ_COLL,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def open_block_inv(
        self, loc: Locatable,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Opens a container inventory. Also works with crafting tables.

        .. rank:: Emperor


        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Location of the block to be accessed.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # location of the block with an inventory to be opened
            p_default.open_block_inv(loc)
            # OR
            Player(PlayerTarget.DEFAULT).open_block_inv(loc)
            # opens the inventory at the given location for the default player
        """
        args = Arguments([
            p_check(loc, Locatable, "loc")
        ])
        return PlayerAction(
            action=PlayerActionType.OPEN_BLOCK_INV,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def open_book(
        self, item: ItemParam,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Opens a written book's menu.

        .. rank:: Emperor


        Parameters
        ----------
        item : :attr:`~.ItemParam`
            Book item to be opened.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        Opened book and quills cannot be edited.


        Examples
        --------
        ::

            item = ItemVar("variable containing my written book")
            p_default.open_book(item)
            # OR
            Player(PlayerTarget.DEFAULT).open_book(item)  # opens the specified book item for the default player to read.

        Todo
        ----
        Add example using class WrittenBook (when it is made)
        """
        args = Arguments([
            p_check(item, ItemParam, "item")
        ])
        return PlayerAction(
            action=PlayerActionType.OPEN_BOOK,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def play_particle_effect(
        self, particle: ParticleParam, loc: Locatable, *, count: typing.Optional[Numeric] = None,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Plays one or more of the particle to the player.

        Parameters
        ----------
        particle : :attr:`~.ParticleParam`
            Particle effect.

        loc : :attr:`~.Locatable`
            Particle location.

        count : Optional[:attr:`~.Numeric`], optional
            Particle count, or ``None`` for a default value. Default is ``None``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            particle = DFParticle(ParticleType.CLOUD)  # the particle type
            loc = DFLocation(1, 2, 3)  # where to play the particles
            p_default.play_particle_effect(particle, loc, count=5)
            # OR
            Player(PlayerTarget.DEFAULT).play_particle_effect(particle, loc, count=5)
            # plays 5 of the cloud particle at the specified location for the default player.
        """
        args = Arguments([
            p_check(particle, ParticleParam, "particle"),
            p_check(loc, Locatable, "loc"),
            p_check(count, Numeric, "count") if count is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.PARTICLE_EFFECT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def perform_command(
        self, text: Textable,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Makes the player execute a plot command.

        .. rank:: Emperor


        Parameters
        ----------
        text : :attr:`~.Textable`
            Plot command to be executed by the player, including the arguments.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.perform_command("some_command arg2 arg3 arg4 a b")
            # OR
            Player(PlayerTarget.DEFAULT).perform_command("some_command arg2 arg3 arg4 a b")
            # equivalent to the default player sending "@some_command arg2 arg3 arg4 a b"; this forces them to do it.
        """
        args = Arguments([
            p_check(text, Textable, "text")
        ])
        return PlayerAction(
            action=PlayerActionType.PERFORM_COMMAND,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    sudo_command = perform_command
    """alias for :meth:`perform_command`"""

    def play_sound(
        self, *sounds: typing.Union[SoundParam, Listable], loc: typing.Optional[Locatable] = None,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Plays a sound effect for the player.

        Parameters
        ----------
        sounds : Union[:attr:`~.SoundParam`, :attr:`~.Listable`]
            Sound(s) to play for the player.

        loc : Optional[:attr:`~.Locatable`], optional
            Playback location, if they should be played at a specific location, or ``None`` to play in no specific
            location (i.e., at the player - no matter to where they move, they hear the sound). Default is ``None``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.play_sound(sounds)
            # OR
            Player(PlayerTarget.DEFAULT).play_sound(sounds)  # TODO: sound example
        """
        args = Arguments([
            *[p_check(sound, typing.Union[SoundParam, Listable], f"sounds[{i}]") for i, sound in enumerate(sounds)],
            p_check(loc, Locatable, "loc") if loc is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.PLAY_SOUND,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def play_sound_sequence(
        self, *sounds: typing.Union[SoundParam, Listable], delay: typing.Optional[Numeric] = None,
        loc: typing.Optional[Locatable] = None,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Plays a sequence of sounds for the player, with a delay after each sound.

        Parameters
        ----------
        sounds : Union[:attr:`~.SoundParam`, :attr:`~.Listable`]
            Sounds to play.

        delay : Optional[:attr:`~.Numeric`], optional
            Sound delay (ticks), or ``None`` for the default (60 ticks = 3 seconds). Default is ``None``.

        loc : Optional[:attr:`~.Locatable`], optional
            Playback location, or ``None`` for no specific location (at the player). Default is ``None``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # where to play the sounds.
            p_default.play_sound_sequence(sounds, delay=40, loc=loc)
            # OR
            Player(PlayerTarget.DEFAULT).play_sound_sequence(sounds, delay=40, loc=loc)  # TODO: sound Example
        """
        args = Arguments([
            *[p_check(sound, typing.Union[SoundParam, Listable], f"sounds[{i}]") for i, sound in enumerate(sounds)],
            p_check(delay, Numeric, "delay") if delay is not None else None,
            p_check(loc, Locatable, "loc") if loc is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.PLAY_SOUND_SEQ,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disguise_as_player(
        self, name: Textable, *, skin: typing.Optional[Textable] = None,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Disguises the player as another player.

        .. rank:: Overlord


        Parameters
        ----------
        name : :attr:`~.Textable`
            Name of the player to disguise as.

        skin : Optional[:attr:`~.Textable`], optional
            Name of the player whose skin should be used, or ``None`` for the skin of the player given in `name`.
            Default is ``None``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.disguise_as_player("John", skin="Notch")
            # OR
            Player(PlayerTarget.DEFAULT).disguise_as_player("John", skin="Notch") # disguises as the Notch skin,
                                                                                  # but named "John".
        """
        args = Arguments([
            p_check(name, Textable, "name"),
            p_check(skin, Textable, "skin") if skin is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.PLAYER_DISGUISE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def enable_proj_coll(self, *, target: typing.Optional[PlayerTarget] = None):
        """Allows projectiles to hit the player.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.proj_coll()
            # OR
            Player(PlayerTarget.DEFAULT).proj_coll()
        """
        return PlayerAction(
            action=PlayerActionType.PROJ_COLL,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    try:  # py 3.8+
        _One_to_Four = typing.Union[typing.Literal[1], typing.Literal[2], typing.Literal[3], typing.Literal[4]]
    except AttributeError:  # up to py 3.7.x
        _One_to_Four = typing.cast(typing.Any, int)

    def remove_boss_bar(
        self,
        *, bar_slot: typing.Optional[_One_to_Four] = None,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Removes the given boss bar from the player if there is one.

        .. rank:: Mythic


        Parameters
        ----------
        bar_slot : Optional[:class:`int`], optional
            The bossbar slot that should be cleared (either 1, 2, 3 or 4), or ``None`` to clear all. Defaults to
            ``None``.
            All Bossbars, 1, 2, 3, 4

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Raises
        ------
        :exc:`ValueError`
            If the bossbar slot given is not one of 1, 2, 3, 4.

        Examples
        --------
        Remove all bossbars::

            p_default.remove_boss_bar()
            # OR
            Player(PlayerTarget.DEFAULT).remove_boss_bar()  # removes all visible bossbars for the default player

        Remove a specific bossbar::

            p_default.remove_boss_bar(bar_slot=3)
            # OR
            Player(PlayerTarget.DEFAULT).remove_boss_bar(bar_slot=3)  # removes the third bossbar for the default player
        """
        if bar_slot is not None and bar_slot not in (1, 2, 3, 4):
            raise ValueError("'bar_slot' arg must either be None or one of 1, 2, 3, 4.")

        args = Arguments([], tags=[
            Tag(
                "Bar Slot", option=bar_slot if bar_slot is not None else "All Bossbars",  # default is All Bossbars
                action=PlayerActionType.REMOVE_BOSS_BAR, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.REMOVE_BOSS_BAR,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def remove_effect(
        self, *potions: typing.Union[Potionable, Listable],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Removes potion effects from the player.

        Parameters
        ----------
        potions : Union[:attr:`~.Potionable`, :attr:`~.Listable`]
            Potion effect(s) to be removed, or a List variable containing them.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        Amplifiers and durations do not have to be the same as the initial potion effect(s).


        Examples
        --------
        ::

            potion_1 = DFPotion(PotionEffect.ABSORPTION, amplifier=5)
            potion_2 = PotionVar("my var containing a potion")
            p_default.remove_effect(potion_1, potion_2)
            # OR
            Player(PlayerTarget.DEFAULT).remove_effect(potion_1, potion_2)  # removes potion_1 and potion_2 effects
                                                                            # from the default player.
        """
        args = Arguments([
            p_check(potion, typing.Union[Potionable, Listable], f"potions[{i}]") for i, potion in enumerate(potions)
        ])
        return PlayerAction(
            action=PlayerActionType.REMOVE_EFFECT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def remove_inv_row(
        self, amount: typing.Optional[Numeric] = None,
        *, row_pos: PARowPos = PARowPos.BOTTOM,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Removes the given number of rows from the bottom or top of the currently open inventory.

        .. rank:: Emperor


        Parameters
        ----------
        amount : Optional[:attr:`~.Numeric`], optional
            Amount of rows to remove, counting from the bottom, or ``None`` for a predetermined amount.
            Default is ``None``.

        row_pos : :class:`~.PARowPos`, optional
            The position from which `n` rows should be removed (for `n` = the number given in the `rows` arg) -
            either :attr:`~.PARowPos.TOP` or :attr:`~.PARowPos.BOTTOM`. Defaults to :attr:`~.PARowPos.BOTTOM`.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.remove_inv_row(3, row_pos=PARowPos.BOTTOM)
            # OR
            Player(PlayerTarget.DEFAULT).remove_inv_row(3, row_pos=PARowPos.BOTTOM)
            # removes the 3 bottom-most rows from the default player's currently open inventory.
        """
        args = Arguments([
            p_check(amount, Numeric, "amount") if amount is not None else None
        ], tags=[
            Tag(
                "Row to Remove", option=PARowPos(row_pos),  # default is Bottom Row
                action=PlayerActionType.REMOVE_INV_ROW, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.REMOVE_INV_ROW,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def remove_item(
        self, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Removes certain items from the player.

        Parameters
        ----------
        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]
            Item(s) to remove. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.Item` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.Item`] for a predetermined list of items.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            item_1 = Item(Material.STONE, name="My Item")
            item_2 = ItemVar("some item var")
            p_default.remove_item(item_1, item_2)
            # OR
            Player(PlayerTarget.DEFAULT).remove_item(item_1, item_2)
            # removes the first instance of the given items from the default player's inventory.
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list
        ])
        return PlayerAction(
            action=PlayerActionType.REMOVE_ITEM,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def replace_item(
        self,
        *from_items: typing.Optional[typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]],
        to_item: ItemParam, amount: typing.Optional[Numeric] = None,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Replaces the specified items with the given item in the player's inventory.

        Parameters
        ----------
        from_items : Optional[Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]], optional
            Item(s) to be replaced. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.Item` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.Item`] for a predetermined list of items.

        to_item : :attr:`~.ItemParam`
            Item to replace any of `from_items` with.

        amount : Optional[:attr:`~.Numeric`], optional
            Amount of `from_items` to replace, or ``None`` to replace all occurrences. Default is ``None`` (replace all).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::
            
            frist_item_1 = Item(Material.STONE, name="My Item")
            first_item_2 = ItemVar("some item var")
            p_default.replace_item(first_item_1, first_item_2, to_item=Item(Material.DIAMOND_SWORD), amount=5)
            # OR
            Player(PlayerTarget.DEFAULT).replace_item(first_item_1, first_item_2, to_item=Item(Material.DIAMOND_SWORD), amount=5)
            # replaces up to 5 of either `first_item_1` or `first_item_2` with a diamond sword within the default player's inventory.
        """
        item_list = flatten(*from_items, except_iterables=[str], max_depth=1)

        args = Arguments([
            *[p_check(obj, typing.Union[ItemParam, Listable], "from_items") for obj in item_list],
            p_check(to_item, ItemParam, "to_item"),
            p_check(amount, Numeric, "amount") if amount is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.REPLACE_ITEM,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def replace_bow_proj(
        self, projectile: typing.Optional[BlockParam] = None, *, name: typing.Optional[Textable] = None,
        particle: typing.Optional[ParticleParam] = None,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Replaces the projectile fired in the Shoot Bow Event.

        .. workswith:: Player Shoot Bow Event

        Parameters
        ----------
        projectile : Optional[Union[:class:`Material`, :attr:`~.ItemParam`, :attr:`~.Textable`]], optional
            The type of Projectile to launch instead of an arrow.

            The type can be specified either as:

            - an instance of :class:`~.Material` (the material of the block to set);
            - an item (:attr:`~.ItemParam` - the item representing the block to set);
            - text (:attr:`~.Textable` - the material of the block to set as text).

        name : Optional[:attr:`~.Textable`], optional
            Optionally, a projectile name, or ``None`` for no name. Default is ``None``.

        particle : Optional[:attr:`~.ParticleParam`], optional
            Optionally, a particle to be the launch trail of the projectile, or ``None`` for no launch trail.
            Default is ``None``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::
            
            new_proj = Material.SNOWBALL  # new projectile fired is a snowball
            partc = DFParticle(ParticleType.CLOUD)  # cloud particle trail
            p_default.replace_projectile(new_proj, name="Proj", particle=partc)
            # OR
            Player(PlayerTarget.DEFAULT).replace_projectile(new_proj, name="Proj", particle=partc)
            # default player's bow will now shoot this, if within a Shoot Bow Event.
        """
        args = Arguments([
            p_check(projectile, typing.Union[ItemParam, Textable], "projectile") if projectile is not None else None,
            p_check(name, Textable, "name") if name is not None else None,
            p_check(particle, ParticleParam, "particle") if particle is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.REPLACE_PROJ,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def respawn(self, *, target: typing.Optional[PlayerTarget] = None):
        """Automatically respawns the player if they are dead.

        .. rank:: Mythic


        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.respawn()
            # OR
            Player(PlayerTarget.DEFAULT).respawn()
        """
        return PlayerAction(
            action=PlayerActionType.RESPAWN,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def ride_entity(
        self, name: Textable,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Mounts the player on top of another player or entity.

        .. rank:: Noble


        Parameters
        ----------
        name : :attr:`~.Textable`
            The name of the player or entity to be ridden.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        Player names will be prioritized before mob names.


        Examples
        --------
        ::

            p_default.ride_entity("Some Entity")
            # OR
            Player(PlayerTarget.DEFAULT).ride_entity("Some Entity")  # The default player will now ride "Some Entity"
        """
        args = Arguments([
            p_check(name, Textable, "name")
        ])
        return PlayerAction(
            action=PlayerActionType.RIDE_ENTITY,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def remove_arrows(self, *, target: typing.Optional[PlayerTarget] = None):
        """Clears any arrows stuck in the player's body.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.remove_arrows()
            # OR
            Player(PlayerTarget.DEFAULT).remove_arrows()
        """
        return PlayerAction(
            action=PlayerActionType.RM_ARROWS,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def remove_world_border(self, *, target: typing.Optional[PlayerTarget] = None):
        """Removes the world border for this player.

        .. rank:: Emperor


        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.remove_world_border()
            # OR
            Player(PlayerTarget.DEFAULT).remove_world_border()
        """
        return PlayerAction(
            action=PlayerActionType.RM_WORLD_BORDER,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def random_teleport(
        self, *locs: typing.Union[Locatable, Listable],
        keep_current_rotation: bool = False,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Teleports the player to a random location from the list of ``locs``.

        .. rank:: Noble


        Parameters
        ----------
        locs : Union[:attr:`~.Locatable`, :attr:`~.Listable`]
            Locations to choose from.

        keep_current_rotation : :class:`bool`, optional
            If the player's current rotation should be kept after teleporting. Defaults to ``False`` (no).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        A different location will be picked for each targeted player, if multiple are selected.


        Examples
        --------
        ::
            
            loc_1 = DFLocation(1, 2, 3)
            loc_2 = LocationVar("some var")
            loc_3 = DFLocation(4, 5, 6)
            p_default.random_teleport(loc_1, loc_2, loc_3, keep_current_rotation=True)
            # OR
            Player(PlayerTarget.DEFAULT).random_teleport(loc_1, loc_2, loc_3, keep_current_rotation=True)
            # Teleports the default player to one of the given locations (chosen randomly), while keeping its rotation.
        """
        args = Arguments([
            p_check(loc, typing.Union[Locatable, Listable], f"locs[{i}]") for i, loc in enumerate(locs)
        ], tags=[
            Tag(
                "Keep Current Rotation", option=bool(keep_current_rotation),  # default is False
                action=PlayerActionType.RNG_TELEPORT, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.RNG_TELEPORT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def rollback_blocks(
        self, time: typing.Optional[Numeric] = None,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Undoes the interactions with blocks by the player.

        .. rank:: Overlord


        Parameters
        ----------
        time : Optional[:attr:`~.Numeric`], optional
            Rollback time in SECONDS (how far back in time block changes should be reverted), or ``None`` to revert
            all changes. Default is ``None``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Examples
        --------
        Revert all changes::

            p_default.rollback_blocks()
            # OR
            Player(PlayerTarget.DEFAULT).rollback_blocks()
            # rolls back all of the default player's block changes in the current plot.
        
        Revert up to some point back in time::

            p_default.rollback_blocks(120)
            # OR
            Player(PlayerTarget.DEFAULT).rollback_blocks(120)
            # rolls back the default player's block changes up to 120 seconds (2 min) ago.
        """
        args = Arguments([
            p_check(time, Numeric, "time") if time is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.ROLLBACK_BLOCKS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def save_inventory(self, *, target: typing.Optional[PlayerTarget] = None):
        """Saves the selected player's current inventory. It can be loaded later with 'Load Saved Inventory'.

        .. rank:: Noble


        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.save_inventory()
            # OR
            Player(PlayerTarget.DEFAULT).save_inventory()
        """
        return PlayerAction(
            action=PlayerActionType.SAVE_INV,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def send_advancement(
        self, text: Textable, icon: typing.Optional[ItemParam] = None,
        *, adv_type: AdvancementType = AdvancementType.ADVANCEMENT,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Sends an advancement popup to the player.

        .. rank:: Mythic


        Parameters
        ----------
        text : :attr:`~.Textable`
            The text within the advancement popup.

        icon : Optional[:attr:`~.ItemParam`], optional
            The popup icon, or ``None``  for no icon. Default is ``None``.

        adv_type : :class:`~.AdvancementType`, optional
            The type of advancement this is (either :attr:`~.AdvancementType.ADVANCEMENT`,
            :attr:`~.AdvancementType.GOAL` or :attr:`~.AdvancementType.CHALLENGE`).
            Defaults to :attr:`~.AdvancementType.ADVANCEMENT`.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.send_advancement("Found a Secret", Material.GRASS_BLOCK)
            # OR
            Player(PlayerTarget.DEFAULT).send_advancement("Found a Secret", Material.GRASS_BLOCK)
            # sends an advancement to the default player reading "Found a Secret", with a grass block as icon.
        """
        args = Arguments([
            p_check(text, Textable, "text"),
            p_check(icon, ItemParam, "icon") if item is not None else None
        ], tags=[
            Tag(
                "Toast Type", option=AdvancementType(adv_type),  # default is Advancement
                action=PlayerActionType.SEND_ADVANCEMENT, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.SEND_ADVANCEMENT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def send_animation(
        self, animation_type: PlayerAnimation,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Makes the player perform an animation.

        Parameters
        ----------
        animation_type : :class:`~.PlayerAnimation`
            The animation to be performed (see PlayerAnimation docs for options).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.send_animation(PlayerAnimation.SWING_RIGHT_ARM)
            # OR
            Player(PlayerTarget.DEFAULT).send_animation(PlayerAnimation.SWING_RIGHT_ARM)
            # forces the default player to swing its right arm.
        """
        args = Arguments([], tags=[
            Tag(
                "Animation Type", option=PlayerAnimation(animation_type),  # default is Swing Right Arm
                action=PlayerActionType.SEND_ANIMATION, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.SEND_ANIMATION,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def send_block(
        self, block_type: BlockParam, loc_1: Locatable, loc_2: typing.Optional[Locatable] = None,
        *metadata: typing.Optional[typing.Union[BlockMetadata, Listable]],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Makes client side, player specific blocks appear at the given location or area.

        .. rank:: Noble


        Parameters
        ----------
        block_type : Union[:class:`Material`, :attr:`~.ItemParam`, :attr:`~.Textable`]
            The type of Block to send.

            The type can be specified either as:

            - an instance of :class:`~.Material` (the material of the block to set);
            - an item (:attr:`~.ItemParam` - the item representing the block to set);
            - text (:attr:`~.Textable` - the material of the block to set as text).

        loc_1 : :attr:`~.Locatable`
            Location of the block, or, if `loc_2` is specified, then the first corner of the region.

        loc_2 : Optional[:attr:`~.Locatable`], optional
            Location 2 - the second corner of the region of blocks to send, or ``None`` for no region (send 1 block).
            Default is ``None``.

        metadata : Optional[Union[:class:`dict`, List[:attr:`~.Textable`], :attr:`~.Listable`]], optional
            Optionally, the metadata of the block to send (``None`` for none). If not ``None``, can be in two forms:

            1. **As a dictionary:** If this is specified, then:
                - The keys must be strings;
                - The values can be one of:
                    - :class:`str` (the written out option);
                    - :class:`int` (is converted into a string accordingly);
                    - :class:`bool` (is turned into "true"/"false" accordingly);
                    - ``None`` (is turned into "none");
                    - :class:`~.DFVariable` / :class:`~.TextVar` (are turned into "%var(name)" accordingly).
                    - Any other types not mentioned will simply be ``str()``\ ed.
                - Example::

                    {
                        "facing": "east",
                        "drag": True,
                        "west": None,
                        "rotation": 8,
                        "powered": DFVariable("my_var")
                    }

            2. **As a list/iterable:** If this is specified, then it must be a list of valid Textable parameters, whose values DF expects to be formatted in one of the following ways:
                - ``"tag=value"``
                - ``"tag:value"``
                - ``"tag,value"``

            3. **As a** :attr:`~.Listable`\ **:** One can also specify a variable representing a List (in DF) of text values in the format specified in `2`.

            .. note::
    
                Example: "rotation:9,waterlogged:true"

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        - Also known as 'ghost blocks'.
        - Can send up to 25 blocks per action.
        - Locations that are outside the plot can be used.


        Examples
        --------
        ::

            block_type = Material.GRASS_BLOCK  # send a ghost grass block
            loc_1 = DFLocation(1, 2, 3)  # first corner of region
            loc_2 = DFLocation(4, 5, 6)  # second corner of region

            p_default.send_block(block_type, loc_1, loc_2)
            # OR
            Player(PlayerTarget.DEFAULT).send_block(block_type, loc_1, loc_2)
            # sends ghost grass blocks to the default player over the specified region
        """
        true_metadata = _load_metadata(metadata, allow_none=True)
        args = Arguments([
            p_check(block_type, typing.Union[ItemParam, Textable], "block_type"),
            p_check(loc_1, Locatable, "loc_1"),
            p_check(loc_2, Locatable, "loc_2") if loc_2 is not None else None,
            *[p_check(meta, Textable, f"metadata[{i}]") for i, meta in enumerate(true_metadata)]
        ])
        return PlayerAction(
            action=PlayerActionType.SEND_BLOCK,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def send_dialogue(
        self, *texts: typing.Union[Textable, Listable], delay: typing.Optional[Numeric] = None,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Sends a series of messages in chat to the player, with a delay after each message.

        .. rank:: Noble


        Parameters
        ----------
        texts : Union[:attr:`~.Textable`, :attr:`~.Listable`]
            Messages to send, in order.

        delay : Optional[:attr:`~.Numeric`], optional
            Delay, in ticks, between each message, or ``None`` for the default (60 ticks = 3s). Default is ``None`` (3s).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.send_dialogue("Hello!", "Welcome!", delay=40)
            # OR
            Player(PlayerTarget.DEFAULT).send_dialogue("Hello!", "Welcome!", delay=40)
            # sends "Hello!" then, 40 ticks (2 seconds) after, "Welcome!" as messages to the default player.
        """
        args = Arguments([
            *[p_check(text, typing.Union[Textable, Listable], f"texts[{i}]") for i, text in enumerate(texts)],
            p_check(delay, Numeric, "delay") if delay is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.SEND_DIALOGUE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def send_hover(
        self, text: Textable, *, hover_text: Textable,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Sends a message to the player. When the player 'hovers' over it with their cursor, a second message appears.

        .. rank:: Mythic


        Parameters
        ----------
        text : :attr:`~.Textable`
            Message to send in chat.

        hover_text : :attr:`~.Textable`
            Message to see on hover.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.send_hover("Hover over me!"", hover_text="Hello!")
            # OR
            Player(PlayerTarget.DEFAULT).send_hover("Hover over me!", hover_text="Hello!")
            # sends the default player the message "Hover over me!" which, when hovered, displays "Hello!".
        """
        args = Arguments([
            p_check(text, Textable, "text"),
            p_check(hover_text, Textable, "hover_text")
        ])
        return PlayerAction(
            action=PlayerActionType.SEND_HOVER,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def send_message(
        self, *texts: typing.Optional[typing.Union[Textable, Listable]],
        centered: bool = False, add_spaces: bool = True,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Sends a chat message to the player.

        Parameters
        ----------
        texts : Union[:attr:`~.Textable`, :attr:`~.Listable`], optional
            Message to send (each text given is part of the total message, separated either by spaces,
            if add_spaces is ``True``, or simply added together, if it is ``False``), or a list var with all the text
            bits. Specify nothing to send an empty message.

            .. note::

                - Multiple text parts will be merged into one message.
                - Numbers and locations given will be converted to text.

        centered : :class:`bool`, optional
            Whether or not the message should be centered in the chat window. Defaults to ``False`` (not centered).

        add_spaces : :class:`bool`, optional
            If ``True``, the different text elements will be joined by a space between each. If ``False``, they will be
            simply added together. Defaults to ``False`` (No added spaces).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Examples
        --------
        ::

            p_default.send_message("a", "b", centered=True, add_spaces=True)
            # OR
            Player(PlayerTarget.DEFAULT).send_message("a", "b", centered=True, add_spaces=True)
            # sends message "a b" to the default player (centered and with a space between each text elements).
        """
        args = Arguments([
            p_check(text, typing.Union[Textable, Listable], f"texts[{i}]") for i, text in
            enumerate(texts)
        ], tags=[
            Tag(
                "Alignment Mode", option="Centered" if centered else "Regular",  # default is Regular
                action=PlayerActionType.SEND_MESSAGE, block=BlockType.PLAYER_ACTION
            ),
            Tag(
                "Text Value Merging", option="Add Spaces" if add_spaces else "No Spaces",  # default is No Spaces
                action=PlayerActionType.SEND_MESSAGE, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.SEND_MESSAGE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def send_title(
        self, title: Textable, subtitle: typing.Optional[Textable] = None,
        *, title_dur: typing.Optional[Numeric] = None,
        start_fade_dur: typing.Optional[Numeric] = None,
        end_fade_dur: typing.Optional[Numeric] = None,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Sends a title message to the player.

        .. rank:: Emperor


        Parameters
        ----------
        title : :attr:`~.Textable`
            Title text.

        subtitle : Optional[:attr:`~.Textable`], optional
            Subtitle text. Default is ``None``.

        title_dur : Optional[:attr:`~.Numeric`], optional
            Title duration (in ticks), or ``None`` for the default (60 ticks = 3s). Default is ``None`` (3s).

        start_fade_dur : Optional[:attr:`~.Numeric`], optional
            Start fade duration (in ticks), or ``None`` for the default (20 ticks = 1s). Default is ``None`` (1s).

        end_fade_dur : Optional[:attr:`~.Numeric`], optional
            End fade duration (in ticks), or ``None`` for the default (20 ticks = 1s). Default is ``None`` (1s).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            title = "Welcome to the plot!"
            subtitle = "Enjoy your stay!"
            p_default.send_title(title, subtitle, title_dur=40, start_fade_dur=10, end_fade_dur=10)
            # OR
            Player(PlayerTarget.DEFAULT).send_title(title, subtitle, title_dur=40, start_fade_dur=10, end_fade_dur=10)
            # displays the title "Welcome to the plot!" and subtitle "Enjoy your stay" to the default player for 2s,
            # with a fade in and fade out duration of 10 ticks = 0.5 s.
        """
        if title_dur is not None and (start_fade_dur is not None or end_fade_dur is not None):
            title_dur = DFNumber(60)

        if start_fade_dur is None and end_fade_dur is not None:
            start_fade_dur = DFNumber(20)

        args = Arguments([
            p_check(title, Textable, "title"),
            p_check(subtitle, Textable, "subtitle") if subtitle is not None else None,
            p_check(title_dur, Numeric, "title_dur") if title_dur is not None else None,
            p_check(start_fade_dur, Numeric, "start_fade_dur") if start_fade_dur is not None else None,
            p_check(end_fade_dur, Numeric, "end_fade_dur") if end_fade_dur is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.SEND_TITLE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_air_ticks(
        self, ticks: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the player's remaining breath ticks.

        Parameters
        ----------
        ticks : :attr:`~.Numeric`
            Remaining breath ticks (1 bubble = 30 air ticks).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        Each bubble is 30 air ticks.


        Examples
        --------
        ::

            p_default.set_air_ticks(40)
            # OR
            Player(PlayerTarget.DEFAULT).set_air_ticks(40)  # sets the default player's remaining breath ticks to 40 (2s).
        """
        args = Arguments([
            p_check(ticks, Numeric, "ticks")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_AIR_TICKS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_armor(
        self, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the armor of the player. Provide the armor in order as the first-fourth parameters, with the first being the helmet and the fourth being the boots.

        Parameters
        ----------
        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]
            Armor to set. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.Item` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.Item`] for a predetermined list of items.

            .. note::

                - The armor must be placed in order, with the first item being the helmet and the fourth, the boots.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        Any block or item can render on the player's head if placed in the 'helmet' slot.


        Examples
        --------
        ::

            helmet = Item(Material.DIAOND_HELMET, name="My Helmet")
            chestplate = ItemVar("some item var with a chestplate")
            p_default.set_armor(helmet, chestplate)
            # OR
            Player(PlayerTarget.DEFAULT).set_armor(helmet, chestplate)  # sets the default player's helmt and chestplate
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list
        ])
        return PlayerAction(
            action=PlayerActionType.SET_ARMOR,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_attack_speed(
        self, speed: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the player's attack speed.

        .. rank:: Mythic


        Parameters
        ----------
        speed : :attr:`~.Numeric`
            The player's new attack speed (number of times the player can attack per second).

            .. note:: The default attack speed is 4.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Examples
        --------
        ::

            p_default.set_attack_speed(10)
            # OR
            Player(PlayerTarget.DEFAULT).set_attack_speed(10)
            # increases the default player's attack speed to 10 attacks per second.
        """
        args = Arguments([
            p_check(speed, Numeric, "speed")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_ATK_SPEED,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_boss_bar(
        self, title: Textable, progress: typing.Optional[Numeric] = None, limit: typing.Optional[Numeric] = None,
        *, color: BossBarColor = BossBarColor.PINK, bar_style: BossBarStyle = BossBarStyle.SOLID,
        fog: bool = False, dark_sky: bool = False, bar_slot: _One_to_Four = 1,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the player's boss bar.

        .. rank:: Mythic


        Parameters
        ----------
        title : :attr:`~.Textable`
            The bossbar's title.

        progress : Optional[:attr:`~.Numeric`], optional
            Progress (i.e., how much of the boss bar is filled, from 0 to `limit`), or ``None`` for 0 (not filled).
            Defaults to ``None``.

        limit : Optional[:attr:`~.Numeric`], optional
            Progress limit (the max value `progress` can reach), or ``None`` for the default (100). Default is ``None``.

        color : :class:`~.BossBarColor`, optional
            The new boss bar's color (see BossBarColor docs for options). Defaults to :attr:`~.BossBarColor.PINK`.

        bar_style : :class:`~.BossBarStyle`, optional
            The new boss bar's style - either :attr:`~.BossBarStyle.SOLID` (just one continuous line) or split into
            several segments (with the amount of segments varying between 6, 10, 12 or 20).
            Defaults to :attr:`~.BossBarStyle.SOLID`.

        fog : :class:`bool`, optional
            Whether the target player's sky should receive a fog effect because of the boss bar. Defaults to ``False``.

        dark_sky : :class:`bool`, optional
            Whether the target player's sky should be darkened because of the boss bar. Defaults to ``False``.

        bar_slot : :class:`int`, optional
            Determines which bar slot should be modified (either 1, 2, 3 or 4) - note that any previous boss bar on
            the slot provided will be overridden by the new one. Defaults to slot 1.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Raises
        ------
        :exc:`ValueError`
            If the bossbar slot given is not one of 1, 2, 3, 4.

        Examples
        --------
        ::

            p_default.set_boss_bar("Boss", 50, color=BossBarColor.BLUE, dark_sky=True, bar_slot=2)
            # OR
            Player(PlayerTarget.DEFAULT).set_boss_bar("Boss", 50, color=BossBarColor.BLUE, dark_sky=True, bar_slot=2)
            # sets the player's boss bar slot #2 to one titled "Boss", at progress 50 (of 100), colored blue, while
            # darkening the sky.
        """
        if bar_slot is not None and bar_slot not in (1, 2, 3, 4):
            raise ValueError("'bar_slot' arg must either be None or one of 1, 2, 3, 4.")

        if limit is not None and progress is None:
            progress = 0

        args = Arguments([
            p_check(title, Textable, "title"),
            p_check(progress, Numeric, "progress") if progress is not None else None,
            p_check(limit, Numeric, "limit") if limit is not None else None
        ], tags=[
            Tag(
                "Bar Color", option=BossBarColor(color),  # default is Pink
                action=PlayerActionType.SET_BOSS_BAR, block=BlockType.PLAYER_ACTION
            ),
            Tag(
                "Bar Style", option=BossBarStyle(bar_style),  # default is Solid
                action=PlayerActionType.SET_BOSS_BAR, block=BlockType.PLAYER_ACTION
            ),
            Tag(
                "Sky Effect", option=(
                    "Fog and Dark Sky" if fog and dark_sky else (
                        "Fog" if fog else (
                            "Dark Sky" if dark_sky else "None"
                        )
                    )
                ),  # default is None
                action=PlayerActionType.SET_BOSS_BAR, block=BlockType.PLAYER_ACTION
            ),
            Tag(
                "Bar Slot", option=bar_slot,  # default is 1
                action=PlayerActionType.SET_BOSS_BAR, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.SET_BOSS_BAR,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_chat_tag(
        self, *chat_tag: typing.Union[Textable, Listable],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the chat tag for the player.

        .. rank:: Mythic


        Parameters
        ----------
        chat_tag : Union[:attr:`~.Textable`, :attr:`~.Listable`], optional
            New chat tag, or nothing to reset it.

            .. note::

                - Multiple text elements will be merged into one to form the chat tag.
                - Leave empty to reset the chat tag.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        - Multiple text items will be merged into one chat tag.
        - Leave empty to reset the chat tag.


        Examples
        --------
        Set the chat tag::

            p_default.set_chat_tag(Color.BLUE + "[tag]")
            # OR
            Player(PlayerTarget.DEFAULT).set_chat_tag(Color.BLUE + "[tag]")  # sets the default player's chat tag

        Reset the chat tag::

            p_default.set_chat_tag()
            # OR
            Player(PlayerTarget.DEFAULT).set_chat_tag()  # resets the default player's chat tag
        """
        args = Arguments([
            p_check(text, typing.Union[Textable, Listable], f"chat_tag[{i}]") for i, text in
            enumerate(chat_tag)
        ])
        return PlayerAction(
            action=PlayerActionType.SET_CHAT_TAG,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_compass_target(
        self, loc: Locatable,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the location compasses point to for the player.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            New compass target.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # where to point the compass.
            p_default.set_compass_target(loc)
            # OR
            Player(PlayerTarget.DEFAULT).set_compass_target(loc)  # now, the default player's compasses point to 'loc'
        """
        args = Arguments([
            p_check(loc, Locatable, "loc")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_COMPASS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_cursor_item(
        self, item: typing.Optional[ItemParam] = None,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the item on the player's cursor.

        Parameters
        ----------
        item : Optional[:attr:`~.ItemParam`], optional
            Item to set. Default is ``None`` (Clear cursor).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            item = Item(Material.DIAMOND_SWORD)  # e.g. a diamond sword
            p_default.set_cursor_item(item)
            # OR
            Player(PlayerTarget.DEFAULT).set_cursor_item(item)  # the default player's cursor item is now a Diamond Sword.
        """
        args = Arguments([
            p_check(item, ItemParam, "item") if item is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.SET_CURSOR_ITEM,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_fall_distance(
        self, distance: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the player's fall distance, affecting fall damage upon landing.

        Parameters
        ----------
        distance : :attr:`~.Numeric`
            Fall distance (in blocks).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.set_fall_distance(20)
            # OR
            Player(PlayerTarget.DEFAULT).set_fall_distance(20)  # sets the default player's fall distance to 20
        """
        args = Arguments([
            p_check(distance, Numeric, "distance")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_FALL_DISTANCE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_fire_ticks(
        self, duration: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the player on fire for a certain number of ticks.

        Parameters
        ----------
        duration : :attr:`~.Numeric`
            Duration of the fire (in ticks), or 0 to extinguish the player.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.set_fire_ticks(40)
            # OR
            Player(PlayerTarget.DEFAULT).set_fire_ticks(40)  # sets the default player on fire for 40 ticks (2 s).
        """
        args = Arguments([
            p_check(duration, Numeric, "duration")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_FIRE_TICKS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_food_level(
        self, level: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the player's food level.

        Parameters
        ----------
        level : :attr:`~.Numeric`
            New hunger level (1-20).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Raises
        ------
        :exc:`~.ValueError`
            If the food level given was a literal (i.e., not a variable) that is not between 1 and 20.

        Examples
        --------
        ::

            p_default.set_food_level(15)
            # OR
            Player(PlayerTarget.DEFAULT).set_food_level(15)  # sets the default player's food level to 15.
        """
        if isinstance(level, (int, float, DFNumber)) and not 1 <= float(level) <= 20:
            raise ValueError("'level' arg must be between 1 and 20.")

        args = Arguments([
            p_check(level, Numeric, "level")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_FOOD_LEVEL,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_hand_item(
        self, item: typing.Optional[ItemParam] = None,
        *, hand_slot: Hand = Hand.MAIN_HAND,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the item in the player's main hand or off hand.

        Parameters
        ----------
        item : Optional[:attr:`~.ItemParam`], optional
            Item to set. Default is ``None``.

        hand_slot : :class:`~.Hand`, optional
            Hand whose item should be set (either (:attr:`~.Hand.MAIN_HAND`) or (:attr:`~.Hand.OFF_HAND`)). Defaults to Main Hand
            (:attr:`~.Hand.MAIN_HAND`).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        Set the main hand::

            item = Item(Material.STONE, name="my item")  # some item
            p_default.set_hand_item(item)
            # OR
            Player(PlayerTarget.DEFAULT).set_hand_item(item)  # checks if the default player has that item at their main hand

        Set the off hand::

            item = Item(Material.STONE, name="my item")  # some item
            p_default.set_hand_item(item, hand_slot=Hand.OFF_HAND)
            # OR
            Player(PlayerTarget.DEFAULT).set_hand_item(item, hand_slot=Hand.OFF_HAND)
            # checks if the default player has that item at the off hand
        """
        args = Arguments([
            p_check(item, ItemParam, "item") if item is not None else None
        ], tags=[
            Tag(
                "Hand Slot", option=hand_slot,  # default is Main Hand
                action=PlayerActionType.SET_HAND_ITEM, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.SET_HAND_ITEM,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_health(
        self, health: Numeric,
        *, absorption: bool = False, combined: bool = False,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the player's health or absorption hearts.

        Parameters
        ----------
        health : :attr:`~.Numeric`
            The player's new health.

            .. note::

                1 health = 0.5 hearts

        absorption : :class:`bool`, optional
            If ``True``, the player's absorption health is set instead of regular health. Defaults to ``False`` (set
            regular health).

        combined : :class:`bool`, optional
            If ``True``, both the player's regular and absorption hearts are set. Defaults to ``False`` (just regular
            health).

            .. note::

                Specifying this overrides what was specified for `absorption`.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        Setting regular health::

            p_default.set_health(15)
            # OR
            Player(PlayerTarget.DEFAULT).set_health(15)  # sets the default player's health to 15 (7.5 hearts).

        Setting absorption health::

            p_default.set_health(15, absorption=True)
            # OR
            Player(PlayerTarget.DEFAULT).set_health(15, absorption=True)  # sets the default player's absorption
                                                                          # health to 15 (7.5 absorp. hearts).

        Setting combined health (regular and absorption health)::

            p_default.set_health(15, combined=True)
            # OR
            Player(PlayerTarget.DEFAULT).set_health(15, combined=True)  # sets the default player's combined to 15
                                                                        # (7.5 hearts in total).
        """
        args = Arguments([
            p_check(health, Numeric, "health")
        ], tags=[
            Tag(
                "Heal Type", option="Combined Health" if combined else (
                    "Absorption Health" if absorption else "Regular Health"
                ),  # default is Regular Health
                action=PlayerActionType.SET_HEALTH, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.SET_HEALTH,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_inv_name(
        self, name: Textable,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Renames the player's currently open plot inventory.

        .. rank:: Emperor


        Parameters
        ----------
        name : :attr:`~.Textable`
            The inventory's new name.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.set_inv_name("Some Inventory")
            # OR
            Player(PlayerTarget.DEFAULT).set_inv_name("Some Inventory")
            # renames the default player's currently open inventory to "Some Inventory"
        """
        args = Arguments([
            p_check(name, Textable, "name")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_INV_NAME,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_item_cooldown(
        self, item: ItemParam, cooldown: Numeric, sound: typing.Optional[SoundParam] = None,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Applies a cooldown visual effect to an item type.

        Parameters
        ----------
        item : :attr:`~.ItemParam`
            Item type to affect.

        cooldown : :attr:`~.Numeric`
            Cooldown in ticks.

        sound : Optional[:attr:`~.SoundParam`], optional
            Cooldown refresh sound, or ``None`` for no sound. Default is ``None``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        The cooldown applies to all items of the given type.


        Examples
        --------
        ::

            item = Material.DIAMOND_SWORD  # affects diamond swords
            sound = SoundVar("some variable with a sound")  # the refresh sound
            p_default.set_item_cooldown(item, 40, sound)
            # OR
            Player(PlayerTarget.DEFAULT).set_item_cooldown(item, 40, sound)
            # sets a 40 ticks-long (2s-long) cooldown on diamond swords for the default player , with the given sound
            # being played once the cooldown is done (optional).
        """
        args = Arguments([
            p_check(item, ItemParam, "item"),
            p_check(cooldown, Numeric, "cooldown"),
            p_check(sound, SoundParam, "sound") if sound is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.SET_ITEM_COOLDOWN,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_inv_items(
        self, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Changes the player's inventory according to the items in the list of parameters.

        Parameters
        ----------
        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]
            Item(s) to give, in their corresponding item slots. It is recommended to use an ItemCollection for this.
            The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a predetermined list of items.

            .. note::

                The top chest row (first 9 items) is the hotbar. The other rows fill the inventory from the top down.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            new_inv = ItemCollection([  # hotbar is the first row (first 9 items)
                None, None, Item(Material.STONE), None, None, Item(Material.COAL, name="item"), None, None, None,
                None, None, None,                 None, None, Item(Material.DIAMOND),           None, None, None
            ])  # example new inventory - all remaining slots are set to nothing (None)
            p_default.set_inv_items(new_inv)
            # OR
            Player(PlayerTarget.DEFAULT).set_inv_items(new_inv)  # sets the default player's inventory
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list
        ])
        return PlayerAction(
            action=PlayerActionType.SET_ITEMS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_list_header(
        self, *content: typing.Optional[typing.Union[Textable, Numeric, Locatable, Listable]],
        player_list_field="Header", footer: bool = False,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the player list header or footer for the player.

        .. rank:: Noble


        Parameters
        ----------
        content : Optional[Union[:attr:`~.Textable`, :attr:`~.Numeric`, :attr:`~.Locatable`, :attr:`~.Listable`]], optional
            New header / footer (multiple text parts are merged into one). Default is ``None``.

            .. note::

                Numbers and locations given will be converted to text.

        footer : :class:`bool`, optional
            If ``True``, the player list footer will be set. If ``False``, the header will be set instead.
            Defaults to ``False``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Examples
        --------
        Set the list header::

            p_default.set_list_header("You're playing my plot!")
            # OR
            Player(PlayerTarget.DEFAULT).set_list_header("You're playing my plot!")
            # sets the default player's player list header to "You're playing my plot!"

        Set the list footer::

            p_default.set_list_header("Thanks for joining!", footer=True)
            # OR
            Player(PlayerTarget.DEFAULT).set_list_header("Thanks for joining!", footer=True)
            # sets the default player's player list footer to "Thanks for joining!"
        """
        args = Arguments([
            p_check(text, typing.Union[Textable, Listable], f"content[{i}]") for i, text in
            enumerate(content)
        ], tags=[
            Tag(
                "Player List Field", option="Footer" if footer else "Header",  # default is Header
                action=PlayerActionType.SET_LIST_HEADER, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.SET_LIST_HEADER,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_max_health(
        self, health: Numeric,
        *, heal_fully: bool = False,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the maximum amount of health that the player can have.

        Parameters
        ----------
        health : :attr:`~.Numeric`
            New maximum health.

        heal_fully : :class:`bool`, optional
            If ``True``, the player is instantly healed to the new max health. Defaults to ``False`` (not healed).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.set_max_health(40, heal_fully=True)
            # OR
            Player(PlayerTarget.DEFAULT).set_max_health(40, heal_fully=True)
            # sets the player's new max health to 40 (20 hearts), while healing to that amount (40 hp) instantly.
        """
        args = Arguments([
            p_check(health, Numeric, "health")
        ], tags=[
            Tag(
                "Heal Player to Max Health", option=bool(heal_fully),  # default is False
                action=PlayerActionType.SET_MAX_HEALTH, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.SET_MAX_HEALTH,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_menu_item(
        self,
        *items: typing.Optional[typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]],
        slots: typing.Union[typing.Iterable[Numeric], Listable],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the specified slot in the player's currently open inventory menu to the specified item.

        .. rank:: Emperor


        Parameters
        ----------
        items : Optional[Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]], optional
            Item(s) to display. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.Item` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.Item`] for a predetermined list of items.

        slots : Union[:attr:`~.Numeric`, `Iterable[:attr:`~.Numeric`], :attr:`~.Listable`]
            Slot(s) to set (either a Numeric param - e.g. ``1`` -, an iterable of Numeric params
            - e.g. ``[1, 2, 3, 4]`` - or a Listable param containing them - e.g. ``ListVar("slots")``).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            item = Item(Material.DIAMOND_SWORD, name="my item")
            p_default.set_menu_item(item, slots=[1, 10, 15])
            # OR
            Player(PlayerTarget.DEFAULT).set_menu_item(item, slots=[1, 10, 15])
            # sets slots 1, 10, 15 to the given item on the default player's open inventory.
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)
        not_iterable = False
        if not isinstance(slots, typing.Iterable):
            not_iterable = True
            slots = [slots]

        args = Arguments([
            *[
                p_check(
                    slot, typing.Union[Numeric, Listable], "slots" if not_iterable else f"slots[{i}]"
                ) for i, slot in enumerate(slots)
            ],
            *[p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list]
        ])
        return PlayerAction(
            action=PlayerActionType.SET_MENU_ITEM,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_name_color(
        self, name_color: Textable,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the color of the player's name tag in chat.

        .. rank:: Noble


        Parameters
        ----------
        name_color : :attr:`~.Textable`
            Name color. (Usage of :class:`~.Color` class is recommended.)

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Notes
        -----
        Leave empty to reset the name color.


        Examples
        --------
        ::

            p_default.set_name_color(Color.BLUE)
            # OR
            Player(PlayerTarget.DEFAULT).set_name_color(Color.BLUE)  # sets the default player's nametag color to blue
        """
        args = Arguments([
            p_check(name_color, Textable, "name_color")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_NAME_COLOR,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_saturation(
        self, level: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the player's saturation level.

        Parameters
        ----------
        level : :attr:`~.Numeric`
            New saturation level (1-20).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Raises
        ------
        :exc:`~.ValueError`
            If the food level given was a literal (i.e., not a variable) that is not between 1 and 20.

        Examples
        --------
        ::

            p_default.set_saturation(15)
            # OR
            Player(PlayerTarget.DEFAULT).set_saturation(15)  # sets the default player's saturation level to 15
        """
        if isinstance(level, (int, float, DFNumber)) and not 1 <= float(level) <= 20:
            raise ValueError("'level' arg must be between 1 and 20.")

        args = Arguments([
            p_check(level, Numeric, "level")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_SATURATION,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_selected_slot(
        self, slot: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets a player's selected hotbar slot.

        Parameters
        ----------
        slot : :attr:`~.Numeric`
            New slot.

            .. note::

                Varies from 1 (left) to 9 (right)

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.


        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Raises
        ------
        :exc:`~.ValueError`
            If the slot given was a literal (i.e., not a variable) that is not between 1 and 9.

        Examples
        --------
        ::

            p_default.set_selected_slot(2)
            # OR
            Player(PlayerTarget.DEFAULT).set_selected_slot(2)
            # the default player's selected hotbar slot is now the 2nd (left-to-right)
        """
        if isinstance(slot, (int, float, DFNumber)) and not 1 <= float(slot) <= 9:
            raise ValueError("'slot' arg must be between 1 and 9.")

        args = Arguments([
            p_check(slot, Numeric, "slot")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_SLOT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_slot_item(
        self, item: typing.Optional[ItemParam], slot: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Like 'Give Items', but you can control which inventory slot the item goes in.

        Parameters
        ----------
        item : Optional[:attr:`~.ItemParam`], optional
            Item to set. Specify ``None`` for air.

        slot : :attr:`~.Numeric`
            Slot to set.

            .. note::

                Slots 1-9 = Hotbar Slots; 10-36 = Inventory (Top to bottom)

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            item = Item(Material.DIAMOND_SWORD, name="my cool sword")  # this will be the item set
            p_default.set_slot_item(item, 15)
            # OR
            Player(PlayerTarget.DEFAULT).set_slot_item(item, 15)  # sets the default player's slot 15 to the given item
        """
        args = Arguments([
            p_check(item, ItemParam, "item") if item is not None else None,
            p_check(slot, Numeric, "slot")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_SLOT_ITEM,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_time(
        self, ticks: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the time of day for the target player only.

        Parameters
        ----------
        ticks : :attr:`~.Numeric`
            Time of day (0 to 24000 ticks).

            .. note::

                - Morning: 1000 Ticks
                - Noon: 6000 Ticks
                - Afternoon: 7700 Ticks
                - Evening: 13000 Ticks
                - Midnight: 18000 Ticks

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Raises
        ------
        :exc:`~.ValueError`
            If the time given was a literal (i.e., not a variable) that is not between 0 and 24000.

        Examples
        --------
        ::

            p_default.set_time(13000)
            # OR
            Player(PlayerTarget.DEFAULT).set_time(13000)
            # sets the time of day to 13000 (evening) for the default player.
        """
        if isinstance(ticks, (int, float, DFNumber)) and not 0 <= float(ticks) <= 24000:
            raise ValueError("'ticks' arg must be between 0 and 24000.")

        args = Arguments([
            p_check(ticks, Numeric, "ticks")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_TIME,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_world_border(
        self, center: Locatable, radius: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Creates a world border visible to only the player.

        .. rank:: Emperor


        Parameters
        ----------
        center : :attr:`~.Locatable`
            Center position of the world border.

        radius : :attr:`~.Numeric`
            The border's radius from the center, in blocks.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            center = DFLocation(1, 2, 3)  # center of the border
            p_default.set_world_border(center, 5)
            # OR
            Player(PlayerTarget.DEFAULT).set_world_border(center, 5)
            # creates a world border of radius 5 blocks, centered at the given location, for the default player.
        """
        args = Arguments([
            p_check(center, Locatable, "center"),
            p_check(radius, Numeric, "radius")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_WORLD_BORDER,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_xp_level(
        self, level: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the player's experience level.

        Parameters
        ----------
        level : :attr:`~.Numeric`
            New experience level.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.set_xp_level(60)
            # OR
            Player(PlayerTarget.DEFAULT).set_xp_level(60)  # sets the default player's experience level to 60.
        """
        args = Arguments([
            p_check(level, Numeric, "level")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_XP_LVL,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_xp_progress(
        self, progress: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the XP progress bar to a certain percentage.

        Parameters
        ----------
        progress : :attr:`~.Numeric`
            Progress % (0-100).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.


        Raises
        ------
        :exc:`~.ValueError`
            If the XP Progress given was a literal (i.e., not a variable) that is not between 0 and 100.

        Examples
        --------
        ::

            p_default.set_xp_progress(50)
            # OR
            Player(PlayerTarget.DEFAULT).set_xp_progress(50)
            # sets the default player's experience progress to 50% (the bar is half-filled).
        """
        if isinstance(progress, (int, float, DFNumber)) and not 0 <= float(progress) <= 100:
            raise ValueError("'progress' arg must be between 0 and 100.")

        args = Arguments([
            p_check(progress, Numeric, "progress")
        ])
        return PlayerAction(
            action=PlayerActionType.SET_XPP_ROG,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def shift_world_border(
        self, *, radius: Numeric, speed: typing.Optional[Numeric] = None,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Changes the player's world border size, if they have one active.

        .. rank:: Emperor


        Parameters
        ----------
        radius : :attr:`~.Numeric`
            New radius.

        speed : Optional[:attr:`~.Numeric`], optional
            Speed of the border's resizing transformation, in blocks per second, or ``None`` for it to be instantaneous.
            Default is ``None``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.shift_world_border(radius=5, speed=10)
            # OR
            Player(PlayerTarget.DEFAULT).shift_world_border(radius=55, speed=10)
            # resizes the default player's world border to have a radius of 55 blocks, at a shift rate of 10 blocks/s.
        """
        args = Arguments([
            p_check(radius, Numeric, "radius"),
            p_check(speed, Numeric, "speed") if speed is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.SHIFT_WORLD_BORDER,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def show_disguise(self, *, target: typing.Optional[PlayerTarget] = None):
        """Shows the player's disguise on their screen.

        .. rank:: Overlord


        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.show_disguise()
            # OR
            Player(PlayerTarget.DEFAULT).show_disguise()
        """
        return PlayerAction(
            action=PlayerActionType.SHOW_DISGUISE,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def show_inventory(
        self,
        *items: typing.Optional[typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Opens a custom item inventory for the player.

        .. rank:: Emperor


        Parameters
        ----------
        items : Optional[Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]], optional
            Items to display in the inventory. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.Item` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.Item`] for a predetermined list of items.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            items = ItemCollection([
                None, None, Item(Material.STONE), None, None, Item(Material.COAL, name="item"), None, None, None,
                None, None, None,                 None, None, Item(Material.DIAMOND),           None, None, None
            ])  # example new inventory

            p_default.show_inventory(items)
            # OR
            Player(PlayerTarget.DEFAULT).show_inventory(items)
            # shows a custom inventory to the default player with the given items
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list
        ])
        return PlayerAction(
            action=PlayerActionType.SHOW_INV,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def stop_sound(
        self, *sounds: typing.Optional[typing.Union[SoundParam, Listable]],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Stops all, or specific sound effects for the player.

        Parameters
        ----------
        sounds : Optional[Union[:attr:`~.SoundParam`, :attr:`~.Listable`]], optional
            Sounds to stop. Default is ``None``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            sound_1 = SoundVar("some sound")
            sound_2 = SoundVar("some other sound")
            p_default.stop_sound(sound_1, sound_2)
            # OR
            Player(PlayerTarget.DEFAULT).stop_sound(sound_1, sound_2)
            # stops playing the given sounds for the default player
        """
        args = Arguments([
            p_check(sound, typing.Union[SoundParam, Listable], f"sounds[{i}]") for i, sound in
            enumerate(sounds)
        ])
        return PlayerAction(
            action=PlayerActionType.STOP_SOUND,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def teleport(
        self, loc: Locatable,
        *, keep_current_rotation: bool = False,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Teleports the player to a location.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            New position (location to which the player is teleported).

        keep_current_rotation : :class:`bool`, optional
            If the player's current rotation should be kept after teleporting. Defaults to ``False``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # where to teleport the player
            p_default.teleport(loc, keep_current_rotation=True)
            # OR
            Player(PlayerTarget.DEFAULT).teleport(loc, keep_current_rotation=True)
            # teleports the default player to the given location, while maintaing their current rotation
        """
        args = Arguments([
            p_check(loc, Locatable, "loc")
        ], tags=[
            Tag(
                "Keep Current Rotation", option=bool(keep_current_rotation),  # default is False
                action=PlayerActionType.TELEPORT, block=BlockType.PLAYER_ACTION
            )
        ])
        return PlayerAction(
            action=PlayerActionType.TELEPORT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def tp_sequence(
        self, *locs: typing.Union[Locatable, Listable], delay: typing.Optional[Numeric] = None,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Teleports the player to multiple locations, with a delay between each teleport.

        .. rank:: Noble


        Parameters
        ----------
        locs : Union[:attr:`~.Locatable`, :attr:`~.Listable`]
            Locations to teleport to (in order of teleportation - the leftmost given location is the first, while
            the rightmost is the last).

        delay : Optional[:attr:`~.Numeric`], optional
            Delay between each teleportation, in ticks, or ``None`` for the default (60 ticks = 3s).
            Default is ``None``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            loc_1 = DFLocation(1, 2, 3)
            loc_2 = LocationVar("some var")
            loc_3 = DFLocation(4, 5, 6)  # sample locations
            p_default.tp_sequence(loc_1, loc_2, loc_3, delay=40)
            # OR
            Player(PlayerTarget.DEFAULT).tp_sequence(loc_1, loc_2, loc_3, delay=40)
            # teleports the player to loc_1 then loc_2 then loc_3, with a delay of 40 ticks (2 s) between each.
        """
        args = Arguments([
            *[p_check(loc, typing.Union[Locatable, Listable], f"locs[{i}]") for i, loc in enumerate(locs)],
            p_check(delay, Numeric, "delay") if delay is not None else None
        ])
        return PlayerAction(
            action=PlayerActionType.TP_SEQUENCE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def undisguise(self, *, target: typing.Optional[PlayerTarget] = None):
        """Removes the player's disguise.

        .. rank:: Overlord


        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.undisguise()
            # OR
            Player(PlayerTarget.DEFAULT).undisguise()
        """
        return PlayerAction(
            action=PlayerActionType.UNDISGUISE,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_walk_speed(
        self, speed: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Sets the player's walk speed.

        .. rank:: Noble


        Parameters
        ----------
        speed : :attr:`~.Numeric`
            % of normal walk speed (0 to 500).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.set_walk_speed(400)
            # OR
            Player(PlayerTarget.DEFAULT).set_walk_speed(400)  # sets the default player's walk speed to 400% (4x faster).
        """
        args = Arguments([
            p_check(speed, Numeric, "speed")
        ])
        return PlayerAction(
            action=PlayerActionType.WALK_SPEED,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_clear_weather(self, *, target: typing.Optional[PlayerTarget] = None):
        """Sets the weather to clear weather for the player only.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.set_clear_weather()
            # OR
            Player(PlayerTarget.DEFAULT).set_clear_weather()
        """
        return PlayerAction(
            action=PlayerActionType.WEATHER_CLEAR,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_rain_weather(self, *, target: typing.Optional[PlayerTarget] = None):
        """Sets the weather to downfall (rain) for the player only.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.PlayerAction`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`PlayerAction`
            The generated PlayerAction instance.

        Examples
        --------
        ::

            p_default.set_rain_weather()
            # OR
            Player(PlayerTarget.DEFAULT).set_rain_weather()
        """
        return PlayerAction(
            action=PlayerActionType.WEATHER_RAIN,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    # endregion:playeractions

    # region:ifplayer

    def is_looking_at(
        self, *block_types_or_locs: typing.Union[BlockParam, Locatable, Listable],
        distance: typing.Optional[Numeric] = None,
        ignore_fluids: bool = True,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if a player is looking at a certain block type or at a certain location.

        Parameters
        ----------
        block_types_or_locs : Union[:class:`Material`, :attr:`~.ItemParam`, :attr:`~.Textable`, :attr:`~.Locatable`, \
:attr:`~.Listable`]
            The type of Block(s) to check for, or the location(s) to check (if the player is looking at them).

            Note that a :attr:`~.Listable` can also be given (i.e., the List of all block types/items/locations).

            The block types can be specified either as:

            - an instance of :class:`~.Material` (the material of the block to set);
            - an item (:attr:`~.ItemParam` - the item representing the block to set);
            - text (:attr:`~.Textable` - the material of the block to set as text);
            - a :attr:`~.Listable` (A List - in DF - variable containing either Item or Text parameters).

        distance : Optional[:attr:`~.Numeric`], optional
            Maximum distance from target block to consider. Default is ``None``.

        ignore_fluids : :class:`bool`, optional
            If ``True``, fluids are ignored when checking at which block the player is looking. If ``False``,
            they are considered. Defaults to ``True``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Warnings
        --------
        Any :class:`~.DFVariable` instances are assumed to refer to block type. In order to specify that it refers
        to the location the entity should be standing on, use :class:`~.LocationVar`.

        Examples
        --------
        ::

            gold_block = Material.GOLD_BLOCK  # either looking at a gold block...
            loc = DFLocation(1, 2, 3)         # ...or at the given location
            with p_default.is_looking_at(gold_block, loc, distance=10):  # at most 10 blocks away
            # OR
            with Player(PlayerTarget.DEFAULT).is_looking_at(gold_block, loc, distance=10):
                # ... code to be executed if the Default Player is looking at either a gold block or at the given \
location, at most 10 blocks away ...
        """
        loaded_btypes = _load_btypes(block_types_or_locs)
        true_btypes = list(
            filter(
                lambda t: p_bool_check(t, typing.Union[ItemParam, Textable, Listable]),
                loaded_btypes
            )
        )
        locs = filter(
            lambda t: p_bool_check(t, Locatable) and t not in true_btypes, block_types_or_locs
        )
        _ = [
            p_check(el, typing.Union[ItemParam, Textable, Locatable, Listable], f"block_types_or_locs[{i}]")
            for i, el in enumerate(loaded_btypes)
        ]
        # error on unknown type

        args = Arguments([
            *true_btypes,
            *locs,
            p_check(distance, Numeric, "distance") if distance is not None else None
        ], tags=[
            Tag(
                "Fluid Mode", option="Ignore Fluids" if ignore_fluids else "Detect Fluids",  # default is Ignore Fluids
                action=IfPlayerType.IS_LOOKING_AT, block=BlockType.IF_PLAYER
            )
        ])
        return IfPlayer(
            action=IfPlayerType.IS_LOOKING_AT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def in_world_border(
        self, loc: typing.Optional[Locatable] = None,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if the player (or a location) is within their world border.

        .. rank:: Emperor


        Parameters
        ----------
        loc : Optional[:attr:`~.Locatable`], optional
            Location to check if is within the player's world border. Default is ``None`` (check the player itself).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            with p_default.in_world_border():
            # OR
            with Player(PlayerTarget.DEFAULT).in_world_border():
                # ... code to be executed if the Default Player is in the world border ...

            # or specify a location to check if that location is within the player's world border.
        """
        args = Arguments([
            p_check(loc, Locatable, "loc") if loc is not None else None
        ])
        return IfPlayer(
            action=IfPlayerType.IN_WORLD_BORDER,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def has_room_for_item(
        self, item: typing.Optional[ItemParam] = None,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if a player's inventory has enough room for an item to be given.

        Parameters
        ----------
        item : Optional[:attr:`~.ItemParam`], optional
            Item (stack) to check. Default is ``None`` (has room for any item).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            item = 32 * Item(Material.STONE)
            with p_default.has_room_for_item(item):
            # OR
            with Player(PlayerTarget.DEFAULT).has_room_for_item(item):
                # ... code to be executed if the Default Player has room for 32 stones ...
        """
        args = Arguments([
            p_check(item, ItemParam, "item") if item is not None else None
        ])
        return IfPlayer(
            action=IfPlayerType.HAS_ROOM_FOR_ITEM,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def no_item_cooldown(
        self, item: ItemParam,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if the player does not have a cooldown applied to an item type (material).

        Parameters
        ----------
        item : :attr:`~.ItemParam`
            Item type to check. (Note that only the Material determines the cooldown.)

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            d_sword = Material.DIAMOND_SWORD
            with p_default.no_item_cooldown(d_sword):
            # OR
            with Player(PlayerTarget.DEFAULT).no_item_cooldown(d_sword):
                # ... code to be executed if the Default Player doesn't have a cooldown on diamond swords ...
        """
        args = Arguments([
            p_check(item, ItemParam, "item")
        ])
        return IfPlayer(
            action=IfPlayerType.NO_ITEM_COOLDOWN,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def has_all_items(
        self, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if a player has all of the given items.

        Parameters
        ----------
        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], \
:attr:`Listable`]]
            Item(s) to check for. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a predetermined list of items.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            item_1 = Item(Material.STONE)          # must have both a Stone (with no other properties)...
            item_2 = Item(Material.DIAMOND_SWORD)  # ...and a diamond sword (with no other properties).
            with p_default.has_all_items(item_1, item_2):
            # OR
            with Player(PlayerTarget.DEFAULT).has_all_items(item_1, item_2):
                # ... code to be executed if the Default Player has both item 1 and item 2 ...
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(item, ItemParam, "items") for item in item_list
        ])
        return IfPlayer(
            action=IfPlayerType.HAS_ALL_ITEMS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def is_swimming(self, *, target: typing.Optional[PlayerTarget] = None):
        """Checks if a player is in water or lava.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Notes
        -----
        Use 'Is Sprinting' to check if a player is swimming with the swimming animation.

        Examples
        --------
        ::

            with p_default.is_swimming():
            # OR
            with Player(PlayerTarget.DEFAULT).is_swimming():
                # ... code to be executed if the Default Player is swimming ...
        """
        return IfPlayer(
            action=IfPlayerType.IS_SWIMMING,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def has_item(
        self, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if a player has an item/any of some given items in their inventory.

        Parameters
        ----------
        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], \
:attr:`Listable`]]
            Item(s) to check for (must have at least one). The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a predetermined list of items.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            item_1 = Item(Material.STONE)          # must have either a Stone (with no other properties)...
            item_2 = Item(Material.DIAMOND_SWORD)  # ...or a diamond sword (with no other properties).
            with p_default.has_item(item_1, item_2):
            # OR
            with Player(PlayerTarget.DEFAULT).has_item(item_1, item_2):
                # ... code to be executed if the Default Player has at least one of the given items.
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(item, ItemParam, "items") for item in item_list
        ])
        return IfPlayer(
            action=IfPlayerType.HAS_ITEM,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    has_any_item = has_item
    """Alias of :meth:`has_item`"""

    # def block_equals(  # already in IfGame
    #     self, *block_types: typing.Union[BlockParam, Listable],
    #     target: typing.Optional[PlayerTarget] = None
    # ):
    #     """Checks if the block in a block interaction event is a certain block, or one of certain blocks.
    #
    #     .. rank:: Emperor
    #
    #     .. workswith:: Player Place Block Event, Player Break Block Event
    #
    #     Parameters
    #     ----------
    #     block_types : Union[:class:`Material`, :attr:`~.ItemParam`, :attr:`~.Textable`, :attr:`~.Listable`]
    #         The type of Block(s) to check for.
    #
    #         The type can be specified either as:
    #
    #         - an instance of :class:`~.Material` (the material of the block to set);
    #         - an item (:attr:`~.ItemParam` - the item representing the block to set);
    #         - text (:attr:`~.Textable` - the material of the block to set as text);
    #         - a :attr:`~.Listable` (A List - in DF - variable containing either Item or Text parameters).
    #
    #         .. note::
    #
    #             If multiple items are given, then the block can be any of them.
    #
    #     target : Optional[:class:`~.PlayerTarget`], optional
    #         The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
    #         Defaults to ``None``.
    #
    #     Returns
    #     -------
    #     :class:`~.IfPlayer`
    #         The generated IfPlayer instance.
    #
    #     Examples
    #     --------
    #     ::
    #
    #         gold_block =
    #         with p_default.block_equals(block_types):
    #         # OR
    #         with Player(PlayerTarget.DEFAULT).block_equals(block_types):
    #             # ... code to be executed if the Default Player # TODO: Example
    #     """
    #     true_btypes = _load_btypes(block_types)
    #
    #     args = Arguments([
    #         p_check(block_type, typing.Union[ItemParam, Textable], f"block_types[{i}]") for i, block_type in
    #         enumerate(true_btypes)
    #     ])
    #     return IfPlayer(
    #         action=IfPlayerType.BLOCK_EQUALS,
    #         args=args,
    #         target=self._digest_target(target),
    #         append_to_reader=False,
    #         invert=False
    #     )

    def is_wearing(
        self, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable],
        wearing_all: bool = False,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if a player is wearing an item in their armour slots.

        Parameters
        ----------
        items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]
            Item(s) to check for. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a predetermined list of items.

        wearing_all : :class:`bool`, optional
            If ``True``, the player must be wearing all given items. If ``False``, the player must be wearing
            at least one of them. Defaults to ``False``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            dia_helm = Item(Material.DIAMOND_HELMET, name="T")     # must be wearing either a diamond helmet named "T",
            iron_chest = Item(Material.IRON_CHESTPLATE, name="E")  # or an iron chestplate named "E".
            with p_default.is_wearing(dia_helm, iron_chest, wearing_all=False):
            # OR
            with Player(PlayerTarget.DEFAULT).is_wearing(dia_helm, iron_chest, wearing_all=False):
                # ... code to be executed if the Default Player wears at least one of the given items ...
                # (set 'wearing_all' to True to require it to be wearing all given items simultaneously)
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(item, ItemParam, "items") for item in item_list
        ], tags=[
            Tag(
                "Check Mode", option="Is Wearing All" if wearing_all else "Is Wearing Some",  # default: Is Wearing Some
                action=IfPlayerType.IS_WEARING, block=BlockType.IF_PLAYER
            )
        ])
        return IfPlayer(
            action=IfPlayerType.IS_WEARING,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def is_near(
        self, *locs: typing.Union[Locatable, Listable], distance: typing.Optional[Numeric] = None,
        ignore_y_axis: bool = False,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if a player is within a certain range of a location. (default: 5 blocks)

        Parameters
        ----------
        locs : Union[:attr:`~.Locatable`, :attr:`~.Listable`]
            Center location(s) - must be near to at least one of them by the given distance amount.
            (A variable representing a list of locations can also be specified.)

        distance : Optional[:attr:`~.Numeric`], optional
            Maximum distance allowed from at least one of the locations, or ``None`` for the default (5 blocks).
            Default is ``None``.

        ignore_y_axis : :class:`bool`, optional
            If the Y-axis should be ignored when calculating distances (i.e., only X and Z should be considered).
            Defaults to ``False``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            loc_1 = DFLocation(1, 2, 3)
            loc_2 = LocationVar("my var")
            with p_default.is_near(loc_1, loc_2, range=10):
            # OR
            with Player(PlayerTarget.DEFAULT).is_near(loc_1, loc_2, range=10):
                # ... code to be executed if the Default Player is at most 10 blocks away from at least one of the \
given locations ...
        """
        args = Arguments([
            *[p_check(loc, typing.Union[Locatable, Listable], f"locs[{i}]") for i, loc in enumerate(locs)],
            p_check(distance, Numeric, "distance") if distance is not None else None
        ], tags=[
            Tag(
                "Ignore Y-Axis", option=bool(ignore_y_axis),  # default is False
                action=IfPlayerType.IS_NEAR, block=BlockType.IF_PLAYER
            )
        ])
        return IfPlayer(
            action=IfPlayerType.IS_NEAR,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def standing_on(
        self, *block_types_or_locs: typing.Union[BlockParam, Locatable, Listable],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if a player is standing on a block of a certain type or at a certain location.

        Parameters
        ----------
        block_types_or_locs : Union[:class:`Material`, :attr:`~.ItemParam`, :attr:`~.Textable`, :attr:`~.Locatable`, :attr:`~.Listable`]
            The type of Block(s) to check for, or the location(s) to check (if the player is standing on at least
            one of them).

            Note that a :attr:`~.Listable` can also be given (i.e., the List of all block types/items/locations).

            The block types can be specified either as:

            - an instance of :class:`~.Material` (the material of the block to set);
            - an item (:attr:`~.ItemParam` - the item representing the block to set);
            - text (:attr:`~.Textable` - the material of the block to set as text);
            - a :attr:`~.Listable` (A List - in DF - variable containing either Item or Text parameters).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            gold_block = Material.GOLD_BLOCK  # must either be standing on a gold block,
            loc = DFLocation(1, 2, 3)         # or on the given location.
            with p_default.standing_on(gold_block, loc):
            # OR
            with Player(PlayerTarget.DEFAULT).standing_on(gold_block, loc):
                # ... code to be executed if the Default Player is standing either on a gold block or on the given \
location ...
        """
        loaded_btypes = _load_btypes(block_types_or_locs)
        true_btypes = list(
            filter(
                lambda t: p_bool_check(t, typing.Union[ItemParam, Textable, Listable]),
                loaded_btypes
            )
        )
        locs = filter(
            lambda t: t not in true_btypes and p_bool_check(t, Locatable), block_types_or_locs
        )
        _ = [
            p_check(el, typing.Union[ItemParam, Textable, Locatable, Listable], f"block_types_or_locs[{i}]")
            for i, el in enumerate(loaded_btypes)
        ]
        # error on unknown type

        args = Arguments([
            *true_btypes,
            *locs
        ])
        return IfPlayer(
            action=IfPlayerType.STANDING_ON,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

#     def cmd_equals(
#         self, *texts: typing.Union[Textable, Listable],
#         check_mode="Check Entire Command", ignore_case: bool = True,
#         target: typing.Optional[PlayerTarget] = None
# ):
    #     """Checks if a player's command is equal to a certain text when the Player Command Event is executed.
    #
    #     .. rank:: Emperor
    #
    #     .. workswith:: Player Command Event
    #
    #     Parameters
    #     ----------
    #     texts : Union[:attr:`~.Textable`, :attr:`~.Listable`]
    #         Text(s) to check for.
    #
    #     check_mode :
    #         Check Entire Command, Check First Word
    #
    #     ignore_case : :class:`bool`, optional
    #         Defaults to ``True``.
    #
    #     target : Optional[:class:`~.PlayerTarget`], optional
    #         The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
    #         Defaults to ``None``.
    #
    #     Returns
    #     -------
    #     :class:`~.IfPlayer`
    #         The generated IfPlayer instance.
    #
    #     Examples
    #     --------
    #     ::
    #
    #         with p_default.cmd_equals(texts):
    #         # OR
    #         with Player(PlayerTarget.DEFAULT).cmd_equals(texts):
    #             # ... code to be executed if the Default Player # TODO: Example
    #     """
    #     args = Arguments([
    #         p_check(text, typing.Union[Textable, Listable], f"texts[{i}]") for i, text in enumerate(texts)
    #     ], tags=[
    #         Tag(
    #             "Check Mode", option=check_mode,  # default is Check Entire Command
    #             action=IfPlayerType.CMD_EQUALS, block=BlockType.IF_PLAYER
    #         ),
    #         Tag(
    #             "Ignore Case", option=bool(ignore_case),  # default is True
    #             action=IfPlayerType.CMD_EQUALS, block=BlockType.IF_PLAYER
    #         )
    #     ])
    #     return IfPlayer(
    #         action=IfPlayerType.CMD_EQUALS,
    #         args=args,
    #         target=self._digest_target(target),
    #         append_to_reader=False,
    #         invert=False
    #     )

    def has_effect(
        self, *potions: typing.Union[Potionable, Listable],
        has_all_effects: bool = False,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if a player has a potion effect.

        Parameters
        ----------
        potions : Union[:attr:`~.Potionable`, :attr:`~.Listable`]
            Potion(s) to check for, or a list variable containing them.

        has_all_effects : :class:`bool`, optional
            If the player must have all potion effects specified, instead of just one of them. Defaults to
            ``False``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Notes
        -----
        Amplifiers and durations do not have to be the same as the initial potion effect(s).


        Examples
        --------
        ::

            potion_1 = DFPotion(PotionType.ABSORPTION)
            potion_2 = DFPotion(PotionType.POISON)
            with p_default.has_effect(potion_1, potion_2, has_all_effects=False):
            # OR
            with Player(PlayerTarget.DEFAULT).has_effect(potion_1, potion_2, has_all_effects=False):
                # ... code to be executed if the Default Player has either Absorption or Poison ...
                # (specify has_all_effects=True to check if the player has all of them simultaneously)
        """
        args = Arguments([
            p_check(potion, typing.Union[Potionable, Listable], f"potions[{i}]") for i, potion in enumerate(potions)
        ], tags=[
            Tag(
                "Check Mode", option="Has All Effects" if has_all_effects else "Has Any Effect",  # d: Has Any Effect
                action=IfPlayerType.HAS_EFFECT, block=BlockType.IF_PLAYER
            )
        ])
        return IfPlayer(
            action=IfPlayerType.HAS_EFFECT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def is_grounded(self, *, target: typing.Optional[PlayerTarget] = None):
        """Checks if a player is supported by a block.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            with p_default.is_grounded():
            # OR
            with Player(PlayerTarget.DEFAULT).is_grounded():
                # ... code to be executed if the Default Player is supported by a block (on the 'ground') ...
        """
        return IfPlayer(
            action=IfPlayerType.IS_GROUNDED,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

#         def item_equals(
#         self, *items: typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable],
#         target: typing.Optional[PlayerTarget] = None
#     ):
    #         """Checks if the items in one of the events below is a certain item.
    #
    #         .. workswith::
    #
    #             Player Click Item Events, Player Pickup Item Event, Player Drop Item Event, Player Consume Item Event
    #
    #         Parameters
    #         ----------
    #         items : Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], \
    # :attr:`Listable`]]
    #             Item(s) to check for (must match one of them). The items can be specified either as:
    #
    #             - ``None`` for an empty slot;
    #             - :class:`~.ItemParam` for one item;
    #             - :attr:`~.Listable` for a variable list of items;
    #             - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a predetermined list of items.
    #
    #             .. note::
    #
    #                 If multiple items given, the event item can be any of them.
    #
    #         target : Optional[:class:`~.PlayerTarget`], optional
    #             The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
    #             Defaults to ``None``.
    #
    #         Returns
    #         -------
    #         :class:`~.IfPlayer`
    #             The generated IfPlayer instance.
    #
    #         Examples
    #         --------
    #         ::
    #
    #             with p_default.item_equals(items):
    #             # OR
    #             with Player(PlayerTarget.DEFAULT).item_equals(items):
    #                 # ... code to be executed if the Default Player # TODO: Example
    #         """
    #         item_list = flatten(*items, except_iterables=[str], max_depth=1)
    #
    #         args = Arguments([
    #             p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list
    #         ])
    #         return IfPlayer(
    #             action=IfPlayerType.ITEM_EQUALS,
    #             args=args,
    #             target=self._digest_target(target),
    #             append_to_reader=False,
    #             invert=False
    #         )

    def cursor_item_equals(
        self,
        *items: typing.Optional[typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if the item that is being moved with a player's cursor is a certain item.

        Parameters
        ----------
        items : Optional[Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]], optional
            Items(s) to check for. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a predetermined list of items.

            .. note::

                If multiple items are given, the player can have any of them on their cursor.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Warnings
        -----
        When used on the Player Click Item in Own Inventory Event, 'Cursor Item Equals' checks the previous cursor item, not the item that was clicked.


        Examples
        --------
        ::

            item_1 = Item(Material.STONE, name="my stone")
            item_2 = Item(Material.GOLD_BLOCK, lore=["e"])
            with p_default.cursor_item_equals(item_1, item_2):
            # OR
            with Player(PlayerTarget.DEFAULT).cursor_item_equals(item_1, item_2):
                # ... code to be executed if the Default Player has either of the given items on its cursor ...
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list
        ])
        return IfPlayer(
            action=IfPlayerType.CURSOR_ITEM,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def hotbar_is(
        self, slot: Numeric,
        *, target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if the player's currently selected hotbar slot corresponds with a slot ID between 1 and 9.

        Parameters
        ----------
        slot : :attr:`~.Numeric`
            Slot ID to check.

            .. note::

                - 1 = Leftmost slot
                - 9 = Rightmost slot

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            with p_default.hotbar_slot_is(5):
            # OR
            with Player(PlayerTarget.DEFAULT).hotbar_slot_is(5):
                # ... code to be executed if the Default Player's currently selected slot is the 5th slot ...
        """
        args = Arguments([
            p_check(slot, Numeric, "slot")
        ])
        return IfPlayer(
            action=IfPlayerType.SLOT_EQUALS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    # def is_holding_main(self, *, target: typing.Optional[PlayerTarget] = None):
    #     """
    #
    #     Parameters
    #     ----------
    #     target : Optional[:class:`~.PlayerTarget`], optional
    #         The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
    #         Defaults to ``None``.
    #
    #     Returns
    #     -------
    #     :class:`~.IfPlayer`
    #         The generated IfPlayer instance.
    #
    #     Examples
    #     --------
    #     ::
    #
    #         with p_default.is_holding_main():
    #         # OR
    #         with Player(PlayerTarget.DEFAULT).is_holding_main():
    #             # ... code to be executed if the Default Player # TODO: desc.
    #     """
    #     return IfPlayer(
    #         action=IfPlayerType.IS_HOLDING_MAIN,
    #         args=Arguments(),
    #         target=self._digest_target(target),
    #         append_to_reader=False,
    #         invert=False
    #     )

    def is_holding(
        self,
        *items: typing.Optional[typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]],
        hand: typing.Optional[Hand] = None,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if a player is holding an item in their hand.

        Parameters
        ----------
        items : Optional[Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]], optional
            Item(s) to check for. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a predetermined list of items.

        hand : Optional[:class:`PlayerHand`]
            The specific hand whose item should be compared against the given items, or ``None`` to compare both hands
            (i.e., accept the player having the item on either hand). Defaults to ``None``.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            item_1 = Item(Material.DIAMOND_SWORD)
            item_2 = Item(Material.DIRT, name="some dirt")
            hand = PlayerHand.MAIN_HAND
            with p_default.is_holding(item_1, item_2, hand=hand):
            # OR
            with Player(PlayerTarget.DEFAULT).is_holding(item_1, item_2, hand=hand):
                # ... code to be executed if the Default Player is holding either of the given items on the main hand ...
                # (do not specify - or specify None to - ``hand=`` in order to accept either hand.)
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        args = Arguments([
            p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list
        ], tags=[
            Tag(
                "Hand Slot", option="Either Hand" if not hand else Hand(hand).value,  # default is Either Hand
                action=IfPlayerType.IS_HOLDING, block=BlockType.IF_PLAYER
            )
        ])
        return IfPlayer(
            action=IfPlayerType.IS_HOLDING,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def menu_slot_equals(
        self, slots: typing.Union[Numeric, Listable, typing.Iterable[Numeric]],
        *items: typing.Optional[typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if the player's currently open inventory menu contains an item in a specific slot.

        Parameters
        ----------
        slots : Union[:attr:`~.Numeric`, :attr:`~.Listable`, Iterable[:attr:`~.Numeric`]]
            Slot ID(s) to check. Can be either a Numeric, a Listable (list var containing numbers) or an iterable of
            Numeric (e.g.: a list of numbers or number variables).

        items : Optional[Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]], optional
            Item(s) to check for. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a predetermined list of items.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            item_1 = Item(Material.DIAMOND_SWORD)
            item_2 = Item(Material.DIRT, name="my dirt")
            with p_default.menu_slot_equals(5, item_1, item_2):
            # OR
            with Player(PlayerTarget.DEFAULT).menu_slot_equals(5, item_1, item_2):
                # ... code to be executed if the Default Player's currently open menu contains either of the given \
items at slot number 5 ...
                # multiple slots can also be specified with an iterable. E.g. [1, 2, 3, 4] -> one of slots 1,2,3,4
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        slots_list = [p_check(slot, typing.Union[Numeric, Listable], f"slots[{i}]") for i, slot in enumerate(slots)] \
            if isinstance(slots, collections.Iterable) else [p_check(slots, typing.Union[Numeric, Listable], "slots")]

        args = Arguments([
            *slots_list,
            *[p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list]
        ])
        return IfPlayer(
            action=IfPlayerType.MENU_SLOT_EQUALS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def is_blocking(self, *, target: typing.Optional[PlayerTarget] = None):
        """Checks if a player is blocking with a shield.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            with p_default.is_blocking():
            # OR
            with Player(PlayerTarget.DEFAULT).is_blocking():
                # ... code to be executed if the Default Player is blocking with a shield ...
        """
        return IfPlayer(
            action=IfPlayerType.IS_BLOCKING,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def is_sneaking(self, *, target: typing.Optional[PlayerTarget] = None):
        """Checks if a player is sneaking.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            with p_default.is_sneaking():
            # OR
            with Player(PlayerTarget.DEFAULT).is_sneaking():
                # ... code to be executed if the Default Player is sneaking ...
        """
        return IfPlayer(
            action=IfPlayerType.IS_SNEAKING,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def is_flying(self, *, target: typing.Optional[PlayerTarget] = None):
        """Checks if a player is flying.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            with p_default.is_flying():
            # OR
            with Player(PlayerTarget.DEFAULT).is_flying():
                # ... code to be executed if the Default Player is flying ...
        """
        return IfPlayer(
            action=IfPlayerType.IS_FLYING,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def name_equals(
        self, *names: typing.Union[Textable, Listable],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if a player's username is equal to one of the usernames given (case insensitive).

        Parameters
        ----------
        names : Union[:attr:`~.Textable`, :attr:`~.Listable`]
            Name(s) to check for.

            .. note:: Works with UUIDs.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        Just specifying each name directly::

            with p_default.name_equals("Bob", "John"):
            # OR
            with Player(PlayerTarget.DEFAULT).name_equals("Bob", "John"):
                # ... code to be executed if the Default Player's name is either Bob or John ...

        Using a predefined list::

            names = ["Foo", "Bar"]
            with p_default.name_equals(names):
            # OR
            with Player(PlayerTarget.DEFAULT).name_equals(names):
                # ... code to be executed if the Default Player's name is either Foo or Bar ...
                # note that a list variable with the possible names can also be given.
        """
        args = Arguments([
            p_check(name, typing.Union[Textable, Listable], f"names[{i}]") for i, name in enumerate(names)
        ])
        return IfPlayer(
            action=IfPlayerType.NAME_EQUALS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def inv_open_type(
        self, inventory_type: IfPOpenInvType = IfPOpenInvType.ANY_INVENTORY,
        target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if a player has a certain inventory type open.

        Parameters
        ----------
        inventory_type : :class:`~.IFPOpenInvType`
            The type of inventory to check for (i.e., check if the player has this type of inventory currently open).
            Defaults to :attr:`~.ANY_INVENTORY` (any inventory type is accepted).

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Warnings
        --------
        Does not work with special screens such as the death screen, chat box, etc..

        Examples
        --------
        ::

            inv_type = IfPOpenInvType.BLAST_FURNACE  # for example
            with p_default.inv_open_type(inv_type):
            # OR
            with Player(PlayerTarget.DEFAULT).inv_open_type(inv_type):
                # ... code to be executed if the Default Player has a Blast Furnace currently open ...
                # (do not specify any inventory type - or specify ANY_INVENTORY - to check if any inventory is open)
        """
        args = Arguments([], tags=[
            Tag(
                "Inventory Type", option=inventory_type,  # default is Any Inventory
                action=IfPlayerType.INV_OPEN, block=BlockType.IF_PLAYER
            )
        ])
        return IfPlayer(
            action=IfPlayerType.INV_OPEN,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def inv_slot_equals(
        self, slots: typing.Union[Numeric, Listable],
        *items: typing.Optional[typing.Union[ItemParam, ItemCollection, typing.Iterable[ItemParam], Listable]],
        target: typing.Optional[PlayerTarget] = None
    ):
        """Checks if a player has an item in a specific inventory slot/one of the given slots.

        Parameters
        ----------
        slots : Union[:attr:`~.Numeric`, :attr:`~.Listable`, Iterable[:attr:`~.Numeric`]]
            Slot ID(s) to check. Can be either a Numeric, a Listable (list var containing numbers) or an iterable of
            Numeric (e.g.: a list of numbers or number variables).

        items : Optional[Optional[Union[:class:`~.ItemParam`, :class:`~.ItemCollection`, Iterable[:class:`~.ItemParam`], :attr:`Listable`]]], optional
            Item(s) to check for. The items can be specified either as:

            - ``None`` for an empty slot;
            - :class:`~.ItemParam` for one item;
            - :attr:`~.Listable` for a variable list of items;
            - :class:`~.ItemCollection` or Iterable[:class:`~.ItemParam`] for a predetermined list of items.

        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            item_1 = Item(Material.STONE)
            item_2 = Item(Material.SNOWBALL)
            with p_default.inv_slot_equals(29, item_1, item_2):
            # OR
            with Player(PlayerTarget.DEFAULT).inv_slot_equals(29, item_1, item_2):
                # ... code to be executed if the Default Player has either of the items at slot 29 ...
                # (you can check multiple slots by giving a list var or an iterable of Numeric instead of slot number.)
        """
        item_list = flatten(*items, except_iterables=[str], max_depth=1)

        slots_list = [p_check(slot, typing.Union[Numeric, Listable], f"slots[{i}]") for i, slot in enumerate(slots)] \
            if isinstance(slots, collections.Iterable) else [p_check(slots, typing.Union[Numeric, Listable], "slots")]

        args = Arguments([
            *slots_list,
            *[p_check(item, typing.Union[ItemParam, Listable], "items") for item in item_list]
        ])
        return IfPlayer(
            action=IfPlayerType.HAS_SLOT_ITEM,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def is_sprinting(self, *, target: typing.Optional[PlayerTarget] = None):
        """Checks if a player is sprinting or using the sprint key to swim.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            with p_default.is_sprinting():
            # OR
            with Player(PlayerTarget.DEFAULT).is_sprinting():
                # ... code to be executed if the Default Player is sprinting, or, if swimming, is using the swim animation ...
        """
        return IfPlayer(
            action=IfPlayerType.IS_SPRINTING,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def is_gliding(self, *, target: typing.Optional[PlayerTarget] = None):
        """Checks if a player is gliding with elytra.

        Parameters
        ----------
        target : Optional[:class:`~.PlayerTarget`], optional
            The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfPlayer`
            The generated IfPlayer instance.

        Examples
        --------
        ::

            with p_default.is_gliding():
            # OR
            with Player(PlayerTarget.DEFAULT).is_gliding():
                # ... code to be executed if the Default Player is gliding with an Elytra ...
        """
        return IfPlayer(
            action=IfPlayerType.IS_GLIDING,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

#     def cmd_arg_equals(
#         self, *texts: typing.Union[Textable, Listable], arg_num: Numeric,
#         ignore_case: bool = True,
#         target: typing.Optional[PlayerTarget] = None
# ):
    #     """Checks if a certain argument of a player's command is equal to a certain text when the Player Command Event is executed.
    #
    #     .. rank:: Emperor
    #
    #     .. workswith:: Player Command Event
    #
    #     Parameters
    #     ----------
    #     texts : Union[:attr:`~.Textable`, :attr:`~.Listable`]
    #         Text(s) to check for.
    #
    #     arg_num : :attr:`~.Numeric`
    #         Argument number.
    #
    #     ignore_case : :class:`bool`, optional
    #         Defaults to ``True``.
    #
    #     target : Optional[:class:`~.PlayerTarget`], optional
    #         The target of this :class:`~.IfPlayer`, or ``None`` for the current :class:`Player` instance's target.
    #         Defaults to ``None``.
    #
    #     Returns
    #     -------
    #     :class:`~.IfPlayer`
    #         The generated IfPlayer instance.
    #
    #     Examples
    #     --------
    #     ::
    #
    #         with p_default.cmd_arg_equals(texts, arg_num):
    #         # OR
    #         with Player(PlayerTarget.DEFAULT).cmd_arg_equals(texts, arg_num):
    #             # ... code to be executed if the Default Player # TODO: Example
    #     """
    #     args = Arguments([
    #         *[p_check(text, typing.Union[Textable, Listable], f"texts[{i}]") for i, text in enumerate(texts)],
    #         p_check(arg_num, Numeric, "arg_num")
    #     ], tags=[
    #         Tag(
    #             "Ignore Case", option=bool(ignore_case),  # default is True
    #             action=IfPlayerType.CMD_ARG_EQUALS, block=BlockType.IF_PLAYER
    #         )
    #     ])
    #     return IfPlayer(
    #         action=IfPlayerType.CMD_ARG_EQUALS,
    #         args=args,
    #         target=self._digest_target(target),
    #         append_to_reader=False,
    #         invert=False
    #     )

    # endregion:ifplayer


remove_u200b_from_doc(Player)
