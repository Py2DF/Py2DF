import typing

from .._block_utils import _load_btype, BlockParam, _load_btypes
from ..actions import EntityAction
from ..ifs import IfEntity
from ...classes import Arguments, Tag, DFNumber
from ...enums import EntityTarget, EntityActionType, IfEntityType, \
    BlockType, Hand, EffectParticleMode, HorseVariant, HorseColor, MooshroomVariant, \
    EntityAnimation, CatType, EntityColor, FoxType, PandaGene, ParrotVariant, ArmorStandPart, RabbitType, \
    TropicalFishPattern, VillagerProfession, VillagerBiome
from ...typings import Textable, Numeric, Locatable, ItemParam, Potionable, ParticleParam, p_check, SpawnEggable, \
    p_bool_check, Listable
from ...utils import remove_u200b_from_doc


__all__ = ("Entity",)


class Entity:
    """Represents a DiamondFire Entity. Used for Entity Action and If Entity humanized methods.

    Parameters
    ----------\u200b
    target : Optional[:class:`~.EntityTarget`], optional
        The target that this instance represents (Default Entity, Last Mob, Victim etc.) or ``None`` for empty target
        (equivalent to leaving the target line empty on DF - becomes the current selection, or the Default Entity).
        Defaults to ``None``.

    Attributes
    ----------\u200b
    target : Optional[:class:`~.EntityTarget`]
        The target that this instance represents (Default Entity, Last Mob, Victim etc.) or ``None`` for empty target
        (equivalent to leaving the target line empty on DF - becomes the current selection, or the Default Entity).
    """
    __slots__ = ("target",)
    target: typing.Optional[EntityTarget]

    def __init__(self, target: typing.Optional[EntityTarget]):
        self.target: typing.Optional[EntityTarget] = EntityTarget(target) if target else None

    def _digest_target(self, target: typing.Optional[EntityTarget]) -> typing.Optional[EntityTarget]:
        """Checks a given entity target for validity.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`]
            The target to check.

        Returns
        -------
        Optional[:class:`~.EntityTarget`]
            Returns the given target as a valid EntityTarget, or ``None``.
        """
        return EntityTarget(target) if target else None

    # region:entityactions

    def set_armor_stand_tags(
        self,
        *, is_visible: typing.Optional[bool] = None, is_marker: typing.Optional[bool] = None,
        allow_item_taking_or_adding: typing.Optional[bool] = None,
        has_physics_or_updates: typing.Optional[bool] = None, is_small: typing.Optional[bool] = None,
        has_arms: typing.Optional[bool] = None, has_base_plate: typing.Optional[bool] = None,
        target: typing.Optional[EntityTarget] = None
    ):
        """Changes the settings of an armor stand, such as visibility.

        .. rank:: Mythic


        Parameters
        ----------
        is_visible : Optional[:class:`bool`], optional
            Whether this Armor Stand is visible.
            Specify ``True`` or ``False`` to change this setting, or ``None`` to leave it untouched. Defaults to
            ``None``.

        is_marker : Optional[:class:`bool`], optional
            Whether this Armor Stand is a marker (has no hitbox).
            Specify ``True`` or ``False`` to change this setting, or ``None`` to leave it untouched. Defaults to
            ``None``.

        allow_item_taking_or_adding : Optional[:class:`bool`], optional
            Whether this armor stand should have item taking/adding allowed.
            Specify ``True`` or ``False`` to change this setting, or ``None`` to leave it untouched. Defaults to
            ``None``.

        has_physics_or_updates : Optional[:class:`bool`], optional
            Specify ``True`` or ``False`` to change this setting, or ``None`` to leave it untouched. Defaults to
            ``None``.

        is_small : Optional[:class:`bool`], optional
            Specify ``True`` or ``False`` to change this setting, or ``None`` to leave it untouched. Defaults to
            ``None``.

        has_arms : Optional[:class:`bool`], optional
            Specify ``True`` or ``False`` to change this setting, or ``None`` to leave it untouched. Defaults to
            ``None``.

        has_base_plate : Optional[:class:`bool`], optional
            Specify ``True`` or ``False`` to change this setting, or ``None`` to leave it untouched. Defaults to
            ``None``.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.set_armor_stand_tags(is_visible=True, has_physics_or_updates=False)  # selects last spawned entity
            # OR
            Entity(EntityTarget.LAST_ENTITY).set_armor_stand_tags(is_visible=True, has_physics_or_updates=False)
            # Makes the armor stand visible and makes it not affected by physics or updates; other params unchanged
        """
        args = Arguments([], tags=[  # Set to True, Set to False, Don't Change
            Tag(
                "Is Visible",
                option="Set to True" if is_visible else (
                    "Set to False" if is_visible is not None else "Don't Change"
                ),  # default is Don't Change
                action=EntityActionType.ARMOR_STAND_TAGS, block=BlockType.ENTITY_ACTION
            ),
            Tag(
                "Is Marker (No Hitbox)",
                option="Set to True" if is_marker else (
                    "Set to False" if is_marker is not None else "Don't Change"
                ),  # default is Don't Change
                action=EntityActionType.ARMOR_STAND_TAGS, block=BlockType.ENTITY_ACTION
            ),
            Tag(
                "Allow Item Taking / Adding",
                option="Set to True" if allow_item_taking_or_adding else (
                    "Set to False" if allow_item_taking_or_adding is not None else "Don't Change"
                ),  # default is Don't Change
                action=EntityActionType.ARMOR_STAND_TAGS, block=BlockType.ENTITY_ACTION
            ),
            Tag(
                "Has Physics / Updates",
                option="Set to True" if has_physics_or_updates else (
                    "Set to False" if has_physics_or_updates is not None else "Don't Change"
                ),  # default is Don't Change
                action=EntityActionType.ARMOR_STAND_TAGS, block=BlockType.ENTITY_ACTION
            ),
            Tag(
                "Is Small",
                option="Set to True" if is_small else (
                    "Set to False" if is_small is not None else "Don't Change"
                ),  # default is Don't Change
                action=EntityActionType.ARMOR_STAND_TAGS, block=BlockType.ENTITY_ACTION
            ),
            Tag(
                "Has Arms",
                option="Set to True" if has_arms else (
                    "Set to False" if has_arms is not None else "Don't Change"
                ),  # default is Don't Change
                action=EntityActionType.ARMOR_STAND_TAGS, block=BlockType.ENTITY_ACTION
            ),
            Tag(
                "Has Base Plate",
                option="Set to True" if has_base_plate else (
                    "Set to False" if has_base_plate is not None else "Don't Change"
                ),  # default is Don't Change
                action=EntityActionType.ARMOR_STAND_TAGS, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.ARMOR_STAND_TAGS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disguise_as_block(
        self, block_type: BlockParam, name: typing.Optional[Textable] = None,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Disguises the entity as a block.

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
            Name of disguise. Default is ``None`` (no special name).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            block_type = Material.GRASS_BLOCK  # disguise as a grass block
            last_entity.disguise_as_block(block_type, "Some Block")
            # OR
            Entity(EntityTarget.LAST_ENTITY).disguise_as_block(block_type, "Some Block")
            # last spawned entity is disguised as a grass block named "Some Block"
        """
        args = Arguments([
            p_check(block_type, typing.Union[ItemParam, Textable], "block_type"),
            p_check(name, Textable, "name") if name is not None else None
        ])
        return EntityAction(
            action=EntityActionType.BLOCK_DISGUISE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_creeper_charged(
        self, is_charged: bool = True,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets whether a creeper has the charged effect.

        Parameters
        ----------
        is_charged : :class:`bool`, optional
            Whether or not the target creeper should be target. Defaults to ``True`` (should be charged).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.creeper_charged(True)
            # OR
            Entity(EntityTarget.LAST_ENTITY).creeper_charged(True)
            # Creeper is now charged; False for not charged.
        """
        args = Arguments([], tags=[
            Tag(
                "Is Charged", option=bool(is_charged),  # default is True
                action=EntityActionType.CREEPER_CHARGED, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.CREEPER_CHARGED,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_creeper_ignited(
        self, is_ignited: bool = True,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets whether a creeper is currently ignited. (getting ready to explode)

        Parameters
        ----------
        is_ignited : :class:`bool`, optional
            Whether or not the Creeper is ignited. Defaults to ``True`` (is ignited).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_creeper_ignited(True)  # works if last mob spawned is a creeper
            # OR
            Entity(EntityTarget.LAST_MOB).set_creeper_ignited(True)  # creeper is now ignited; False for not ignited
        """
        args = Arguments([], tags=[
            Tag(
                "Is Ignited", option=bool(is_ignited),  # default is True
                action=EntityActionType.CREEPER_IGNITED, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.CREEPER_IGNITED,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_creeper_max_fuse(
        self, ticks: Numeric,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets the starting amount of fuse ticks of a creeper.

        Parameters
        ----------
        ticks : :attr:`~.Numeric`
            Fuse ticks.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_creeper_max_fuse(40)  # if last mob spawned is a creeper, this will work
            # OR
            Entity(EntityTarget.LAST_MOB).set_creeper_max_fuse(40)  # fuse is now 2 seconds
        """
        args = Arguments([
            p_check(ticks, Numeric, "ticks")
        ])
        return EntityAction(
            action=EntityActionType.CREEPER_MAX_FUSE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_creeper_radius(
        self, radius: Numeric,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets the explosion radius of a creeper.

        Parameters
        ----------
        radius : :attr:`~.Numeric`
            The new explosion radius.

            .. note::

                The maximum radius is 25.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.


        Raises
        ------
        :exc:`ValueError`
            If the explosion radius is not within the range `0 <= radius <= 25`.

        Examples
        --------
        ::

            last_mob.set_creeper_radius(5)
            # OR
            Entity(EntityTarget.LAST_MOB).set_creeper_radius(5)  # the last spawned mob, if a creeper, now has its
                                                                 # explosion radius set to 5 blocks wide.
        """
        if isinstance(radius, (int, float, DFNumber)) and not 0 <= radius <= 25:
            raise ValueError("Invalid creeper explosion radius (must be between 0 and 25).")

        args = Arguments([
            p_check(radius, Numeric, "radius")
        ])
        return EntityAction(
            action=EntityActionType.CREEPER_RADIUS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def damage(
        self, damage: Numeric,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Damages the mob.

        Parameters
        ----------
        damage : :attr:`~.Numeric`
            Damage to inflict.

            .. note::

                1 damage = 0.5 hearts

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.damage(6)
            # OR
            Entity(EntityTarget.LAST_ENTITY).damage(6)  # deals 3 hearts of damage to the last spawned entity
        """
        args = Arguments([
            p_check(damage, Numeric, "damage")
        ])
        return EntityAction(
            action=EntityActionType.DAMAGE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disable_glowing(self, *, target: typing.Optional[EntityTarget] = None):
        """Makes the entity no longer glow.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.disable_glowing()
            # OR
            Entity(EntityTarget.LAST_ENTITY).disable_glowing()
        """
        return EntityAction(
            action=EntityActionType.DISABLE_GLOWING,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def enable_drop_items(self, *, target: typing.Optional[EntityTarget] = None):
        """After this code block is executed, the mob will drop their equipment and loot when they die.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.enable_drop_items()
            # OR
            Entity(EntityTarget.LAST_ENTITY).enable_drop_items()
        """
        return EntityAction(
            action=EntityActionType.DROP_ITEMS,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def enable_ai(self, *, target: typing.Optional[EntityTarget] = None):
        """Enables the AI of the mob.

        .. rank:: Noble


        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.enable_ai()
            # OR
            Entity(EntityTarget.LAST_ENTITY).enable_ai()
        """
        return EntityAction(
            action=EntityActionType.ENABLE_AI,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def enable_glowing(self, *, target: typing.Optional[EntityTarget] = None):
        """Makes the entity glow.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.enable_glowing()
            # OR
            Entity(EntityTarget.LAST_ENTITY).enable_glowing()
        """
        return EntityAction(
            action=EntityActionType.ENABLE_GLOWING,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_end_crystal_target(
        self, loc: typing.Optional[Locatable] = None,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets an end crystal's beam target.

        Parameters
        ----------
        loc : Optional[:attr:`~.Locatable`], optional
            The end crystal beam's new target, or ``None`` to remove the beam. Default is ``None``.

            .. note::

                - To remove the beam, specify ``None`` (i.e., not a location).
                - The target location is rounded to the nearest block.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # location of the new beam target
            last_entity.set_end_crystal_target(loc)
            # OR
            Entity(EntityTarget.LAST_ENTITY).set_end_crystal_target(loc)  # sets the last spawned entity's beam target,
                                                                          # should it be an ender crystal.
        """
        args = Arguments([
            p_check(loc, Locatable, "loc") if loc is not None else None
        ])
        return EntityAction(
            action=EntityActionType.END_CRYSTAL_TARGET,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def explode_creeper(self, *, target: typing.Optional[EntityTarget] = None):
        """Causes a creeper to instantly explode.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.explode_creeper()
            # OR
            Entity(EntityTarget.LAST_MOB).explode_creeper()
        """
        return EntityAction(
            action=EntityActionType.EXPLODE_CREEPER,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def give_effect(
        self, *potions: typing.Union[Potionable, Listable],
        effect_particle_mode: EffectParticleMode = EffectParticleMode.SHOWN,
        overwrite_existing_effect: bool = False,
        target: typing.Optional[EntityTarget] = None
    ):
        """Gives the mob one or more potion effects.

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

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            potion_1 = DFPotion(PotionEffect.ABSORPTION, amplifier=255, duration=(5, 0))  # Absorption 255, 5 min dur.
            potion_2 = PotionVar("my var")  # potion variable
            last_entity.give_effect(potion_1, potion_2, effect_particle_mode=EffectParticleMode.BEACON)
            # OR
            Entity(EntityTarget.LAST_ENTITY).give_effect(potion_1, potion_2, effect_particle_mode=EffectParticleMode.BEACON)
            # gives two potion effects with beacon-mode particles.
        """
        args = Arguments([
            p_check(potion, typing.Union[Potionable, Listable], f"potions[{i}]") for i, potion in enumerate(potions)
        ], tags=[
            Tag(
                "Effect Particle Mode", option=effect_particle_mode,  # default is Shown
                action=EntityActionType.GIVE_EFFECT, block=BlockType.ENTITY_ACTION
            ),
            Tag(
                "Overwrite Existing Effect", option=bool(overwrite_existing_effect),  # default is False
                action=EntityActionType.GIVE_EFFECT, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.GIVE_EFFECT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def enable_gravity(self, *, target: typing.Optional[EntityTarget] = None):
        """Enables gravity for the entity.

        .. rank:: Overlord


        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.enable_gravity()
            # OR
            Entity(EntityTarget.LAST_ENTITY).enable_gravity()
        """
        return EntityAction(
            action=EntityActionType.GRAVITY,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def heal(
        self, amount: typing.Optional[Numeric] = None,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Restores the mob's health fully or by an amount.

        Parameters
        ----------
        amount : Optional[:attr:`~.Numeric`], optional
            Amount to heal, or ``None`` to restore fully. Default is ``None`` (restore all of the mob's health).

            .. note::

                1 health = 0.5 hearts

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.heal(6)
            # OR
            Entity(EntityTarget.LAST_ENTITY).heal(6)  # Heals 3 hearts (+3 added)
            # do not specify anything to heal entirely
        """
        args = Arguments([
            p_check(amount, Numeric, "amount") if amount is not None else None
        ])
        return EntityAction(
            action=EntityActionType.HEAL,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def hide_name(self, *, target: typing.Optional[EntityTarget] = None):
        """Hides the name tag of the entity.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.hide_name()
            # OR
            Entity(EntityTarget.LAST_ENTITY).hide_name()
        """
        return EntityAction(
            action=EntityActionType.HIDE_NAME,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_horse_appearance(
        self,
        *, horse_color: typing.Optional[HorseColor] = None,
        horse_variant: typing.Optional[HorseVariant] = None,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets the appearance (the variant) of a horse.

        Parameters
        ----------
        horse_color : Optional[:class:`~.HorseColor`]
            The new color of the horse, or ``None`` to keep unchanged. Defaults to ``None``.

        horse_variant : Optional[:class:`~.HorseVariant`]
            The new variant of the horse, or ``None`` to keep unchanged. Defaults to ``None``.

            .. warning::

                For no variant, specify :attr:`~.HorseVariant.NONE`, not ``None`` (``None`` is to keep unchanged).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            h_color = HorseColor.CHESTNUT  # new color: chestnut
            h_variant = HorseVariant.WHITE  # new variant: white
            last_mob.set_horse_appearance(horse_color=h_color, horse_variant=h_variant)
            # OR
            Entity(EntityTarget.LAST_MOB).set_horse_appearance(horse_color=h_color, horse_variant=h_variant)
            # If the last mob is a horse, then its color and variant are set accordingly.
        """
        args = Arguments([], tags=[
            Tag(
                "Horse Color", option=HorseColor(horse_color) if horse_color else "Don't Change",
                action=EntityActionType.HORSE_APPEARANCE, block=BlockType.ENTITY_ACTION
            ),
            Tag(
                "Horse Variant", option=HorseVariant(horse_variant) if horse_variant else "Don't Change",
                action=EntityActionType.HORSE_APPEARANCE, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.HORSE_APPEARANCE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_jump_strength(
        self, strength: Numeric,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets the jump strength of a horse.

        .. workswith:: Horse, Donkey, Mule, Llama, Trader Llama, Skeleton Horse, Zombie Horse

        Parameters
        ----------
        strength : :attr:`~.Numeric`
            The new jump strength.

            .. note::

                - A jump strength of 0 will prevent jumping.
                - Must be between 0 and 2, otherwise a ValueError is raised (if a constant is specified, i.e., not
                a variable).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.


        Raises
        ------
        :exc:`ValueError`
            If `strength` is not between 0 and 2.

        Examples
        --------
        ::

            last_entity.set_jump_strength(2)
            # OR
            Entity(EntityTarget.LAST_ENTITY).set_jump_strength(2)  # last spawned mob, if horse, now has jump strength of 2
        """
        if isinstance(strength, (int, float, DFNumber)) and not 0 <= strength <= 2:
            raise ValueError("Invalid jump strength (must be between 0 and 2).")

        args = Arguments([
            p_check(strength, Numeric, "strength")
        ])
        return EntityAction(
            action=EntityActionType.JUMP_STRENGTH,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def launch_forward(
        self, power: Numeric,
        *, yaw_only: bool = False,
        target: typing.Optional[EntityTarget] = None
    ):
        """Launches the entity a certain amount forward or backward.

        Parameters
        ----------
        power : :attr:`~.Numeric`
            Launch power.

            .. note::

                A positive launch power is forward, and a negative one is backward.

        yaw_only : :class:`bool`, optional
            If ``True``, only yaw is considered on launch axis. If ``False``, pitch is also considered. Defaults
            to ``False``.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.launch_forward(5)
            # OR
            Entity(EntityTarget.LAST_ENTITY).launch_forward(5)  # launches last spawned mob forward with a power of 5
            # -5 for backwards with same power
        """
        args = Arguments([
            p_check(power, Numeric, "power")
        ], tags=[
            Tag(
                "Launch Axis", option="Yaw Only" if yaw_only else "Pitch and Yaw",  # default is Pitch and Yaw
                action=EntityActionType.LAUNCH_FWD, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.LAUNCH_FWD,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def launch_projectile(
        self, projectile: BlockParam, *, loc: typing.Optional[Locatable] = None,
        name: typing.Optional[Textable] = None, speed: typing.Optional[Numeric] = None,
        inaccuracy: typing.Optional[Numeric] = None, particle: typing.Optional[ParticleParam] = None,
        target: typing.Optional[EntityTarget] = None
    ):
        """Launches a projectile from the mob.

        Parameters
        ----------
        projectile : Union[:class:`Material`, :attr:`~.ItemParam`, :attr:`~.Textable`]
            The type of Projectile to launch.

            The type can be specified either as:

            - an instance of :class:`~.Material` (the material of the block to set);
            - an item (:attr:`~.ItemParam` - the item representing the block to set);
            - text (:attr:`~.Textable` - the material of the block to set as text).

        loc : Optional[:attr:`~.Locatable`], optional
            Launch point (where the projectile is launched from). Default is ``None`` (from the mob in a predetermined
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

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.


        Raises
        ------
        :exc:`ValueError`
            Raised if `inaccuracy` was specified, while `speed` was not.

        Examples
        --------
        ::

            proj = Material.ARROW  # launch an arrow from the mob
            partc = ParticleType.BUBBLE  # bubble trail
            last_entity.launch_projectile(proj, name="My Arrow", speed=5, inaccuracy=2, particle=partc)
            # OR
            Entity(EntityTarget.LAST_ENTITY).launch_projectile(proj, name="My Arrow", speed=5, inaccuracy=2, particle=partc)
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
        return EntityAction(
            action=EntityActionType.LAUNCH_PROJ,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def launch_toward(
        self, loc: Locatable, power: typing.Optional[Numeric] = None,
        *, ignore_distance: bool = False,
        target: typing.Optional[EntityTarget] = None
    ):
        """Launches the entity toward a certain location.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Launch destination.

        power : Optional[:attr:`~.Numeric`], optional
            Launch power. Default is ``None`` (a default value is assigned for power).

            .. note:;

                A negative launch power will launch the entity away from the location.

        ignore_distance : :class:`bool`, optional
            If the distance between the entity and the location should be ignored when calculating the strength of the
            pull. Defaults to ``False``.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # the location where to launch towards
            last_entity.launch_toward(loc, 10)
            # OR
            Entity(EntityTarget.LAST_ENTITY).launch_toward(loc, 10)  # launch last spawned entity towards location
                                                                     # with a power of 10
        """
        args = Arguments([
            p_check(loc, Locatable, "loc"),
            p_check(power, Numeric, "power") if power is not None else None
        ], tags=[
            Tag(
                "Ignore Distance", option=bool(ignore_distance),  # default is False
                action=EntityActionType.LAUNCH_TOWARD, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.LAUNCH_TOWARD,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def launch_up(
        self, power: Numeric,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Launches the entity a certain amount up or down. A positive amount is up, and a negative amount is down.

        Parameters
        ----------
        power : :attr:`~.Numeric`
            Launch power.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.launch_up(10)
            # OR
            Entity(EntityTarget.LAST_ENTITY).launch_up(10)  # Launches the entity up with power 10 (use -10 for down).
        """
        args = Arguments([
            p_check(power, Numeric, "power")
        ])
        return EntityAction(
            action=EntityActionType.LAUNCH_UP,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disguise_as_mob(
        self, spawn_egg: SpawnEggable, name: typing.Optional[Textable] = None,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Disguises the entity as a mob.

        .. rank:: Overlord


        Parameters
        ----------
        spawn_egg : :attr:`~.SpawnEggable`
            Mob to disguise as (a spawn egg).

        name : Optional[:attr:`~.Textable`], optional
            Disguise name (of the mob). Default is ``None`` (no name).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            mob = Material.ZOMBIE_SPAWN_EGG  # disguise as zombie
            last_entity.disguise_as_mob(mob, "Zomb")
            # OR
            Entity(EntityTarget.LAST_ENTITY).disguise_as_mob(mob, "Zomb")  # disguise the last spawned entity as a zombie
                                                                           # named "Zomb"
        """
        args = Arguments([
            p_check(spawn_egg, SpawnEggable, "spawn_egg"),
            p_check(name, Textable, "name") if name is not None else None
        ])
        return EntityAction(
            action=EntityActionType.MOB_DISGUISE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_mooshroom_variant(
        self, mooshroom_variant: MooshroomVariant = MooshroomVariant.RED,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets the skin type of a mooshroom.

        Parameters
        ----------
        mooshroom_variant : :class:`~.MooshroomVariant`
            The new variant (either :attr:`~.MooshroomVariant.RED` or :attr:`~.MooshroomVariant.BROWN`).
            Defaults to :attr:`~.MooshroomVariant.RED`.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_mooshroom_variant(MooshroomVariant.BROWN)
            # OR
            Entity(EntityTarget.LAST_MOB).set_mooshroom_variant(MooshroomVariant.BROWN)  # if the last spawned mob is a
                                                                                         # mooshroom, it becomes of
                                                                                         # brown variant.
        """
        args = Arguments([], tags=[
            Tag(
                "Mooshroom Variant", option=MooshroomVariant(mooshroom_variant),  # default is Red
                action=EntityActionType.MOOSHROOM_VARIANT, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.MOOSHROOM_VARIANT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def move_to(
        self, loc: Locatable, speed: typing.Optional[Numeric] = None,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Instructs the mob's AI to always pathfind to a certain location at a certain speed.

        .. rank:: Overlord


        Parameters
        ----------
        loc : :attr:`~.Locatable`
            Target location.

        speed : Optional[:attr:`~.Numeric`], optional
            The walk speed the mob should have. Default is ``None`` (default walk speed).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Warnings
        -----
        'Move To' only works if the mob is close enough to the target so that its AI can pathfind to it.


        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # target location
            last_mob.move_to(loc, 5)
            # OR
            Entity(EntityTarget.LAST_MOB).move_to(loc, 5)  # Tells AI to move to target location at speed of 5
        """
        args = Arguments([
            p_check(loc, Locatable, "loc"),
            p_check(speed, Numeric, "speed") if speed is not None else None
        ])
        return EntityAction(
            action=EntityActionType.MOVE_TO,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disable_ai(self, *, target: typing.Optional[EntityTarget] = None):
        """Disables the AI of the mob.

        .. rank:: Noble


        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.disable_ai()
            # OR
            Entity(EntityTarget.LAST_MOB).disable_ai()
        """
        return EntityAction(
            action=EntityActionType.NO_AI,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disable_drops(self, *, target: typing.Optional[EntityTarget] = None):
        """After this code block is executed, the mob will no longer drop their equipment and loot when they die.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.disable_drops()
            # OR
            Entity(EntityTarget.LAST_MOB).disable_drops()
        """
        return EntityAction(
            action=EntityActionType.NO_DROPS,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disable_gravity(self, *, target: typing.Optional[EntityTarget] = None):
        """Disables gravity for the entity.

        .. rank:: Overlord


        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.disable_gravity()
            # OR
            Entity(EntityTarget.LAST_ENTITY).disable_gravity()
        """
        return EntityAction(
            action=EntityActionType.NO_GRAVITY,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disable_proj_coll(self, *, target: typing.Optional[EntityTarget] = None):
        """Prevents projectiles from hitting the mob.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.disable_proj_coll()
            # OR
            Entity(EntityTarget.LAST_MOB).disable_proj_coll()
        """
        return EntityAction(
            action=EntityActionType.NO_PROJ_COLL,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def disguise_as_player(
        self, name: Textable, *, skin: typing.Optional[Textable] = None,
        target: typing.Optional[EntityTarget] = None
    ):
        """Disguises the entity as a player.

        .. rank:: Overlord


        Parameters
        ----------
        name : :attr:`~.Textable`
            Name of the player to disguise as.

        skin : Optional[:attr:`~.Textable`], optional
            Name of the player whose skin should be used, or ``None`` for the skin of the player given in `name`.
            Default is ``None``.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.disguise_as_player("John", skin="Notch")  # (last spawned entity)
            # OR
            Entity(EntityTarget.LAST_ENTITY).disguise_as_player("John", skin="Notch")  # disguises as the Notch skin,
                                                                                       # but named "John".
            # do not specify skin in order to apply the skin assigned to the given name (in this case, "John").
        """
        args = Arguments([
            p_check(name, Textable, "name"),
            p_check(skin, Textable, "skin") if skin is not None else None
        ])
        return EntityAction(
            action=EntityActionType.PLAYER_DISGUISE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def enable_proj_coll(self, *, target: typing.Optional[EntityTarget] = None):
        """Allows projectiles to hit the mob.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.enable_proj_coll()
            # OR
            Entity(EntityTarget.LAST_ENTITY).enable_proj_coll()
        """
        return EntityAction(
            action=EntityActionType.PROJ_COLL,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_projectile_item(
        self, item: ItemParam,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets the item the projectile displays as.

        .. workswith:: Snowball, Egg, Small Fireball, Ghast Fireball, Ender Pearl, Experience Bottle

        Parameters
        ----------
        item : :attr:`~.ItemParam`
            Item for the projectile to display as.

            .. note:: Does not work with air.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.


        Examples
        --------
        ::

            item = Item(Material.STONE, name="My Stone")  # displays as a stone block named "My Stone"
            last_entity.projectile_item(item)
            # OR
            Entity(EntityTarget.LAST_ENTITY).projectile_item(item)
        """
        args = Arguments([
            p_check(item, ItemParam, "item")
        ])
        return EntityAction(
            action=EntityActionType.PROJECTILE_ITEM,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def remove(self, *, target: typing.Optional[EntityTarget] = None):
        """Deletes the entity.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.remove()
            # OR
            Entity(EntityTarget.LAST_ENTITY).remove()
        """
        return EntityAction(
            action=EntityActionType.REMOVE,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def remove_effect(
        self, *potions: typing.Union[Potionable, Listable],
        target: typing.Optional[EntityTarget] = None
    ):
        """Removes one or more potion effects from the mob.

        Parameters
        ----------
        potions : Union[:attr:`~.Potionable`, :attr:`~.Listable`]
            Potion effect(s) to be removed, or a List variable containing them.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Notes
        -----
        Amplifiers and durations do not have to be the same as the initial potion effect(s).


        Examples
        --------
        ::

            potion_1 = DFPotion(PotionEffect.ABSORPTION, amplifier=5)
            potion_2 = PotionVar("my var containing a potion")
            last_entity.remove_effect(potion_1, potion_2)
            # OR
            Entity(EntityTarget.LAST_ENTITY).remove_effect(potion_1, potion_2)  # removes potion_1 and potion_2 effects
                                                                                # from the last spawned entity.
        """
        args = Arguments([
            p_check(potion, typing.Union[Potionable, Listable], f"potions[{i}]") for i, potion in enumerate(potions)
        ])
        return EntityAction(
            action=EntityActionType.REMOVE_EFFECT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def ride_entity(
        self, name: Textable,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Mounts the target entity on top of another player or entity.

        .. rank:: Noble


        Parameters
        ----------
        name : :attr:`~.Textable`
            Name of player or entity to be ridden.

            .. note:: Player names will be prioritized before mob names.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.


        Examples
        --------
        ::

            last_entity.ride_entity("Something")
            # OR
            Entity(EntityTarget.LAST_ENTITY).ride_entity("Something")  # mounts the last spawned entity on top of either
                                                                       # a player named "Something" or, if none, an
                                                                       # entity named "Something".
        """
        args = Arguments([
            p_check(name, Textable, "name")
        ])
        return EntityAction(
            action=EntityActionType.RIDE_ENTITY,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def send_animation(
        self, animation_type: EntityAnimation,
        target: typing.Optional[EntityTarget] = None
    ):
        """Makes the mob perform an animation.

        Parameters
        ----------
        animation_type : :class:`~.EntityAnimation`
            The type of animation to send (see the EntiytAnimation enum documentation for options).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.send_animation(EntityAnimation.SWING_RIGHT_ARM)
            # OR
            Entity(EntityTarget.LAST_ENTITY).send_animation(EntityAnimation.SWING_RIGHT_ARM)  # makes the last spawned entity
                                                                                              # swing its right arm.
        """
        args = Arguments([], tags=[
            Tag(
                "Animation Type", option=EntityAnimation(animation_type),  # default is Swing Right Arm
                action=EntityActionType.SEND_ANIMATION, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SEND_ANIMATION,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_age_or_size(
        self, age_or_size: Numeric,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets the age or size of the mob.

        Parameters
        ----------
        age_or_size : :attr:`~.Numeric`
            Mob age or size to set.

            .. note::

                - Ages below 0 make the mob a baby. For animals, age increases constantly.
                - For slimes, magma cubes and phantoms, size is set instead of age.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_age_or_size(2)
            # OR
            Entity(EntityTarget.LAST_MOB).set_age_or_size(2)  # sets the last spawned mob's age or size to 2.
        """
        args = Arguments([
            p_check(age_or_size, Numeric, "age_or_size")
        ])
        return EntityAction(
            action=EntityActionType.SET_AGE_OR_SIZE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_is_age_locked(
        self, is_locked: bool = True,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets whether a mob should age.

        Parameters
        ----------
        is_locked : :class:`bool`, optional
            Whether or not the mob should be unable to age. Defaults to ``True`` (mob cannot age).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_age_locked(True)
            # OR
            Entity(EntityTarget.LAST_MOB).set_age_locked(True)  # last spawned mob can no longer age
        """
        args = Arguments([], tags=[
            Tag(
                "Is Locked", option=bool(is_locked),  # default is True
                action=EntityActionType.SET_AGE_LOCKED, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_AGE_LOCKED,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    # def set_armor(self, *, target: typing.Optional[EntityTarget] = None):
    #     """
    #
    #     Parameters
    #     ----------
    #     target : Optional[:class:`~.EntityTarget`], optional
    #         The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
    #         Defaults to ``None``.
    #
    #     Returns
    #     -------
    #     :class:`EntityAction`
    #         The generated EntityAction instance.
    #
    #     Examples
    #     --------
    #     ::
    #
    #         last_entity.set_armor()
    #         # OR
    #         Entity(EntityTarget.LAST_ENTITY).set_armor()
    #     """
    #     return EntityAction(
    #         action=EntityActionType.SET_ARMOR,
    #         args=Arguments(),
    #         target=self._digest_target(target),
    #         append_to_reader=True
    #     )

    def set_cat_type(
        self, skin_type: CatType,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets the skin type of a cat.

        Parameters
        ----------
        skin_type : :class:`~.CatType`
            The new skin type of the cat (see the CatType docs for options).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_cat_type(CatType.TABBY)
            # OR
            Entity(EntityTarget.LAST_MOB).set_cat_type(CatType.TABBY)  # if the last spawned mob is a cat, its cat type
                                                                       # becomes "Tabby"
        """
        args = Arguments([], tags=[
            Tag(
                "Skin Type", option=CatType(skin_type),  # default is Tabby
                action=EntityActionType.SET_CAT_TYPE, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_CAT_TYPE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_color(
        self, color: EntityColor,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets the color of a mob.

        .. workswith:: Sheep, Shulker, Dog (collar), Cat (collar)

        Parameters
        ----------
        color : :class:`~.EntityColor`
            The new color of the mob (see EntityColor docs for options).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_color(EntityColor.WHITE)
            # OR
            Entity(EntityTarget.LAST_MOB).set_color(EntityColor.WHITE)  # sets the last spawned mob's color to white
        """
        args = Arguments([], tags=[
            Tag(
                "Color", option=EntityColor(color),  # default is White
                action=EntityActionType.SET_COLOR, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_COLOR,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_fall_distance(
        self, distance: Numeric,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets the entity's fall distance, affecting fall damage upon landing.

        Parameters
        ----------
        distance : :attr:`~.Numeric`
            Fall distance (in blocks).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.set_fall_distance(10)
            # OR
            Entity(EntityTarget.LAST_ENTITY).set_fall_distance(10)  # Sets the last spawned entity's fall distance to 10 blocks.
        """
        args = Arguments([
            p_check(distance, Numeric, "distance")
        ])
        return EntityAction(
            action=EntityActionType.SET_FALL_DISTANCE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_fire_ticks(
        self, duration: Numeric,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets the entity on fire for a certain number of ticks.

        Parameters
        ----------
        duration : :attr:`~.Numeric`
            Duration for which the entity should be on fire (in ticks).

            .. note::

                A duration of 0 extinguishes the entity (i.e., removes fire).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.


        Examples
        --------
        ::

            last_entity.set_fire_ticks(60)
            # OR
            Entity(EntityTarget.LAST_ENTITY).set_fire_ticks(60)  # Last spawned entity is now on fire for 3 seconds
        """
        args = Arguments([
            p_check(duration, Numeric, "duration")
        ])
        return EntityAction(
            action=EntityActionType.SET_FIRE_TICKS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_fox_type(
        self, fox_type: FoxType,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets the fur type of a fox.

        Parameters
        ----------
        fox_type : :class:`~.FoxType`
            The new type of fox fur (either :attr:`~.FoxType.RED` or :attr:`~.FoxType.SNOW`).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_fox_type(FoxType.RED)
            # OR
            Entity(EntityTarget.LAST_MOB).set_fox_type(FoxType.RED)  # Sets the last spawned mob's fox type to a Red Fox.
        """
        args = Arguments([], tags=[
            Tag(
                "Fox Type", option=FoxType(fox_type),  # default is Red
                action=EntityActionType.SET_FOX_TYPE, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_FOX_TYPE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_hand_item(
        self, item: typing.Optional[ItemParam] = None,
        *, hand_slot: Hand = Hand.MAIN_HAND,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets the item in the mob's main hand or off hand.

        Parameters
        ----------
        item : Optional[:attr:`~.ItemParam`], optional
            Item to set. Default is ``None``.

        hand_slot : :class:`~.Hand`, optional
            The hand this item should be given to (either :attr:`~.Hand.MAIN_HAND` or :attr:`~.Hand.OFF_HAND`).
            Defaults to :attr:`~.Hand.MAIN_HAND`.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            item = Item(Material.DIAMOND, name="Some Diamond")  # item to give
            last_entity.set_hand_item(item, hand_slot=Hand.OFF_HAND)
            # OR
            Entity(EntityTarget.LAST_ENTITY).set_hand_item(item, hand_slot=Hand.OFF_HAND)  # sets the last spawned entity's
                                                                                           # offhand to the given item.
        """
        args = Arguments([
            p_check(item, ItemParam, "item") if item is not None else None
        ], tags=[
            Tag(
                "Hand Slot", option=Hand(hand_slot),  # default is Main Hand
                action=EntityActionType.SET_HAND_ITEM, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_HAND_ITEM,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_health(
        self, health: Numeric,
        *, absorption: bool = False, combined: bool = False,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets the mob's health or absorption hearts.

        Parameters
        ----------
        health : :attr:`~.Numeric`
            New health.

            .. note::

                1 health = 0.5 hearts

        absorption : :class:`bool`, optional
            If ``True``, the mob's absorption health is set instead of regular health. Defaults to ``False`` (set regular
            health).

        combined : :class:`bool`, optional
            If ``True``, both the mob's regular and absorption hearts are set. Defaults to ``False`` (just regular health).

            .. note::

                Specifying this overrides what was specified for `absorption`.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        Setting regular health::

            last_mob.set_health(15)
            # OR
            Entity(EntityTarget.LAST_MOB).set_health(15)  # sets the last spawned mob's health to 15 (7.5 hearts).

        Setting absorption health::

            last_mob.set_health(15, absorption=True)
            # OR
            Entity(EntityTarget.LAST_MOB).set_health(15, absorption=True)  # sets the last spawned mob's absorption
                                                                           # health to 15 (7.5 absorp. hearts).

        Setting combined health (regular and absorption health)::

            last_mob.set_health(15, combined=True)
            # OR
            Entity(EntityTarget.LAST_MOB).set_health(15, combined=True)  # sets the last spawned mob's combined to 15
                                                                           # (7.5 hearts in total).
        """
        args = Arguments([
            p_check(health, Numeric, "health")
        ], tags=[
            Tag(
                "Heal Type", option="Combined Health" if combined else (
                    "Absorption Health" if absorption else "Regular Health"
                ),  # default is Regular Health
                action=EntityActionType.SET_HEALTH, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_HEALTH,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_horse_armor(
        self, item: typing.Optional[ItemParam] = None,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets the armor of a horse.

        Parameters
        ----------
        item : Optional[:attr:`~.ItemParam`], optional
            Armor item. Default is ``None`` (no armor).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            armor = Item(Material.DIAMOND_HORSE_ARMOR)  # a diamond horse armor
            last_mob.set_horse_armor(armor)
            # OR
            Entity(EntityTarget.LAST_MOB).set_horse_armor(armor)  # last spawned mob, if horse, gets diamond horse armor
        """
        args = Arguments([
            p_check(item, ItemParam, "item") if item is not None else None
        ])
        return EntityAction(
            action=EntityActionType.SET_HORSE_ARMOR,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_horse_chest(
        self, has_chest: bool = True,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets whether a horse has a chest equipped.

        .. workswith:: Donkey, Mule, Llama, Trader Llama

        Parameters
        ----------
        has_chest : :class:`bool`, optional
            If ``True``, the horse will have a chest equipped. If ``False``, it won't. Defaults to ``True`` (has chest).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_horse_chest(True)
            # OR
            Entity(EntityTarget.LAST_MOB).set_horse_chest(True)  # if the last spawned mob is a valid horse, it will
                                                                 # have a chest equipped. (Specify False to remove.)
        """
        args = Arguments([], tags=[
            Tag(
                "Has Chest", option=bool(has_chest),  # default is True
                action=EntityActionType.SET_HORSE_CHEST, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_HORSE_CHEST,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_invulnerable(
        self, invulnerable: bool = True,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets whether an entity is invulnerable to damage.

        Parameters
        ----------
        invulnerable : :class:`bool`, optional
            If ``True``, the entity will be invulnerable. Otherwise (``False``), vulnerable. Defaults to ``True``.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.set_invulnerable(True)
            # OR
            Entity(EntityTarget.LAST_ENTITY).set_invulnerable(True)  # last spawned entity is now invulnerable (False to undo)
        """
        args = Arguments([], tags=[
            Tag(
                "Invulnerable", option=bool(invulnerable),  # default is True
                action=EntityActionType.SET_INVULNERABLE, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_INVULNERABLE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_item_owner(
        self, uuid: typing.Optional[Textable] = None,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets an item's owner.

        Parameters
        ----------
        uuid : Optional[:attr:`~.Textable`], optional
            The new owner's UUID. Default is ``None``.

            .. note:: Specifying no owner will clear the item's owner.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Notes
        -----
        Items with owners can only be picked up by their owner until the item is within 10 seconds of despawning.

        Examples
        --------
        ::

            uuid = TextVar("some var with an UUID")  # uuid of new item owner
            last_entity.set_item_owner(uuid)
            # OR
            Entity(EntityTarget.LAST_ENTITY).set_item_owner(uuid)  # If the last spawned entity is an item, its owner
                                                                   # will be set to the player who owns that UUID.
        """
        args = Arguments([
            p_check(uuid, Textable, "uuid") if uuid is not None else None
        ])
        return EntityAction(
            action=EntityActionType.SET_ITEM_OWNER,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_max_health(
        self, health: Numeric,
        *, heal_fully: bool = False,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets the maximum amount of health that the mob can have.

        Parameters
        ----------
        health : :attr:`~.Numeric`
            New maximum health of the mob.

        heal_fully : :class:`bool`, optional
            If ``True``, the mob is healed to the new max health. Defaults to ``False`` (not healed).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.set_max_health(26)
            # OR
            Entity(EntityTarget.LAST_ENTITY).set_max_health(26)  # mob's max health is now 26 (13 hearts).
        """
        args = Arguments([
            p_check(health, Numeric, "health")
        ], tags=[
            Tag(
                "Heal Mob to Max Health", option=bool(heal_fully),  # default is False
                action=EntityActionType.SET_MAX_HEALTH, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_MAX_HEALTH,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_mob_sitting(
        self, is_sitting: bool = True,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets whether a tamed mob is sitting.

        Parameters
        ----------
        is_sitting : :class:`bool`, optional
            If ``True``, the mob will be sitting. Defaults to ``True``.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_mob_sitting(True)
            # OR
            Entity(EntityTarget.LAST_MOB).set_mob_sitting(True)  # Last spawned mob will now be sitting; False to undo
        """
        args = Arguments([], tags=[
            Tag(
                "Is Sitting", option=bool(is_sitting),  # default is True
                action=EntityActionType.SET_MOB_SITTING, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_MOB_SITTING,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_name(
        self, name: Textable,
        *, hide_name_tag: bool = False,
        target: typing.Optional[EntityTarget] = None
    ):
        """Changes the name of the entity.

        Parameters
        ----------
        name : :attr:`~.Textable`
            The entity's new name.

        hide_name_tag : :class:`bool`, optional
            If ``True``, the entity's name will be hidden (i.e., not show up above it). Defaults to ``False`` (visible).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.set_name("My Entity", hide_name_tag=True)
            # OR
            Entity(EntityTarget.LAST_ENTITY).set_name("My Entity", hide_name_tag=True)  # Sets the last spawned entity's
                                                                                        # name to "My Entity", while
                                                                                        # keeping it hidden.
        """
        args = Arguments([
            p_check(name, Textable, "name")
        ], tags=[
            Tag(
                "Hide Name Tag", option=bool(hide_name_tag),  # default is False
                action=EntityActionType.SET_NAME, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_NAME,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_panda_genes(
        self,
        *, main_gene: typing.Optional[PandaGene] = None, hidden_gene: typing.Optional[PandaGene] = None,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets the genes (traits) of a panda.

        Parameters
        ----------
        main_gene : Optional[:class:`~.PandaGene`]
            The panda's new main gene (see PandaGene docs for options), or ``None`` to not change. Defaults to ``None``.

        hidden_gene : Optional[:class:`~.PandaGene`]
            The panda's new hidden gene (see PandaGene docs for options), or ``None`` to not change. Defaults to ``None``.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_panda_genes(main_gene=PandaGene.LAZY, hidden_gene=PandaGene.AGGRESSIVE)
            # OR
            Entity(EntityTarget.LAST_MOB).set_panda_genes(main_gene=PandaGene.LAZY, hidden_gene=PandaGene.AGGRESSIVE)
        """
        args = Arguments([], tags=[  # hidden goes first!!!
            Tag(
                "Hidden Gene", option=PandaGene(hidden_gene) if hidden_gene is not None else None,
                # default is Don't Change
                action=EntityActionType.SET_PANDA_GENES, block=BlockType.ENTITY_ACTION
            ),
            Tag(
                "Main Gene", option=PandaGene(main_gene) if main_gene is not None else None,  # default is Don't Change
                action=EntityActionType.SET_PANDA_GENES, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_PANDA_GENES,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_parrot_variant(
        self, parrot_variant: ParrotVariant,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets the skin variant of a parrot.

        Parameters
        ----------
        parrot_variant : :class:`~.ParrotVariant`
            The new variant of the target parrot (see ParrotVariant docs for options).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_parrot_variant(ParrotVariant.RED)
            # OR
            Entity(EntityTarget.LAST_MOB).set_parrot_variant(ParrotVariant.RED)  # last spawned mob, if parrot,
                                                                                 # is now a red parrot.
        """
        args = Arguments([], tags=[
            Tag(
                "Parrot Variant", option=ParrotVariant(parrot_variant),  # default is Red
                action=EntityActionType.SET_PARROT_VARIANT, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_PARROT_VARIANT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_pickup_delay(
        self, delay: Numeric,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets an item's pickup delay.

        Parameters
        ----------
        delay : :attr:`~.Numeric`
            New pickup delay (in ticks).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.set_pickup_delay(60)
            # OR
            Entity(EntityTarget.LAST_ENTITY).set_pickup_delay(60)  # Last spawned entity, if an item, will have its
                                                                   # pickup delay set to 3 seconds (60 ticks).
        """
        args = Arguments([
            p_check(delay, Numeric, "delay")
        ])
        return EntityAction(
            action=EntityActionType.SET_PICKUP_DELAY,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_armorstand_pose(
        self, x_rot: typing.Optional[Numeric] = None, y_rot: typing.Optional[Numeric] = None,
        z_rot: typing.Optional[Numeric] = None,
        *, part: ArmorStandPart = ArmorStandPart.HEAD,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets the three-dimensional rotation of an armor stand part.

        .. rank:: Mythic


        Parameters
        ----------
        x_rot : Optional[:attr:`~.Numeric`], optional
            X Rotation (0 to 360 degrees). Default is ``None``.

        y_rot : Optional[:attr:`~.Numeric`], optional
            Y Rotation (0 to 360 degrees). Default is ``None``.

        z_rot : Optional[:attr:`~.Numeric`], optional
            Z Rotation (0 to 360 degrees). Default is ``None``

        part : :class:`~.ArmorStandPart`, optional
            The part of the armor stand to be rotated (either :attr:`~.ArmorStandPart.HEAD`,
            :attr:`~.ArmorStandPart.BODY`, :attr:`~.ArmorStandPart.LEFT_ARM`, :attr:`~.ArmorStandPart.RIGHT_ARM`,
            :attr:`~.ArmorStandPart.LEFT_LEG` or :attr:`~.ArmorStandPart.RIGHT_LEG`). Defaults to HEAD.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.set_armorstand_pose(45, 45, 45, part=ArmorStandPart.HEAD)
            # OR
            Entity(EntityTarget.LAST_ENTITY).set_armorstand_pose(45, 45, 45, part=ArmorStandPart.HEAD)
            # if the last spawned entity is an armor stand, its head is rotated 45 degrees on each of x, y, z.
        """
        if isinstance(x_rot, (int, float, DFNumber)):
            x_rot = DFNumber(x_rot % 360)

        if isinstance(y_rot, (int, float, DFNumber)):
            y_rot = DFNumber(y_rot % 360)

        if isinstance(z_rot, (int, float, DFNumber)):
            z_rot = DFNumber(z_rot % 360)

        args = Arguments([
            p_check(x_rot, Numeric, "x_rot") if x_rot is not None else None,
            p_check(y_rot, Numeric, "y_rot") if y_rot is not None else None,
            p_check(z_rot, Numeric, "z_rot") if z_rot is not None else None
        ], tags=[
            Tag(
                "Armor Stand Part", option=ArmorStandPart(part),  # default is Head
                action=EntityActionType.SET_POSE, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_POSE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_rabbit_type(
        self, skin_type: RabbitType,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets the skin type of a rabbit.

        Parameters
        ----------
        skin_type : :class:`~.RabbitType`
            The new skin type of the rabbit (see RabbitType docs for options).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_rabbit_type(RabbitType.BROWN)
            # OR
            Entity(EntityTarget.LAST_MOB).set_rabbit_type(RabbitType.BROWN)
            # if the last spawned mob is a rabbit, then its skin type is changed to Brown
        """
        args = Arguments([], tags=[
            Tag(
                "Skin Type", option=RabbitType(skin_type),  # default is Brown
                action=EntityActionType.SET_RABBIT_TYPE, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_RABBIT_TYPE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_saddle(
        self, item: typing.Optional[ItemParam],
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets the saddle or carpet item of a mob.

        .. workswith:: Horses, Pigs, Llamas (Decor)

        Parameters
        ----------
        item : Optional[:attr:`~.ItemParam`], optional
            New saddle item, or ``None`` to remove it.

            .. note:: Specifying no saddle item will remove the mob's saddle.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Notes
        -----
        Pigs do not retain saddle metadata, only that they have a saddle.


        Examples
        --------
        ::

            saddle = Item(Material.SADDLE)  # the new saddle item. Specify None instead to remove it.
            last_mob.set_saddle(saddle)
            # OR
            Entity(EntityTarget.LAST_MOB).set_saddle(saddle)  # if the last spawned mob can have a saddle, its saddle item
                                                              # is set to the specified one.
        """
        args = Arguments([
            p_check(item, ItemParam, "item") if item is not None else None
        ])
        return EntityAction(
            action=EntityActionType.SET_SADDLE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_sheep_sheared(
        self, is_sheared: bool = True,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets whether a sheep is currently sheared.

        Parameters
        ----------
        is_sheared : :class:`bool`, optional
            Whether or not the sheep should be sheared. Defaults to ``True``.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_sheep_sheared(True)
            # OR
            Entity(EntityTarget.LAST_MOB).set_sheep_sheared(True)
            # if the last spawned mob is a sheep, it will become sheared. (Specify False to set to not sheared)
        """
        args = Arguments([], tags=[
            Tag(
                "Is Sheared", option=bool(is_sheared),  # default is True
                action=EntityActionType.SET_SHEEP_SHEARED, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_SHEEP_SHEARED,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_slime_ai(
        self, enable_ai: bool = True,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Allows a slime's AI to be enabled and disabled, but unlike the disable AI action, the slime can still be moved.

        .. workswith:: Slime, Magma Cube

        Parameters
        ----------
        enable_ai : :class:`bool`, optional
            Whether or not the Slime/Magma Cube's AI should be enabled (True) or disabled (False). Defaults to ``True``.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_slime_ai(False)
            # OR
            Entity(EntityTarget.LAST_MOB).set_slime_ai(False)
            # if the last spawned mob is a Slime, then its AI is disabled, but it will still be able to be moved.
            # Specify True to re-enable.
        """
        args = Arguments([], tags=[
            Tag(
                "Do AI", option=bool(enable_ai),  # default is True
                action=EntityActionType.SET_SLIME_AI, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_SLIME_AI,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_target(
        self, name: Textable,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Instructs the mob's AI to target a specific mob or player.

        .. rank:: Overlord


        Parameters
        ----------
        name : :attr:`~.Textable`
            Target's name (either a player's or a mob's name).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_target("John")
            # OR
            Entity(EntityTarget.LAST_MOB).set_target("John")
            # the last spawned mob will now target the mob or player named John, if any.
        """
        args = Arguments([
            p_check(name, Textable, "name")
        ])
        return EntityAction(
            action=EntityActionType.SET_TARGET,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_tropical_fish_type(
        self,
        *, pattern_color: typing.Optional[EntityColor] = None, body_color: typing.Optional[EntityColor] = None,
        pattern: typing.Optional[TropicalFishPattern] = None,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets the appearance of a tropical fish.

        Parameters
        ----------
        pattern_color : Optional[:class:`~.EntityColor`], optional
            The new color of the fish's pattern, or ``None`` to keep it unchanged. Defaults to ``None``.

        body_color : Optional[:class:`~.EntityColor`], optional
            The new color of the fish's body, or ``None`` to keep it unchanged. Defaults to ``None``.

        pattern : Optional[:class:`~.TropicalFishPattern`], optional
            The fish's new pattern, or ``None`` to keep it unchanged. Defaults to ``None``. (See TropicalFishPattern docs for options.)

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_tropical_fish_type(pattern_color=EntityColor.RED, body_color=EntityColor.BLACK, pattern=TropicalFishPattern.KOB)
            # OR
            Entity(EntityTarget.LAST_MOB).set_tropical_fish_type(pattern_color=EntityColor.RED, body_color=EntityColor.BLACK, pattern=TropicalFishPattern.KOB)
            # if the last spawned mob is a tropical fish, then its characteristics are changed accordingly.
        """
        args = Arguments([], tags=[
            Tag(
                "Pattern Color", option=EntityColor(pattern_color) if pattern_color is not None else "Don't Change",
                action=EntityActionType.SET_TROP_FISH_TYPE, block=BlockType.ENTITY_ACTION
            ),
            Tag(
                "Body Color", option=EntityColor(body_color) if body_color is not None else "Don't Change",
                action=EntityActionType.SET_TROP_FISH_TYPE, block=BlockType.ENTITY_ACTION
            ),
            Tag(
                "Pattern", option=TropicalFishPattern(pattern) if pattern is not None else "Don't Change",
                action=EntityActionType.SET_TROP_FISH_TYPE, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_TROP_FISH_TYPE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_villager_profession(
        self, profession: typing.Optional[VillagerProfession] = VillagerProfession.NONE,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets a villager's profession.

        Parameters
        ----------
        profession : Optional[:class:`~.VillagerProfession`], optional
            The new villager's profession, or ``None`` / :attr:`~.VillagerProfession.NONE` for no profession.
            Defaults to ``None``.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_villager_profession(VillagerProfession.LIBRARIAN)
            # OR
            Entity(EntityTarget.LAST_MOB).set_villager_profession(VillagerProfession.LIBRARIAN)
            # if the last spawned mob is a Villager, then its profession is set to Librarian.
        """
        args = Arguments([], tags=[
            Tag(
                "Profession", option=VillagerProfession(profession) if profession is not None else "None",
                action=EntityActionType.SET_VILLAGER_PROF, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_VILLAGER_PROF,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_villager_biome(
        self, biome: VillagerBiome,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets the biome type of a villager.

        Parameters
        ----------
        biome : :class:`~.VillagerBiome`
            The villager's new biome type (see VillagerBiome docs for options).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_villager_biome(VillagerBiome.DESERT)
            # OR
            Entity(EntityTarget.LAST_MOB).set_villager_biome(VillagerBiome.DESERT)
            # if the last spawned mob is a villager, then its biome type is set to Desert.
        """
        args = Arguments([], tags=[
            Tag(
                "Biome", option=VillagerBiome(biome),  # default is Desert
                action=EntityActionType.SET_VILLAGER_TYPE, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_VILLAGER_TYPE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def set_wolf_angry(
        self, is_angry: bool = True,
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Sets whether a wolf is angry.

        Parameters
        ----------
        is_angry : :class:`bool`, optional
            Whether or not the wolf is angry. Defaults to ``True``.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.set_wolf_angry(True)
            # OR
            Entity(EntityTarget.LAST_MOB).set_wolf_angry(True)  # if the last spawned mob is a wolf, then it will be angry
        """
        args = Arguments([], tags=[
            Tag(
                "Is Angry", option=bool(is_angry),  # default is True
                action=EntityActionType.SET_WOLF_ANGRY, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SET_WOLF_ANGRY,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def shear_sheep(self, *, target: typing.Optional[EntityTarget] = None):
        """Causes a sheep to be sheared.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.shear_sheep()
            # OR
            Entity(EntityTarget.LAST_MOB).shear_sheep()  # if the last spawned mob is a sheep, then it will be sheared.
        """
        return EntityAction(
            action=EntityActionType.SHEAR_SHEEP,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def sheep_eat(self, *, target: typing.Optional[EntityTarget] = None):
        """Causes a sheep to eat grass.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.sheep_eat()
            # OR
            Entity(EntityTarget.LAST_MOB).sheep_eat()  # if the last spawned mob is a sheep, then it will eat grass.
        """
        return EntityAction(
            action=EntityActionType.SHEEP_EAT,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def show_name(self, *, target: typing.Optional[EntityTarget] = None):
        """Shows the name tag of the entity.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.show_name()
            # OR
            Entity(EntityTarget.LAST_ENTITY).show_name()  # the last spawned entity's name tag is now shown.
        """
        return EntityAction(
            action=EntityActionType.SHOW_NAME,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def silence(self, *, target: typing.Optional[EntityTarget] = None):
        """Prevents the entity from making any sounds.

        .. rank:: Noble


        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.silence()
            # OR
            Entity(EntityTarget.LAST_ENTITY).silence()  # the last spawned entity will be silenced (unable to make sounds).
        """
        return EntityAction(
            action=EntityActionType.SILENCE,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def snowman_pumpkin(
        self, has_pumpkin: bool = True,
        target: typing.Optional[EntityTarget] = None
    ):
        """Sets whether a snowman is wearing a pumpkin.

        Parameters
        ----------
        has_pumpkin : :class:`bool`, optional
            Whether or not the snowman should wear a pumpkin. Defaults to ``True``.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_mob.snowman_pumpkin(False)
            # OR
            Entity(EntityTarget.LAST_MOB).snowman_pumpkin(False)
            # if the last spawned mob is a snowman, then it will no longer wear a pumpkin.
        """
        args = Arguments([], tags=[
            Tag(
                "Has Pumpkin", option=bool(has_pumpkin),  # default is True
                action=EntityActionType.SNOWMAN_PUMPKIN, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.SNOWMAN_PUMPKIN,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def tame(
        self, name: typing.Optional[Textable],
        *, target: typing.Optional[EntityTarget] = None
    ):
        """Tames the mob (if possible).

        Parameters
        ----------
        name : Optional[:attr:`~.Textable`]
            Name of the mob's new owner, or ``None`` to untame.

            .. note::

                - Specifying no owner (``None``) will untame the mob.
                - Can overwrite a previous owner.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.


        Examples
        --------
        ::

            last_mob.tame("John")
            # OR
            Entity(EntityTarget.LAST_MOB).tame("John")  # "John" will be the last spawned mob's new owner, if tameable.
            # Specify None instead of "John" to untame.
        """
        args = Arguments([
            p_check(name, Textable, "name") if name is not None else None
        ])
        return EntityAction(
            action=EntityActionType.TAME,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def teleport(
        self, loc: Locatable,
        *, keep_current_rotation: bool = False,
        target: typing.Optional[EntityTarget] = None
    ):
        """Teleports the entity to a specified location.

        Parameters
        ----------
        loc : :attr:`~.Locatable`
            The entity's new position.

        keep_current_rotation : :class:`bool`, optional
            If ``True``, the entity will keep its current rotation. Defaults to ``False``.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            loc = DFLocation(1, 2, 3)  # where to teleport the entity
            last_entity.teleport(loc, keep_current_rotation=True)
            # OR
            Entity(EntityTarget.LAST_ENTITY).teleport(loc, keep_current_rotation=True)
            # teleports the last spawned entity to the given location, while keeping its current rotation.
        """
        args = Arguments([
            p_check(loc, Locatable, "loc")
        ], tags=[
            Tag(
                "Keep Current Rotation", option=bool(keep_current_rotation),  # default is False
                action=EntityActionType.TELEPORT, block=BlockType.ENTITY_ACTION
            )
        ])
        return EntityAction(
            action=EntityActionType.TELEPORT,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def teleport_sequence(
        self, *locs: typing.Union[Locatable, Listable], delay: typing.Optional[Numeric] = None,
        target: typing.Optional[EntityTarget] = None
    ):
        """Teleports the entity to multiple locations, with a delay between each teleport.

        .. rank:: Noble


        Parameters
        ----------
        locs : Union[:attr:`~.Locatable`, :attr:`~.Listable`]
            Locations to teleport to, in order of teleportation.

        delay : Optional[:attr:`~.Numeric`], optional
            Delay between each teleport (in ticks), or ``None`` for the default (60 ticks = 3s). Defaults to ``None``.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            loc_1 = DFLocation(1, 2, 3)
            loc_2 = LocationVar("my var")
            loc_3 = DFLocation(4, 5, 6)
            last_entity.tp_sequence(loc_1, loc_2, loc_3, delay=120)
            # OR
            Entity(EntityTarget.LAST_ENTITY).tp_sequence(loc_1, loc_2, loc_3, delay=120)
            # teleports the last spawned entity to loc_1 then loc_2 then loc_3, with a delay of 120 ticks (6 seconds)
            # between each teleport.
        """
        args = Arguments([
            *[p_check(loc, typing.Union[Locatable, Listable], f"locs[{i}]") for i, loc in enumerate(locs)],
            p_check(delay, Numeric, "delay") if delay is not None else None
        ])
        return EntityAction(
            action=EntityActionType.TP_SEQUENCE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=True
        )

    def undisguise(self, *, target: typing.Optional[EntityTarget] = None):
        """Removes the entity's disguise.

        .. rank:: Overlord


        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.undisguise()
            # OR
            Entity(EntityTarget.LAST_ENTITY).undisguise()  # the last spawned entity is undisguised.
        """
        return EntityAction(
            action=EntityActionType.UNDISGUISE,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    def unsilence(self, *, target: typing.Optional[EntityTarget] = None):
        """Allows the entity to make sounds.

        .. rank:: Noble


        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.EntityAction`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`EntityAction`
            The generated EntityAction instance.

        Examples
        --------
        ::

            last_entity.unsilence()
            # OR
            Entity(EntityTarget.LAST_ENTITY).unsilence()  # the last spawned entity will be allowed to make sounds.
        """
        return EntityAction(
            action=EntityActionType.UNSILENCE,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=True
        )

    # endregion:entityactions

    # region:ifentity

    def is_vehicle(self, *, target: typing.Optional[EntityTarget] = None) -> IfEntity:
        """Checks if an entity is a vehicle.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.IfEntity`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfEntity`
            The generated IfEntity instance.

        Examples
        --------
        ::

            with last_entity.is_vehicle():
            # OR
            with Entity(EntityTarget.LAST_ENTITY).is_vehicle():
                # ... code to execute if the Last Spawned Entity is a vehicle ...
        """
        return IfEntity(
            action=IfEntityType.IS_VEHICLE,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def is_item(self, *, target: typing.Optional[EntityTarget] = None):
        """Checks if an entity is an item.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.IfEntity`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfEntity`
            The generated IfEntity instance.

        Examples
        --------
        ::

            with last_entity.is_item():
            # OR
            with Entity(EntityTarget.LAST_ENTITY).is_item():
                # ... code to be executed if the Last Spawned Entity is an item ...
        """
        return IfEntity(
            action=IfEntityType.IS_ITEM,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def exists(self, *, target: typing.Optional[EntityTarget] = None):
        """Checks if an entity still exists in the world.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.IfEntity`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfEntity`
            The generated IfEntity instance.

        Notes
        -----
        Entities which have been removed still remain in selections.


        Examples
        --------
        ::

            with last_entity.exists():
            # OR
            with Entity(EntityTarget.LAST_ENTITY).exists():
                # ... code to be executed if code to be executed if the Last Spawned Entity still exists ...
        """
        return IfEntity(
            action=IfEntityType.EXISTS,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def is_near(
        self, center: Locatable, range: typing.Optional[Numeric] = None,
        *, ignore_y_axis: bool = False,
        target: typing.Optional[EntityTarget] = None
    ):
        """Checks if an entity is within a certain distance of a location.

        Parameters
        ----------
        center : :attr:`~.Locatable`
            Center location with which to check how near the entity is to it.

        range : Optional[:attr:`~.Numeric`], optional
            Maximum distance permitted from the location, or ``None`` for the default (5 blocks). Default is ``None``.

        ignore_y_axis : :class:`bool`, optional
            Whether the Y-axis should be ignored when calculating distance. Defaults to ``False`` (no).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.IfEntity`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfEntity`
            The generated IfEntity instance.

        Examples
        --------
        ::

            center = DFLocation(1, 2, 3)  # where the entity should be near to
            distance = 10  # 10 blocks max distance
            with last_entity.is_near(center, distance, ignore_y_axis=False):
            # OR
            with Entity(EntityTarget.LAST_ENTITY).is_near(center, distance, ignore_y_axis=False):
                # ... code to be executed if the Last Spawned Entity is at most 10 blocks away from 'center' ...
        """
        args = Arguments([
            p_check(center, Locatable, "center"),
            p_check(range, Numeric, "distance") if range is not None else None
        ], tags=[
            Tag(
                "Ignore Y-Axis", option=bool(ignore_y_axis),  # default is False
                action=IfEntityType.IS_NEAR, block=BlockType.IF_ENTITY
            )
        ])
        return IfEntity(
            action=IfEntityType.IS_NEAR,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def is_type(
        self, *entity_types: typing.Union[SpawnEggable, ItemParam, Textable],
        target: typing.Optional[EntityTarget] = None
    ):
        """Checks if an entity is of a certain type.

        Parameters
        ----------
        entity_types : Union[:attr:`~.SpawnEggable`, :attr:`~.ItemParam`, :attr:`~.Textable`]
            Spawn egg (to check if it is a certain mob), projectile, or vehicle.
            The code is executed if the entity matches the type/one of the types specified.

            .. note:: 'Textable' type would be for specifying the item material as text.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.IfEntity`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfEntity`
            The generated IfEntity instance.

        Examples
        --------
        ::

            type_1 = Material.ENDERMAN_SPAWN_EGG  # either an enderman,
            type_2 = Material.SNOWBALL            # a snowball,
            type_3 = Material.MINECART            # or a minecart.

            with last_entity.is_type(type_1, type_2, type_3):
            # OR
            with Entity(EntityTarget.LAST_ENTITY).is_type(type_1, type_2, type_3):
                # ... code to be executed if the Last Spawned Entity is either an Enderman, a snowball, or a minecart \
...
        """
        args = Arguments([
            p_check(_load_btype(entity_type), typing.Union[SpawnEggable, ItemParam, Textable], f"entity_types[{i}]") for
            i, entity_type in enumerate(entity_types)
        ])
        return IfEntity(
            action=IfEntityType.IS_TYPE,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def standing_on(
        self, *block_types_or_locs: typing.Union[BlockParam, Locatable],
        target: typing.Optional[EntityTarget] = None
    ):
        """Checks if an entity is standing on a block of a certain type or at a certain location.

        Parameters
        ----------
        block_types_or_locs : Union[:class:`Material`, :attr:`~.ItemParam`, :attr:`~.Textable`, :attr:`~.Locatable`]
            The type of Block(s) to check for, or the location(s) to check (if the entity is standing on them).

            The block types can be specified either as:

            - an instance of :class:`~.Material` (the material of the block to set);
            - an item (:attr:`~.ItemParam` - the item representing the block to set);
            - text (:attr:`~.Textable` - the material of the block to set as text).

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.IfEntity`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfEntity`
            The generated IfEntity instance.

        Warnings
        --------
        Any :class:`~.DFVariable` instances are assumed to refer to block type. In order to specify that it refers
        to the location the entity should be standing on, use :class:`~.LocationVar`.

        Examples
        --------
        ::

            gold_block = Material.GOLD_BLOCK  # Must either be standing on any gold block, or...
            loc = DFLocation(1, 2, 3)         # ...on some specific location.
            with last_entity.standing_on(gold_block, loc):
            # OR
            with Entity(EntityTarget.LAST_ENTITY).standing_on(gold_block, loc):  # TODO: Example
                # ... code to be executed if the Last Spawned Entity is either standing on a gold block or on the \
given location ...
        """
        loaded_btypes = _load_btypes(block_types_or_locs)
        true_btypes = list(
            filter(
                lambda t: p_bool_check(t, typing.Union[ItemParam, Textable]),
                loaded_btypes
            )
        )
        locs = filter(
            lambda t: p_bool_check(t, Locatable) and t not in true_btypes, block_types_or_locs
        )
        _ = [
            p_check(el, typing.Union[ItemParam, Textable, Locatable], f"block_types_or_locs[{i}]")
            for i, el in enumerate(loaded_btypes)
        ]
        # error on unknown type

        args = Arguments([
            *true_btypes,
            *locs
        ])
        return IfEntity(
            action=IfEntityType.STANDING_ON,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def name_equals(
        self, *names: Textable,
        target: typing.Optional[EntityTarget] = None
    ):
        """Checks if an entity's name is equal to the text given/any of the texts given.

        Parameters
        ----------
        names : :attr:`~.Textable`
            Name(s) to check for.

        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.IfEntity`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfEntity`
            The generated IfEntity instance.

        Notes
        -----
        - 'Name Equals' also works with entities with custom names.
        - Works with UUID's.


        Examples
        --------
        ::

            with last_entity.name_equals("John", "Salad"):
            # OR
            with Entity(EntityTarget.LAST_ENTITY).name_equals("John", "Salad"):
                # ... code to be executed if the Last Spawned Entity's name is equal to either "John" or "Salad" ...
        """
        args = Arguments([
            p_check(name, Textable, f"names[{i}]") for i, name in enumerate(names)
        ])
        return IfEntity(
            action=IfEntityType.NAME_EQUALS,
            args=args,
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def is_projectile(self, *, target: typing.Optional[EntityTarget] = None):
        """Checks if an entity is a projectile.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.IfEntity`, or ``dNone`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfEntity`
            The generated IfEntity instance.

        Examples
        --------
        ::

            with last_entity.is_projectile():
            # OR
            with Entity(EntityTarget.LAST_ENTITY).is_projectile():
                # ... code to be executed if the Last Spawned Entity is a projectile ...
        """
        return IfEntity(
            action=IfEntityType.IS_PROJ,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    def is_mob(self, *, target: typing.Optional[EntityTarget] = None):
        """Checks if an entity is a mob.

        Parameters
        ----------
        target : Optional[:class:`~.EntityTarget`], optional
            The target of this :class:`~.IfEntity`, or ``None`` for the current :class:`Entity` instance's target.
            Defaults to ``None``.

        Returns
        -------
        :class:`~.IfEntity`
            The generated IfEntity instance.

        Examples
        --------
        ::

            with last_entity.is_mob():
            # OR
            with Entity(EntityTarget.LAST_ENTITY).is_mob():
                # ... code to be executed if if the Last Spawned Entity is a mob ...
        """
        return IfEntity(
            action=IfEntityType.IS_MOB,
            args=Arguments(),
            target=self._digest_target(target),
            append_to_reader=False,
            invert=False
        )

    # endregion:ifentity


remove_u200b_from_doc(Entity)
