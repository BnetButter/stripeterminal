import types
import json
import asyncio

class _StripeAPI:

    def __init__(self, attribute, method):
        self._attribute = attribute
        self._method = method
        self._stripe_api_ = True
    
    def __get__(self, obj, typeobj=None):
        if obj is None:
            return self._method
        return types.MethodType(self._method, obj)


# _Metawrapper delegates obj.method call to a wrapper
# defined by obj's type's metaclass. ie. type(type(obj))
# Normally, calling obj.func is the result of types.MethodType(func, obj)
# which marshals in obj as the first argument of type(obj).func.
class _Metawrapper:

    def __new__(cls, wrapper_factory, name):
        obj = super().__new__(cls)
        cls.__init__(obj, wrapper_factory, name)
        setattr(wrapper_factory.__self__, name, obj)


    def __init__(self, wrapper_factory, name):
        self._typeobj = wrapper_factory.__self__
        self._function_def = self._get_type_attribute(name)
        self._wrapper_factory = wrapper_factory

    
    def __get__(self, obj, typeobj=None):
        if obj is None:
            return self._function_def
        return self._wrapper_factory(self._function_def, obj)
    

    def _get_type_attribute(self, name):
        attribute = self._typeobj.__dict__.get(name)
        if attribute is not None:
            return attribute
        
        else:
            for cls in self._typeobj.__mro__:
                attribute = getattr(cls, name, False)
                if attribute and not isinstance(cls, type(self._typeobj)):
                    return attribute

