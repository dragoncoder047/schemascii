from __future__ import annotations

import abc
import typing
import warnings
from dataclasses import dataclass, field

import schemascii.data as _data
import schemascii.errors as _errors
import schemascii.svg as _svg


@dataclass
class OptionsSet[T]:
    self_opts: set[Option[T]]
    inherit: set[str] | bool = True
    inherit_from: list[type[DataConsumer]] | None = None


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

    options: typing.ClassVar[OptionsSet] = OptionsSet([
        Option("scale", float, "Scale by which to enlarge the "
               "entire diagram by", 15),
        Option("linewidth", float, "Width of drawn lines", 2),
        Option("color", str, "Default color for everything", "black"),
    ], False)
    css_class: typing.ClassVar[str] = ""

    registry: typing.ClassVar[dict[str, type[DataConsumer]]] = {}

    def to_xml_string(self, data: _data.Data) -> str:
        """Pull options relevant to this node from data, calls
        self.render(), and wraps the output in a <g>."""
        # TODO: fix this with the new OptionsSet inheritance mode
        # recurse to get all of the namespaces
        # recurse to get all of the pulled values
        # then the below
        raise NotImplementedError
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
                f"unknown data key {key!r} for {self.namespaces[0]}",
                stacklevel=3)
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

    @classmethod
    def register[T: type[DataConsumer]](
            cls, namespace: str | None = None) -> typing.Callable[[T], T]:
        def register(cls2: type[DataConsumer]):
            if namespace:
                if namespace in cls.registry:
                    raise ValueError(f"{namespace} already registered")
                cls.registry[namespace] = cls2
            if (cls2.options.inherit_from is None
                    and DataConsumer in cls2.mro()):
                cls2.options.inherit_from = cls2.__bases__
            return cls2
        return register
