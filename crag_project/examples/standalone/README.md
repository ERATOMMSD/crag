# Usage of CRAG as a standalone tool

CRAG can be run as a standalone executable. This folder provides an example for such a use case. In particular, we search for roads that result in large jerk (derivative of acceleration).

To start the search install CRAG and in this folder, execute

~~~sh
python example_as_a_standalone.py
~~~

This should result in a figure showing all generated roads and the one road that cause a vehicle with PID-controlled bicycle model to have the largest total jerk.

