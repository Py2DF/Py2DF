import typing
from .enum_util import AutoLowerNameEnum
from enum import auto, unique, IntFlag
from ..constants import SECTION_SIGN
from ..utils import remove_u200b_from_doc


class HideFlags(IntFlag):
    """Represents flags to hide from an :class:`~.Item` (i.e., to not display). Note that they can be OR'ed to
    hide multiple flags (i.e., ``a | b`` to hide both `a` and `b`). Use HIDE_ALL_FLAGS for all flags combined.

    Note that this subclasses :class:`enum.IntFlag` which, in turn, subclasses :class:`int`, meaning all integer
    operations are supported.


    .. container:: comparisons

        .. describe:: a == b, a != b

            Checks if two HideFlags instances represent the same flags.

        .. describe:: a > b, a < b, a >= b, a <= b

            Compares the HideFlags instances' values.

    .. container:: operations

        Note that all integer operations not listed here are supported, but return an :class:`int` instead of a
        :class:`HideFlags` (when applicable).

        .. describe:: a | b

            Combines both flags. (E.g.: ``HideFlags.ENCHANTMENTS | HideFlags.ATTRIBUTE_MODIFIERS`` means that
            both enchantments and attribute modifiers should be hidden from the item.)

        .. describe:: ~a

            Obtains a :class:`HideFlags` instance representing all except `a`'s flag(s).

        .. describe:: b in a

            Returns ``True`` if `a` contains all of `b`'s flags, otherwise ``False``.

        .. describe:: a & b, a ^ b

            Runs the specified logic operations (AND and XOR, respectively) between the values,
            returning the corresponding :class:`HideFlags` instance.

        .. describe:: a + b, a - b, a / b, ...

            Executes the given operation in the same way as integers.


    Attributes
    ------------\u200b
    value : :class:`int`
        The unique integer representing the hidden flags of this instance. This is the value used
        when executing integer operations (such as ``a + b`` or ``a - b``).

    """
    ENCHANTMENTS = 1
    ATTRIBUTE_MODIFIERS = 2
    UNBREAKABLE = 4
    BLOCKS_CAN_DESTROY = 8
    BLOCKS_CAN_PLACE_ON = 16
    MISC_FLAGS = 32  # such as potion effects, "StoredEnchantments", written book "generation" and "author",
    # "Explosion", "Fireworks", and map tooltips

    def __repr__(self):  # from `re.RegexFlag`
        if self._name_ is not None:
            return f'HideFlags.{self._name_}'
        value = self._value_
        members = []
        negative = value < 0
        if negative:
            value = ~value
        for m in self.__class__:
            if value & m._value_:
                value &= ~m._value_
                members.append(f'HideFlags.{m._name_}')
        if value:
            members.append(hex(value))
        res = '|'.join(members)
        if negative:
            if len(members) > 1:
                res = f'~({res})'
            else:
                res = f'~{res}'
        return res


ALL_HIDE_FLAGS = HideFlags(sum(list(HideFlags)))
"""The :class:`HideFlags` instance containing all flags, meaning all kinds of flags should be hidden."""


