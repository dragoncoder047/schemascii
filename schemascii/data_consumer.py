from __future__ import annotations

import abc
import types
import typing
import warnings
from dataclasses import dataclass, field

import schemascii.data as _data
import schemascii.errors as _errors
import schemascii.svg as _svg

_OPT_IS_REQUIRED = object()


@dataclass
class Option[T]:
    """Represents an allowed name used in Schemascii's internals
    somewhere. Normal users have no need for this class.
    """

    name: str
    type: type[T] | list[T]
    help: str = field(repr=False)
    default: T = _OPT_IS_REQUIRED


@dataclass
class DataConsumer(abc.ABC):
    """Base class for any Schemascii AST node that needs data
    to be rendered. This class registers the options that the class
    declares with Data so that they can be checked, automatically pulls
    the needed options when to_xml_string() is called, and passes the dict of
    options to render() as keyword arguments.
    """

    options: typing.ClassVar[list[Option
                                  | types.EllipsisType
                                  | tuple[str, ...]]] = [
        Option("scale", float, "Scale by which to enlarge the "
               "entire diagram by", 15),
        Option("linewidth", float, "Width of drawn lines", 2),
        Option("color", str, "Default color for everything", "black"),
    ]
    css_class: typing.ClassVar[str] = ""

    @property
    def namespaces(self) -> tuple[str, ...]:
        # base case to stop recursion
        return ()

    def __init_subclass__(cls, namespaces: tuple[str, ...] = None):

        if not namespaces:
            # allow anonymous helper subclasses
            return

        if not hasattr(cls, "namespaces"):
            # don't clobber it if a subclass already overrides it!
            @property
            def __namespaces(self) -> tuple[str, ...]:
                return super(type(self), self).namespaces + namespaces
            cls.namepaces = __namespaces

        for b in cls.mro():
            if (b is not cls
                    and issubclass(b, DataConsumer)
                    and b.options is cls.options):
                # if we literally just inherit the attribute,
                # don't bother reprocessing it - just assign it in the
                # namespaces
                break
        else:
            def coalesce_options(cls: type[DataConsumer]) -> list[Option]:
                if DataConsumer not in cls.mro():
                    return []
                seen_inherit = False
                opts: list[Option] = []
                for opt in cls.options:
                    if opt is ...:
                        if seen_inherit:
                            raise ValueError("can't use 'inherit' twice")
                        for base in cls.__bases__:
                            opts.extend(coalesce_options(base))
                        seen_inherit = True
                    elif isinstance(opt, tuple):
                        for base in cls.__bases__:
                            opts.extend(o for o in coalesce_options(base)
                                        if o.name in opt)
                    elif isinstance(opt, Option):
                        opts.append(opt)
                    else:
                        raise TypeError(f"unknown option definition: {opt!r}")
                return opts

            cls.options = coalesce_options(cls)

        for ns in namespaces:
            for option in cls.options:
                _data.Data.define_option(ns, option)

    def to_xml_string(self, data: _data.Data) -> str:
        """Pull options relevant to this node from data, calls
        self.render(), and wraps the output in a <g>."""
        values = {}
        for name in self.namespaces:
            values |= data.get_values_for(name)
        # validate the options
        for opt in self.options:
            if opt.name not in values:
                if opt.default is _OPT_IS_REQUIRED:
                    raise _errors.NoDataError(
                        f"missing value for {self.namespaces[0]}.{name}")
                values[opt.name] = opt.default
                continue
            if isinstance(opt.type, list):
                if values[opt.name] not in opt.type:
                    raise _errors.BOMError(
                        f"{self.namespaces[0]}.{opt.name}: "
                        f"invalid choice: {values[opt.name]!r} "
                        f"(valid options are "
                        f"{', '.join(map(repr, opt.type))})")
                continue
            try:
                values[opt.name] = opt.type(values[opt.name])
            except ValueError as err:
                raise _errors.DataTypeError(
                    f"option {self.namespaces[0]}.{opt.name}: "
                    f"invalid {opt.type.__name__} value: "
                    f"{values[opt.name]!r}") from err
        for key in values:
            if any(opt.name == key for opt in self.options):
                continue
            warnings.warn(
                f"unknown data key {key!r} for styling {self.namespaces[0]}",
                stacklevel=2)
        # render
        result = self.render(**values, data=data)
        if self.css_class:
            result = _svg.group(result, class_=self.css_class)
        return result

    @abc.abstractmethod
    def render(self, data: _data.Data, **options) -> str:
        """Render self to a string of XML. This is a private method and should
        not be called by non-Schemascii-extending code. External callers should
        call to_xml_string() instead.

        Subclasses must implement this method.
        """
        raise NotImplementedError
