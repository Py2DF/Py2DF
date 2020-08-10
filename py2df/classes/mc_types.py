"""
Classes related to DiamondFire (DF) variable types.
"""
import typing
import math
import re
import collections
import operator
import json
import nbtlib as nbt
from nbtlib.tag import Base
from .. import constants
from ..enums import (
    Material, HideFlags, SoundType, ParticleType, CustomSpawnEggType, PotionEffect, Color, Enchantments,
    IfVariableType, BlockType, ItemEqComparisonMode)
from .subcollections import Lore
from .dataclass import Enchantment, Tag
from .abc import DFType, Itemable
from ..utils import remove_u200b_from_doc, clamp, select_dict, nbt_to_python, serialize_tag, dumps_json
from ..schemas import ItemSchema, ItemTagSchema, ItemDisplaySchema, ItemEnchantmentSchema
from ..constants import (
    DEFAULT_VAL, DEFAULT_SOUND_PITCH, DEFAULT_SOUND_VOL, MAX_PITCH_DEGREES, MAX_YAW_DEGREES,
    MAX_ITEM_STACK_SIZE, MIN_ITEM_STACK_SIZE
)

if typing.TYPE_CHECKING:
    from ..codeblocks import IfVariable
    from ..typings import Numeric, Locatable, ItemParam


