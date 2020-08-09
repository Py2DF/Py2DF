# Py2DF
==========

An easy to use and feature-rich tool to convert written, easier to understand python code to a DiamondFire template.

Installing
----------

**Python 3.6 or higher is required**

To install the library you can just run the following command:   THIS ISN'T LIVE YET BUT WILL BE SOON TM


    # Linux/macOS
    python3 -m pip install -U Py2DF.py

    # Windows
    py -3 -m pip install -U Py2DF.py


Quick Example
--------------
```py
@PlayerEvent.Join
def on_join():
    player.send_message("Test")
    player.give_items(Item(material=Material.DIAMOND_SWORD, name="My Sword", lore=["My custom sword"]))
    player.teleport(Location(50, 50, 50))
```
        

You can find more examples in the examples directory.

Links
------

- `Documentation <https://py2df.readthedocs.io/en/latest/index.html>`
- `Official Discord Server <https://discord.gg/eUVVRyE>`
