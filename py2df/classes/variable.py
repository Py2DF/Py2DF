import abc
import collections
import re
import typing
import json

from collections import deque

from .. import constants
from ..constants import SMALL_CHEST_SIZE
from .abc import DFType
from .mc_types import DFText
from .collections import Arguments
from .dataclass import Tag
from ..utils import remove_u200b_from_doc, flatten, TrueLiteral, FalseLiteral, all_attr_eq
from ..enums import SetVarType, VariableScope, BlockType, IfVariableType, PlayerTarget, EntityTarget, GameValueType, \
    Target, ItemEqComparisonMode, IfVVarType
from ..constants import ITEM_ID_DYNAMIC_VAR, DEFAULT_VAL
from ..errors import LimitReachedError

if typing.TYPE_CHECKING:
    from .. import typings as _tp
    from ..codeblocks.ifs import IfVariable, IfVariable as _IfVariable
    from ..codeblocks.utilityblock import SetVar  # lazy import in Var init
    from ..typings import (
        Param, Numeric, Locatable, Textable, Listable, ItemParam, ParticleParam, SoundParam, Potionable
    )


_VarOpEl = typing.Union["Numeric", "_Var", "Locatable", "VarOp"]

op_to_expr = {
    SetVarType.SET_TO: "=",
    SetVarType.SET_TO_ADDITION: "+",
    SetVarType.SET_TO_SUBTRACTION: "-",
    SetVarType.SET_TO_QUOTIENT: "/",
    SetVarType.SET_TO_MOD: "%",
    SetVarType.SET_TO_POWER: "**",
    SetVarType.SET_TO_PRODUCT: "*"
}


def _heavy_imports() -> bool:
    global _SetVar, _tp, _IfVariable
    try:
        _a = _SetVar
        _b = _tp
        _c = _IfVariable

        return False

    except NameError:
        from ..codeblocks.utilityblock import SetVar  # lazy import to avoid cyclic imports
        from .. import typings  # ^
        from ..codeblocks.ifs import IfVariable  # ^

        _SetVar = SetVar
        _tp = typings
        _IfVariable = IfVariable

        return True


class VarOp:
    """Represents an operation between 2+ variables. Note that they are applied within DiamondFire, using a SetVar
    block. Use this as the parameter of :meth:`DFVariable.set`.

    Parameters
    ----------\u200b
    setv_type : :class:`~.SetVarType`
        The type of :class:`~.SetVar` that this operation will produce.

    vars : Union[Union[:attr:`~.Numeric`, :attr:`~.Locatable`, :class:`VarOp`], \
Iterable[:attr:`~.Numeric`, :attr:`~.Locatable`, :class:`VarOp`]]
        Variables that participate in this operation. One of Numeric, Locatable or VarOp. (Any iterables will be
        flattened.)

        .. note::

            The variables can only be a Locatable (i.e., a Location) alongside with Numeric if the operation in
            question is **addition** (+) or **subtraction** (-); otherwise, it can only be a param of Numeric type.

    tags : Iterable[:class:`~.Tag`], optional
        All tags used in this operation's set var block (if any). At the moment, this is only used for division.
        Defaults to empty tuple (no tags).

    check_type : Optional[Union[:attr:`~.Numeric` object, :attr:`~.Locatable` object]], optional
        The type of this variable, if valid. Defaults to ``None`` (Numeric is checked for instead).

    Warnings
    --------
    Instantiation of this class is only done internally; to obtain an instance, realize operations between variables.


    .. container:: operations

        .. describe:: a + b, a - b, a * b, a ** b, a / b, a // b, a % b

            Adds `b`, of :attr:`~.Numeric` type, to the list of variables that partake in this operation.

            .. warning::

                **You cannot mix operations.** For example, ``a + b - c * d ** e`` will raise. Stick to only one
                at once, and have one :meth:`~DFVariable.set` call for each kind. (There is only one Set Var for each
                kind.)
                (However, operations with multiple variables, up to 27, work: ``a + b + c + ... + z``)

                If there is an attempt to mix operations, a :exc:`TypeError` is raised.

                Similarly, if there is an attempt to have an operation with more than 26 variables (chest size is
                up to 27 items, while 1 slot is the variable being set), then a :exc:`~.LimitReachedError` is raised
                instead.

            .. note::
                If the operation is addition or subtraction, `b` can also be a :attr:`~.Locatable` parameter (represent
                a location), besides Numeric.

    Attributes
    ----------\u200b
    setv_type : :class:`~.SetVarType`
        The type of :class:`~.SetVar` that this operation will produce.

    vars : Deque[Union[:attr:`~.Numeric`, :attr:`~.Locatable`]]
        Variables that participate in this operation.

    tags : List[:class:`~.Tag`]
        Any tags used in this operation's set var block.
    """
    __slots__ = ("setv_type", "vars", "tags")

    setv_type: SetVarType
    vars: typing.Deque[_VarOpEl]
    tags: typing.List[Tag]

    def __init__(
        self, setv_type: SetVarType, *vars: typing.Union[_VarOpEl, typing.Iterable[_VarOpEl]],
        tags: typing.Iterable[Tag] = tuple(), check_type: typing.Optional[typing.Any] = None
    ):
        _heavy_imports()
        self.setv_type = SetVarType(setv_type)

        self.tags = list(tags)

        valid_types = check_type if check_type and check_type in (_tp.Numeric, _tp.Locatable) else (
            typing.Union[_tp.Numeric, _tp.Locatable] if setv_type in (
                SetVarType.SET_TO_ADDITION, SetVarType.SET_TO_SUBTRACTION
            ) else _tp.Numeric
        )

        if any(map(lambda v_op: v_op.setv_type != setv_type, filter(lambda o: isinstance(o, VarOp), vars))):
            raise TypeError(
                "Cannot have different types of operations between variables at the same time; each kind "
                "should be evaluated in its own .set()."
            )  # different kind of operation found.

        self.vars = deque(
            _tp.p_check(
                o, valid_types, f"vars[{i}]"
            ) for i, o in enumerate(flatten(vars, except_iterables=[str], max_depth=2))
        )

    @typing.overload
    def _add_var(
        self, var: typing.Iterable[_VarOpEl], op: SetVarType,
        *, append_left: bool = False, is_rsub: bool = False, allow_other_iters: TrueLiteral,
        error_incompatible: bool = False, modify_self: bool = False
    ) -> typing.List["VarOp"]: ...

    @typing.overload
    def _add_var(
        self, var: _VarOpEl, op: SetVarType,
        *, append_left: bool = False, is_rsub: bool = False, allow_other_iters: bool = False,
        error_incompatible: bool = False, modify_self: bool = False
    ) -> "VarOp": ...

    def _add_var(
        self, var: typing.Union[_VarOpEl, typing.Iterable[_VarOpEl]], op: SetVarType,
        *, append_left: bool = False, is_rsub: bool = False, allow_other_iters: bool = False,
        error_incompatible: bool = False, modify_self: bool = False
    ) -> typing.Union["VarOp", typing.List["VarOp"]]:
        """Adds a variable to participate in this operation.

        Parameters
        ----------
        var : Union[:class:`DFVariable`, :class:`VarOp`, :attr:`~.Numeric`]
            The variable(s) to add.

        op : :class:`~.SetVarType`
            The operation that was done, in order to check for mismatches/mixed ops.

        append_left : :class:`bool`, optional
            If the variable(s) should, instead, be appended to the left. Used in __rsub__. Defaults to ``False``.

        is_rsub : :class:`bool`, optional
            If this is an __rsub__ operation, for more specific type checks. Defaults to ``False``.

        allow_other_iters : :class:`bool`, optional
            If iterables other than VarOp should be accepted. Defaults to ``False``.

        error_incompatible : :class:`bool`, optional
            If `self` should be modified instead of generating a new VarOp. Defaults to ``False``.

        Returns
        -------
        ``None``
            ``None``

        Raises
        ------
        :exc:`~.LimitReachedError`
            If there was an attempt to execute an operation between more variables than a chest can contain.

        :exc:`~.TypeError`
            Either if there was an attempt to mix operations (e.g. A + B * C) or if ``error_incompatible=True`` and
            an invalid Numeric/Locatable was given.
        """
        if (
            not isinstance(var, (DFVariable, VarOp))  # not a variable; or
                and not _tp.p_bool_check(var, _tp.Numeric)  # not a number
                and (
                    not _tp.p_bool_check(var, _tp.Locatable)  # + and - can also accept locations
                    if op in (SetVarType.SET_TO_ADDITION, SetVarType.SET_TO_SUBTRACTION) else True
                )
        ):
            if allow_other_iters and isinstance(var, collections.Iterable):
                return [
                    self._add_var(v, op, append_left=append_left, is_rsub=is_rsub, allow_other_iters=True)
                    for v in var
                ]
            else:
                if error_incompatible:
                    raise TypeError(f"Cannot realize variable operation with '{type(var)}'")
                return NotImplemented

        own_type = self.setv_type
        valid_rsub_ops = (SetVarType.SET_TO_ADDITION, SetVarType.SET_TO_SUBTRACTION)
        inverted_own_type = SetVarType.SET_TO_ADDITION if own_type == SetVarType.SET_TO_SUBTRACTION \
            else SetVarType.SET_TO_SUBTRACTION

        if (
            (  # if this is a __rsub__ and the current op is not an addition/subtraction...
                is_rsub and (
                    own_type not in valid_rsub_ops
                    or isinstance(var, VarOp) and (
                        var.setv_type not in valid_rsub_ops
                        or var.setv_type != inverted_own_type
                    )
                )
            )
            or not is_rsub and (  # or it isn't and we are trying to mix operation types...
                op != own_type
                or (
                    isinstance(var, VarOp)
                    and (
                        var.setv_type != own_type
                        or var.setv_type != op
                    )
                )
            )
        ):
            raise TypeError(
                "Cannot have different types of operations between variables at the same time; each kind "
                "should be evaluated in its own .set()."
            )

        vars = self.vars if modify_self else self.vars.copy()

        if len(vars) >= (SMALL_CHEST_SIZE - 1):  # There's also the variable that is going to be set, so -1
            raise LimitReachedError(f"Cannot execute an operation between more than {SMALL_CHEST_SIZE - 1} vars.")

        if isinstance(var, collections.Iterable):
            if append_left:
                vars.extendleft(var)
            else:
                vars.extend(var)
        else:
            if append_left:
                vars.appendleft(var)
            else:
                vars.append(var)

        return self if modify_self else VarOp(inverted_own_type if is_rsub else self.setv_type, vars, tags=self.tags)

    def __iter__(self):
        for x in self.vars:
            yield x

    def __repr__(self):
        return f"<{self.__class__.__name__}: {f' {op_to_expr[self.setv_type]} '.join(map(repr, self.vars))}>"

    def __str__(self):
        return f" {op_to_expr[self.setv_type]} ".join(map(str, self.vars))

    def __add__(self, other: typing.Union["Numeric", "Locatable", "VarOp"]) -> "VarOp":
        return self._add_var(other, SetVarType.SET_TO_ADDITION)

    def __radd__(self, other: typing.Union["Numeric", "Locatable", "VarOp"]) -> "VarOp":
        return self.__add__(other)

    def __sub__(self, other: typing.Union["Numeric", "Locatable", "VarOp"]) -> "VarOp":
        return self._add_var(other, SetVarType.SET_TO_SUBTRACTION)

    def __rsub__(self, other: typing.Union["Numeric", "Locatable", "VarOp"]) -> "VarOp":
        return self._add_var(other, SetVarType.SET_TO_SUBTRACTION, append_left=True, is_rsub=True)

    def __mul__(self, other: typing.Union["Numeric", "VarOp"]) -> "VarOp":
        return self._add_var(other, SetVarType.SET_TO_PRODUCT)

    def __rmul__(self, other: typing.Union["Numeric", "VarOp"]) -> "VarOp":
        return self.__mul__(other)

    def __pow__(self, power: typing.Union["Numeric", "VarOp"], modulo=None) -> "VarOp":
        if len(self.vars) >= 2:
            raise LimitReachedError("Cannot realize operation '**' between more than two variables.")

        return self._add_var(power, SetVarType.SET_TO_POWER)

    def __mod__(self, other: typing.Union["Numeric", "VarOp"]) -> "VarOp":
        if len(self.vars) >= 2:
            raise LimitReachedError("Cannot realize operation '%' between more than two variables.")

        return self._add_var(other, SetVarType.SET_TO_MOD)

    def __truediv__(self, other: typing.Union["Numeric", "VarOp"]) -> "VarOp":
        return self._add_var(other, SetVarType.SET_TO_QUOTIENT)
        # [Tag("Divison Mode", option="Default", action=SetVarType.SET_TO_QUOTIENT, block=BlockType.SET_VAR)]

    def __floordiv__(self, other: typing.Union["Numeric", "VarOp"]) -> "VarOp":
        return self._add_var(other, SetVarType.SET_TO_QUOTIENT)
        # [Tag("Divison Mode", option="Round to Integer", action=SetVarType.SET_TO_QUOTIENT, block=BlockType.SET_VAR)]


