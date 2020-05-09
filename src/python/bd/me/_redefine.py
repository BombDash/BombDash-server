# Copyright (c) 2020 BombDash
from __future__ import annotations

from typing import TYPE_CHECKING

from types import FunctionType
import enum

if TYPE_CHECKING:
    from typing import Type, Callable, Any, Tuple


def redefine_method(dst: Tuple[Any, str], src: Tuple[Any, str]) -> None:
    if hasattr(getattr(*src), '__redefine_type') and getattr(*src).__redefine_type in (
            RedefineFlag.DECORATE_PRE, RedefineFlag.DECORATE_AFTER, RedefineFlag.DECORATE_ADVANCED):
        new = getattr(*src)
        old = getattr(*dst)
        func: Callable
        if getattr(*src).__redefine_type == RedefineFlag.DECORATE_AFTER:
            def func(*args, **kwargs):
                returned = old(*args, **kwargs)
                return new(*args, **kwargs, returned=returned)
        elif getattr(*src).__redefine_type == RedefineFlag.DECORATE_PRE:
            def func(*args, **kwargs):
                new(*args, **kwargs)
                return old(*args, **kwargs)
        else:
            def func(*args, **kwargs):
                return new(*args, **kwargs, old_function=old)

        setattr(*dst, func)
    else:
        setattr(*dst, getattr(*src))

    # Fucking super()!
    # dst.__code__ = CodeType(
    #     src.__code__.co_argcount,
    #     src.__code__.co_posonlyargcount,
    #     src.__code__.co_kwonlyargcount,
    #     src.__code__.co_nlocals,
    #     src.__code__.co_stacksize,
    #     src.__code__.co_flags,
    #     src.__code__.co_code,
    #     src.__code__.co_consts,
    #     src.__code__.co_names,
    #     src.__code__.co_varnames,
    #     src.__code__.co_filename,
    #     dst.__code__.co_name,
    #     src.__code__.co_firstlineno,
    #     src.__code__.co_lnotab,
    #     dst.__code__.co_freevars,
    #     dst.__code__.co_cellvars)


def redefine_class_methods(orig_cls: Type[object]) -> Callable[[Any], None]:
    """Returns decorator that redefines all class methods

    Parameters:
         orig_cls (Type[object]): class that will redefined"""

    def decorator(cls) -> None:
        # for method in filter(lambda x: isinstance(getattr(cls, x), FunctionType), dir(cls)):
        for method in cls._redefine_methods:
            if hasattr(orig_cls, method):
                redefine_method((orig_cls, method), (cls, method))
            else:
                setattr(orig_cls, method, getattr(cls, method))
                # setattr(getattr(orig_cls, 'self'), '__class__', getattr(cls, method))  # Fucking super()!!!!

    return decorator


class RedefineFlag(enum.Enum):
    REDEFINE = 0
    DECORATE_AFTER = 1
    DECORATE_PRE = 2
    DECORATE_ADVANCED = 3
    DECORATE = DECORATE_AFTER


def redefine_flag(*flags: RedefineFlag) -> Callable[[Callable], Callable]:
    def decorator(func: Callable) -> Callable:
        for flag in flags:
            if flag in (RedefineFlag.DECORATE_AFTER, RedefineFlag.REDEFINE, RedefineFlag.DECORATE_PRE,
                        RedefineFlag.DECORATE_ADVANCED):
                func.__redefine_type = flag
        return func

    return decorator

# if __name__ == '__main__':  # Simple testing
#     class Base:
#         def a(self):
#             print('base a')
#
#         def c(self):
#             print('method c')
#
#     class Egg(Base):
#         def a(self):
#             super().a()
#             print('hello!')
#
#         def b(self, name):
#             print(f'hello {name}!')
#             return 123
#
#         def d(self):
#             print('just d')
#
#     egg = Egg()
#
#     @redefine_class_methods(Egg)
#     class RedefineEgg(Base):
#         _redefine_methods = ('a', 'b', 'c')
#
#         def a(self):
#             Base.a(self)
#             print('bye!')
#
#         @redefine_flag(RedefineFlag.DECORATE_AFTER)
#         def b(self, name, returned=None):
#             print(f'bye, {name}! {returned=}')
#
#         def c(self):
#             print('redefined c')
#
#     egg.a()
#     egg.b('roma')
#     egg.c()
#     egg.d()
