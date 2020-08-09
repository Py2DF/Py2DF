# Py2DF
==========

.. image:: https://img.shields.io/pypi/v/py2df.svg
   :target: https://pypi.python.org/pypi/py2df
   :alt: PyPI version info
.. image:: https://img.shields.io/pypi/pyversions/py2df.svg
   :target: https://pypi.python.org/pypi/py2df
   :alt: PyPI supported Python versions

An easy to use and feature-rich tool to convert written, easier to understand python code to a DiamondFire template.

Installing
----------

**Python 3.6 or higher is required**

To install the library you can just run the following command:


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
