"""
Classes forming major DF-related collections.
"""
import typing
import collections
from .. import constants, errors
from .dataclass import Tag
from .abc import DFType, JSONData
from .mc_types import DFTyping
from ..utils import remove_u200b_from_doc


__all__ = ("Arguments", "ItemCollection")


class Arguments:
    """A container for arguments. In general, only holds the "items" attribute. This class is used in case any other
    properties are added in the future.

    Parameters\u200b
    ----------
    items : Optional[Union[:class:`ItemCollection`, :class:`Arguments`, Iterable[Union[:class:`DFType`, \
    :class:`JSONData`]]]], optional
        The items held by this :class:`Arguments` instance.

    tags : Optional[List[:class:`~py2df.classes.dataclass.Tag`]], optional
        Optionally, tags to be added at the very end of items. **Be aware that this will override the last `n` items
        of the item collection** (where `n` is the length of the list given for the ``tags`` parameter).

    Attributes
    ----------\u200b
        items : :class:`ItemCollection`
            The :class:`ItemCollection` instance held by this :class:`Arguments` instance.
    """
    items: "ItemCollection"

    def __init__(
        self, items: typing.Optional[
            typing.Union["ItemCollection", "Arguments", typing.Iterable["OAcceptableItem"]]
        ] = None,
        *, tags: typing.Optional[typing.Iterable[Tag]] = None
    ):
        """
        Initialize :class:`Arguments` .
        
        Parameters
        ----------
        items : Optional[Union[:class:`ItemCollection`, :class:`Arguments`, Iterable[Union[:class:`DFType`, \
        :class:`JSONData`]]]], optional
            The items held by this :class:`Arguments` instance.
            
        tags : Optional[Iterable[:class:`~py2df.classes.dataclass.Tag`]], optional
            Optionally, tags to be added at the very end of items. **Be aware that this will override the last `n` items
            of the item collection** (where `n` is the length of the list given for the ``tags`` parameter).
        """
        if isinstance(items, Arguments):
            self.items = items.items
        else:
            self.items = ItemCollection(items) if items else ItemCollection()

        if tags:  # let's add them to the end of the item collection.
            l_tags = list(tags)
            n_tags = len(l_tags)
            max_len = self.items.max_len
            if n_tags > max_len:
                raise errors.LimitReachedError(f"Can not assign {n_tags} tags to {max_len} items.")
            
            start_pos = max_len - n_tags
            self.items.data[start_pos:] = l_tags

    def as_json_data(self) -> dict:
        return dict(items=self.items.as_json_data() if self.items else dict())

    def __repr__(self) -> str:
        start_str = "<Arguments"
        if self.items:
            start_str += " items=" + repr(self.items)

        start_str += ">"
        return start_str

    def __str__(self) -> str:
        return "<Arguments>"


AcceptableItem = typing.Union[DFTyping, DFType, JSONData]  # for better code linting
OAcceptableItem = typing.Optional[AcceptableItem]


