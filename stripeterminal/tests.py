import asyncio
import unittest

from stripeterminal.src._wrappers import _Metawrapper
from stripeterminal.src import StripeTerminal

class test_Metawrapper(unittest.TestCase):
    def setUp(self):
        self.SomeBase_obj = self.SomeBase()
        self.SomeSubclass_obj = self.SomeSubclass()
        self.AnotherSubclass_obj = self.AnotherSubclass()

    # call the wrapper returned by SomeSubclass._method_wrapper_factory
    def test_SomeSubclass_is_ten_plus_one(self):
        self.assertEqual(self.SomeSubclass_obj.return_ten(), 11)
    
    # test super call to a base class (which is not instanced by SomeType)
    # is preserved
    def test_super_is_ten_plus_one(self):
        self.assertEqual(
            super(self.SomeSubclass, self.SomeSubclass_obj).return_ten(),
            10,
            )
    
    # test wrapper is applied to function defined 
    # by SomeSubclass' namespace.
    def test_return_one_is_two(self):
        self.assertEqual(self.SomeSubclass_obj.return_one(), 2)

    # test wrapper is applied only to
    # instance.method, not class.function
    def test_return_ten_is_return_ten(self):
        self.assertEqual(
            self.SomeSubclass.return_ten,
            self.SomeBase.return_ten,
            )
    
    def test_super_call_to_a_SomeType_instance(self):
        self.assertEqual(
            super(self.AnotherSubclass, self.AnotherSubclass_obj).return_one(),
            2,
            )

    class SomeBase:
        def return_ten(self):
            return 10

    class SomeType(type):

        def _method_wrapper_factory(self, func, obj):

            # calling a method wrapped by _Metawrapped executes this function            
            def wrapper(*args, **kwargs):
                return func(obj, *args, **kwargs) + 1
            return wrapper

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # apply wrappers to function
            _Metawrapper(
                self._method_wrapper_factory,
                "return_ten",
                )
            _Metawrapper(
                self._method_wrapper_factory,
                "return_one",
                )


    class SomeSubclass(SomeBase, metaclass=SomeType):
        
        # calling return_one should return two
        def return_one(self):
            return 1
    

    class AnotherSubclass(SomeSubclass):
        ...


if __name__ == "__main__":
    unittest.main()
