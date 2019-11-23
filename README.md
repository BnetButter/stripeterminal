I am not affiliated with stripe in anyway.

Stripe's SDK for their P400 Terminal requires a web browser/driver. Not very helpful
if one has a non-browser based POS system. This package bridges the gap between
python and webdriver. Currently runs only on linux and requires chromedriver in /usr/local/bin/. 
You'll also need a stripe api key. Most of the testing I've done was on a physical terminal.
Not sure what happens if you use a virtual terminal. If you have all those things, use this package
at your discretion.

`pip install stripeterminal`