class Item(DFType, Itemable):  # TODO: Bonus Item classes - WrittenBook, for example, or Chest/EnderChest
    """Represents a Minecraft Item stack.

    Parameters
    ----------\u200b

    material : :class:`Material`
        Instance of the Materials enum; represents what this item actually is.

    amount : :class:`int`
        The amount of items in this item stack, between 1 and 64. By default, 1.

    name : Optional[Union[:class:`str`, :class:`DFText`]]
        An optional custom name to be given to this item, as a `:class:`str`` or :class:`DFText`. Default: None

    lore : Union[`Lore`, Optional[Iterable[:class:`str`]]]
        A Lore for this item (either Lore instance or list of `:class:`str``). Default: empty Lore instance.

    enchantments : Optional[Iterable[:class:`~py2df.classes.dataclass.Enchantment`]]
        A list of :class:`~py2df.classes.dataclass.Enchantment` instances.

    damage : :class:`int`
        The damage of this item (i.e., amount of uses so far). Defaults to 0 (not used).

    unbreakable : :class:`bool`
        Whether or not this item is unbreakable. Defaults to False.

    hide_flags : Optional[Union[:class:`~py2df.enums.misc_mc_enums.HideFlags`, :class:`int`]]
        Flags to be hidden, such as unbreakability. See the enum documentation for more info.


    Other Parameters
    ----------------\u200b
    leather_armor_color : Optional[:class:`int`]
        If this is a piece of leather armor, specify its color through an integer. Tip: Use
        ``0x......`` for hexadecimal colors.

    entity_tag : Optional[Union[:class:`dict`, :class:`str`, :class:`nbtlib.Compound`]]
        An optional TAG_Compound (NBT) representing Entity NBT tags applied on entities that are spawned
        through this item. Applies to the materials: (X)_SPAWN_EGG; TROPICAL_FISH_BUCKET; ARMOR_STAND. Default:
        None (Note: If this is given a string, it must be a valid SNBT string)

    extra_tags : Optional[Union[:class:`dict`, :class:`str`]]
        Any extra NBT tags you'd like to give your item, either as a :class:`dict` of NBT tags or a valid NBT
        :class:`str`. Please ensure those tags do not conflict with the previous ones to avoid spooky errors in
        DiamondFire. Default: ``None``.
        (Please ensure this is a valid TAG_Compound in NBT, a.k.a. `:class:`dict` in pythonic language.)


    .. container:: comparisons

        .. describe:: a == b, a != b

            Checks if every attribute except :attr:`amount` is equal between the two items.

        .. describe:: a > b, a < b, a >= b, a <= b

            Compares the items' amounts, **if they are equal** (otherwise raises a TypeError).

    .. container:: operations

        .. describe:: a + b, a - b, a * b, a ** b, a / b, a // b

            Executes the given operation between the items' amounts.

            .. note::

                The resulting item is a copy of the one that comes first**, with its 'amount' set to the result
                of the operation.

            .. warning::

                Raises a :exc:`ValueError` if there was an attempt to set to a stack outside of the bounds 1 <= n <= 64.

        .. describe:: +a, abs(a), ceil(a), floor(a)

            Returns `a` (self).

        .. describe:: hash(a)

            Returns an unique hash representing its material, name, damage, unbreakability and which flags are hidden.


    Attributes
    -------------\u200b

        material : :class:`~py2df.enums.materials.Material`
            Tells what kind of item this is.
    
        amount : :class:`int`
            The amount there is in this Item stack. (From 1 to 64 - any number outside those bounds will error!)
    
        name : :class:`str`
            The item's name.
    
        lore : :class:`~py2df.classes.subcollections.Lore`
            The item's lore, as an instance of Lore.
    
        enchantments : List[:class:`~py2df.classes.dataclass.Enchantment`]
            A list containing instances of Enchantment.
    
        damage : :class:`int`
            How broken this item is (0 = not broken at all; the higher, the closer to breaking it is). The max
            amount this attribute can have depends on the item's durability, for which there are many lists online.
    
        unbreakable : :class:`bool`
            If True, this item cannot lose durability, and remains at damage = 0.
    
        hide_flags : Union[:class:`~py2df.enums.misc_mc_enums.HideFlags`, :class:`int`]
            Flags to be hidden. Use the :class:`~py2df.enums.misc_mc_enums.HideFlags` enum for this.
            One flag is of the form ``HideFlags.FLAG_NAME``, while, to use more than one, use the OR (bar) operator
            (``HideFlags.FLAG_NAME | HideFlags.OTHER_FLAG_NAME | ...``). For all flags, use :data:`~.ALL_HIDE_FLAGS`.
            For all flags except `x`, use ``~x``.
    
        leather_armor_color : :class:`int`
            An integer that represents the color of a leather armor. Tip: write `0x......` for a
            hexadecimal representation. (This is not present in non-leather armor items.)
    
        entity_tag : Optional[:class:`nbtlib.Compound`]
            Entity NBT. Any NBT that
            modifies entities generated by either spawn eggs, the armor stand item or tropical fish buckets.
            (For other :class:`Material`s, this attribute should always be None.)
    
        extra_tags : Optional[:class:`nbtlib.Compound`]
            Extra NBT, representing any extra tags not covered here.
    """
    __slots__ = (
        "material", "_amount", "name", "lore", "enchantments", "damage", "unbreakable", "hide_flags",
        "leather_armor_color", "entity_tag", "extra_tags"
    )

    def __init__(
        self, material: Material, amount: int = 1,
        *, name: typing.Optional[typing.Union[str, "DFText"]] = None,
        lore: typing.Union[Lore, typing.Optional[typing.Iterable[str]]] = Lore(),
        enchantments: typing.Optional[typing.Iterable[Enchantment]] = None,
        damage: int = 0, unbreakable: bool = False, hide_flags: typing.Optional[typing.Union[HideFlags, int]] = None,
        leather_armor_color: typing.Optional[int] = None,
        entity_tag: typing.Optional[typing.Union[dict, str]] = None,
        extra_tags: typing.Optional[typing.Union[dict, str]] = None
    ):
        """
        Parameters
        ----------

        material : :class:`Material`
            Instance of the Materials enum; represents what this item actually is.

        amount : :class:`int`
            The amount of items in this item stack, between 1 and 64. By default, 1.

        name : Optional[Union[:class:`str`, :class:`DFText`]]
            An optional custom name to be given to this item, as a `:class:`str`` or :class:`DFText`. Default: None

        lore : Union[`Lore`, Optional[Iterable[:class:`str`]]]
            A Lore for this item (either Lore instance or list of `:class:`str``). Default: empty Lore instance.

        enchantments : Optional[Iterable[:class:`~py2df.classes.dataclass.Enchantment`]]
            A list of :class:`~py2df.classes.dataclass.Enchantment` instances.

        damage : :class:`int`
            The damage of this item (i.e., amount of uses so far). Defaults to 0 (not used).

        unbreakable : :class:`bool`
            Whether or not this item is unbreakable. Defaults to False.

        hide_flags : Optional[:class:`~py2df.enums.misc_mc_enums.HideFlags`]
            Flags to be hidden, such as unbreakability. See the enum documentation for more info.
        """
        self.material: Material = material
        self._amount: int = 1
        self.amount = amount
        self.name: str = str(name) if name else None
        self.lore: Lore = Lore(lore)

        if enchantments and any(type(i) != Enchantment for i in enchantments):
            raise TypeError("Non-Enchantment instance found in given 'enchantments' arg.")

        self.enchantments = list(enchantments) if enchantments else []

        self.damage: int = int(damage)

        self.unbreakable: bool = bool(unbreakable)

        self.hide_flags: HideFlags = HideFlags(hide_flags) if hide_flags else None

        if self.material in (
            Material.LEATHER_HELMET, Material.LEATHER_CHESTPLATE, Material.LEATHER_LEGGINGS, Material.LEATHER_BOOTS
        ):
            self.leather_armor_color: typing.Optional[int] = int(leather_armor_color) \
                if leather_armor_color is not None else None
        else:
            self.leather_armor_color: typing.Optional[int] = None

        if entity_tag and "SPAWN_EGG" in self.material.value.upper() or self.material in (
            Material.ARMOR_STAND, Material.TROPICAL_FISH_BUCKET
        ):
            if isinstance(entity_tag, (str, collections.UserString)):
                entity_tag = nbt.parse_nbt(str(entity_tag))

            self.entity_tag: typing.Optional[nbt.Compound] = nbt.Compound(entity_tag)
        else:
            self.entity_tag: typing.Optional[nbt.Compound] = None

        if extra_tags:
            if isinstance(extra_tags, (str, collections.UserString)):
                extra_tags = nbt.parse_nbt(str(extra_tags))

            self.extra_tags: typing.Optional[nbt.Compound] = nbt.Compound(extra_tags)
        else:
            self.extra_tags = None

    @property
    def amount(self) -> int:
        return self._amount

    @amount.setter
    def amount(self, new_amt: int) -> None:
        i_n_amt = int(new_amt)
        if i_n_amt > MAX_ITEM_STACK_SIZE:
            raise ValueError(f"Maximum item stack size is {MAX_ITEM_STACK_SIZE}.")

        if i_n_amt < MIN_ITEM_STACK_SIZE:
            raise ValueError(f"Minimum item stack size is {MIN_ITEM_STACK_SIZE}.")

        self._amount = i_n_amt

    def as_nbt(self) -> nbt.Compound:
        """Produces a NBT representation of this Item.

        Returns
        -------
        :class:`nbtlib.Compound`
            A NBT Tag_Compound (dictionary-like structure) representing this item.
        """
        tag = ItemTagSchema()
        if self.damage > 0:
            tag["Damage"] = int(self.damage)

        if self.unbreakable:
            tag["Unbreakable"] = 1

        if self.entity_tag:  # custom entity-related nbt
            ent_t = self.entity_tag
            if isinstance(ent_t, str) or isinstance(ent_t, collections.UserString):
                tag["EntityTag"] = nbt.parse_nbt(ent_t)
            else:  # must be a nbtlib.Compound or dict already
                tag["EntityTag"] = ent_t

        if self.enchantments:
            tag["Enchantments"] = [
                ItemEnchantmentSchema(
                    id=f"minecraft:{enchant.ench_type.value}", lvl=enchant.level
                ) for enchant in self.enchantments
            ]
        
        if any([self.leather_armor_color is not None, self.name, self.lore]):
            display = ItemDisplaySchema()
            if self.name:
                display["Name"] = dumps_json(str(self.name), ensure_ascii=False)

            if self.lore:
                display["Lore"] = self.lore.as_json_data()

            if self.leather_armor_color is not None:
                display["color"] = int(self.leather_armor_color)

            tag["display"] = display

        if self.hide_flags and self.hide_flags.value:
            tag["HideFlags"] = int(typing.cast(int, self.hide_flags.value))

        if self.extra_tags:
            ext_t = self.extra_tags
            tag.update(
                serialize_tag(
                    ext_t
                ) if isinstance(ext_t, (str, collections.UserString)) else ext_t
            )

        main_nbt = ItemSchema(
            id=f"minecraft:{self.material.value}",
            Count=clamp(int(self.amount), 1, 64),
            tag=tag
        )
        return main_nbt

    def as_snbt(self) -> str:
        """Returns this item as a NBT string.

        Returns
        -------
        :class:`str`
            SNBT string.
        """
        return serialize_tag(self.as_nbt())

    @classmethod
    def from_nbt(cls, data: typing.Union[typing.Dict[str, Base], nbt.Compound]) -> "Item":
        """Produces an Item instance from a TAG_Compound (the Item's NBT).

        Parameters
        ----------
        data : Union[Dict[:class:`str`, :class:`nbtlib.Base`], :class:`nbtlib.Compound`]
            The item's NBT data (either a dict or a Compound class from nbtlib).

        Returns
        -------
        :class:`Item`
            The Item instance representing this NBT data.

        See Also
        --------
        :meth:`Item.from_snbt`
        """
        data = ItemSchema(data)

        new = cls(Material.STONE)

        id_: nbt.String = data.get("id")
        count: nbt.Byte = data.get("Count")

        if id_:
            new.material = Material(nbt_to_python(id_).replace("minecraft:", ""))  # remove surrounding quotes; etc

        if count:
            new.amount = nbt_to_python(count)

        tag: ItemTagSchema = data.get("tag")

        if tag:
            for tag_a, item_a in (
                ("Damage", "damage"), ("Unbreakable", "unbreakable")
            ):
                if tag_a in tag:
                    setattr(new, item_a, nbt_to_python(tag[tag_a]))

            hide_flags: nbt.Int = tag.get("HideFlags")
            enchants: nbt.List[ItemEnchantmentSchema] = tag.get("Enchantments")
            display: ItemDisplaySchema = tag.get("display")
            entity_tag: nbt.Compound = tag.get("EntityTag")
            extra_tags: set = set(tag.keys()) - {
                "Damage", "Unbreakable", "HideFlags", "Enchantments", "display", "EntityTag"
            }

            if hide_flags:
                i_hide_flags = int(nbt_to_python(hide_flags))
                new.hide_flags = HideFlags(i_hide_flags)

            if enchants:  # convert the Enchantment schemas
                new.enchantments = [Enchantment(Enchantments(obj["id"]), obj["lvl"]) for obj in nbt_to_python(enchants)]

            if display:
                disp_dict = nbt_to_python(display)
                for disp_a, item_a in (
                    ("Name", "name"), ("color", "leather_armor_color")
                ):
                    if disp_a in tag:
                        setattr(new, item_a, disp_dict[disp_a])

                if "Lore" in disp_dict:
                    def parse_line(line: str):
                        try:
                            parsed = json.loads(line)
                            if type(parsed) == str:
                                return parsed or None
                            elif type(parsed) == dict:
                                return parsed.get("text") or None
                            else:
                                return None
                        except json.JSONDecodeError:
                            return line or ""

                    new.lore = Lore(map(parse_line, disp_dict["Lore"]))

            if entity_tag:
                new.entity_tag = entity_tag

            if extra_tags:
                new.extra_tags = nbt.Compound(select_dict(tag, extra_tags))

        return new

    @classmethod
    def from_snbt(cls, data: str) -> "Item":
        """Produces an Item instance from a string of SNBT.

        Parameters
        ----------
        data : :class:`str`
            The item's NBT data, as a string.

        Returns
        -------
        :class:`Item`
            The Item instance representing this NBT data.

        See Also
        --------
        :meth:`Item.from_nbt`
        """

        return cls.from_nbt(nbt.parse_nbt(data))

    def as_json_data(self) -> dict:
        """Returns this item as valid DF json representation (as a serializable :class:`dict`, not as a string).

        Returns
        -------
        :class:`dict`
            A JSON-serializable dict.
        """
        return dict(
            id=constants.ITEM_ID_ITEM,
            data=dict(
                item=self.as_snbt()  # it seems "DF_NBT = 1976" is just a means of representing version; can be ignored.
            )
        )

    @classmethod
    def from_json_data(cls, data: dict) -> "Item":
        """Produces an :class:`Item` instance from a valid parsed JSON dict.

        Parameters
        ----------
        data : :class:`dict`
            The parsed JSON data.

        Returns
        -------
        :class:`Item`
            The equivalent :class:`Item` instance.
        """
        if (
            not isinstance(data, dict)
            # or "id" not in data  # not really required
            or "data" not in data
            or not isinstance(data["data"], dict)
            or "item" not in data["data"]
            or not type(data["data"]["item"]) == str
        ):
            raise TypeError(
                "Malformed Item parsed JSON data! Must be a dict with, at least, a 'data' dict and an 'item' str value."
            )

        return cls.from_snbt(data["data"]["item"])

    def to_item(self) -> "Item":
        """Obtains an Item representation of this Item instance.

        Returns
        -------
        :class:`Item`
            An identical copy of this :class:`Item` .
        """
        return self.copy()  # well... yeah

    def set(self, material: Material = DEFAULT_VAL, *args, **kwargs) -> "Item":
        """Refer to __init__'s documentation.

        Parameters
        ----------
        material : :class:`~py2df.enums.Material`
             This item's material.
        *args :
            
        **kwargs :
            

        Returns
        -------
        ``Item``
            self to allow chaining.

        Todo
        ----
        Finish this function.
        """
        pass

    def copy(self) -> "Item":
        """Makes an identical copy of this item stack.

        Returns
        -------
        :class:`Item`

        """
        return Item(
            self.material, self.amount, name=self.name, lore=self.lore, enchantments=self.enchantments,
            damage=self.damage,
            unbreakable=self.unbreakable, hide_flags=self.hide_flags, leather_armor_color=self.leather_armor_color,
            entity_tag=self.entity_tag, extra_tags=self.extra_tags
        )

    def has_item_tag(self, *tags: "Textable") -> "IfVariable":
        """Checks if this Item has the given custom item tag(s).

        Parameters
        ----------
        tags : :attr:`~.Textable`
            The tags to have their presence within the item (self) checked.

        Returns
        -------
        :class:`~.IfVariable`
            The generated IfVariable codeblock for this condition.

        See Also
        --------
        :meth:`~.VarOperable.has_item_tag`

        Examples
        --------
        ::

            with my_item.has_item_tag(var_a, var_b):
                # ... code to run in DF if the tags of 'my_item' include the values of var_a and var_b ...
        """
        from ..typings import p_check, Textable  # lazy import to avoid cyclic imports
        from ..codeblocks import IfVariable
        from .collections import Arguments

        args = Arguments(
            [self] + [p_check(o, Textable, f"tags[{i}]") for i, o in enumerate(tags)]
        )

        return IfVariable(
            action=IfVariableType.ITEM_HAS_TAG,
            args=args,
            append_to_reader=False,
            invert=False
        )

    def __repr__(self):
        base_str = f"<{self.__class__.__name__} minecraft:{self.material.value} x {self.amount}"
        extras = []
        if self.name:
            extras.append(f"name={repr(self.name)}")

        if self.unbreakable:
            extras.append(f"unbreakable=True")
        
        if extras:
            base_str += f" | {' '.join(extras)}"
        
        base_str += ">"
        return base_str

    def __str__(self):
        return f"minecraft:{self.material.value}"

    def __eq__(self, other: "Item"):
        attrs_to_compare = set(self.__class__.__slots__) - {"_amount", }  # compare all except amount

        return type(self) == type(other) and all(
            getattr(self, attr) == getattr(other, attr) for attr in attrs_to_compare
        )

    def __ne__(self, other: "Item"):
        return not self.__eq__(other)

    def __gt__(self, other: "Item"):
        if type(self) != type(other):
            return NotImplemented

        if self != other:
            raise TypeError("Cannot compare different items (must be equal)")

        return self._amount > other._amount

    def __ge__(self, other: "Item"):
        if type(self) != type(other):
            return NotImplemented

        if self != other:
            raise TypeError("Cannot compare different items (must be equal)")

        return self._amount >= other._amount

    def __lt__(self, other: "Item"):
        if type(self) != type(other):
            return NotImplemented

        if self != other:
            raise TypeError("Cannot compare different items (must be equal)")

        return self._amount < other._amount

    def __le__(self, other: "Item"):
        if type(self) != type(other):
            return NotImplemented

        if self != other:
            raise TypeError("Cannot compare different items (must be equal)")

        return self._amount <= other._amount

    def __mul__(self, other: typing.Union[int, "Item"]):
        new = self.copy()
        new.amount *= other._amount if type(self) == type(other) else other
        return new

    def __rmul__(self, other: typing.Union[int, "Item"]):
        return self.__mul__(other)

    def __add__(self, other: typing.Union[int, "Item"]):
        new = self.copy()
        new.amount += other._amount if type(self) == type(other) else other
        return new

    def __radd__(self, other: typing.Union[int, "Item"]):
        return self.__add__(other)

    def __pow__(self, power: typing.Union[int, "Item"]):
        new = self.copy()
        new.amount **= power._amount if type(self) == type(power) else power
        return new

    def __truediv__(self, other: typing.Union[int, "Item"]):  # always rounded.
        return self.__floordiv__(other)

    def __floordiv__(self, other: typing.Union[int, "Item"]):
        new = self.copy()
        new.amount //= other._amount if type(self) == type(other) else other
        return new

    def __sub__(self, other: typing.Union[int, "Item"]):
        new = self.copy()
        new.amount -= other._amount if type(self) == type(other) else other
        return new

    def __ceil__(self):
        return self

    def __floor__(self):
        return self

    def __abs__(self):
        return self

    def __pos__(self):
        return self

    def __hash__(self):
        return hash((self.material, self.name, self.hide_flags, self.damage, self.unbreakable))