class VarOperable(metaclass=abc.ABCMeta):
    """An ABC for classes that support variable-related operations (i.e., :class:`DFGameValue` and :class:`DFVariable`).

    This class is used to hold operations and functions that are common to :class:`DFGameValue` and :class:`DFVariable`.
    Note that each implement their own operations as well; see the documentation for each.

    Implements all the If Variable humanized methods.

    .. container:: comparisons

        .. describe:: a == b, a != b

            Returns the equivalent :class:`~.IfVariable` block for equals/not equals. Has two uses:

            1. **Is used to compare the variables with an If Var.** Note that equaling to an iterable means checking \
if the variable is equal to at least one of its elements. Example usage::

                with var_a == var_b:
                    # code that is only executed in DiamondFire if 'var_a' and 'var_b' are equal in value.

                with var_c != var_d:
                    # code that is only executed in DiamondFire if 'var_c' and 'var_d' are different in value.

                with var_e == (var_f, var_g, var_i):
                    # code that is only executed in DiamondFire if 'var_e' is equal to one of 'var_f', 'var_g' or \
'var_i'.

            2. **Is used to compare, IN PYTHON, the variables' attributes** (by calling :func:`bool` on the \
            generated IfVariable block). Note that :class:`DFGameValue` and :class:`DFVariable` implement this \
            differently; see their respective documentations.

        .. describe:: a > b, a >= b, a < b, a <= b

            Returns the equivalent :class:`~.IfVariable` block for the given comparison. **Its only usage is as
            a Codeblock** (in a `with`).
            For example::

                with var_a > var_b:
                    # code that is only executed in DiamondFire if 'var_a' is bigger than 'var_b' in value.

                with var_c < var_d:
                    # code that is only executed in DiamondFire if 'var_c' is less than 'var_d' in value.

            .. note::

                Those comparisons are not usable in Python if's; if a :func:`bool` is attempted on the resulting
                IfVariable block, it will always return True. This mechanism is only implemented for ``==`` and ``!=``.

            .. warning::

                Assuming that one of them is a DFVariable, the other has to be a valid :attr:`~.Numeric` parameter.
                Otherwise, a TypeError may be raised (if the given type does not support operations with DFVariable,
                which is likely).

    .. container:: operations

        .. describe:: a + b, a - b, a * b, a ** b, a / b, a // b, a % b

            Creates a :class:`VarOp` instance representing this operation between different variables/variables
            and values/etc.
            It is meant to be given as the parameter for :meth:`DFVariable.set`, which will then place the appropriate
            Set Variable type (setting the variable instance to this operation)

            `a` is the :class:`VarOperable` instance, while `b`, in this case, is the :attr:`~.Numeric` to realize this
            operation with.

            .. note::

                If the operation is addition or subtraction, `b` can also be a :attr:`~.Locatable` parameter (represent
                a location), besides Numeric.

            .. warning::

                **You cannot mix operations.** For example, ``a + b - c * d ** e`` will raise. Stick to only one
                at once, and have one :meth:`DFVariable.set` call for each kind.
                (There is only one Set Var for each kind.)
                (However, operations with multiple variables, up to 27, work: ``a + b + c + ... + z``)

                If there is an attempt to mix operations, a :exc:`TypeError` is raised.

                Similarly, if there is an attempt to have an operation with more than 26 variables (chest size is
                up to 27 items, while 1 slot is the variable being set), then a :exc:`~.LimitReachedError` is raised
                instead.
    """

    def __new__(cls, *args, **kwargs):
        _heavy_imports()
        return object.__new__(cls)

    # region:var_ifs

    def text_contains(self, *texts, ignore_case: bool = False) -> "IfVariable":
        """Checks if this text variable (self must be a valid :attr:`~.Textable`) contains another Textable.
        Note that this is also implemented within :class:`DFText`.

        Also note that, if using :class:`TextVar`, one can simply ``var.contains(*texts)``.

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

        Examples
        --------
        ::

            with var_a.text_contains("Foo", ignore_case=True):
                # ... code to execute in DF if var_a's text contains "Foo", case insensitively ...

            with var_b.text_contains("test", "ok", "no", ignore_case=False):
                # ... code to execute in DF if var_c contains one of "test", "ok" or "no", case sensitively ...
        """
        args = Arguments([
            _tp.p_check(self, _tp.Textable, "self"),
            *[_tp.p_check(text, _tp.Textable, f"texts[{i}]") for i, text in enumerate(texts)]
        ], tags=[
            Tag(
                "Ignore Case", option=str(bool(ignore_case)),
                action=IfVariableType.TEXT_MATCHES, block=BlockType.IF_VAR
            )
        ])

        return _IfVariable(
            action=IfVariableType.CONTAINS,
            args=args,
            append_to_reader=False,
            invert=False
        )

    @typing.overload
    def in_range(
        self, min_val: "Numeric", max_val: "Numeric"
    ) -> "IfVariable":
        ...

    @typing.overload
    def in_range(
        self, min_val: "Locatable", max_val: "Locatable"
    ) -> "IfVariable":
        ...

    def in_range(
        self, min_val: typing.Union["Numeric", "Locatable"], max_val: typing.Union["Numeric", "Locatable"]
    ) -> "IfVariable":
        """Checks if this number var is within 2 other numbers, or if this location var is within the region of 2 other
        locations. Note that this method is also implemented within :class:`~.DFNumber` and :class:`~.DFLocation`.

        Parameters
        ----------
        min_val : Union[:attr:`~.Numeric`, :attr:`~.Locatable`]
            The minimum value for this number, or the first location (one of the two corners of the region to check),
            if this is a Locatable.

        max_val : Union[:attr:`~.Numeric`, :attr:`~.Locatable`]
            The maximum value for this number, or the second location (the other corner, determining that `self` has
            to be a location staying inbetween `min_val` and `max_val`), if this is a Locatable.

        Returns
        -------
        :class:`~.IfVariable`
            The generated IfVariable codeblock for this condition.

        Examples
        --------
        ::

            with var_a.in_range(5, 10):
                # ... code that is only executed in DF if 'var_a' is between 5 and 10 ...

            with var_b.in_range(DFLocation(1, 2, 3), DFLocation(4, 5, 6)):
                # ... code that is only executed in DF if 'var_b' is a location within the two specified locs ...
        """

        args = Arguments(
            [
                _tp.p_check(self, typing.Union[_tp.Numeric, _tp.Locatable], "self"),
                _tp.p_check(min_val, typing.Union[_tp.Numeric, _tp.Locatable], "min_val"),
                _tp.p_check(max_val, typing.Union[_tp.Numeric, _tp.Locatable], "max_val")
            ]
        )

        return _IfVariable(
            action=IfVariableType.IN_RANGE,
            args=args,
            append_to_reader=False,
            invert=False
        )

    def is_near(
        self, center_val: typing.Union["Numeric", "Locatable"], valid_range: "Numeric"
    ) -> "IfVariable":
        """Checks if this :attr:`~.Numeric` is within a certain distance of another number or if
        this :attr:`~.Locatable` is near another location. Note that this method is also implemented
        within :class:`~.DFNumber` and :class:`~.DFLocation`.

        Parameters
        ----------
        center_val : Union[:attr:`~.Numeric`, :attr:`~.Locatable`]
            The value to be compared with `self`.

        valid_range : :attr:`~.Numeric`
            The accepted distance between `self` and `center_val`.

        Returns
        -------
        :class:`~.IfVariable`
            The generated IfVariable codeblock for this condition.

        Examples
        --------
        ::

            with var_a.is_near(var_b, 10):
                # ... code to execute in DF if var_a is at most at a distance of 10 units (or blocks, if locs) from \
var_b ...
        """

        args = Arguments(
            [
                _tp.p_check(self, typing.Union[_tp.Numeric, _tp.Locatable], "self"),
                _tp.p_check(center_val, typing.Union[_tp.Numeric, _tp.Locatable], "center_val"),
                _tp.p_check(valid_range, _tp.Numeric, "valid_range"),
            ]
        )

        return _IfVariable(
            action=IfVariableType.IS_NEAR,
            args=args,
            append_to_reader=False,
            invert=False
        )

    def item_equals(
        self, item: "ItemParam",
        *, mode: ItemEqComparisonMode = ItemEqComparisonMode.EXACTLY_EQUALS
    ) -> "IfVariable":
        """Works the same as Variable = but has a few extra options for item comparison.

        Parameters
        ----------
        item : :attr:`~.ItemParam`
            The item to compare self (which must be a valid :attr:`~.ItemParam` as well) to.

        mode : :class:`~.ItemEqComparisonMode`, optional
            The mode of comparison that will determine the equality between self and
            the given item. (:attr:`~.EXACTLY_EQUAL`, :attr:`~.IGNORE_STACK_SIZE`, 
            :attr:`~.IGNORE_DURABILITY_AND_STACK_SIZE`, :attr:`~.MATERIAL_ONLY) `Defaults to :attr:`~.EXACTLY_EQUAL`.

        Returns
        -------
        :class:`~.IfVariable`
            The generated IfVariable codeblock for this condition.

        Examples
        --------
        ::

            with var_a.item_equals(Item(Material.STONE, name="My Stone"), \
mode=ItemEqComparisonMode.MATERIAL_ONLY):
                # ... code to execute in DF if 'var_a' item has the same material as the given item; in this case, \
Stone ...
        """

        args = Arguments(
            [_tp.p_check(self, _tp.ItemParam, "self"), _tp.p_check(item, _tp.ItemParam, "item")],
            tags=[
                Tag(
                    "Comparison Mode", option=ItemEqComparisonMode(mode),
                    action=IfVariableType.ITEM_EQUALS, block=BlockType.IF_VAR
                )
            ]
        )

        return _IfVariable(
            action=IfVariableType.ITEM_EQUALS,
            args=args,
            append_to_reader=False,
            invert=False
        )

    def has_item_tag(self, *tags: "Textable") -> "IfVariable":
        """Checks if this instance (has to be a valid :attr:`~.ItemParam`) has the given custom item tag(s).
        Note that this method is also implemented in :class:`~.Item`.

        Parameters
        ----------
        tags : :attr:`~.Textable`
            The tags to have their presence within the item (self) checked.

        Returns
        -------
        :class:`~.IfVariable`
            The generated IfVariable codeblock for this condition.

        Examples
        --------
        ::

            with var_a.has_item_tag("SomeTag", "AnotherTag"):
                # ... code to run in DF if 'var_a' item has tags "SomeTag" or "AnotherTag"
        """

        args = Arguments(
            [_tp.p_check(self, _tp.ItemParam, "self")] + [
                _tp.p_check(o, _tp.Textable, f"tags[{i}]") for i, o in enumerate(tags)
            ]
        )

        return _IfVariable(
            action=IfVariableType.ITEM_HAS_TAG,
            args=args,
            append_to_reader=False,
            invert=False
        )

    def list_contains(self, *objs: "Param") -> "IfVariable":
        """Checks if any of a list's contents match the given value. Note that this instance (self)
        must be a valid :attr:`~.Listable` (i.e., the type of the Game Value, or the type of the Variable, if using
        typed var classes).

        Note that, if using :class:`ListVar`, then this is the same as doing simply ``var.contains(obj)``.

        Parameters
        ----------
        objs : :attr:`~.Param`
            The object(s) that will be checked for being inside the list (i.e. if the list contains it/them).

        Returns
        -------
        :class:`~.IfVariable`
            The generated IfVariable codeblock for this condition.

        Examples
        --------
        ::

            with var_a.list_contains("h", 5, DFLocation(1, 2, 3)):
                # ... code that is only executed if var_a contains "h", 5 or a Location of x,y,z equal to 1,2,3 ...
        """

        args = Arguments([
            _tp.p_check(self, _tp.Listable, arg_name="self"),
            *[_tp.p_check(obj, _tp.Param, arg_name=f"objs[{i}]") for i, obj in enumerate(objs)]
        ])

        return _IfVariable(
            action=IfVariableType.LIST_CONTAINS,
            args=args,
            append_to_reader=False,
            invert=False
        )

    def list_value_eq(self, index: "Numeric", value: "Param") -> "IfVariable":
        """Checks if a list's value at an index is equal to a given value. Note that `self` has to be a
        valid :attr:`~.Listable` (i.e. be a valid list).

        Note
        ----
        Using this method shouldn't be necessary; with :class:`ListVar`, using ``var[i] == val``
        (which is much more readable) should produce the same result; the same applies if using a :class:`DFGameValue`,
        which will allow that if the given Game Value Type has a Return Type of `Listable`.

        Parameters
        ----------
        index : :attr:`~.Numeric`
            The index of the list element to compare.

        value : :attr:`~.Param`
            The value to be compared to the element at the given list index.

        Returns
        -------
        :class:`~.IfVariable`
            The generated IfVariable codeblock for this condition.

        Examples
        --------
        ::

            with var_a.list_value_eq(5, "Foo"):
                # ... code that is only executed in DF if the value at index 5 of 'var_a' is equal to "Foo"

            with list_var_a[5] == "Foo":
                # same as above

            with gval_a[5] == "Foo":
                # same as above
        """

        args = Arguments([
            _tp.p_check(self, _tp.Listable, "self"),
            _tp.p_check(index, _tp.Numeric, "index"),
            _tp.p_check(value, _tp.Param, "value")
        ])

        return _IfVariable(
            action=IfVariableType.LIST_VALUE_EQ,
            args=args,
            append_to_reader=False,
            invert=False
        )

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

        Examples
        --------
        Example usage::

            with var_a.text_matches("Foo", ignore_case=True):
                # ... code to execute in DF if var_a's text matches "Foo", case insensitively ...

            with var_b.text_matches(re.compile(r"Ba(?:r|th)", re.IGNORE_CASE)):
                # ... code to execute in DF if var_b's text matches the given regex pattern, case insensitively ...

            with var_c.text_matches("Foo", "Bar", "Baz", ignore_case=False):
                # ... code to execute in DF if var_c matches one of "Foo", "Bar" or "Baz", case sensitively ...
        """
        text_list: typing.List[typing.Union[str, typing.Pattern]] = list(texts)
        for i, text in enumerate(text_list):
            if isinstance(text, re.Pattern):
                regexp = True
                ignore_case = re.IGNORECASE in text.flags if ignore_case == DEFAULT_VAL else ignore_case
                text = text.pattern

            text_list[i] = _tp.p_check(text, _tp.Textable, f"texts[{i}]")

        args = Arguments([
            _tp.p_check(self, _tp.Textable, "self"),
            *text_list
        ], tags=[
            Tag(
                "Ignore Case", option=str(bool(ignore_case)),
                action=IfVariableType.TEXT_MATCHES, block=BlockType.IF_VAR
            ),
            Tag(
                "Regular Expressions", option="Enable" if regexp else "Disable",
                action=IfVariableType.TEXT_MATCHES, block=BlockType.IF_VAR
            )
        ])

        return _IfVariable(
            action=IfVariableType.TEXT_MATCHES,
            args=args,
            append_to_reader=False,
            invert=False
        )

    def is_type(self, v_type: IfVVarType) -> "IfVariable":
        """Checks if a variable is a certain type of variable.

        Parameters
        ----------
        v_type : :class:`~.IfVVarType`
            The type of variable that `self` is expected to be.

        Returns
        -------
        :class:`~.IfVariable`
            The generated IfVariable codeblock for this condition.

        Examples
        --------
        ::

            with var_a.is_type(IfVVarType.NUMBER):
                # ... code that is only executed in DF if var_a is a Number in DiamondFire ...
        """

        args = Arguments(
            [self],
            tags=[Tag(
                "Variable Type", option=IfVVarType(v_type).value,
                action=IfVariableType.VAR_IS_TYPE, block=BlockType.IF_VAR
            )]
        )

        return _IfVariable(
            action=IfVariableType.VAR_IS_TYPE,
            args=args,
            append_to_reader=False,
            invert=False
        )

    # endregion:var_ifs

    # region:var_comparison

    def __eq__(self, other: typing.Union["Param", typing.Iterable["Param"]]) -> "IfVariable":
        if not _tp.p_bool_check(other, _tp.Param) and not isinstance(other, typing.Iterable):
            return NotImplemented

        args: Arguments
        if _tp.p_bool_check(other, _tp.Param):
            args = Arguments([self, _tp.p_check(other, _tp.Param, "other")])
        else:
            args = Arguments([self, *[_tp.p_check(obj, _tp.Param, f"other[{i}]") for i, obj in enumerate(other)]])

        gen_if = _IfVariable(  # allow "with var_a == var_b:"
            action=IfVariableType.EQUALS,
            args=args,
            append_to_reader=False
        )
        gen_if._called_by_var = True  # allow "if var_a == var_b"

        return gen_if

    def __ne__(self, other: typing.Union["Param", typing.Iterable["Param"]]) -> "IfVariable":
        if not _tp.p_bool_check(other, _tp.Param) and not isinstance(other, typing.Iterable):
            return NotImplemented

        args: Arguments
        if _tp.p_bool_check(other, _tp.Param):
            args = Arguments([self, _tp.p_check(other, _tp.Param, "other")])
        else:
            args = Arguments([self, *[_tp.p_check(obj, _tp.Param, f"other[{i}]") for i, obj in enumerate(other)]])

        gen_if = _IfVariable(  # allow "with var_a != var_b:"
            action=IfVariableType.NOT_EQUALS,
            args=args,
            append_to_reader=False
        )
        gen_if._called_by_var = True  # allow "if var_a != var_b"

        return gen_if

    def __gt__(self, other: "Numeric") -> "IfVariable":
        if not _tp.p_bool_check(other, _tp.Numeric, error_on_gameval=True):
            return NotImplemented

        return _IfVariable(
            action=IfVariableType.GREATER_THAN,
            args=Arguments([self, _tp.p_check(other, _tp.Numeric, "other")]),
            append_to_reader=False
        )

    def __ge__(self, other: "Numeric") -> "IfVariable":
        if not _tp.p_bool_check(other, _tp.Numeric, error_on_gameval=True):
            return NotImplemented

        return _IfVariable(
            action=IfVariableType.GREATER_THAN_OR_EQUAL_TO,
            args=Arguments([self, _tp.p_check(other, _tp.Param, "other")]),
            append_to_reader=False
        )

    def __lt__(self, other: "Numeric") -> "IfVariable":
        if not _tp.p_bool_check(other, _tp.Numeric, error_on_gameval=True):
            return NotImplemented

        return _IfVariable(
            action=IfVariableType.LESS_THAN,
            args=Arguments([self, _tp.p_check(other, _tp.Numeric, "other")]),
            append_to_reader=False
        )

    def __le__(self, other: "Numeric") -> "IfVariable":
        if not _tp.p_bool_check(other, _tp.Numeric, error_on_gameval=True):
            return NotImplemented

        return _IfVariable(
            action=IfVariableType.LESS_THAN_OR_EQUAL_TO,
            args=Arguments([self, _tp.p_check(other, _tp.Numeric, "other")]),
            append_to_reader=False
        )

    # endregion:var_comparison

    # region:var_ops

    def __add__(self, other: typing.Union["Numeric", "Locatable", VarOp, "_Var"]):
        check_type = self.check_type \
            if hasattr(self, "check_type") and self.check_type in (_tp.Numeric, _tp.Locatable) \
            else typing.Union[_tp.Numeric, _tp.Locatable]

        if not isinstance(other, (DFVariable, VarOp)) and not _tp.p_bool_check(
            other, check_type, error_on_gameval=True
        ) or not _tp.p_bool_check(self, check_type, error_on_gameval=True):
            return NotImplemented

        return VarOp(SetVarType.SET_TO_ADDITION, self, other, check_type=check_type)

    def __radd__(self, other: typing.Union["Numeric", "Locatable", VarOp, "_Var"]):
        return self.__add__(other)

    def __sub__(self, other: typing.Union["Numeric", "Locatable", VarOp, "_Var"]):
        check_type = self.check_type \
            if hasattr(self, "check_type") and self.check_type in (_tp.Numeric, _tp.Locatable) \
            else typing.Union[_tp.Numeric, _tp.Locatable]

        if not isinstance(other, (DFVariable, VarOp)) and not _tp.p_bool_check(
            other, check_type, error_on_gameval=True
        ) or not _tp.p_bool_check(self, check_type, error_on_gameval=True):
            return NotImplemented

        return VarOp(SetVarType.SET_TO_SUBTRACTION, self, other, check_type=check_type)

    def __rsub__(self, other: typing.Union["Numeric", "Locatable", VarOp, "_Var"]):
        check_type = self.check_type \
            if hasattr(self, "check_type") and self.check_type in (_tp.Numeric, _tp.Locatable) \
            else typing.Union[_tp.Numeric, _tp.Locatable]

        if not isinstance(other, (DFVariable, VarOp)) and not _tp.p_bool_check(
            other, check_type, error_on_gameval=True
        ) or not _tp.p_bool_check(self, check_type, error_on_gameval=True):
            return NotImplemented

        res = VarOp(SetVarType.SET_TO_SUBTRACTION, self, check_type=check_type)
        res._add_var(
            other, SetVarType.SET_TO_SUBTRACTION, append_left=True, is_rsub=True, allow_other_iters=False,
            error_incompatible=True, modify_self=True
        )

    def __mul__(self, other: typing.Union["Numeric", VarOp, "_Var"]):
        if not isinstance(other, (DFVariable, VarOp)) and not _tp.p_bool_check(
            other, _tp.Numeric, error_on_gameval=True
        ) or not _tp.p_bool_check(self, _tp.Numeric, error_on_gameval=True):
            return NotImplemented

        return VarOp(SetVarType.SET_TO_PRODUCT, self, other)

    def __rmul__(self, other: typing.Union["Numeric", VarOp, "_Var"]) -> VarOp:
        return self.__mul__(other)

    def __pow__(self, power: typing.Union["Numeric", VarOp, "_Var"], modulo=None) -> VarOp:
        if isinstance(power, VarOp):
            vars = power.vars
            if len(vars) > 1:
                raise LimitReachedError("Cannot realize operation '**' between more than two variables.")

            if power.setv_type != SetVarType.SET_TO_POWER:
                raise TypeError(
                    "Cannot have different types of operations between variables at the same time; each kind "
                    "should be evaluated in its own .set()."
                )

            power = vars[0]

        if not isinstance(power, DFVariable) and not _tp.p_bool_check(
            power, _tp.Numeric, error_on_gameval=True
        ) or not _tp.p_bool_check(self, _tp.Numeric, error_on_gameval=True):
            return NotImplemented

        return VarOp(SetVarType.SET_TO_POWER, self, power)

    def __rpow__(self, other: typing.Union["Numeric", VarOp, "_Var"]) -> VarOp:
        if isinstance(other, VarOp):
            vars = other.vars
            if len(vars) > 1:
                raise LimitReachedError("Cannot realize operation '**' between more than two variables.")

            if other.setv_type != SetVarType.SET_TO_POWER:
                raise TypeError(
                    "Cannot have different types of operations between variables at the same time; each kind "
                    "should be evaluated in its own .set()."
                )

            other = vars[0]

        if not isinstance(other, DFVariable) and not _tp.p_bool_check(
            other, _tp.Numeric, error_on_gameval=True
        ) or not _tp.p_bool_check(self, _tp.Numeric, error_on_gameval=True):
            return NotImplemented

        return VarOp(SetVarType.SET_TO_POWER, other, self)

    def __mod__(self, other: typing.Union["Numeric", VarOp, "_Var"]) -> VarOp:
        if isinstance(other, VarOp):
            vars = other.vars
            if len(vars) > 1:
                raise LimitReachedError("Cannot realize operation '%' between more than two variables.")

            if other.setv_type != SetVarType.SET_TO_MOD:
                raise TypeError(
                    "Cannot have different types of operations between variables at the same time; each kind "
                    "should be evaluated in its own .set()."
                )

            other = vars[0]

        if not isinstance(other, DFVariable) and not _tp.p_bool_check(
            other, _tp.Numeric, error_on_gameval=True
        ) or not _tp.p_bool_check(self, _tp.Numeric, error_on_gameval=True):
            return NotImplemented

        return VarOp(SetVarType.SET_TO_MOD, self, other)

    def __rmod__(self, other: typing.Union["Numeric", VarOp, "_Var"]) -> VarOp:
        if isinstance(other, VarOp):
            vars = other.vars
            if len(vars) > 1:
                raise LimitReachedError("Cannot realize operation '%' between more than two variables.")

            if other.setv_type != SetVarType.SET_TO_MOD:
                raise TypeError(
                    "Cannot have different types of operations between variables at the same time; each kind "
                    "should be evaluated in its own .set()."
                )

            other = vars[0]

        if not isinstance(other, DFVariable) and not _tp.p_bool_check(
            other, _tp.Numeric, error_on_gameval=True
        ) or not _tp.p_bool_check(self, _tp.Numeric, error_on_gameval=True):
            return NotImplemented

        return VarOp(SetVarType.SET_TO_MOD, other, self)  # notice the change in order.

    def __truediv__(self, other: typing.Union["Numeric", VarOp, "_Var"]) -> VarOp:
        if not isinstance(other, (DFVariable, VarOp)) and not _tp.p_bool_check(
            other, _tp.Numeric, error_on_gameval=True
        ) or not _tp.p_bool_check(self, _tp.Numeric, error_on_gameval=True):
            return NotImplemented

        return VarOp(
            SetVarType.SET_TO_QUOTIENT, self, other,
            tags=[
                Tag("Division Mode", option="Default", action=SetVarType.SET_TO_QUOTIENT, block=BlockType.SET_VAR)]
        )

    def __rtruediv__(self, other: typing.Union["Numeric", VarOp, "_Var"]) -> VarOp:
        if not isinstance(other, (DFVariable, VarOp)) and not _tp.p_bool_check(
            other, _tp.Numeric, error_on_gameval=True
        ) or not _tp.p_bool_check(self, _tp.Numeric, error_on_gameval=True):
            return NotImplemented

        return VarOp(
            SetVarType.SET_TO_QUOTIENT, other, self,
            tags=[
                Tag("Division Mode", option="Default", action=SetVarType.SET_TO_QUOTIENT, block=BlockType.SET_VAR)]
        )

    def __floordiv__(self, other: typing.Union["Numeric", VarOp, "_Var"]) -> VarOp:
        if not isinstance(other, (DFVariable, VarOp)) and not _tp.p_bool_check(
            other, _tp.Numeric, error_on_gameval=True
        ) or not _tp.p_bool_check(self, _tp.Numeric, error_on_gameval=True):
            return NotImplemented

        return VarOp(
            SetVarType.SET_TO_QUOTIENT, self, other,
            tags=[Tag(
                "Division Mode", option="Round to Integer", action=SetVarType.SET_TO_QUOTIENT,
                block=BlockType.SET_VAR
            )]
        )

    def __rfloordiv__(self, other: typing.Union["Numeric", VarOp, "_Var"]) -> VarOp:
        if not isinstance(other, (DFVariable, VarOp)) and not _tp.p_bool_check(
            other, _tp.Numeric, error_on_gameval=True
        ) or not _tp.p_bool_check(self, _tp.Numeric, error_on_gameval=True):
            return NotImplemented

        return VarOp(
            SetVarType.SET_TO_QUOTIENT, other, self,
            tags=[Tag(
                "Division Mode", option="Round to Integer", action=SetVarType.SET_TO_QUOTIENT,
                block=BlockType.SET_VAR
            )]
        )

    # endregion:var_ops


class DFGameValue(DFType, VarOperable):
    """Used for game values, that change depending on the plot's state.

    Parameters
    ----------\u200b
    gval_type : :class:`~py2df.enums.dftypes.GameValueType`
        The type of Game Value this is.

    target : Optional[:class:`~py2df.enums.targets.Target`], optional
        The target of this Game Value, or None. Defaults to None.


    .. container:: comparisons

        .. describe:: a == b, a != b

            Returns the equivalent :class:`~.IfVariable` block for equals/not equals. Has two uses:

            1. **Is used to compare the variables with an If Var.** Note that equaling to an iterable means checking \
