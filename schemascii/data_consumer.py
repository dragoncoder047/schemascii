from __future__ import annotations

import abc
import itertools
import typing
import warnings
from dataclasses import dataclass, field

import schemascii.data as _data
import schemascii.errors as _errors
import schemascii.svg as _svg


@dataclass
class OptionsSet[T]:
    self_opts: list[Option[T]]
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
    ], False)  # don't inherit, this is the base case

    css_class: typing.ClassVar[str] = ""

    registry: typing.ClassVar[dict[str, type[DataConsumer]]] = {}

    def dynamic_namespaces() -> tuple[str, ...]:
        return ()

    @classmethod
    @typing.final
    def get_namespaces(cls) -> list[str]:
        copt = cls.options
        nss = [
            k for k, v in cls.registry.items() if v is cls]
        if copt.inherit:
            nss.extend(itertools.chain.from_iterable(
                p.get_namespaces() for p in copt.inherit_from))
        return nss

    @classmethod
    @typing.final
    def get_options(cls) -> list[Option]:
        copt = cls.options
        out = copt.self_opts.copy()
        if copt.inherit:
            paropts: itertools.chain[Option] = itertools.chain.from_iterable(
                p.get_options() for p in copt.inherit_from)
            if isinstance(copt.inherit, bool):
                out.extend(paropts)
            else:
                out.extend(opt for opt in paropts
                           if opt.name in copt.inherit)
        return out

    def to_xml_string(self, data: _data.Data) -> str:
        """Pull options relevant to this node from data, calls
        self.render(), and wraps the output in a <g>."""
        # recurse to get all of the namespaces
        namespaces = list(itertools.chain(
            self.get_namespaces(), self.dynamic_namespaces()))
        # recurse to get all of the pulled values
        options = self.get_options()
        # then the below
        values = {}
        for name in namespaces:
            values |= data.get_values_for(name)
        # validate the options
        print("***", options)
        for opt in options:
            if opt.name not in values:
                if opt.default is _OPT_IS_REQUIRED:
                    raise _errors.NoDataError(
                        f"missing value for {namespaces[-1]}.{opt.name}")
                values[opt.name] = opt.default
                continue
            if isinstance(opt.type, list):
                if values[opt.name] not in opt.type:
                    raise _errors.BOMError(
                        f"{namespaces[-1]}.{opt.name}: "
                        f"invalid choice: {values[opt.name]!r} "
                        f"(valid options are "
                        f"{', '.join(map(repr, opt.type))})")
                continue
            try:
                values[opt.name] = opt.type(values[opt.name])
            except ValueError as err:
                raise _errors.DataTypeError(
                    f"option {namespaces[-1]}.{opt.name}: "
                    f"invalid {opt.type.__name__} value: "
                    f"{values[opt.name]!r}") from err
        for key in values:
            if any(opt.name == key for opt in options):
                continue
            warnings.warn(
                f"unknown data key {key!r} for {namespaces[-1]}",
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

    @classmethod
    @typing.final
    def register[T: type[DataConsumer]](
            cls, namespace: str | None = None) -> typing.Callable[[T], T]:
        def register(cls2: type[DataConsumer]):
            if namespace:
                if namespace in cls.registry:
                    raise ValueError(f"{namespace} already registered as {
                        cls.registry[namespace]
                    }")
                cls.registry[namespace] = cls2
            if (cls2.options.inherit_from is None
                    and DataConsumer in cls2.mro()):
                cls2.options.inherit_from = cls2.__bases__
            return cls2
        return register