class DFText(collections.UserString, DFType):
    """Represents a DiamondFire Text variable. (note: this is not a dynamic variable.)
    
    Subclasses `collections.UserString`; therefore, supports all :class:`str` operations.

    Parameters
    ----------\u200b
    text : :class:`str`
        Text, defaults to "" (empty :class:`str`).
    convert_color : :class:`bool`
        Boolean; whether or not should convert &x to color codes (§x). (Defaults to True)

    Attributes
    ----------\u200b
        data : Union[:class:`str`, :class:`DFText`]
            The value of the text variable.
    
        convert_color : :class:`bool`
            Whether or not should convert "&" to "§" (section sign) to allow easier color code writing.
            Defaults to True.

    """
    __slots__ = ("convert_color",)
    convert_color: bool

    def __init__(self, text: typing.Union[str, "DFText"] = "", *, convert_color: bool = True):
        """
        Init text variable.

        Parameters
        ----------
        text : :class:`str`
            Text, defaults to "" (empty :class:`str`).
        convert_color : :class:`bool`
            Boolean; whether or not should convert &x to color codes (§x). (Defaults to True)
        """
        super().__init__(str(text))
        self.data = str(text)
        self.convert_color = bool(convert_color)

    def set(self, new_text: typing.Union[str, "DFText"]) -> "DFText":
        """Set the value of this text variable.

        Parameters
        ----------
        new_text : :class:`str`
            The new text.

        Returns
        -------
        :class:`DFText`
            self to allow chaining

        """
        self.data = str(new_text)

        return self

    def as_json_data(self) -> dict:
        """Obtain this variable represented as a JSON object (:class:`dict`).

        Parameters
        ----------

        Returns
        -------
        :class:`dict`
        """
        converted_str: str = re.sub(
            constants.STR_COLOR_CODE_REGEX, constants.SECTION_SIGN + r"\1", self.data
        ) if self.convert_color else self.data  # convert color

        return dict(
            id=constants.ITEM_ID_TEXT_VAR,
            data=dict(
                name=converted_str
            )
        )

    @classmethod
    def from_json_data(cls, data: dict):
        """Obtain variable from pre-existing parsed JSON data.

        Must be of the form (have at least those parameters)::

            { "data": { "name": str } }

        Where ``str`` would be the type of the property.

        Parameters
        ----------
        data : :class:`dict`
            The parsed JSON :class:`dict`.

        Returns
        -------
        :class:`DFText`
            :class:`DFText` instance.

        Raises
        ------
        :exc:`TypeError`
            If the data is malformed (does not follow the structure detailed above).
        """
        if (
            not isinstance(data, dict)
            # or "id" not in data  # not really required
            or "data" not in data
            or not isinstance(data["data"], dict)
            or "name" not in data["data"]
            or not type(data["data"]["name"]) == str
        ):
            raise TypeError(
                "Malformed DFText parsed JSON data! Must be a dict with, at least, a 'data' dict and a name str value."
            )

        return cls(data["data"]["name"])

    def text_contains(self, *texts, ignore_case: bool = False) -> "IfVariable":
        """Checks if this DFText's text contains another Textable.

        Parameters
        ----------
        texts : :attr:`~.Textable`
            The text(s) to check if they are contained within `self` or not.

        ignore_case : :class:`bool`, optional
            Whether or not the containing check should ignore whether letters are uppercase or not. Defaults to
            ``False``.

        Returns
        -------
        :class:`~.IfVariable`
            The generated IfVariable codeblock for this condition.

        See Also
        --------
        :meth:`~.VarOperable.text_contains`

        Examples
        --------
        ::

            with DFText("Foo Bar").text_contains(var, ignore_case=True):
                # ... code to execute in DF if var's text is within "Foo Bar", case insensitively ...

            with DFText("Bar Baz").text_contains(var_a, var_b, var_c, ignore_case=False):
                # ... code to execute in DF if "Bar Baz" contains one of var_a, var_b or var_c's text, case sensitive ...

        """
        from ..typings import p_check, Textable  # lazy import to avoid cyclic imports
        from ..codeblocks import IfVariable
        from .collections import Arguments

        args = Arguments([
            self,
            *[p_check(text, Textable, f"texts[{i}]") for i, text in enumerate(texts)]
        ], tags=[
            Tag(
                "Ignore Case", option=str(bool(ignore_case)),
                action=IfVariableType.TEXT_MATCHES, block=BlockType.IF_VAR
            )
        ])

        return IfVariable(
            action=IfVariableType.CONTAINS,
            args=args,
            append_to_reader=False,
            invert=False
        )

    contains = text_contains

    def text_matches(
        self, *texts: typing.Union["Textable", typing.Pattern],
        ignore_case: bool = DEFAULT_VAL, regexp: bool = False
    ) -> "IfVariable":
        """Checks if this :attr:`~.Textable` matches another text. Note that this method is also implemented within
        :class:`~.DFText`.

        Parameters
        ----------
        texts : Union[:attr:`~.Textable`, :class:`re.Pattern`]
            The text(s) to compare `self` to, or a Regular Expression pattern.

        ignore_case : :class:`bool`, optional
            Whether or not the comparison should ignore if letters are uppercase or not. Defaults to ``False``.

        regexp : :class:`bool`, optional
            Whether or not `text` represents a Regex (Regular Expression) pattern. Defaults to ``False``.

            .. note::
                If a :class:`re.Pattern` object is given, then this is automatically set to True.

        Returns
        -------
        :class:`~.IfVariable`
            The generated IfVariable codeblock for this condition.

        See Also
        --------
        :meth:`~.VarOperable.text_matches`

        Examples
        --------
        Example usage::

            with DFText("Foo").text_matches(var_a, ignore_case=True):
                # ... code to execute in DF if "Foo" matches var_a's text, case insensitively ...

            with DFText("Bar").text_matches(var_b, var_c, var_d, ignore_case=False):
                # ... code to execute in DF if "Bar" matches one of var_b's, var_c's or var_d's values, case \
sensitively ...
        """
        from ..typings import p_check, Textable  # lazy import to avoid cyclic imports
        from ..codeblocks import IfVariable
        from .collections import Arguments

        text_list: typing.List[typing.Union[str, typing.Pattern]] = list(texts)
        for i, text in enumerate(text_list):
            if isinstance(text, re.Pattern):
                regexp = True
                ignore_case = re.IGNORECASE in text.flags if ignore_case == DEFAULT_VAL else ignore_case
                text = text.pattern

            text_list[i] = p_check(text, Textable, f"texts[{i}]")

        args = Arguments([
            self,
            *text_list
        ], tags=[
            Tag(
                "Ignore Case", option=bool(ignore_case),
                action=IfVariableType.TEXT_MATCHES, block=BlockType.IF_VAR
            ),
            Tag(
                "Regular Expressions", option="Enable" if regexp else "Disable",
                action=IfVariableType.TEXT_MATCHES, block=BlockType.IF_VAR
            )
        ])

        return IfVariable(
            action=IfVariableType.TEXT_MATCHES,
            args=args,
            append_to_reader=False,
            invert=False
        )

    # def to_item(self) -> Item:
    #     pass  # TODO: implement this as book and stuff

    def __repr__(self):
        return f"<{self.__class__.__name__} data={repr(self.data)}>"


AnyNumber = typing.Union[int, float]