if the value is equal to at least one of its elements. Example usage::

                with val_a == val_b:
                    # code that is only executed in DiamondFire if 'val_a' and 'val_b' are equal in value.

                with val_c != val_d:
                    # code that is only executed in DiamondFire if 'val_c' and 'val_d' are different in value.

                with val_e == (val_f, val_g, val_i):
                    # code that is only executed in DiamondFire if 'val_e' is equal to one of 'val_f', 'val_g' or \
'val_i'.

            2. **Is used to compare, IN PYTHON, the values'** :attr:`gval_type` **and** :attr:`target` attrs \
(by calling :func:`bool` on the generated IfVariable block). Example usage::

                if val_a == val_b:
                    # code that is only read, IN PYTHON, if 'val_a' and 'val_b' have the same 'gval_type' and 'target' \
attrs.

                if val_c != val_d:
                    # code that is only read, IN PYTHON, if 'val_c' and 'val_b' have a different 'gval_type' or \
'target' attr.

        .. describe:: a > b, a >= b, a < b, a <= b

            Returns the equivalent :class:`~.IfVariable` block for the given comparison. **Its only usage is as
            a Codeblock** (in a `with`).
            For example::

                with var_a > var_b:
                    # code that is only executed in DiamondFire if 'var_a' is bigger than 'var_b' in value.

                with var_c < var_d:
                    # code that is only executed in DiamondFire if 'var_c' is less than 'var_d' in value.

            .. note::

                Those comparisons are not usable in Python if's; if a :func:`bool` is attempted on the resulting
                IfVariable block, it will always return True. This mechanism is only implemented for ``==`` and ``!=``.

            .. warning::

                Assuming that one of them is a DFVariable, the other has to be a valid :attr:`~.Numeric` parameter.
                Otherwise, a TypeError may be raised (if the given type does not support operations with DFVariable,
                which is likely).

    .. container:: operations

        .. describe:: a + b, a - b, a * b, a ** b, a / b, a // b, a % b

            Creates a :class:`VarOp` instance representing this operation between different variables/variables
            and values/etc.
            It is meant to be given as the parameter for :meth:`DFVariable.set`, which will then place the appropriate
            Set Variable type (setting the variable instance to this operation)

            `a` is the :class:`VarOperable` instance, while `b`, in this case, is the :attr:`~.Numeric` to realize this
            operation with.

            .. note::

                If the operation is addition or subtraction, `b` can also be a :attr:`~.Locatable` parameter (represent
                a location), besides Numeric.

            .. warning::

                **You cannot mix operations.** For example, ``a + b - c * d ** e`` will raise. Stick to only one
                at once, and have one :meth:`DFVariable.set` call for each kind.
                (There is only one Set Var for each kind.)
                (However, operations with multiple variables, up to 27, work: ``a + b + c + ... + z``)

                If there is an attempt to mix operations, a :exc:`TypeError` is raised.

                Similarly, if there is an attempt to have an operation with more than 26 variables (chest size is
                up to 27 items, while 1 slot is the variable being set), then a :exc:`~.LimitReachedError` is raised
                instead.

        .. describe:: str(a)

            Returns ``a.gval_type.value`` (the type of Game Value).

        .. describe:: hash(a)

            Returns an unique hash identifying this Game Value by its Game Value type and its target.


    Attributes
    ----------\u200b
        gval_type : :class:`~py2df.enums.dftypes.GameValueType`
            The type of Game Value this is.

        target : Optional[:class:`~py2df.enums.targets.Target`], optional
            The target of this Game Value, or None. Defaults to None.
    """
    __slots__ = ("gval_type", "target")

    gval_type: GameValueType
    target: typing.Optional[Target]

    def __init__(self, gval_type: GameValueType, target: typing.Optional[Target] = None):
        """
        Initializes the Game Value.

        Parameters
        ----------
        gval_type : :class:`~py2df.enums.dftypes.GameValueType`
            The type of Game Value this is.

        target : Optional[:class:`~py2df.enums.targets.Target`], optional
            The target of this Game Value, or None. Defaults to None.
        """

        self.gval_type = GameValueType(gval_type)
        self.target = target or None

    def set(
        self, gval_type: GameValueType = DEFAULT_VAL, target: typing.Optional[Target] = DEFAULT_VAL
    ) -> "DFGameValue":
        """Configures this Game Value. Note that this does not create a Set Var like with DFVariable; instead, it
        changes, IN PYTHON, the attributes of this Game Value.

        Parameters
        ----------
        gval_type : :class:`~py2df.enums.dftypes.GameValueType`
            The type of Game Value this is.

        target : Optional[:class:`~py2df.enums.targets.Target`], optional
            The target of this Game Value, or None.

        Returns
        -------
        :class:`DFGameValue`
            self to allow chaining.
        """

        if gval_type != DEFAULT_VAL:
            self.gval_type = GameValueType(gval_type)

        if target != DEFAULT_VAL:
            self.target = target or None

        return self

    def __repr__(self):
        return f"<{self.__class__.__name__} gval_type={repr(self.gval_type.value)} \
target={repr(str(self.target) if self.target else self.target)}>"

    def __str__(self):
        return self.gval_type.value

    def as_json_data(self) -> dict:
        """Obtains a JSON-serializable dict representation of this Game Value.

        Returns
        -------
        :class:`dict`
            A JSON-serializable dict.
        """
        return dict(
            id=constants.ITEM_ID_GAME_VALUE,
            data=dict(
                type=self.gval_type.value,
                target=self.target.value if self.target else "none"
            )
        )

    @classmethod
    def from_json_data(cls, data: dict):
        """Obtain a Game Value from pre-existing parsed JSON data.

        Must be of the form (have at least those keys)::

            { "data": { "type": str, "target": str } }

        Where ``str`` would be the type of the value.

        Parameters
        ----------
        data : :class:`dict`
            The parsed JSON :class:`dict`.

        Returns
        -------
        :class:`DFGameValue`
            :class:`DFGameValue` instance.

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
                or "type" not in data["data"]
                or type(data["data"]["type"]) != str
                or "target" not in data["data"]
                or type(data["data"]["target"]) != str
        ):
            raise TypeError(
                "Malformed DFGameValue parsed JSON data! Must be a dict with, at least, a 'data' dict containing"
                "'type' and 'target' str values."
            )

        in_data = data["data"]
        target_str = in_data["target"]
        target_instance = None
        if target_str.lower() != "none":
            try:
                target_instance = PlayerTarget(target_str)
            except ValueError:
                try:
                    target_instance = EntityTarget(target_str)
                except ValueError as e:
                    raise ValueError("Invalid target specified in Game Value JSON data.") from e

        return cls(GameValueType(in_data["type"]), target_instance)

    # def to_item(self) -> "Item":
    #     pass  # TODO: Apple

    def __hash__(self):
        return hash((self.__class__.__name__, self.gval_type, str(self.target)))


