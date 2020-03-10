# Contributing

First read the overall project contributing guidelines. These are all
included in the qiskit documentation:

https://qiskit.org/documentation/contributing_to_qiskit.html

## Contributing to Qiskit Honeywell Provider

In addition to the general guidelines there are specific details for
contributing to the Honeywell provider, these are documented below.

### Tests

Once you've made a code change, it is important to verify that your change
does not break any existing tests and that any new tests that you've added
also run successfully. Before you open a new pull request for your change,
you'll want to run the test suite locally.

The easiest way to run the test suite is to use
[**tox**](https://tox.readthedocs.io/en/latest/#). You can install tox
with pip: `pip install -U tox`. Tox provides several advantages, but the
biggest one is that it builds an isolated virtualenv for running tests. This
means it does not pollute your system python when running. Additionally, the
environment that tox sets up matches the CI environment more closely and it
runs the tests in parallel (resulting in much faster execution). To run tests
on all installed supported python versions and lint/style checks you can simply
run `tox`. Or if you just want to run the tests once run for a specific python
version: `tox -epy37` (or replace py37 with the python version you want to use,
py35 or py36).

If you just want to run a subset of tests you can pass a selection regex to
the test runner. For example, if you want to run all tests that have "dag" in
the test id you can run: `tox -epy37 -- credentials`. You can pass arguments
directly to the test runner after the bare `--`. To see all the options on test
selection you can refer to the stestr manual:
https://stestr.readthedocs.io/en/stable/MANUAL.html#test-selection

If you want to run a single test module, test class, or individual test method
you can do this faster with the `-n`/`--no-discover` option. For example:

to run a module:
```
tox -epy37 -- -n test.test_honeywell_credentials
```
or to run the same module by path:

```
tox -epy37 -- -n test/test_honeywell_credentials.py
```
to run a class:

```
tox -epy37 -- -n test.test_honeywell_credentials.TestCredentials
```
to run a method:
```
tox -epy37 -- -n test.test_honeywell_credentials.TestCredentials.test_discover_credentials_no_creds
```

##### Online Tests

Some tests require that you have a Honeywell account configured. These tests
will be skipped if no credentials are available. If you want to run these tests
you need to have credentials configured either via the `HQS_API_KEY` environment
variable, or via a saved account locally. If you do not want to run these tests
but have configured credentials you can set the `QISKIT_TEST_SKIP_ONLINE` to
`True` (or `1`) and the online tests will also be skipped.
