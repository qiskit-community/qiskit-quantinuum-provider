# Qiskit Honeywell Provider

[![License](https://img.shields.io/github/license/qiskit-community/qiskit-honeywell-provider.svg?style=popout-square)](https://opensource.org/licenses/Apache-2.0)[![Build Status](https://img.shields.io/travis/com/qiskit-community/qiskit-honeywell-provider/master.svg?style=popout-square)](https://travis-ci.com/qiskit-community/qiskit-honeywell-provider)[![](https://img.shields.io/github/release/qiskit-community/qiskit-honeywell-provider.svg?style=popout-square)](https://github.com/qiskit-community/qiskit-honeywell-provider/releases)[![](https://img.shields.io/pypi/dm/qiskit-honeywell-provider.svg?style=popout-square)](https://pypi.org/project/qiskit-honeywell-provider/)

**Qiskit** is an open-source framework for working with noisy quantum computers at the level of pulses, circuits, and algorithms.

This project contains a provider that allows access to Honeywell quantum
devices.

## Installation

You can install the provider using pip:

```bash
pip3 install qiskit-honeywell-provider
```

`pip` will handle installing all the python dependencies automatically and you
will always install the latest version.

## Setting up the Honeywell Provider

Once the package is installed, you can access the provider from Qiskit via the following import:

```python3
from qiskit.providers.honeywell import Honeywell
```

You will need credentials for the Honeywell Quantum Service. This can either be
set via the `HQS_API_KEY` environment variable, or you can save that token to
disk with:

```python3
Honeywell.save_account('MYToken')
```

The credentials will then be loaded automatically on calls that return Backends,
or you can manually load the credentials with:

```python3
Honeywell.load_account()
```

which will first check if the env variable is set and use that token and if not
it will load any save credentials from disk.

With credentials loaded then you can access the backends from the provider:

```python3
backends = Honeywell.backends()
backend = Honeywell.get_backend(device)
```

You can then use that backend like you would use any other qiskit backend. For
example, running a bell state circuit:

```python3
from qiskit import *
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0,1], [0,1])
result = execute(qc, backend).result()
print(result.get_counts(qc))
```

## Using a proxy

To configure a proxy include it in the save account configuration:

```python3
Honeywell.save_account('MYToken', proxies = {'urls': {'http': 'http://user:password@myproxy:8080', 'https': 'http://user:password@myproxy:8080'}})
```

To remove the proxy you can save with an empty dictionary:

```python3
Honeywell.save_account('MYToken', proxies = {})
```

The 'urls' field must be a dictionary that maps a protocol type or url to a specific proxy.  Additional information/details can be found [here](https://requests.readthedocs.io/en/master/user/advanced/#proxies).

## License

[Apache License 2.0].

[Apache License 2.0]: https://github.com/qiskit-community/qiskit-honeywell-provider/blob/master/LICENSE.txt