_var_docs = """Represents a DiamondFire {0} variable. **Note that all variables with same 'name' attribute represent the 
same var.**

Parameters
----------\u200b
name : :class:`str`
    The name of this variable. This uniquely identifies it, along with its scope.

init_value : Optional[Union[:attr:`~.{1}`, :class:`VarOp`, Iterable[:attr:`~.{1}`]]], optional
    An optional initial value for this variable. Defaults to ``None`` (i.e., doesn't set a value).

    .. note::

        If any value is specified, **this creates a Set Var block**. As such, **this behaves identically to**
        :meth:`set` (therefore, see its documentation).

scope : :class:`~.VariableScope`, optional
    The scope of this variable. This can also be set through the kwargs ``unsaved``, ``saved`` and ``local`` .
    Defaults to :attr:`~.VariableScope.UNSAVED`.

unsaved : :class:`bool`, optional
    If ``True``, the variable's scope is set to :attr:`~.VariableScope.UNSAVED` - i.e., the value does not persist
    between successive plot uses (when the amount of players reaches 0, the variable is reset).


.. container:: comparisons

    .. describe:: a == b, a != b

        Returns the equivalent :class:`~.IfVariable` block for equals/not equals. Has two uses:

        1. **Is used to compare the variables with an If Var.** Note that equaling to an iterable means checking \
if the variable is equal to at least one of its elements. Example usage::

            with var_a == var_b:
                # code that is only executed in DiamondFire if 'var_a' and 'var_b' are equal in value.

            with var_c != var_d:
                # code that is only executed in DiamondFire if 'var_c' and 'var_d' are different in value.

            with var_e == (var_f, var_g, var_i):
                # code that is only executed in DiamondFire if 'var_e' is equal to one of 'var_f', 'var_g' or \
'var_i'.

        2. **Is used to compare, IN PYTHON, the variables' names and scopes** (by calling :func:`bool` on the \
generated IfVariable block). Example usage::

            if var_a == var_b:
                # code that is only read, IN PYTHON, if 'var_a' and 'var_b' have the same 'name' and 'scope' attrs.

            if var_c != var_d:
                # code that is only read, IN PYTHON, if 'var_c' and 'var_b' have a different 'name' or 'scope' attr.{2}

.. container:: operations

{3}    .. describe:: str(a)

        Returns this variable as a string in the form ``%var(name)``, where `name` is the variable's name.
        When used in a string, DiamondFire replaces it with the variable's value.

    .. describe:: hash(a)

        Returns an unique hash identifying this variable by name and scope.


Attributes
----------\u200b
name : :class:`str`
    The name of this variable. This uniquely identifies it, along with its scope.

scope : :class:`~.VariableScope`
    The scope of this variable (:attr:`~.UNSAVED`, :attr:`~.SAVED` or :attr:`~.LOCAL`).

check_type : :attr:`~.{1}` object
    The acceptable parameter type for this variable (in this class's case, {0} parameter).
"""

