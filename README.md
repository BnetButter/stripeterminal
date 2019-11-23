I am not affiliated with stripe in anyway.

Stripe's SDK for their P400 Terminal requires a web browser/driver. Not very helpful
if one has a non-browser based POS system. This package bridges the gap between
python and webdriver. Currently runs only on linux and requires chromedriver in /usr/local/bin/. 
You'll also need a stripe api key. Most of the testing I've done was on a physical terminal.
Not sure what happens if you use a virtual terminal. If you have all those things, use this package
at your discretion.

`pip install stripeterminal` doesn't work.

To use the provided interface...

```python
from stripeterminal import StripeTerminal

terminal = StripeTerminal("your_secret_key")

async def run_payment_flow_once():
    reader = (await terminal.discover_readers())[0]
    await terminal.connect_reader(reader)
    intent = PaymentIntent(
        amount=100,
        currency="usd",
        payment_method_types=["card_present"],
        capture_method="manual",
        )
    intent = await terminal.collect_payment_method(intent["client_secret"])
    intent = await terminal.process_payment(intent)
    intent.capture()

loop = asyncio.get_event_loop()
task = loop.create_task(run_payment_flow_once())
task.add_done_callback(lambda task: exit())
loop.run_forever()
```

To provide another interface...

```python
from stripeterminal import StripeInterfaceType

class MyStripeTerminal(metaclass=StripeInterfaceType):
  
    @StripeAPI("discoverReaders") # name of method
    def discoverReaders(message, simulated=None, location=None): # function prototype
        # process return message and return list of discovered readers.
        return message["discoveredReaders"]
    
    # implement other callbacks
```
