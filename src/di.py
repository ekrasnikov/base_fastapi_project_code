import abc
from typing import Callable, Type, TypeVar

import punq
from fastapi import Depends

T = TypeVar("T")
container = punq.Container()


def register(*args, **kwargs):
    if len(args) == 1 and not kwargs and callable(args[0]):
        cls = args[0]
        bases = cls.__bases__

        if len(bases) == 1 and bases[0] is object:
            container.register(cls)
        elif len(bases) == 1 and bases[0] is abc.ABC:
            raise ValueError("Cannot register ABC class")
        elif cls.__orig_bases__:
            # It looks like a generic dependency, register it as regular class
            container.register(cls)

        for base in cls.__bases__:
            container.register(base, cls)

        return cls
    else:

        def resolver(*resolve_args, **resolver_kwargs):
            scope = punq.Scope.singleton if kwargs.get("singleton", False) else punq.Scope.transient
            factory = punq.empty
            target = resolve_args[0]
            container.register(target, factory=factory, scope=scope, **resolver_kwargs)
            return target

        return resolver


def resolve(base: Type[T], **kwargs) -> Callable[[], T]:
    def resolver():
        return container.resolve(base, **kwargs)

    return resolver


def resolve_depends(base: Type[T], **kwargs) -> T:
    return Depends(resolve(base, **kwargs))