class ItemCollection(collections.UserList):  # [DFType]
    """A container for items or other DF types (text variables, number variables...)
    
    Subclasses `collections.UserList`. Supports, as a consequence, most list operations. Do note that it does not allow
    changing the actual size of the list - it's always at the max length, with empty slots of items filled with `None`.
    However, `len()` returns the amount of FILLED slots (amount of items). Also, attempting to `del` or `remove()` will
    only turn the item into an empty slot (None).
    
    Also, `append()` will add to the empty slot with lowest index, erroring if there are not any. `extend()` will
    execute in a similar condition to `append()` for every element in the iterable (i.e., will append every element
    over empty slots until there are None, when it errors).

    The error for limit-related issues is always an instance of :exc:`~py2df.errors.LimitReachedError`.

    Parameters
    ----------\u200b
    data : Optional[Union[Iterable[Union[:class:`~py2df.classes.abc.DFType`, :class:`~py2df.classes.abc.JSONData`]]\
, Union[:class:`~py2df.classes.abc.DFType`, :class:`~py2df.classes.abc.JSONData`]]]
        An iterable of items (:class:`list`, :class:`ItemCollection`, etc.) or a single
        :class:`~py2df.classes.mc_types.Item`/DFType to be used with the `items` arg.

    items : Optional[Union[:class:`~py2df.classes.abc.DFType`, :class:`~py2df.classes.abc.JSONData`]]
        Any other items to add. If `data` is an iterable, this is not considered.

    max_len : :class:`int`
        The maximum length of this collection, defaults to 27 items (small chest).
    
    Attributes
    -------------\u200b
        data : List[:class:`~py2df.classes.abc.DFType`]
            The internal item list; this should not be modified by the user.
        
        max_len : :class:`int`
            Maximum length of the item collection, defaults to 27 (small chest).

    """
    __slots__ = ("max_len",)

    max_len: int

    def __init__(
        self, data: typing.Optional[
            typing.Union[typing.Iterable[AcceptableItem], AcceptableItem]
        ] = constants.DEFAULT_VAL,
        *items: OAcceptableItem,  # any other items/empty slots
        max_len: typing.Optional[int] = constants.DEFAULT_ITEM_COLLECTION_MAX_LEN
    ):
        """
        Initializes an item collection.

        Parameters
        ----------
        data : Optional[Union[Iterable[Union[:class:`~py2df.classes.abc.DFType`, :class:`~py2df.classes.abc.JSONData`]]\
, Union[:class:`~py2df.classes.abc.DFType`, :class:`~py2df.classes.abc.JSONData`]]]
            An iterable of items (:class:`list`, :class:`ItemCollection`, etc.) or a single
            :class:`~py2df.classes.mc_types.Item`/DFType to be used with the `items` arg.

        items : Optional[Union[:class:`~py2df.classes.abc.DFType`, :class:`~py2df.classes.abc.JSONData`]]
            Any other items to add. If `data` is an iterable, this is not considered.

        max_len : :class:`int`
            The maximum length of this collection, defaults to 27 items (small chest).
        """
        super().__init__()
        self.max_len: int = max_len or constants.DEFAULT_ITEM_COLLECTION_MAX_LEN

        if data is not constants.DEFAULT_VAL:  # if something was given...
            if isinstance(data, collections.abc.Iterable):
                if any(not isinstance(it, JSONData) and it is not None for it in data):
                    raise TypeError("There is a non-Item/DFType/None object within the given `data` arg.")
                
                self.data = list(data)
            else:
                if not isinstance(data, JSONData):
                    raise TypeError("`data` arg passed is not an Iterable nor an Item/DFType.")
                
                if any(not isinstance(it, JSONData) and it is not None for it in items):
                    raise TypeError("There is a non-Item/DFType/None object within the given `items` arg.")
                
                self.data = [data, *items]
            
            length_given = len(self.data)
            
            if length_given > max_len:  # bigger than limit
                raise errors.LimitReachedError(
                    f"Collection items given form a list bigger than max length ({max_len} items for this instance)."
                )
            
            if length_given < max_len:
                self.data.extend([None] * (max_len - length_given))  # fill out the missing empty slots.
        else:
            self.data: typing.List[typing.Optional[JSONData]] = [None] * max_len

    def as_json_data(self) -> typing.List[dict]:
        """Convert this to a JSON-exportable list of dicts. (For internal use.)"""
        gen_list: typing.List[dict] = [
            dict(
                item=item.as_json_data(),
                slot=slot                 # We have to filter the enumeration in order to keep the slot indexes.
            ) for slot, item in filter(lambda tup: tup[1] is not None, enumerate(self.data))
        ]

        return gen_list

    def append(self, val: AcceptableItem) -> None:
        """Appends an :class:`~py2df.classes.mc_types.Item`/DFType to the first empty slot available
        (smallest None index).

        Parameters
        ----------
        val : Union[:class:`~py2df.classes.abc.DFType`, :class:`~py2df.classes.abc.JSONData`]
            The item/DFType to append.

        Returns
        -------
        ``None``
            ``None``

        Raises
        ------
        :exc:`TypeError`
            If there was an attempt to add `None` or non-`:class:`~py2df.classes.mc_types.Item`` /
            :class:`~py2df.classes.abc.DFType` .
        :exc:`LimitReachedError`
            If there is no empty slot where to append the :class:`~py2df.classes.mc_types.Item`/DFType to.

        """
        if not isinstance(val, DFType):
            raise TypeError("Cannot append non-Item/DFType to ItemCollection.")

        first_available_slot = self.data.index(None)
        if first_available_slot == -1:
            raise errors.LimitReachedError("Cannot append to this item collection: there are no empty slots left.")

        self[first_available_slot] = typing.cast(DFType, val)

    def remove(self, x: AcceptableItem) -> None:
        """Removes an :class:`~py2df.classes.mc_types.Item`/DFType, setting it to None.

        Parameters
        ----------
        x : DFType
            :class:`~py2df.classes.mc_types.Item`/DFType to remove.

        Returns
        -------
        None
            None

        """
        if x is None:
            raise TypeError("Cannot remove None (empty slot) from ItemCollection.")
            
        index_at = self.data.index(x)
        if index_at == -1:
            raise ValueError("ItemCollection.remove(x): Item/DFType not in collection.")

        super().__delitem__(index_at)  # remove data
        super().insert(index_at, None)

    def insert(self, i: int, other: OAcceptableItem) -> None:
        """
        Inserts an Item somewhere in the list.

        Parameters
        ----------
        i : :class:`int`
            Index to insert at.

        other : :class:`~py2df.classes.abc.DFType`
            Item to insert.

        Returns
        -------
        None
            None

        Warnings
        --------
        Whatever is at the last slot is removed.
        """
        super().insert(i, other)
        super().__delitem__(-1)

    def clear(self) -> None:
        """Replaces the entire item collection with empty slots."""
        old_len = len(self.data)
        super().clear()  # clears data
        self.data = [None] * old_len  # sets it all to None

    def extend(self, other: typing.Iterable[AcceptableItem]) -> None:
        """Appends multiple items by replacing empty slots.

        Parameters
        ----------
        other : Iterable[:class:`~py2df.classes.abc.DFType`]
            Iterable of :class:`~py2df.classes.mc_types.Item`/:class:`~py2df.classes.abc.DFType`.

        Returns
        -------
        None
            None
        """
        empty_slots = list(map(lambda t: t[0], filter(lambda tup: tup[1] is None, enumerate(self.data))))
        if len(empty_slots) < 1:
            raise errors.LimitReachedError("Cannot extend this item collection: there are no empty slots left.")

        empty_slots.append(None)  # so we can detect if the max length has been surpassed, otherwise zip just stops.

        for item, slot in zip(other, empty_slots):
            if not isinstance(item, JSONData):
                raise TypeError("Iterable to extend with contains non-Item/DFType.")

            if slot is None:
                raise errors.LimitReachedError("Cannot extend this item collection: there are no empty slots left.")

            super().__setitem__(slot, item)

    def __repr__(self) -> str:
        return "<{0} len={1} [{2}]>".format(
            self.__class__.__name__, len(self), ", ".join(el.__repr__() for el in self.data)
        )

    def __len__(self) -> int:
        """Amount of non-None items in the collection."""
        return len(list(filter(None, self.data)))

    @typing.overload
    def __getitem__(self, ii: slice) -> typing.List[OAcceptableItem]: ...

    @typing.overload
    def __getitem__(self, ii: int) -> OAcceptableItem: ...

    def __getitem__(
        self, item: typing.Union[int, slice]
    ) -> typing.Union[OAcceptableItem, typing.Iterable[OAcceptableItem]]:
        """
        Get an item at an index. Returns ``None`` if there is no item.

        Parameters
        ----------
        ii : Union[:class:`int`, :class:`slice`]
            The index(es) of the desired item(s).

        Returns
        -------
        Optional[Union[:class:`~py2df.classes.abc.DFType`, :class:`~py2df.classes.abc.JSONData`]]
            Returns the appropriate element, if any, otherwise None.
        """
        ii = item.stop if type(item) == slice else item
        if (ii - 1) > self.max_len:
            raise IndexError(f"Item collection index out of range (max for this instance: {self.max_len - 1}).")

        if type(item) == slice:
            return self.data[item]
        else:
            return super().__getitem__(item)

    def __delitem__(self, ii: int) -> None:
        """Delete an item from an index, turning it into an empty slot (None)."""

        if (ii - 1) > self.max_len:
            raise IndexError(
                f"Item collection assignment index out of range (max for this instance: {self.max_len - 1})."
            )

        super().__delitem__(ii)
        self.data.insert(ii, None)
    
    @typing.overload
    def __setitem__(self, item: int, val: OAcceptableItem) -> None: ...
    
    @typing.overload
    def __setitem__(self, item: slice, val: typing.Iterable[OAcceptableItem]) -> None: ...
    
    def __setitem__(
        self, item: typing.Union[int, slice], val: typing.Union[
            OAcceptableItem,
            typing.Iterable[OAcceptableItem]
        ]
    ) -> None:
        """
        Set an item somewhere in the :class:`~py2df.classes.mc_types.Item` Collection/grid.

        :param item: Index to set, or :class:`slice`
        :param val: :class:`~py2df.classes.mc_types.Item`/DF type to set, or an Iterable thereof (if ``item`` is slice)
        """
        ii = item.stop if type(item) == slice else item
        if (ii - 1) > self.max_len:
            raise IndexError(
                f"Item collection assignment index out of range (max for this instance: {self.max_len - 1})."
            )

        if val is not None and not isinstance(val, collections.Iterable) and not isinstance(val, JSONData):
            raise TypeError("Attempt to set non-Item/DF type and non-None value to an ItemCollection instance.")

        super().__setitem__(item, val)

    def __delslice__(self, i, j) -> None:
        the_slice = self.data[i:j]
        self.data[i:j] = [None] * len(the_slice)  # replace with None


_col_classes = (Arguments, ItemCollection)
remove_u200b_from_doc(_col_classes)
