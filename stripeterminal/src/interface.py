from stripeterminal.src import _wrappers
from stripeterminal.src.errors import StripeError
from stripeterminal.src import client
import types
import abc
import json
import asyncio
import websockets
import stripe

def StripeAPI(attribute):
    """Retrieve attribute from JavaScript client object"""
    return types.MethodType(_wrappers._StripeAPI, attribute)


class StripeInterfaceType(abc.ABCMeta):
    """This class defines the protocol, default arguments, and instance values
    to execute the RPC protocol. They are defined by the metaclass because
    the attributes must agree with the JavaScript client.
    The class definition of StripeInterfaceType's instance must define the
    following:
    >   - Property name of the JS terminal object with the @StripeAPI decorator

    >   - Method name which starts the execution of the RPC via a function def
    
    >   - Fucntion prototype for arguments and how to handle the returned

    In the unlikely event that an API method name would change, updating
    this package is a simple matter of changing the property name argument of
    @StripeAPI decorator. Unless the `window.StripeTerminal.create` path changes
    in the SDK, the browser client code need never be recompiled.
    To preserve source compatibility, under no circumstances should the names of
    the methods which execute the RPC call be changed.

    example terminal interface implementation
    ```
    class StripeTerminal(metaclass=StripeInterfaceType):

        # does not require a stripe.api_key to be set
        @StripeAPI("discoverReaders")
        def discover_readers(
                message,
                simulated=None,
                location=None
                ) -> list:
            "Returns a list of discovered readers on this network"
            return message["discoveredReaders"]


    if __name__ == "__main__":
        terminal = StripeTerminal()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(terminal.discover_readers(simulated=True))
    >>> [{...}]
    ```"""
    instance = None # meta-singleton

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = asyncio.get_event_loop()
        return_handlers = (
            method for method in self.__dict__.values()
                if getattr(method, "_stripe_api_", False)
                )

        for _stripe_api_ in list(return_handlers):
            attr = _stripe_api_._method.__name__
            setattr(self, "_" + attr, self._remote_call_wrapper_factory)
            _wrappers._Metawrapper(self._remote_call_wrapper_factory, attr)

        # readonly
        self.connection_token = property(
            lambda instance: stripe.terminal.ConnectionToken.create()
            )

        # when terminal disconnects, javascript client will send a message
        # alerting python host. the server handler should call this method
        self.unexpected_disconnect_handler = property(
            self._disconnect_handler_getter,
            self._disconnect_handler_setter,
            )
        
        # readonly
        self.remote_call_executor = property(
            lambda instance: instance._remote_call_executor
            )
        self.websocket_server_handler = property(
            lambda instance: instance._websocket_server_handler
            )


    def __call__(self, *args, **kwargs):
        # StripeInterfaceType may instance several types. However
        # only one instance of any type may be instanced to preclude the
        # possiblity of multiple calls.
        cls = type(self)
        if cls.instance is None:
            # consume keyword arguments
            loop = kwargs.pop("loop", None)
            host = kwargs.pop("host", None)
            port = kwargs.pop("port", None)
            
            loop = asyncio.get_event_loop() if loop is None else loop
            host = "localhost" if host is None else host

            port = 5000 if port is None else port # websockets port
            client.run(host, 8000)                # http port

            cls.instance = super().__call__(*args, **kwargs)
            cls.instance._unexpected_disconnect_handler = None
            cls.instance._browser_client = None
            cls.instance._client_connected_event = asyncio.Event(loop=loop)
            cls.instance._result_returned_event = asyncio.Event(loop=loop)
            cls.instance._result = None
            cls.instance
            cls.instance._loop = (
                asyncio.get_event_loop() if loop is None else loop)
                        
            # bind methods which execute RPC protocol
            cls.instance._remote_call_executor = types.MethodType(
                self._remote_call_executor,
                cls.instance
                )
            cls.instance._websocket_server_handler = types.MethodType(
                self._websocket_server_handler,
                cls.instance
                )
            
            cls.instance._loop.run_until_complete(
                websockets.serve(
                    cls.instance.websocket_server_handler,
                    host,
                    port,
                ))
        return cls.instance


    def _remote_call_wrapper_factory(self, func, obj):
        async def executor(*args, **kwargs):
            message = json.dumps(
                {
                    "attribute":func._attribute,
                    "args":args,
                    "kwargs":kwargs
                })
            result = await self._remote_call_executor(obj, message)
            if result == "undefined" or result is None:
                raise AttributeError(
                    f"'{type(obj).__name__}'' has no attribute"
                    f" '{func._method.__name__}'"
                )
            result = json.loads(result)
            if isinstance(result, dict) and "error" in result:
                err, err_msg = result["error"]
                raise StripeError(err, err_msg)
            else:
                return (
                    await func._method(result, *args, **kwargs)
                    if asyncio.iscoroutinefunction(func._method) else
                        func._method(result, *args, **kwargs))

        return executor


    @staticmethod
    def _disconnect_handler_setter(instance, handler):
        instance._unexpected_disconnect_handler = handler


    @staticmethod
    def _disconnect_handler_getter(instance):
        if instance._unexpected_disconnect_handler is None:
            # default handler
            def handler():
                raise RuntimeError("terminal disconnected")
            return handler
        return instance._unexpected_disconnect_handler

    
    @staticmethod
    async def _remote_call_executor(instance, message):
        await instance._client_connected_event.wait()
        assert instance._browser_client is not None
        await instance._browser_client.send(message)

        # wait for js client to finish the request
        await instance._result_returned_event.wait()
        result = instance._result

        # clear the event to process the next message
        instance._result_returned_event.clear()
        return result

    @staticmethod
    async def _websocket_server_handler(instance, ws, path):
        instance._client_connected_event.set()
        instance._browser_client = ws
        async for message in ws:

                rc = json.loads(message)
                if "attribute" in rc:
                    attribute = getattr(instance, rc["attribute"])
                    if callable(attribute):
                        args = rc["args"]
                        kwargs = rc["kwargs"]
                        reply = {
                            "attribute": rc["attribute"],
                            "result": await attribute(*args, **kwargs)
                                if asyncio.iscoroutinefunction(attribute)
                                else attribute(*args, **kwargs)
                        }
                    else:
                        reply = {
                            "attribute": rc["attribute"],
                            "result": attribute,
                            }
                    await ws.send(json.dumps(reply))
                else:
                    instance._result = message
                    instance._result_returned_event.set()
       
        instance._browser_client = None
        instance._client_connected_event.clear()


__all__ = ["StripeInterfaceType", "StripeAPI"]