@unique
class Enchantments(AutoLowerNameEnum):
    """Enchantment types in Minecraft 1.15.2."""
    #  New in 1.16, Soul Speed
    AQUA_AFFINITY         = auto()  #: Speeds up how fast you can mine blocks underwater.
    BANE_OF_ARTHROPODS    = auto()  #: Increases attack damage against arthropods.
    BINDING_CURSE         = auto()  #: Cursed item can not be removed from player.
    BLAST_PROTECTION      = auto()  #: Reduces blast and explosion damage.
    CHANNELING            = auto(
    )  #: Summons a lightning bolt at a targeted mob when enchanted item is thrown (target mob must stand in rain).
    DEPTH_STRIDER         = auto()  #: Speeds up how fast you can move underwater.
    EFFICIENCY            = auto()  #: Increases how fast you can mine.
    FEATHER_FALLING       = auto()  #: Reduces fall and teleportation damage.
    FIRE_ASPECT           = auto()  #: Sets target on fire.
    FIRE_PROTECTION       = auto()  #: Reduces damage caused by fire and lava.
    FLAME                 = auto()  #: Turns arrows into flaming arrows.
    FORTUNE               = auto()  #: Increases block drops from mining.
    FROST_WALKER          = auto()  #: Freezes water into ice so that you can walk on it.
    IMPALING              = auto()  #: Increases attack damage against sea creatures.
    INFINITY              = auto()  #: Shoots an infinite amount of arrows.
    KNOCKBACK             = auto()  #: Increases knockback dealt (enemies repel backwards).
    LOOTING               = auto()  #: Increases amount of loot dropped when mob is killed.
    LOYALTY               = auto()  #: Returns your weapon when it is thrown like a spear.
    LUCK_OF_THE_SEA       = auto()  #: Increases chances of catching valuable items.
    LURE                  = auto()  #: Increases the rate of fish biting your hook.
    MENDING               = auto()  #: Uses xp to mend your tools, weapons and armor.
    MULTISHOT             = auto()  #: Shoots 3 arrows at once but only costs 1 arrow (from your inventory).
    PIERCING              = auto()  #: Arrow can pierce through multiple entities.
    POWER                 = auto()  #: Increases damage dealt by bow.
    PROJECTILE_PROTECTION = auto()  #: Reduces projectile damage (arrows, fireballs, fire charges).
    PROTECTION            = auto()  #: General protection against attacks, fire, lava, and falling.
    PUNCH                 = auto()  #: Increases knockback dealt (enemies repel backwards).
    QUICK_CHARGE          = auto()  #: Reduces the amount of time to reload a crossbow.
    RESPIRATION           = auto()  #: Extends underwater breathing (see better underwater).
    RIPTIDE               = auto()  #: Propels the player forward when enchanted item is thrown while in water or rain.
    SHARPNESS             = auto()  #: Increases attack damage dealt to mobs.
    SILK_TOUCH            = auto()  #: Mines blocks themselves (fragile items).
    SOUL_SPEED            = auto()  #: Walk quicker on soul blocks.
    SMITE                 = auto()  #: Increases attack damage against undead mobs.
    SWEEPING              = auto()  #: Increases damage of sweep attack.
    THORNS                = auto()  #: Causes damage to attackers.
    UNBREAKING            = auto()  #: Increases durability of item.
    VANISHING_CURSE       = auto()  #: Cursed item will disappear after player dies.
    
    # Aliases:
    CURSE_OF_BINDING = BINDING_CURSE
    CURSE_OF_VANISHING = VANISHING_CURSE

  
class Color:
    """Represents all possible colors and formats of Minecraft. Accessing any attribute returns a string."""
    BLACK         = SECTION_SIGN + "0"
    DARK_BLUE     = SECTION_SIGN + "1"
    DARK_GREEN    = SECTION_SIGN + "2"
    DARK_AQUA     = SECTION_SIGN + "3"
    DARK_RED      = SECTION_SIGN + "4"
    DARK_PURPLE   = SECTION_SIGN + "5"
    GOLD          = SECTION_SIGN + "6"
    GRAY          = SECTION_SIGN + "7"
    DARK_GRAY     = SECTION_SIGN + "8"
    BLUE          = SECTION_SIGN + "9"
    GREEN         = SECTION_SIGN + "a"
    AQUA          = SECTION_SIGN + "b"
    RED           = SECTION_SIGN + "c"
    LIGHT_PURPLE  = SECTION_SIGN + "d"
    YELLOW        = SECTION_SIGN + "e"
    WHITE         = SECTION_SIGN + "f"
    OBFUSCATED    = SECTION_SIGN + "k"
    BOLD          = SECTION_SIGN + "l"
    STRIKETHROUGH = SECTION_SIGN + "m"
    UNDERLINE     = SECTION_SIGN + "n"
    ITALIC        = SECTION_SIGN + "o"
    RESET         = SECTION_SIGN + "r"
    
    GREY = GRAY
    DARK_GREY = DARK_GRAY
    
Colour = ChatColor = Color  # aliases


remove_u200b_from_doc(HideFlags)