_var_num_op_docs = """    .. describe:: a + b, a - b, a * b, a ** b, a / b, a // b, a % b

        Creates a :class:`VarOp` instance representing this operation between different variables/variables
        and values/etc.
        It is meant to be given as the parameter for :meth:`set`, which will then place the appropriate
        Set Variable type.

        `a` is the :class:`DFVariable`, while `b`, in this case, is the :attr:`~.Numeric` to realize this
        operation with.

        .. note::

            If the operation is addition or subtraction, `b` can also be a :attr:`~.Locatable` parameter (represent
            a location), besides Numeric.

        .. warning::

            **You cannot mix operations.** For example, ``a + b - c * d ** e`` will raise. Stick to only one
            at once, and have one :meth:`set` call for each kind. (There is only one Set Var for each kind.)
            (However, operations with multiple variables, up to 27, work: ``a + b + c + ... + z``)

            If there is an attempt to mix operations, a :exc:`TypeError` is raised.

            Similarly, if there is an attempt to have an operation with more than 26 variables (chest size is
            up to 27 items, while 1 slot is the variable being set), then a :exc:`~.LimitReachedError` is raised
            instead.

    .. describe:: a += b, a -= b, a *= b, a **= b, a /= b, a //= b, a %= b

        Same behavior as ``a.set(a ? b)``, where ``?`` is the given operation (`b` must be :attr:`~.Numeric`).

        .. note::

            If the operation given is either ``+=`` or ``-=``, then it will place the respective
            ``+=`` and ``-=`` Set Var blocks instead of ``a.set(a +/- b)``. This is because those are
            the only ones that have a SetVar equivalent.

"""

