# Copyright (C) <2019>  <Kevin Lai>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from stripeterminal.src.interface import StripeInterfaceType, StripeAPI
from stripeterminal.src.errors import StripeError
import stripe
import asyncio
import websockets
import enum


class PaymentStatus(enum.Enum):
    READY = "ready"
    NOT_READY = "not_ready"
    WAITING_FOR_INPUT = "waiting_for_input"
    PROCESSING = "processing"


# Enumerates the connection status to the physical terminal
class ConnectionStatus(enum.Enum):
    CONNECTED = "connected"
    CONNECTING = "connecting"
    NOT_CONNECTED = "not_connected"


class PaymentIntent(dict):
    
    def __init__(self, payment_intent=None, **kwargs):
        # cast dict obj to PaymentIntent object
        if isinstance(payment_intent, dict):
            super().__init__(payment_intent)
        
        # string value must be the id of a stripe.PaymentIntent object
        elif isinstance(payment_intent, str):
            super().__init__(self.retrieve(payment_intent))

        # create a new PaymentIntent object
        else:
            super().__init__(stripe.PaymentIntent.create(**kwargs))

    
    @staticmethod
    def retrieve(intent_id, client_secret=None):
        return stripe.PaymentIntent.retrieve(intent_id, client_secret)
    
    
    @staticmethod
    def all(**kwargs):
        stripe.PaymentIntent.list(**kwargs)
    
    
    def update(self, **kwargs):
        super().update(
            stripe.PaymentIntent.modify(
                self["id"],
                **kwargs
                ))
    

    def confirm(self, **kwargs):
        stripe.PaymentIntent.confirm(self["id"], **kwargs)
    

    def capture(self, **kwargs):
        stripe.PaymentIntent.capture(self["id"], **kwargs)


    def cancel(self, **kwargs):
        stripe.PaymentIntent.cancel(self["id"], **kwargs)



class PaymentMethod(dict):
    
    def __init__(self, obj=None, **kwargs):
        if isinstance(obj, dict):
            super().__init__(obj)
        elif isinstance(obj, str):
            super().__init__(stripe.PaymentMethod.retrieve(obj))
        else:
            super().__init__(stripe.PaymentMethod.create(**kwargs))


class DisplayInfo(dict):
    def __init__(self, line_items:list=None, tax:int=None, total:int=None,
            currency:str=None):
        
        super().__init__(
            type="cart",
            cart={
                "line_items": list() if line_items is None else list(),
                "tax":0 if tax is None else tax,
                "total": 0 if total is None else total,
                "currency": "usd" if total is None else currency,
                })
        

# pylint: disable=E0213
# pylint: disable=unsupported-membership-test
# pylint: disable=unsubscriptable-object
class StripeTerminal(metaclass=StripeInterfaceType):

    def __init__(self, secret, **kwargs): # silence pylint
        stripe.api_key = secret


    @StripeAPI("discoverReaders")
    def discover_readers(response,
            simulated:bool=None,
            location:dict=None) -> list:
        """Begins discovering readers. Returns a list of discovered readers."""
        return response["discoveredReaders"]

    @StripeAPI("connectReader")
    def connect_reader(response, reader:dict) -> dict:
        """Attempts to connect to the given reader. If successful, the given
        reader is returned. Otherwise raises StripeError"""
        return response["reader"]
    
    @StripeAPI("disconnectReader")
    def disconnect_reader(response) -> None:
        """Disconnects from the connected reader"""
        return None
    

    @StripeAPI("getConnectionStatus")
    def get_connection_status(response) -> ConnectionStatus:
        """Returns the current connection status."""
        return ConnectionStatus(response)
            

    @StripeAPI("getPaymentStatus")
    def get_payment_status(response) -> PaymentStatus:
        """Returns the reader's payment"""
        return PaymentStatus(response)


    @StripeAPI("clearCachedCredentials")
    def clear_cached_credentials(response) -> None:
        """Clears the current ConnectionToken, and any other cached 
        credentials."""
        return None
    

    @StripeAPI("collectPaymentMethod")
    def collect_payment_method(response, client_secret:str) -> PaymentIntent:
        """Begins collecting a payment method for a PaymentIntent. This method 
        takes a single argument, the 'client_secret' field from a PaymentIntent
        object. Returns the updated PaymentIntent object"""
        return PaymentIntent(response["paymentIntent"])


    @StripeAPI("cancelCollectPaymentMethod")
    def cancel_collect_payment_method(response) -> None:
        """Cancels an outstanding collectPaymentMethod command."""
        return None


    @StripeAPI("processPayment")
    def process_payment(
            response, payment_intent:PaymentIntent) -> PaymentIntent:
        """Processes a payment after a payment method has been collected.
        This method takes a single parameter, a PaymentIntent object obtained
        from a successful call to collect_payment_method."""
        return PaymentIntent(response["paymentIntent"])
    

    @StripeAPI("readReusableCard")
    def read_reusable_card(response) -> PaymentMethod:
        """Reads a card for reuse online."""
        return PaymentMethod(response)
            
    
    @StripeAPI("cancelReadReusableCard")
    def cancel_read_reusable_card(response) -> None:
        """Cancels an outstanding readReusableCard command."""
        return None


    @StripeAPI("setReaderDisplay")
    def set_reader_display(response, display_info:DisplayInfo) -> None:
        """Updates the reader display with cart details."""
        return None
    
    @StripeAPI("clearReaderDisplay")
    def clear_reader_display(response) -> None:
        """Clears the reader display and resets it to the splash screen."""
        return None
    