class DFNumber(DFType):
    """Represents a DiamondFire Number variable.
    
    Supports practically all :class:`int`/:class:`float`-related operations and comparisons.

    Parameters
    ----------\u200b
        value : Union[:class:`int`, :class:`float`]
            Value of this :class:`DFNumber`. Defaults to ``0.0``

    Attributes\u200b
    ------------
        value : :class:`float`
            The value of the number variable.
    """
    __slots__ = ("_value",)
    _value: float

    def __init__(self, value: typing.Union["DFNumber", AnyNumber] = 0.0):
        """
        Init number variable.

        Parameters
        ----------
            value : Union[:class:`int`, :class:`float`]
                Value of this :class:`DFNumber`. Defaults to ``0.0``
        """
        self.value = value

    @property
    def value(self) -> float:
        """The value of this number variable.

        Returns
        -------
        :class:`float`
        """
        return self._value

    @value.setter
    def value(self, new_value: AnyNumber):
        """Set the value of this number variable.

        Parameters
        ----------
        new_value : Union[:class:`int`, :class:`float`]
            The new value.

        """
        self._value = float(new_value)

    def set(self, new_value: typing.Union["DFNumber", AnyNumber]) -> "DFNumber":
        """Set the value of this number variable.

        Parameters
        ----------
        new_value : Union[:class:`int`, :class:`float`]
            The new value.

        Returns
        -------
        :class:`DFNumber`
            self to allow chaining
        """
        self._value = float(new_value)

        return self

    def as_json_data(self) -> dict:
        """Obtain this variable represented as a JSON object (:class:`dict`).

        Returns
        -------
        :class:`dict`
        """
        val = self.value
        int_val = int(val)
        return dict(
            id=constants.ITEM_ID_NUMBER_VAR,
            data=dict(
                name=dumps_json(int_val if int_val == val else val)
            )
        )

    @classmethod
    def from_json_data(cls, data: dict) -> "DFNumber":
        """Obtain a DFNumber from pre-existing parsed JSON data (a dict).

        Must have, at least, the following keys (the following structure)::

            { "data": { "name": str } }

        where `str` represents the type of the value.

        Parameters
        ----------
        data : :class:`dict`
            The parsed JSON :class:`dict`.
            

        Returns
        -------
        :class:`DFNumber`
            :class:`DFNumber` instance.

        """
        if (
            not isinstance(data, dict)
            # or "id" not in data  # not really required
            or "data" not in data
            or not isinstance(data["data"], dict)
            or "name" not in data["data"]
            or type(data["data"]["name"]) not in (int, float, str)
        ):
            raise TypeError(
                "Malformed DFNumber parsed JSON data! Must be a dict with, at least, a 'data' dict and a name value."
            )

        return cls(float(data["data"]["name"]))

    def copy(self) -> "DFNumber":
        """
        Obtain an identical copy of this :class:`DFNumber` instance.

        Returns
        -------
        :class:`DFNumber`
            Identical copy of this instance.
        """
        return DFNumber(self.value)

    # def to_item(self) -> Item:
    #     pass  # TODO: implement this as slimeball and stuff

    def is_near(
        self, center_val: "Numeric", valid_range: "Numeric"
    ) -> "IfVariable":
        """Checks if this number is within a certain distance of another number.
        Note that this method is also implemented within :class:`~.VarOperable` (i.e., :class:`~.DFGameValue`
        and :class:`~.DFVariable`) and :class:`~.DFLocation`.

        Parameters
        ----------
        center_val : :attr:`~.Numeric`
            The value to be compared with `self`.

        valid_range : :attr:`~.Numeric`
            The accepted difference between `self` and `center_val`.

        Returns
        -------
        :class:`~.IfVariable`
            The generated IfVariable codeblock for this condition.

        Examples
        --------
        ::

            with DFNumber(2).is_near(var, 10):
                # ... code to execute in DF if 2 has at most a difference of 10 units from var ...
        """
        from ..typings import p_check, Numeric  # lazy import to avoid cyclic imports
        from ..codeblocks import IfVariable
        from .collections import Arguments

        args = Arguments(
            [
                self,
                p_check(center_val, Numeric, "center_val"),
                p_check(valid_range, Numeric, "valid_range")
            ]
        )

        return IfVariable(
            action=IfVariableType.IS_NEAR,
            args=args,
            append_to_reader=False,
            invert=False
        )

    def in_range(
        self, min_val: "Numeric", max_val: "Numeric"
    ) -> "IfVariable":
        """Checks if this number is within 2 other number vars.

        Parameters
        ----------
        min_val : :attr:`~.Numeric`
            The minimum value for this number.

        max_val : :attr:`~.Numeric`
            The maximum value for this number.

        Returns
        -------
        :class:`~.IfVariable`
            The generated IfVariable codeblock for this condition.

        See Also
        --------
        :meth:`~.VarOperable.in_range`

        Examples
        --------
        ::

            with DFNumber(5).in_range(var_a, var_b):
                # ... code that is only executed in DF if 5 is between var_a and var_b ...
        """
        from ..typings import p_check, Numeric  # lazy import to avoid cyclic imports
        from ..codeblocks import IfVariable
        from .collections import Arguments

        args = Arguments(
            [
                self,
                p_check(min_val, Numeric, "min_val"),
                p_check(max_val, Numeric, "max_val")
            ]
        )

        return IfVariable(
            action=IfVariableType.IN_RANGE,
            args=args,
            append_to_reader=False,
            invert=False
        )

    @staticmethod
    def _extract_val(possible_num: typing.Union[int, float, "DFNumber"]):
        if isinstance(possible_num, DFNumber):
            return possible_num.value

        return possible_num

    def __repr__(self):
        return f"<{self.__class__.__name__} value={self.value}>"

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return type(self) == type(other) and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return self.value > DFNumber._extract_val(other)

    def __ge__(self, other):
        return self.value >= DFNumber._extract_val(other)

    def __lt__(self, other):
        return self.value < DFNumber._extract_val(other)

    def __le__(self, other):
        return self.value <= DFNumber._extract_val(other)

    def __add__(self, other):
        return DFNumber(self.value + DFNumber._extract_val(other))

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return DFNumber(self.value - DFNumber._extract_val(other))

    def __rsub__(self, other):
        return DFNumber(DFNumber._extract_val(other) - self.value)

    def __mul__(self, other):
        return DFNumber(self.value * DFNumber._extract_val(other))

    def __rmul__(self, other):
        return self.__mul__(other)

    def __mod__(self, other):
        return DFNumber(self.value % DFNumber._extract_val(other))

    def __rmod__(self, other):
        return other % self.value

    def __truediv__(self, other):
        return DFNumber(self.value / DFNumber._extract_val(other))

    def __rtruediv__(self, other):
        return DFNumber(DFNumber._extract_val(other) / self.value)

    def __floordiv__(self, other):
        return DFNumber(self.value // DFNumber._extract_val(other))

    def __rfloordiv__(self, other):
        return DFNumber(DFNumber._extract_val(other) / self.value)

    def __pow__(self, power, modulo=None):
        return DFNumber(pow(self.value, DFNumber._extract_val(power), modulo))

    def __rpow__(self, other):
        return DFNumber(other ** self)

    def __neg__(self):
        return DFNumber(-self.value)

    def __pos__(self):
        return self.copy()

    def __abs__(self):
        return DFNumber(abs(self.value))

    def __ceil__(self):
        return DFNumber(math.ceil(self.value))

    def __floor__(self):
        return DFNumber(math.floor(self.value))

    def __bool__(self):
        return self.value != 0.0

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __and__(self, other):
        return DFNumber(self.value & DFNumber._extract_val(other))

    def __rand__(self, other):
        return DFNumber(DFNumber._extract_val(other) & self.value)

    def __or__(self, other):
        return DFNumber(self.value | DFNumber._extract_val(other))

    def __ror__(self, other):
        return DFNumber(DFNumber._extract_val(other) | self.value)

    def __xor__(self, other):
        return DFNumber(self.value ^ DFNumber._extract_val(other))

    def __rxor__(self, other):
        return DFNumber(DFNumber._extract_val(other) ^ self.value)

    def __invert__(self):
        return DFNumber(~self.value)


class DFLocation(DFType):
    """Represents a DiamondFire Location.

    Parameters
    ----------\u200b
    x : Union[:class:`int`, :class:`float`]
        The value of the x position.

    y : Union[:class:`int`, :class:`float`]
        The value of the y position.

    z : Union[:class:`int`, :class:`float`]
        The value of the z position.

    pitch : Union[:class:`int`, :class:`float`]
        The pitch value (up/down rotation). Varies between ``-90.0`` and ``90.0`` (any higher/lower will be %'ed).

    yaw : Union[:class:`int`, :class:`float`]
        The yaw value (left/right rotation). Varies between ``-180.0`` and ``180.0`` (any higher/lower will be %ed).

    is_block : :class:`bool`
        Whether or not this location represents a solid (non-air) block. (:class:`bool`) Defaults to False.



    .. container:: comparisons

        .. describe:: a == b, a != b

            Equal if `a` and `b` have the same x,y,z,pitch,yaw; not equal if at lesat one is different.

        .. describe:: a > b, a < b

            True if at least one of the coordinates x,y,z of `a` is bigger (>)/smaller (<) than the
            respective coordinate's value in `b`; False otherwise.

        .. describe:: a >= b, a <= b

            Applies the given comparison between each coordinate x,y,z of `a` and `b`; if any is True, returns True.

    .. container:: operations

        .. describe:: a + b, a - b, a * b, a ** b, a / b, a // b

            Executes the given operation between the two locations' x, y, z; pitch (mod 90), yaw (mod 180).

            .. warning::
                They are all applied in-place with given values, not dynamically in DiamondFire! For a SetVar,
                see :class:`~.DFVariable`.

            .. note::
                If `b` is an **iterable** (tuple, list etc.), then the operation is done between the x,y,z;pitch,yaw
                of `a` and with the respective items 0-4 of the iterable.
                If, however, `b` is an :class:`int`/:class:`float`, then that value is used for the op. to each of
                x,y,z (pitch, yaw remain untouched).

        .. describe:: -a, abs(a)

            Applies the given operation to each of x,y,z,;pitch,yaw of `a`, returning a new DFLocation.

        .. describe:: +a

            Returns `a` (self).

        .. describe:: hash(a)

            A unique hash representing this location's x, y, z, pitch and yaw.


    Attributes\u200b
    -------------
    
        x : :class:`float`
            The value of the x position.
    
        y : :class:`float`
            The value of the y position.
    
        z : :class:`float`
            The value of the z position.
    
        pitch : :class:`float`
            The pitch value (up/down rotation). Varies between ``-90.0`` and ``90.0``
    
        yaw : :class:`float`
            The yaw value (left/right rotation). Varies between ``-180.0`` and ``180.0``
    
        is_block : :class:`bool`
            Whether or not this location represents a solid (non-air) block. Defaults to False.
    """
    __slots__ = ("x", "y", "z", "pitch", "yaw", "is_block")  # , "world_least", "world_most")

    x: float
    y: float
    z: float
    pitch: float
    yaw: float
    is_block: bool
    # world_least: typing.Optional[:class:`int`]
    # world_most: typing.Optional[:class:`int`]

    def __init__(
        self, x: AnyNumber = 0.0, y: AnyNumber = 0.0, z: AnyNumber = 0.0, pitch: AnyNumber = 0.0,
        yaw: AnyNumber = 0.0,
        *, is_block: bool = False,
        # world_least: typing.Optional[:class:`int`] = None, world_most: typing.Optional[:class:`int`] = None
        # locs are now relative
    ):
        """
        Init the location.

        Parameters
        ----------
        x : Union[:class:`int`, :class:`float`]
            The value of the x position.

        y : Union[:class:`int`, :class:`float`]
            The value of the y position.

        z : Union[:class:`int`, :class:`float`]
            The value of the z position.

        pitch : Union[:class:`int`, :class:`float`]
            The pitch value (up/down rotation). Varies between ``-90.0`` and ``90.0`` (any higher/lower will be %'ed).

        yaw : Union[:class:`int`, :class:`float`]
            The yaw value (left/right rotation). Varies between ``-180.0`` and ``180.0`` (any higher/lower will be %ed).

        is_block : :class:`bool`
            Whether or not this location represents a solid (non-air) block. (:class:`bool`) Defaults to False.
        """
        # :param world_least: A constant :class:`int` related to DF; this shouldn't need to be defined by the
        #   library user. None to let the library handle it.
        # :param world_most: A constant :class:`int` related to DF; this shouldn't need to be defined by the
        # library user. None to let the library handle it.
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

        fl_pitch = float(pitch)
        fl_yaw = float(yaw)

        self.pitch = math.copysign(abs(fl_pitch) % MAX_PITCH_DEGREES, fl_pitch)
        self.yaw = math.copysign(abs(fl_yaw) % MAX_YAW_DEGREES, fl_yaw)
        
        self.is_block = bool(is_block)
        # self.world_least = None if world_least is None else :class:`int`(world_least)
        # self.world_most = None if world_most is None else :class:`int`(world_most)

    def set(
        self, x: AnyNumber = DEFAULT_VAL, y: AnyNumber = DEFAULT_VAL, z: AnyNumber = DEFAULT_VAL,
        pitch: AnyNumber = DEFAULT_VAL, yaw: AnyNumber = DEFAULT_VAL,
        *, is_block: bool = DEFAULT_VAL,
        # world_least: typing.Optional[:class:`int`] = DEFAULT_VAL, world_most: typing.Optional[:class:`int`] \
        # = DEFAULT_VAL
    ) -> "DFLocation":
        """Set the location.

        Parameters
        ----------
        x : Union[:class:`int`, :class:`float`], optional
            The value of the x position (:class:`float`).

        y : Union[:class:`int`, :class:`float`], optional
            The value of the y position (:class:`float`).

        z : Union[:class:`int`, :class:`float`], optional
            The value of the z position (:class:`float`).

        pitch : Union[:class:`int`, :class:`float`], optional
            The pitch value (:class:`float`).

        yaw : Union[:class:`int`, :class:`float`], optional
            The yaw value (:class:`float`).

        is_block : :class:`bool`, optional
            Whether or not this location represents a solid (non-air) block. (:class:`bool`) Defaults to False.

        Returns
        -------
        :class:`DFLocation`
            self to allow chaining

        Note
        ----
        All parameters are optional here, meaning that one can pass :const:`~py2df.constants.utility_consts.DEFAULT_VAL`
        to omit a parameter - or, more simply, only use kwargs to choose which values to set.

        Warnings
        --------
        Passing ``None`` will set the value to that! If your intention is to omit a parameter, use
        :const:`~py2df.constants.utility_consts.DEFAULT_VAL` or simply use kwargs to choose which values to set.
        """
        # :param world_least: A constant :class:`int` related to DF; this shouldn't need to be defined by
        # the library user. None to let the library handle it.
        # :param world_most: A constant :class:`int` related to DF; this shouldn't need to be defined by
        # the library user. None to let the library handle it

        self.x = self.x if x == DEFAULT_VAL else float(x)
        self.y = self.y if y == DEFAULT_VAL else float(y)
        self.z = self.z if z == DEFAULT_VAL else float(z)
        self.pitch = self.pitch if pitch == DEFAULT_VAL else float(pitch)
        self.yaw = self.yaw if yaw == DEFAULT_VAL else float(yaw)
        self.is_block = self.is_block if is_block == DEFAULT_VAL else bool(is_block)
        # self.world_least = self.world_least if world_least == DEFAULT_VAL else (
        #     None if world_least is None else :class:`int`(world_least)
        # )
        # self.world_least = self.world_most if world_most == DEFAULT_VAL else (
        #     None if world_most is None else :class:`int`(world_most)
        # )

        return self

    def set_to_other(self, loc: "DFLocation") -> "DFLocation":
        """Imports another location's values into this one, making it identical.

        Parameters
        ----------
        loc : :class:`DFLocation`
            Other location to set.

        Returns
        -------
        :class:`DFLocation`
            `self` to allow chaining

        """
        return self.set(
            loc.x, loc.y, loc.z, loc.pitch, loc.yaw, is_block=loc.is_block,
            # world_least=loc.world_least, world_most=loc.world_most
        )

    def as_json_data(self) -> dict:
        """Obtain this location represented as a JSON object (:class:`dict`).

        Returns
        -------
        :class:`dict`
        """
        return dict(
            id=constants.ITEM_ID_LOCATION,
            data=dict(
                isBlock=self.is_block,
                loc=dict(
                    x=self.x,
                    y=self.y,
                    z=self.z,
                    pitch=self.pitch,
                    yaw=self.yaw
                )
            )
        )

    @classmethod
    def from_json_data(cls, data: dict) -> "DFLocation":
        """Obtain variable from pre-existing parsed JSON data.

        Parameters
        ----------
        data : :class:`dict`
            The parsed JSON :class:`dict`.

        Returns
        -------
        :class:`DFLocation`
            :class:`DFNumber` instance.

        """
        required_attrs = ("x", "y", "z", "isBlock", "pitch", "yaw", "worldLeast", "worldMost")
        if (
                not isinstance(data, dict)
                # or "id" not in data
                or "data" not in data
                or not isinstance(data["data"], dict)
                or not all(attr in data["data"] for attr in required_attrs)
        ):
            raise TypeError(
                f"Malformed DFLocation parsed JSON data! Must be a dict with a 'data' dict including the \
                following attributes: {', '.join(required_attrs)}."
            )

        d_dict = data["data"]

        return cls(
            d_dict.x, d_dict.y, d_dict.z, d_dict.pitch, d_dict.yaw,
            is_block=d_dict.isBlock
        )

    def copy(self) -> "DFLocation":
        """Creates an identical copy of this location.

        Returns
        -------
        :class:`DFLocation`
            Copied location.
        """
        new_loc = DFLocation()
        new_loc.set_to_other(self)
        return new_loc

    def _exec_arithmetic(
        self, other: typing.Union[
            "DFLocation",
            typing.Optional[typing.Iterable[AnyNumber]],
            AnyNumber
        ], arithmetic: typing.Callable, *, op_name: str
    ):
        """Executes some arithmetic within the Location and returns a new one.

        Parameters
        ----------
        other : Union[:class:`DFLocation`, Optional[Iterable[Union[:class:`int`, :class:`float`]], \
`Union`[`:class:`int``, `:class:`float``]]
            The other :class:`DFLocation`, an iterable of the form (x,y,z,pitch,yaw) (use None on any spot to keep
            unchanged), or a :class:`float` that is distributed upon x,y,z.
        arithmetic : `Callable`
            The function that executes the operation.
        op_name : `:class:`str``
            The operation name, to be used in the Error message.

        Returns
        -------
        :class:`DFLocation`
            New :class:`DFLocation`.

        Raises
        ------
        :exc:`TypeError`
            Invalid type provided for arithmetic.

        """
        new_loc = self.copy()

        if type(other) == DFLocation:
            x, y, z, pitch, yaw = map(float, (other.x, other.y, other.z, other.pitch, other.yaw))

        elif isinstance(other, collections.Iterable):
            attr_list = [None] * 5  # initialize an empty array
            for i, value in enumerate(other):
                if i > len(attr_list) - 1:
                    break  # we don't need more values.

                attr_list[i] = value

            x, y, z, pitch, yaw = attr_list

        elif type(other) in (int, float):
            num = float(other)
            x, y, z = [num] * 3
            pitch, yaw = [None] * 2

        else:
            return NotImplemented

        for attr, val in zip(("x", "y", "z"), (x, y, z)):
            if val is None:
                continue  # keep current value

            old_val = getattr(new_loc, attr)

            if op_name == "division" and old_val == val == 0:
                continue  # nope; division by zero

            setattr(new_loc, attr, float(arithmetic(float(old_val), float(val))))

        for mod_attr, val, max_deg in zip(
                ("pitch", "yaw"), (pitch, yaw), (MAX_PITCH_DEGREES, MAX_YAW_DEGREES)
        ):  # gotta do this mod 360, they're rotation values.
            if val is None:
                continue  # keep current value

            old_val = getattr(new_loc, mod_attr)

            if op_name == "division" and old_val == val == 0:
                continue  # nope; division by zero

            result_val = float(
                arithmetic(float(old_val), float(val))
            )
            setattr(
                new_loc, mod_attr, math.copysign(abs(result_val) % max_deg, result_val)
            )                                                       # mod 90/180 degrees, keeping the sign (- or +).

        return new_loc

    # def to_item(self) -> "Item":
    #     pass  # TODO: paper thing

    def is_near(
            self, center_val: "Locatable", valid_range: "Numeric"
    ) -> "IfVariable":
        """Checks if this DFLocation is within a certain distance of another location var.
        Note that this method is also implemented within :class:`~.VarOperable` (i.e., :class:`~.DFGameValue`
        and :class:`~.DFVariable`) and :class:`DFNumber`.

        Parameters
        ----------
        center_val : :attr:`~.Locatable`
            The location to be compared with `self`.

        valid_range : :attr:`~.Numeric`
            The accepted distance between `self` and `center_val`.

        Returns
        -------
        :class:`~.IfVariable`
            The generated IfVariable codeblock for this condition.

        Examples
        --------
        ::

            with DFLocation(1, 2, 3).is_near(var, 10):
                # ... code to execute in DF if 2 is at most at a distance of 10 blocks from var ...
        """
        from ..typings import p_check, Locatable, Numeric  # lazy import to avoid cyclic imports
        from ..codeblocks import IfVariable
        from .collections import Arguments

        args = Arguments(
            [
                self,
                p_check(center_val, Locatable, "center_val"),
                p_check(valid_range, Numeric, "valid_range")
            ]
        )

        return IfVariable(
            action=IfVariableType.IS_NEAR,
            args=args,
            append_to_reader=False,
            invert=False
        )

    def in_range(
        self, min_loc: "Locatable", max_loc: "Locatable"
    ) -> "IfVariable":
        """Checks if this location is within the region formed by 2 other locations (the corners).

        Parameters
        ----------
        min_loc : :attr:`~.Locatable`
            The first corner of the region to check.

        max_loc : :attr:`~.Locatable`
            The second corner, forming a region with min_loc; the code will execute if `self` (location) is within
            that region.

        Returns
        -------
        :class:`~.IfVariable`
            The generated IfVariable codeblock for this condition.

        See Also
        --------
        :meth:`~.VarOperable.in_range`

        Examples
        --------
        ::

            with DFLocation(1, 2, 3).in_range(var_a, var_b):
                # ... code that is only executed in DF if the location of x,y,z = 1,2,3 is within var_a and var_b ...
        """
        from ..typings import p_check, Locatable  # lazy import to avoid cyclic imports
        from ..codeblocks import IfVariable
        from .collections import Arguments

        args = Arguments(
            [
                self,
                p_check(min_loc, Locatable, "min_val"),
                p_check(max_loc, Locatable, "max_val")
            ]
        )

        return IfVariable(
            action=IfVariableType.IN_RANGE,
            args=args,
            append_to_reader=False,
            invert=False
        )

    def __eq__(self, other: "DFLocation") -> bool:
        attrs_to_check = set(self.__class__.__slots__)  # - {"world_least", "world_most"}
        return type(self) == type(other) and all(getattr(self, attr) == getattr(other, attr) for attr in attrs_to_check)

    def __ne__(self, other: "DFLocation"):
        return not self.__eq__(other)

    def __gt__(self, other: "DFLocation") -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        positional_attrs = ("x", "y", "z")
        return any(getattr(self, attr) > getattr(other, attr) for attr in positional_attrs)

    def __ge__(self, other: "DFLocation") -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        positional_attrs = ("x", "y", "z")
        return all(getattr(self, attr) >= getattr(other, attr) for attr in positional_attrs)

    def __lt__(self, other: "DFLocation") -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        positional_attrs = ("x", "y", "z")
        return any(getattr(self, attr) < getattr(other, attr) for attr in positional_attrs)

    def __le__(self, other: "DFLocation") -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        positional_attrs = ("x", "y", "z")
        return all(getattr(self, attr) <= getattr(other, attr) for attr in positional_attrs)

    def __repr__(self):
        return f"<{self.__class__.__name__} x={self.x} y={self.y} z={self.z} pitch={self.pitch} yaw={self.yaw}>"

    def __str__(self):
        return str((self.x, self.y, self.z, self.pitch, self.yaw))

    def __getitem__(self, item: typing.Union[int, str, slice]):
        if item in self.__class__.__slots__:  # ["x"]
            return getattr(self, item)  # give them self.x

        positional_attrs = (self.x, self.y, self.z)
        return positional_attrs[item]  # [0] = x ; [1] = y ; [2] = z

    def __setitem__(self, key: typing.Union[int, str, slice], value: typing.Union[int, float]):
        fl_val = float(value)
        if key in self.__class__.__slots__:
            return setattr(self, key, fl_val)

        pos_attrs = ("x", "y", "z")
        attr_s_to_set = pos_attrs[key]
        if type(attr_s_to_set) == str:
            setattr(self, attr_s_to_set, fl_val)
        else:
            for attr_name in attr_s_to_set:
                setattr(self, attr_name, fl_val)

    def __iter__(self):
        for coord in (self.x, self.y, self.z):
            yield coord

    def __add__(
        self,
        other: typing.Union[
            "DFLocation",
            typing.Optional[typing.Iterable[AnyNumber]],
            AnyNumber
        ]
    ) -> "DFLocation":
        return self._exec_arithmetic(other, operator.add, op_name="addition")

    def __radd__(
        self,
        other: typing.Union[
            "DFLocation",
            typing.Optional[typing.Iterable[AnyNumber]],
            AnyNumber
        ]
    ) -> "DFLocation":
        return self.__add__(other)

    def __sub__(
        self,
        other: typing.Union[
            "DFLocation",
            typing.Optional[typing.Iterable[AnyNumber]],
            AnyNumber
        ]
    ) -> "DFLocation":
        return self._exec_arithmetic(other, operator.sub, op_name="subtraction")

    def __rsub__(
        self,
        other: typing.Union[
            "DFLocation",
            typing.Optional[typing.Iterable[AnyNumber]],
            AnyNumber
        ]
    ) -> "DFLocation":
        return DFLocation.__add__(-self, other)

    def __mul__(
        self,
        other: typing.Union[
            "DFLocation",
            typing.Optional[typing.Iterable[AnyNumber]],
            AnyNumber
            ]
    ) -> "DFLocation":
        return self._exec_arithmetic(other, operator.mul, op_name="multiplication")

    def __rmul__(
            self,
            other: typing.Union[
                "DFLocation",
                typing.Optional[typing.Iterable[AnyNumber]],
                AnyNumber
            ]
    ) -> "DFLocation":
        return self.__mul__(other)

    def __truediv__(
        self,
        other: typing.Union[
            "DFLocation",
            typing.Optional[typing.Iterable[AnyNumber]],
            AnyNumber
        ]
    ) -> "DFLocation":
        return self._exec_arithmetic(other, operator.truediv, op_name="division")

    def __floordiv__(
        self,
        other: typing.Union[
            "DFLocation",
            typing.Optional[typing.Iterable[AnyNumber]],
            AnyNumber
        ]
    ) -> "DFLocation":
        return self._exec_arithmetic(other, operator.floordiv, op_name="division")

    def __pow__(
        self,
        other: typing.Union[
            "DFLocation",
            typing.Optional[typing.Iterable[AnyNumber]],
            AnyNumber
            ]
    ) -> "DFLocation":
        return self._exec_arithmetic(other, pow, op_name="power")

    def __neg__(self):
        new_loc = self.copy()
        for attr in ("x", "y", "z", "pitch", "yaw"):
            setattr(new_loc, attr, -1 * (getattr(self, attr)))

        return new_loc

    def __pos__(self):
        return self

    def __abs__(self):
        new_loc = self.copy()
        for attr in ("x", "y", "z", "pitch", "yaw"):
            setattr(new_loc, attr, abs(getattr(self, attr)))

        return new_loc

    def __ceil__(self):
        new_loc = self.copy()
        for attr in ("x", "y", "z", "pitch", "yaw"):
            setattr(new_loc, attr, float(math.ceil(getattr(self, attr))))

        return new_loc

    def __floor__(self):
        new_loc = self.copy()
        for attr in ("x", "y", "z", "pitch", "yaw"):
            setattr(new_loc, attr, float(math.floor(getattr(self, attr))))

        return new_loc

    def __hash__(self):
        return hash(tuple(getattr(self, attr) for attr in ("x", "y", "z", "pitch", "yaw")))


class DFSound(DFType):
    """Used for DF Sounds (Blaze Death, XP Level up etc.)

    Parameters\u200b
    ----------
        sound_type : :class:`SoundType`
            The enum instance that specifies which sound is this.

        pitch : :class:`float`
            The pitch of this sound (between ``0.0`` and ``2.0``, inclusive). Defaults to 1.0

        volume : :class:`float`
            The volume of this sound. Defaults to 2.0

    Raises
    ------\u200b
    :exc:`ValueError`
        Raised if the given pitch is outside the distance ``0.0 <= x <= 2.0`` .


    .. container: comparisons

        .. describe:: a == b, a != b

            Compares every attribute of `a` and `b`.

    
    Attributes\u200b
    -------------
    
        sound_type : :class:`SoundType`
            The enum instance that specifies which sound is this.

        pitch : :class:`float`
            The pitch of this sound. Defaults to 1.0

        volume : :class:`float`
            The volume of this sound. Defaults to 2.0

    """
    __slots__ = ("sound_type", "_pitch", "volume")
    sound_type: SoundType
    _pitch: float
    volume: float

    def __init__(
        self, sound_type: SoundType, *, volume: float = DEFAULT_SOUND_VOL,
        pitch: AnyNumber = DEFAULT_SOUND_PITCH
    ):
        """
        Parameters
        ----------
            sound_type : :class:`SoundType`
                The enum instance that specifies which sound is this.

            pitch : :class:`float`
                The pitch of this sound (between ``0.0`` and ``2.0``, inclusive). Defaults to 1.0

            volume : :class:`float`
                The volume of this sound. Defaults to 2.0

        Raises
        ------
        :exc:`ValueError`
            Raised if the given pitch is outside the distance ``0.0 <= x <= 2.0`` .
        """
        self.sound_type: SoundType = SoundType(sound_type)

        self._pitch: float = 2.0
        self.pitch = pitch  # trigger property setter
        self.volume: float = float(volume)

    @property
    def pitch(self) -> float:
        return float(self._pitch)

    @pitch.setter
    def pitch(self, val: float) -> None:
        if not 0.0 <= val <= 2.0:
            raise ValueError("Sound pitch must be between 0.0 and 2.0")

        self._pitch = float(val)

    def set(
        self, sound_type: SoundType = DEFAULT_VAL, pitch: AnyNumber = DEFAULT_VAL, volume: float = DEFAULT_VAL
    ) -> "DFSound":
        """Immediately modify this :class:`DFSound`. Note that this is not changed dynamically, in DiamondFire.
        For that, use a dynamic variable.

        Parameters
        ----------
        sound_type : :class:`SoundType`
            The new sound type. (Can be omitted)
            (Default value = DEFAULT_VAL)

        pitch : Union[:class:`int`, :class:`float`]
            The new sound pitch. (Can be omitted)
            (Default value = DEFAULT_VAL)

        volume : :class:`float`
            The new volume. (Can be omitted)
            (Default value = DEFAULT_VAL)

        Returns
        -------
        :class:`DFSound`
            self to allow chaining
        """

        if sound_type != DEFAULT_VAL:
            self.sound_type = SoundType(sound_type)

        if pitch != DEFAULT_VAL:
            self.pitch = float(pitch)

        if volume != DEFAULT_VAL:
            self.volume = float(volume)

        return self

    def set_to_other(self, other: "DFSound") -> "DFSound":
        """
        Set this instance to become identical to another :class:`DFSound` instance.
        
        Parameters
        ----------
        other : :class:`DFSound`
            Other sound to set this instance to.

        Returns
        -------
        :class:`DFSound`
            self to allow chaining
        """
        self.set(sound_type=other.sound_type, pitch=other.pitch, volume=other.volume)
        return self

    # def to_item(self) -> "Item":
    #     pass  # TODO: Sea shell and crap

    def copy(self) -> "DFSound":
        """
        Creates an identical copy of this :class:`DFSound` instance.

        Returns
        -------
        :class:`DFSound`
            Copy of this sound.
        """
        return DFSound(sound_type=self.sound_type, pitch=self.pitch, volume=self.volume)

    def as_json_data(self) -> dict:
        """Representation of this :class:`DFSound` as a valid json-serializable :class:`dict`.

        Returns
        -------
        :class:`dict`
            JSON-serializable :class:`dict`
        """
        return dict(
            id=constants.ITEM_ID_SOUND,
            data=dict(
                sound=self.sound_type.value,
                pitch=float(self.pitch),
                vol=float(self.volume)
            )
        )

    @classmethod
    def from_json_data(cls: typing.Type["DFSound"], data: dict) -> "DFSound":
        """Obtain :class:`DFSound` from pre-existing parsed JSON data.

        Parameters
        ----------
        data : :class:`dict`
            The parsed JSON :class:`dict`.

        Returns
        -------
        :class:`DFSound`
            New :class:`DFSound` instance.
        """
        if (
            not isinstance(data, dict)
            # or "id" not in data  # not really required
            or "data" not in data
            or not isinstance(data["data"], dict)
            or "sound" not in data["data"]
            or not type(data["data"]["sound"]) == str
        ):
            raise TypeError(
                "Malformed DFSound parsed JSON data! Must be a dict with, at least, a 'data' dict and a sound value."
            )

        given_pitch = data["data"].get("pitch")
        pitch: float = float(given_pitch if given_pitch is not None else DEFAULT_SOUND_PITCH)

        given_vol = data["data"].get("vol")
        vol: float = float(given_vol if given_vol is not None else DEFAULT_SOUND_VOL)
        return cls(SoundType(data["data"]["sound"]), pitch=pitch, volume=vol)

    def __repr__(self):
        return f"<{self.__class__.__name__} sound_type={repr(self.sound_type.value)} pitch={self.pitch} \
volume={self.volume}>"

    def __str__(self):
        return self.sound_type.value

    def __hash__(self):
        return hash((self.sound_type.value, self.pitch, self.volume))

    def __eq__(self, other: "DFSound") -> bool:
        return type(self) == type(other) and all(
            getattr(self, attr) == getattr(other, attr) for attr in DFSound.__slots__
        )


class DFParticle(DFType):
    """Used for DF Particles (Smoke, Large Smoke etc.)

    Parameters
    ----------\u200b
    particle_type : :class:`~py2df.enums.dftypes.ParticleType`
        The enum instance that specifies which particle is this.


    .. container:: comparisons

        .. describe:: a == b, a != b

            Checks if two particles have the same :class:`ParticleType` enum value.


    Attributes\u200b
    -------------
    
        particle_type : :class:`~py2df.enums.dftypes.ParticleType`
            The enum instance that specifies which particle is this.

    """
    __slots__ = ("particle_type",)
    particle_type: ParticleType

    def __init__(self, particle_type: ParticleType):
        """
        Initialize this DFParticle.

        Parameters
        ----------
        particle_type : :class:`~py2df.enums.dftypes.ParticleType`
            The enum instance that specifies which particle is this.
        """
        self.particle_type = ParticleType(particle_type)

    def set(self, particle_type: ParticleType) -> "DFParticle":
        """Immediately set the type of this :class:`DFParticle`. Note that this is not changed dynamically,
        in DiamondFire. For that, use a dynamic variable.

        Parameters
        ----------
        particle_type : :class:`ParticleType`
            The new particle type.


        Returns
        -------
        :class:`DFParticle`
            self to allow chaining

        """
        if not isinstance(particle_type, ParticleType):
            raise TypeError("Particle type must be an instance of ParticleType enum.")

        self.particle_type = particle_type

        return self

    # def to_item(self):
    #     pass  # TODO: Sparkly thing and stuff

    def as_json_data(self) -> dict:
        """Representation of this :class:`DFParticle` as a valid json-serializable :class:`dict`.

        Returns
        -------
        :class:`dict`
            JSON data.
        """
        return dict(
            id=constants.ITEM_ID_PARTICLE,
            data=dict(
                particle=self.particle_type.value
            )
        )

    @classmethod
    def from_json_data(cls: typing.Type["DFParticle"], data: dict) -> "DFParticle":
        """Obtain :class:`DFParticle` from pre-existing parsed JSON data.

        Parameters
        ----------
        data : :class:`dict`
            The parsed JSON :class:`dict`.

        Returns
        -------
        :class:`DFParticle`
            :class:`DFParticle` instance.

        """
        if (
            not isinstance(data, dict)
            # or "id" not in data  # not really required
            or "data" not in data
            or not isinstance(data["data"], dict)
            or "particle" not in data["data"]
            or not type(data["data"]["particle"]) == str
        ):
            raise TypeError(
                "Malformed DFSound parsed JSON data! Must be a dict with, at least, a 'data' dict and a particle value."
            )

        return cls(ParticleType(data["data"]["particle"]))

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} particle_type={repr(self.particle_type.value)}>"

    def __str__(self) -> str:
        return str(self.particle_type.value)

    def __eq__(self, other: "DFParticle") -> bool:
        return type(self) == type(other) and self.particle_type == other.particle_type

    def __ne__(self, other: "DFParticle") -> bool:
        return not self.__eq__(other)


