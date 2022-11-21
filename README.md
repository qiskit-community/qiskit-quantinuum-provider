# Qiskit Quantinuum Provider

[![License](https://img.shields.io/github/license/qiskit-community/qiskit-quantinuum-provider.svg?style=popout-square)](https://opensource.org/licenses/Apache-2.0)[![Build Status](https://img.shields.io/travis/com/qiskit-community/qiskit-quantinuum-provider/master.svg?style=popout-square)](https://travis-ci.com/qiskit-community/qiskit-quantinuum-provider)[![](https://img.shields.io/github/release/qiskit-community/qiskit-quantinuum-provider.svg?style=popout-square)](https://github.com/qiskit-community/qiskit-quantinuum-provider/releases)[![](https://img.shields.io/pypi/dm/qiskit-quantinuum-provider.svg?style=popout-square)](https://pypi.org/project/qiskit-quantinuum-provider/)

**Qiskit** is an open-source framework for working with noisy quantum computers at the level of pulses, circuits, and algorithms.

This project contains a provider that allows access to Quantinuum quantum
devices.

## Installation

You can install the provider using pip:

```bash
pip3 install qiskit-quantinuum-provider
```

`pip` will handle installing all the python dependencies automatically and you
will always install the latest version.

## Setting up the Quantinuum Provider

Once the package is installed, you can access the provider from Qiskit via the following import:

```python3
from qiskit_quantinuum import Quantinuum
```

You will need credentials for the Quantinuum Quantum Service. Credentials are
tied to an e-mail address that can be stored on disk with:

```python3
Quantinuum.save_account('username@company.com')
```

After the initial saving of your account information, you will be prompted to enter
your password which will be used to acquire a token that will enable continuous
interaction until it expires.  Your password will **not** be saved to disk and will
be required infrequently to update the credentials stored on disk or when a new
machine must be authenticated.

The credentials will then be loaded automatically on calls that return Backends,
or can be manually loaded with:

```python3
Quantinuum.load_account()
```

This will load the most recently saved credentials from disk so that they can be provided
for each interaction with Quantinuum's devices.

Storing a new account will **not** invalidate your other stored credentials.  You may have an arbitrary
number of credentials saved.  To delete credentials you can use:

```python3
Quantinuum.delete_credentials()
```

Which will delete the current accounts credentials from the credential store.  Please keep in mind
this only deletes the current accounts credentials, and not all credentials stored.

With credentials loaded you can access the backends from the provider:

```python3
backends = Quantinuum.backends()
backend = Quantinuum.get_backend(device)
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

## License

[Apache License 2.0].

[Apache License 2.0]: https://github.com/qiskit-community/qiskit-quantinuum-provider/blob/master/LICENSE.txt