_var_num_comp_docs = """

    .. describe:: a > b, a >= b, a < b, a <= b

        Returns the equivalent :class:`~.IfVariable` block for the given comparison. **Its only usage is as
        a Codeblock** (in a `with`).
        For example::

            with var_a > var_b:
                # code that is only executed in DiamondFire if 'var_a' is bigger than 'var_b' in value.

            with var_c < var_d:
                # code that is only executed in DiamondFire if 'var_c' is less than 'var_d' in value.

        .. note::

            Those comparisons are not usable in Python if's; if a :func:`bool` is attempted on the resulting
            IfVariable block, it will always return True. This mechanism is only implemented for ``==`` and ``!=``.

        .. warning::

            Assuming that one of them is a DFVariable, the other has to be a valid :attr:`~.Numeric` parameter.
            Otherwise, a TypeError may be raised (if the given type does not support operations with DFVariable,
            which is likely)."""


class _Var(DFType, VarOperable):
    """Represents a DiamondFire variable. **Note that all variables with same 'name' attribute represent the same
    var.**

    Parameters
    ----------\u200b
    name : :class:`str`
        The name of this variable. This uniquely identifies it, along with its scope.

    init_value : Optional[Union[:attr:`~.Param`, :class:`VarOp`, Iterable[:attr:`~.Param`]]], optional
        An optional initial value for this variable. Defaults to ``None`` (i.e., doesn't set a value).

        .. note::

            If any value is specified, **this creates a Set Var block**. As such, **this behaves identically to**
            :meth:`set` (therefore, see its documentation).

    scope : :class:`~.VariableScope`, optional
        The scope of this variable. This can also be set through the kwargs ``unsaved``, ``saved`` and ``local`` .
        Defaults to :attr:`~.VariableScope.UNSAVED`.

    unsaved : :class:`bool`, optional
        If ``True``, the variable's scope is set to :attr:`~.VariableScope.UNSAVED` - i.e., the value does not persist
        between successive plot uses (when the amount of players reaches 0, the variable is reset).


    .. container:: comparisons

        .. describe:: a == b, a != b

            Returns the equivalent :class:`~.IfVariable` block for equals/not equals. Has two uses:

            1. **Is used to compare the variables with an If Var.** Note that equaling to an iterable means checking \
if the variable is equal to at least one of its elements. Example usage::

                with var_a == var_b:
                    # code that is only executed in DiamondFire if 'var_a' and 'var_b' are equal in value.

                with var_c != var_d:
                    # code that is only executed in DiamondFire if 'var_c' and 'var_d' are different in value.

                with var_e == (var_f, var_g, var_i):
                    # code that is only executed in DiamondFire if 'var_e' is equal to one of 'var_f', 'var_g' or \
'var_i'.

            2. **Is used to compare, IN PYTHON, the variables' names and scopes** (by calling :func:`bool` on the \
generated IfVariable block). Example usage::

                if var_a == var_b:
                    # code that is only read, IN PYTHON, if 'var_a' and 'var_b' have the same 'name' and 'scope' attrs.

                if var_c != var_d:
                    # code that is only read, IN PYTHON, if 'var_c' and 'var_b' have a different 'name' or 'scope' attr.

        .. describe:: a > b, a >= b, a < b, a <= b

            Returns the equivalent :class:`~.IfVariable` block for the given comparison. **Its only usage is as
            a Codeblock** (in a `with`).
            For example::

                with var_a > var_b:
                    # code that is only executed in DiamondFire if 'var_a' is bigger than 'var_b' in value.

                with var_c < var_d:
                    # code that is only executed in DiamondFire if 'var_c' is less than 'var_d' in value.

            .. note::

                Those comparisons are not usable in Python if's; if a :func:`bool` is attempted on the resulting
                IfVariable block, it will always return True. This mechanism is only implemented for ``==`` and ``!=``.

            .. warning::

                Assuming that one of them is a DFVariable, the other has to be a valid :attr:`~.Numeric` parameter.
                Otherwise, a TypeError may be raised (if the given type does not support operations with DFVariable,
                which is likely).

    .. container:: operations

        .. describe:: a + b, a - b, a * b, a ** b, a / b, a // b, a % b

            Creates a :class:`VarOp` instance representing this operation between different variables/variables
            and values/etc.
            It is meant to be given as the parameter for :meth:`set`, which will then place the appropriate
            Set Variable type.

            `a` is the :class:`DFVariable`, while `b`, in this case, is the :attr:`~.Numeric` to realize this
            operation with.

            .. note::

                If the operation is addition or subtraction, `b` can also be a :attr:`~.Locatable` parameter (represent
                a location), besides Numeric.

            .. warning::

                **You cannot mix operations.** For example, ``a + b - c * d ** e`` will raise. Stick to only one
                at once, and have one :meth:`set` call for each kind. (There is only one Set Var for each kind.)
                (However, operations with multiple variables, up to 27, work: ``a + b + c + ... + z``)

                If there is an attempt to mix operations, a :exc:`TypeError` is raised.

                Similarly, if there is an attempt to have an operation with more than 26 variables (chest size is
                up to 27 items, while 1 slot is the variable being set), then a :exc:`~.LimitReachedError` is raised
                instead.

        .. describe:: a += b, a -= b, a *= b, a **= b, a /= b, a //= b, a %= b

            Same behavior as ``a.set(a ? b)``, where ``?`` is the given operation (`b` must be :attr:`~.Numeric`).

            .. note::

                If the operation given is either ``+=`` or ``-=``, then it will place the respective
                ``+=`` and ``-=`` Set Var blocks instead of ``a.set(a +/- b)``. This is because those are
                the only ones that have a SetVar equivalent.

        .. describe:: str(a)

            Returns this variable as a string in the form ``%var(name)``, where `name` is the variable's name.
            When used in a string, DiamondFire replaces it with the variable's value.

        .. describe:: hash(a)

            Returns an unique hash identifying this variable by name and scope.


    Attributes
    ----------\u200b
    name : :class:`str`
        The name of this variable. This uniquely identifies it, along with its scope.

    scope : :class:`~.VariableScope`
        The scope of this variable (:attr:`~.UNSAVED`, :attr:`~.SAVED` or :attr:`~.LOCAL`).

    check_type : :attr:`~.Param`
        The acceptable parameter type for this variable (in this class's case, any parameter).
    """
    __slots__ = ("name", "scope")

    name: str
    scope: VariableScope
    check_type: "Param"

    def __init__(
        self, name: typing.Union[str, DFText], init_value: typing.Optional["Param"] = None,
        *, scope: VariableScope = DEFAULT_VAL, unsaved: bool = True,
        saved: bool = False, local: bool = False
    ):
        _heavy_imports()

        if not hasattr(self, "check_type") or not self.check_type:
            self.check_type = Param

        self.name: str = str(name)

        if scope != DEFAULT_VAL:
            self.scope: VariableScope = VariableScope(scope)
        elif saved:
            self.scope: VariableScope = VariableScope.SAVED
        elif local:
            self.scope: VariableScope = VariableScope.LOCAL
        elif unsaved:
            self.scope: VariableScope = VariableScope.UNSAVED

        if init_value:
            self.set(init_value)

    def set(self, value: typing.Union["Param", VarOp, typing.Iterable["Param"]]) -> "SetVar":
        """
        Set this variable. Note that this simply creates a Set Var block and returns it. Example usage::

            var_a.set(var_b)  # SetVar (=): Sets a's value to b's
            var_a.set(var_b + var_c + 5)  # SetVar (+): Adds the values of var_b, var_c and 5
            var_a.set(["hello", 5, var_b])  # SetVar (Create List): Creates a list var with those values.

        See the 'Supported Operations' section for more info on operations. Note that they cannot be mixed (i.e.,
        can only set one kind of operation at a time - 'a + b * c' is not allowed, for example).

        Parameters
        ----------
        value : Union[:attr:`~.Param`, :class:`VarOp`, Iterable[:attr:`~.Param`]]
            The value. Can consist of any valid Param type, a var operation or an iterable of Params.
            The codeblock creation relation is as follows:

            +---------------------------+------------------------------------------------------------------------+
            |       Type(s) given       |                           Codeblock created                            |
            +===========================+========================================================================+
            | :attr:`~.Param`           | Set Var: = (:attr:`~.SET_TO`)                                          |
            +---------------------------+------------------------------------------------------------------------+
            | :class:`VarOp`            | One of: Set Var: +, -, %, x, Exponent, Divide (depending on operation) |
            +---------------------------+------------------------------------------------------------------------+
            | Iterable[:attr:`~.Param`] | Set Var: Create List (:attr:`~.CREATE_LIST`)                           |
            +---------------------------+------------------------------------------------------------------------+

            .. warning::
                If using a typed class (such as TextVar or the likes), then the parameter type must correspond to
                that of the typed class's type.


        Returns
        -------
        :class:`~.SetVar`
            The generated SetVar block.
        """
        setv_type = SetVarType.SET_TO
        args: Arguments
        if isinstance(value, VarOp):  # a var operation was given
            setv_type = SetVarType(value.setv_type)
            tp_to_check = typing.Union[_tp.Numeric, _tp.Locatable] if setv_type in (
                SetVarType.SET_TO_ADDITION, SetVarType.SET_TO_SUBTRACTION
            ) else _tp.Numeric

            if (
                self.has_check_type
                and (
                    tp_to_check == typing.Union[_tp.Numeric, _tp.Locatable]
                        and self.check_type not in (Numeric, Locatable)
                    or tp_to_check == _tp.Numeric and self.check_type != tp_to_check
                )
            ):
                raise

            args = Arguments(
                [self] + [_tp.p_check(o, tp_to_check, "value") for o in value.vars],
                tags=value.tags or []
            )

        elif _tp.p_bool_check(value, self.check_type):  # a parameter was given
            args = Arguments([self] + [_tp.p_check(value, self.check_type, "value")])

        elif isinstance(value, collections.Iterable):  # an iterable of parameters was given
            setv_type = SetVarType.CREATE_LIST
            # args = Arguments([self] + [_tp.p_check(o, self.check_type, "value") for o in value])  # fixed type lists? Nah?
            args = Arguments([self] + [_tp.p_check(o, _tp.Param, "value") for o in value])

        else:
            _tp.p_check(value, self.check_type, "value")  # this will error
            raise TypeError  # prevent execution in case the above fails to raise; this shouldn't ever be needed

        return _SetVar(
            action=setv_type,
            args=args,
            append_to_reader=True
        )

    def as_json_data(self) -> dict:
        """Exports this class a valid JSON-serializable dict.

        Returns
        -------
        :class:`dict`
        """
        return dict(
            id=ITEM_ID_DYNAMIC_VAR,
            data=dict(
                name=self.name,
                scope=self.scope.value
            )
        )

    @property
    def has_check_type(self) -> bool:
        return self.check_type and self.check_type != Param

    @classmethod
    def from_json_data(cls, data: dict) -> "_Var":
        """Obtain a DFVariable from pre-existing parsed JSON data (as a dict).

        Must have, at least, the following keys with the following format::

            { "data": { "name": str, "scope": str } }

        Parameters
        ----------
        data : :class:`dict`
            The parsed JSON :class:`dict`.


        Returns
        -------
        :class:`DFVariable`
            :class:`DFVariable` instance.

        """
        if (
            not isinstance(data, dict)
            # or "id" not in data  # not really required
            or "data" not in data
            or not isinstance(data["data"], dict)
            or "name" not in data["data"]
            or type(data["data"]["name"]) != str
            or "scope" not in data["scope"]
            or type(data["data"]["scope"]) != str
        ):
            raise TypeError(
                "Malformed Variable parsed JSON data! Must be a dict with, at least, a 'data' dict and 'name' and"
                "'scope' str values."
            )

        return cls(data["data"]["name"], scope=VariableScope(data["data"]["scope"]))

    def __repr__(self):
        return f"<{self.__class__.__name__} name={repr(self.name)} scope={repr(self.scope.value)}>"

    def __str__(self):
        return f"%var({self.name})"

    def __iadd__(self, other: typing.Union["Numeric", VarOp, "_Var"]) -> "_Var":
        if _tp.p_bool_check(self, _tp.Locatable) and not _tp.p_bool_check(self, _tp.Numeric):
            self.set(self.__add__(other))  # += is not compatible with locations
            return self

        if not isinstance(other, (DFVariable, VarOp)) and not _tp.p_bool_check(
            other, _tp.Numeric, error_on_gameval=True
        ):
            return NotImplemented

        _SetVar(
            action=SetVarType.ADD,
            args=Arguments(
                [_tp.p_check(self, _tp.Numeric, "self")] + (
                    [_tp.p_check(o, _tp.Numeric, f"other[{i}]") for i, o in enumerate(other.vars)]
                    if isinstance(other, VarOp) else [
                        _tp.p_check(other, _tp.Numeric, "other")
                    ]
                )
            ),
            append_to_reader=True
        )

        return self

    def __isub__(self, other: typing.Union["Numeric", VarOp, "_Var"]) -> "_Var":
        if _tp.p_bool_check(self, _tp.Locatable) and not _tp.p_bool_check(self, _tp.Numeric):
            self.set(self.__sub__(other))  # -= is not compatible with locations
            return self

        if not isinstance(other, (DFVariable, VarOp)) and not _tp.p_bool_check(
            other, _tp.Numeric, error_on_gameval=True
        ):
            return NotImplemented

        _SetVar(
            action=SetVarType.SUBTRACT,
            args=Arguments(
                [_tp.p_check(self, _tp.Numeric, "self")] + (
                    [_tp.p_check(o, _tp.Numeric) for o in other.vars] if isinstance(other, VarOp) else [
                        _tp.p_check(other, _tp.Numeric)
                    ]
                )
            ),
            append_to_reader=True
        )

        return self

    def __imul__(self, other: typing.Union["Numeric", VarOp, "_Var"]) -> "_Var":
        self.set(self.__mul__(other))

        return self

    def __ipow__(self, power: typing.Union["Numeric", VarOp, "_Var"], modulo=None) -> "_Var":
        self.set(self.__pow__(power))

        return self

    def __imod__(self, other: typing.Union["Numeric", VarOp, "_Var"]) -> "_Var":
        self.set(self.__mod__(other))

        return self

    def __itruediv__(self, other: typing.Union["Numeric", VarOp, "_Var"]) -> "_Var":
        self.set(self.__truediv__(other))

        return self
        # [Tag("Division Mode", option="Default", action=SetVarType.SET_TO_QUOTIENT, block=BlockType.SET_VAR)]

    def __ifloordiv__(self, other: typing.Union["Numeric", VarOp, "_Var"]) -> "_Var":
        self.set(self.__floordiv__(other))

        return self
        # [Tag("Division Mode", option="Round to Integer", action=SetVarType.SET_TO_QUOTIENT, block=BlockType.SET_VAR)]

    def __hash__(self):
        return hash((self.name, self.scope))