class DFCustomSpawnEgg(DFType, Itemable):
    """Used for the custom spawn egg types provided by DiamondFire (Giant, Iron Golem etc.)

    Parameters\u200b
    ----------

        egg_type : :class:`py2df.enums.dftypes.CustomSpawnEggType`
            The enum instance that specifies which spawn egg is this.

    Attributes\u200b
    ---------------

        egg_type : :class:`py2df.enums.dftypes.CustomSpawnEggType`
            The enum instance that specifies which spawn egg is this.


    .. container: comparisons

        .. describe: a == b, a != b

            Checks if two instances have the same `egg_type` attribute.
    """
    __slots__ = ("egg_type",)
    egg_type: CustomSpawnEggType

    def __init__(self, egg_type: CustomSpawnEggType):
        self.egg_type = CustomSpawnEggType(egg_type)

    def set(self, egg_type: CustomSpawnEggType) -> "DFCustomSpawnEgg":
        """Immediately set the type of this :class:`DFParticle`. Note that this is not changed dynamically,
        in DiamondFire. For that, use a dynamic variable.

        Parameters
        ----------
        egg_type : :class:`CustomSpawnEggType`
            The new spawn egg type.

        Returns
        -------
        :class:`DFCustomSpawnEgg`
            self to allow chaining

        """
        self.egg_type = egg_type

        return self

    def as_json_data(self) -> dict:
        """Representation of this :class:`DFCustomSpawnEgg` as a valid json-serializable :class:`dict`.

        Returns
        -------
        :class:`dict`
            JSON-serializable dict.
        """
        return self.to_item().as_json_data()

    @classmethod
    def from_json_data(cls, data: dict) -> "DFCustomSpawnEgg":
        """Obtain :class:`DFCustomSpawnEgg` from pre-existing parsed JSON data.

        Parameters
        ----------
        data : :class:`dict`
            The parsed JSON :class:`dict`.

        Returns
        -------
        :class:`DFCustomSpawnEgg`
            :class:`DFCustomSpawnEgg` instance.

        """
        new_item: Item = Item.from_json_data(data)
        type_name = new_item.name.replace(Color.YELLOW, "")

        return cls(getattr(CustomSpawnEggType, type_name.upper()))

    def to_item(self) -> Item:
        return Item(
            self.egg_type.value[0],
            name=Color.YELLOW + self.egg_type.value[1]
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} egg_type={repr(self.egg_type.name)}>"

    def __str__(self) -> str:
        return str(self.egg_type.name)

    def __eq__(self, other: "DFCustomSpawnEgg") -> bool:
        return type(self) == type(other) and self.egg_type == other.egg_type

    def __ne__(self, other: "DFCustomSpawnEgg") -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash(("DFCustomSpawnEgg", self.egg_type.value))


