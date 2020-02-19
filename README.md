# Qiskit Honeywell Provider

Qiskit-compliant implementation of provider that allows accessing the Honeywell quantum devices

The current implementation was developed off of version 0.8.0 of qiskit-terra. Use other versions at your own risk.

## Installation

To install this provider you must have qiskit-terra installed.
Installing this provider will automatically install qiskit-terra when using PIP.

We encourage installing this via the PIP tool (a python package manager), which will handle the dependencies as necessary (you may need C++ build dependencies)
```bash
pip3 install qiskit-honeywell-provider
```

## Setting up the Honeywell Provider
Once the package is installed, you can access the provider from Qiskit via the following import:

```python3
from qiskit.providers.honeywell import Honeywell
```

For convenience, it is also possible to replace the `__init__.py` in the top level qiskit-terra folder with the one in this archive under qiskit. Or simply add the following segment after the addition of the IBMQ Provider (~line 72 in 0.8.0):

```python3
# Try to import the Honeywell provider if installed.
try:
    from qiskit.providers.honeywell import Honeywell
except ImportError:
    pass
```