class DFVariable(_Var):
    __doc__ = _Var.__doc__
    pass


class NumberVar(_Var):
    __doc__ = _var_docs.format("number", "Numeric", _var_num_comp_docs, _var_num_op_docs)

    def __init__(
        self, name: typing.Union[str, DFText], init_value: typing.Optional["Numeric"] = None,
        *, scope: VariableScope = DEFAULT_VAL, unsaved: bool = True,
        saved: bool = False, local: bool = False
    ):
        _heavy_imports()
        self.check_type = _tp.Numeric
        super().__init__(name, init_value, scope=scope, unsaved=unsaved, saved=saved, local=local)

    def set(self, value: typing.Union["Numeric", VarOp, typing.Iterable["Numeric"]]) -> "SetVar":
        return super().set(value)


class TextVar(_Var):
    __doc__ = _var_docs.format("text", "Textable", "", "")

    def __init__(
        self, name: typing.Union[str, DFText], init_value: typing.Optional["Textable"] = None,
        *, scope: VariableScope = DEFAULT_VAL, unsaved: bool = True,
        saved: bool = False, local: bool = False
    ):
        _heavy_imports()
        self.check_type = _tp.Textable
        super().__init__(name, init_value, scope=scope, unsaved=unsaved, saved=saved, local=local)

    def set(self, value: typing.Union["Textable", VarOp, typing.Iterable["Textable"]]) -> "SetVar":
        return super().set(value)