class DFPotion(DFType):
    """
    Used for potion effects in potion-effect-related actions.

    Parameters\u200b
    --------------

        effect : :class:`PotionEffect`
            The PotionEffect enum instance that specifies which potion effect this :class:`DFPotion` represents.

        amplifier : :class:`int`
            Represents the strength of the effect. This should vary between -255 and 255.

        duration: Tuple[:class:`int`, :class:`int`]
            Tuple (:class:`int`, :class:`int`). Represents the duration of the effect in the form (min, seconds).



    .. container: comparisons

        .. describe:: a == b, a != b

            Checks if two instances have the same `effect`, `amplifier` and `duration` attributes.

        .. describe:: a > b, a >= b, a < b, a <= b

            Applies the given comparison between the amplifiers of the two potions.


    .. container: operations


        .. describe:: a + b, a - b, a * b, a ** b, a / b, a // b, a % b

            Applies the given operation between the amplifiers of the two potions. **The new potion returned
            will be a copy of the one that comes first** (`a`), **with** :attr:`amplifier` **modified.**

            .. note:
                If `b` is an int/float, its value is used instead. Note that the result is always rounded down
                into an int.

        .. describe:: +a, abs(a), floor(a), ceil(a)

            Returns `a` (self).

        .. describe:: bool(a)

            Returns whether or not the duration is bigger than 00:00 (``duration > (0,0)``).

        .. describe:: hash(a)

            Returns an unique hash representing this potion's effect, amplifier and duration.

    Attributes\u200b
    --------------

        effect : :class:`PotionEffect`
            The PotionEffect enum instance that specifies which potion effect this :class:`DFPotion` represents.

        amplifier : :class:`int`
            Represents the strength of the effect. This should vary between -255 and 255.

        duration: Tuple[:class:`int`, :class:`int`]
            Tuple (:class:`int`, :class:`int`). Represents the duration of the effect in the form (min, seconds).
    """
    __slots__ = ("effect", "amplifier", "duration")

    effect: PotionEffect
    amplifier: int
    duration: typing.Tuple[int, int]

    def __init__(self, effect: PotionEffect, *, amplifier: int = 1, duration: typing.Iterable[int] = (0, 5)):
        """
        Init this :class:`DFPotion`.

        :param effect: The effect that this :class:`DFPotion` represents.
        :param amplifier: An amplifier :class:`int`.
        :param duration: A duration in the form (:class:`int`, :class:`int`). Can be any Iterable with two ints.
        """
        self.effect = PotionEffect(effect)
        self.amplifier = int(amplifier)
        self.duration = typing.cast(typing.Tuple[int, int], tuple(map(int, duration))[:2])

    def set(
        self, effect: PotionEffect = DEFAULT_VAL,
        *, amplifier: int = DEFAULT_VAL, duration: typing.Iterable[int] = DEFAULT_VAL
    ) -> "DFPotion":
        """Set certain attributes of this :class:`DFPotion`. Specify `constants.DEFAULT_VAL` to not change one.

        Parameters
        ----------
        effect : `PotionEffect`
            The new potion effect.
        amplifier : :class:`int`
            The new amplifier.
        duration : Iterable[:class:`int`]
            The new duration.

        Returns
        -------
        :class:`DFPotion`
            self for chaining

        """
        if effect != DEFAULT_VAL:
            self.effect = PotionEffect(effect)

        if amplifier != DEFAULT_VAL:
            self.amplifier = int(amplifier)

        if duration != DEFAULT_VAL:
            self.duration = typing.cast(typing.Tuple[int, int], tuple(map(int, duration))[:2])

        return self

    def as_json_data(self) -> dict:
        """Returns this :class:`DFPotion` as a valid json serializable :class:`dict`.

        Returns
        -------
        :class:`dict`
        """
        return dict(
            id=constants.ITEM_ID_POTION,
            data=dict(
                pot=self.effect.value,
                dur=self.duration[0] * 60 * 20 + self.duration[1] * 20,  # (min; seconds) => ticks
                amp=self.amplifier
            )
        )

    @classmethod
    def from_json_data(cls, data: dict) -> "DFPotion":
        """Obtain variable from pre-existing parsed JSON data.

        Must be of the form (have at least those keys)::

            { "data": { "pot": str, "dur": int, "amp": int } }

        Where ``str`` or ``int`` are the respective types of the values.

        Parameters
        ----------
        data : :class:`dict`
            The parsed JSON :class:`dict`.

        Returns
        -------
        :class:`DFPotion`
            The equivalent :class:`DFPotion` instance.

        Raises
        ------
        :exc:`TypeError`
            If the data is malformed (does not follow the structure detailed above).
        """
        if (
            not isinstance(data, dict)
            # or "id" not in data  # not really required
            or "data" not in data
            or not isinstance(data["data"], dict)
            or "pot" not in data["data"]
            or type(data["data"]["pot"]) != str
            or "dur" not in data["data"]
            or type(data["data"]["pot"]) not in (int, float)
            or "amp" not in data["data"]
            or type(data["data"]["pot"]) not in (int, float)
        ):
            raise TypeError(
                "Malformed DFPotion parsed JSON data! Must be a dict with, at least, a 'data' dict containing"
                "a 'pot' key of type str and 'dur' and 'amp' keys, both of type int."
            )

        in_data = data["data"]

        pot = PotionEffect(in_data["pot"])

        int_given_dur = int(in_data["dur"])
        total_secs = int_given_dur / 20
        minutes = total_secs // 60
        seconds = total_secs % 60
        dur = (minutes, seconds)

        amp = int(in_data["amp"])

        return cls(pot, dur, amp)

    # def to_item(self) -> Item:
    #     pass  # TODO

    def copy(self) -> "DFPotion":
        """Creates an identical copy of this :class:`DFPotion`.

        Returns
        -------
        :class:`DFPotion`
            Copied :class:`DFPotion` instance.
        """
        return DFPotion(self.effect, amplifier=self.amplifier, duration=self.duration)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} effect={repr(self.effect.value)} amplifier={self.amplifier} \
