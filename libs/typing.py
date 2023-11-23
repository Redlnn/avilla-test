import contextlib
import types
import typing
from typing import TYPE_CHECKING, Annotated, Any, TypeVar, Union, get_args


def get_origin(obj: Any) -> Any:
    return typing.get_origin(obj) or obj


def generic_isinstance(obj: Any, par: type | Any | tuple[type, ...]) -> bool:
    """检查 obj 是否是 args 中的一个类型, 支持泛型, Any, Union

    Args:
        obj (Any): 要检查的对象
        par (Union[type, Any, Tuple[type, ...]]): 要检查的对象的类型

    Returns:
        bool: 是否是类型
    """
    if TYPE_CHECKING:
        AnnotatedType = type
    else:
        AnnotatedType = type(Annotated[int, lambda x: x > 0])

    Unions: tuple[Any, ...] = (Union, types.UnionType)

    if par is Any:
        return True
    with contextlib.suppress(TypeError):
        if isinstance(par, AnnotatedType):
            return generic_isinstance(obj, get_args(par)[0])
        if isinstance(par, type | tuple):
            return isinstance(obj, par)
        if get_origin(par) in Unions:
            return any(generic_isinstance(obj, p) for p in get_args(par))
        if isinstance(par, TypeVar):
            if par.__constraints__:
                return any(generic_isinstance(obj, p) for p in par.__constraints__)
            if par.__bound__:
                return generic_isinstance(obj, par.__bound__)
    return False