class ItemVar(_Var):
    __doc__ = _var_docs.format("item", "ItemParam", "", "")

    def __init__(
        self, name: typing.Union[str, DFText], init_value: typing.Optional["ItemParam"] = None,
        *, scope: VariableScope = DEFAULT_VAL, unsaved: bool = True,
        saved: bool = False, local: bool = False
    ):
        _heavy_imports()
        self.check_type = _tp.ItemParam
        super().__init__(name, init_value, scope=scope, unsaved=unsaved, saved=saved, local=local)

    def set(self, value: typing.Union["ItemParam", VarOp, typing.Iterable["ItemParam"]]) -> "SetVar":
        return super().set(value)


class PotionVar(_Var):
    __doc__ = _var_docs.format("potion", "Potionable", "", "")

    def __init__(
        self, name: typing.Union[str, DFText], init_value: typing.Optional["Potionable"] = None,
        *, scope: VariableScope = DEFAULT_VAL, unsaved: bool = True,
        saved: bool = False, local: bool = False
    ):
        _heavy_imports()
        self.check_type = _tp.Potionable
        super().__init__(name, init_value, scope=scope, unsaved=unsaved, saved=saved, local=local)

    def set(self, value: typing.Union["Potionable", VarOp, typing.Iterable["Potionable"]]) -> "SetVar":
        return super().set(value)


class LocationVar(_Var):
    __doc__ = _var_docs.format(
        "location", "Locatable", "",
        re.sub(
            (
                r"(?:"
                r"(?<=describe:: )|(?<=a [^a-zA-Z0-9] b, )|(?<=a [^a-zA-Z0-9]{2} b, )"
                r"|(?<=a [^a-zA-Z0-9]= b, )|(?<=a [^a-zA-Z0-9]{2}= b, )"
                r")"
                r"a [^+\-\n=a-zA-Z0-9]+?=? b(?:, )?"
            ),
            "", _var_num_op_docs
        ).replace(", \n", "\n")
    )

    def __init__(
        self, name: typing.Union[str, DFText], init_value: typing.Optional["Locatable"] = None,
        *, scope: VariableScope = DEFAULT_VAL, unsaved: bool = True,
        saved: bool = False, local: bool = False
    ):
        _heavy_imports()
        self.check_type = _tp.Locatable
        super().__init__(name, init_value, scope=scope, unsaved=unsaved, saved=saved, local=local)

    def set(self, value: typing.Union["Locatable", VarOp, typing.Iterable["Locatable"]]) -> "SetVar":
        return super().set(value)


class ListVar(_Var):
    __doc__ = _var_docs.format("list", "Listable", "", "")

    def __init__(
        self, name: typing.Union[str, DFText], init_value: typing.Optional["Listable"] = None,
        *, scope: VariableScope = DEFAULT_VAL, unsaved: bool = True,
        saved: bool = False, local: bool = False
    ):
        _heavy_imports()
        self.check_type = _tp.Listable
        super().__init__(name, init_value, scope=scope, unsaved=unsaved, saved=saved, local=local)

    def set(self, value: typing.Union["Listable", VarOp, typing.Iterable["Listable"]]) -> "SetVar":
        return super().set(value)


class ParticleVar(_Var):
    __doc__ = _var_docs.format("particle", "ParticleParam", "", "")

    def __init__(
        self, name: typing.Union[str, DFText], init_value: typing.Optional["ParticleParam"] = None,
        *, scope: VariableScope = DEFAULT_VAL, unsaved: bool = True,
        saved: bool = False, local: bool = False
    ):
        _heavy_imports()
        self.check_type = _tp.ParticleParam
        super().__init__(name, init_value, scope=scope, unsaved=unsaved, saved=saved, local=local)

    def set(self, value: typing.Union["ParticleParam", VarOp, typing.Iterable["ParticleParam"]]) -> "SetVar":
        return super().set(value)


class SoundVar(_Var):
    __doc__ = _var_docs.format("sound", "SoundParam", "", "")

    def __init__(
        self, name: typing.Union[str, DFText], init_value: typing.Optional["SoundParam"] = None,
        *, scope: VariableScope = DEFAULT_VAL, unsaved: bool = True,
        saved: bool = False, local: bool = False
    ):
        _heavy_imports()
        self.check_type = _tp.SoundParam
        super().__init__(name, init_value, scope=scope, unsaved=unsaved, saved=saved, local=local)

    def set(self, value: typing.Union["SoundParam", VarOp, typing.Iterable["SoundParam"]]) -> "SetVar":
        return super().set(value)


remove_u200b_from_doc(
    _Var, DFVariable, VarOp, DFGameValue, VarOperable,
    NumberVar, TextVar, ItemVar, PotionVar, LocationVar, ListVar, ParticleVar, SoundVar
)