duration={self.duration[0]}:{self.duration[1]}>"

    def __str__(self) -> str:
        return str(self.effect.value)

    def __hash__(self):
        return hash((self.effect.value, self.amplifier, self.duration))

    def __bool__(self) -> bool:
        return self.duration > (0, 0)

    def __eq__(self, other: "DFPotion") -> bool:
        return type(self) == type(other) and self.effect == other.effect and self.amplifier == other.amplifier \
            and self.duration == other.duration

    def __ne__(self, other: "DFPotion") -> bool:
        return not self.__eq__(other)

    def __gt__(self, other: "DFPotion") -> bool:
        if type(self) != type(other) and type(other) not in (int, float):
            return NotImplemented

        if not type(self) == type(other) and not self.effect == other.effect:
            raise TypeError(f"DFPotion must be compared with another DFPotion of same effect.")

        return self.amplifier > other.amplifier

    def __ge__(self, other: "DFPotion") -> bool:
        if type(self) != type(other) and type(other) not in (int, float):
            return NotImplemented

        if not type(self) == type(other) and not self.effect == other.effect:
            raise TypeError(f"DFPotion must be compared with another DFPotion of same effect.")

        return self.amplifier >= other.amplifier

    def __lt__(self, other: "DFPotion") -> bool:
        if type(self) != type(other) and type(other) not in (int, float):
            return NotImplemented

        if not type(self) == type(other) and not self.effect == other.effect:
            raise TypeError(f"DFPotion must be compared with another DFPotion of same effect.")

        return self.amplifier < other.amplifier

    def __le__(self, other: "DFPotion") -> bool:
        if type(self) != type(other) and type(other) not in (int, float):
            return NotImplemented

        if not type(self) == type(other) and not self.effect == other.effect:
            raise TypeError(f"DFPotion must be compared with another DFPotion of same effect.")

        return self.amplifier <= other.amplifier

    def __add__(self, other: typing.Union["DFPotion", AnyNumber]) -> "DFPotion":
        if type(self) != type(other) and type(other) not in (int, float):
            return NotImplemented

        if type(self) == type(other) and not self.effect == other.effect:
            raise TypeError(f"DFPotion must be added with another DFPotion of same effect, or with an int/float.")

        copy = self.copy()
        copy.amplifier += other.amplifier if isinstance(other, type(self)) else other
        copy.amplifier = int(copy.amplifier)
        return copy

    def __radd__(self, other: typing.Union["DFPotion", AnyNumber]) -> "DFPotion":
        return self.__add__(other)

    def __mul__(self, other: typing.Union["DFPotion", AnyNumber]) -> "DFPotion":
        if type(self) != type(other) and type(other) not in (int, float):
            return NotImplemented

        if type(self) == type(other) and not self.effect == other.effect:
            raise TypeError(f"DFPotion must be multiplied with another DFPotion of same effect, or with an int/float.")

        copy = self.copy()
        copy.amplifier *= other.amplifier if isinstance(other, type(self)) else other
        copy.amplifier = int(copy.amplifier)
        return copy

    def __rmul__(self, other: typing.Union["DFPotion", AnyNumber]) -> "DFPotion":
        return self.__mul__(other)

    def __sub__(self, other: typing.Union["DFPotion", AnyNumber]) -> "DFPotion":
        if type(self) != type(other) and type(other) not in (int, float):
            return NotImplemented

        if type(self) == type(other) and not self.effect == other.effect:
            raise TypeError(f"DFPotion must be subtracted from another DFPotion of same effect, or from an int/float.")

        copy = self.copy()
        copy.amplifier -= other.amplifier if isinstance(other, type(self)) else other
        copy.amplifier = int(copy.amplifier)
        return copy

    def __pow__(self, other: typing.Union["DFPotion", AnyNumber], modulo=None) -> "DFPotion":
        if type(self) != type(other) and type(other) not in (int, float):
            return NotImplemented

        if type(self) == type(other) and not self.effect == other.effect:
            raise TypeError(
                f"DFPotion must be taken to the power of another DFPotion of same effect, or of an int/float."
            )

        copy = self.copy()
        copy.amplifier = int(pow(
            copy.amplifier, other.amplifier if isinstance(other, type(self)) else other,
            modulo
        ))
        return copy

    def __truediv__(self, other: typing.Union["DFPotion", AnyNumber]) -> "DFPotion":
        if type(self) != type(other) and type(other) not in (int, float):
            return NotImplemented

        if type(self) == type(other) and not self.effect == other.effect:
            raise TypeError(f"DFPotion must be subtracted from another DFPotion of same effect, or from an int/float.")

        copy = self.copy()
        copy.amplifier /= other.amplifier if isinstance(other, type(self)) else other
        copy.amplifier = int(copy.amplifier)
        return copy

    def __floordiv__(self, other: typing.Union["DFPotion", AnyNumber]) -> "DFPotion":
        if type(self) != type(other) and type(other) not in (int, float):
            return NotImplemented

        if type(self) == type(other) and not self.effect == other.effect:
            raise TypeError(f"DFPotion must be subtracted from another DFPotion of same effect, or from an int/float.")

        copy = self.copy()
        copy.amplifier //= other.amplifier if isinstance(other, type(self)) else other
        copy.amplifier = int(copy.amplifier)
        return copy

    def __mod__(self, other: typing.Union["DFPotion", AnyNumber]) -> "DFPotion":
        if type(self) != type(other) and type(other) not in (int, float):
            return NotImplemented

        if type(self) == type(other) and not self.effect == other.effect:
            raise TypeError(f"DFPotion must be subtracted from another DFPotion of same effect, or from an int/float.")

        copy = self.copy()
        copy.amplifier %= other.amplifier if isinstance(other, type(self)) else other
        copy.amplifier = int(copy.amplifier)
        return copy

    def __ceil__(self):
        return self

    def __floor__(self):
        return self

    def __pos__(self):
        return self

    def __abs__(self):
        return self


_classes = (Item, DFText, DFNumber, DFLocation, DFSound, DFParticle, DFCustomSpawnEgg, DFPotion)

DFTyping = typing.Union[
    Item, DFText, DFNumber, DFLocation, DFSound, DFParticle, DFCustomSpawnEgg, DFPotion, "DFGameValue", "DFVariable"
]

remove_u200b_from_doc(_classes)
