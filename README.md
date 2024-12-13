# HORIBA Python SDK

<div align="center">

[![build](https://github.com/HORIBAEzSpecSDK/horiba-python-sdk/actions/workflows/build.yml/badge.svg)](https://github.com/HORIBAEzSpecSDK/horiba-python-sdk/actions/workflows/build.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/horiba-sdk)](https://pypi.org/project/horiba-sdk/)
[![Python Version](https://img.shields.io/pypi/pyversions/horiba-sdk.svg)](https://pypi.org/project/horiba-sdk/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/HORIBAEzSpecSDK/horiba-python-sdk/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/HORIBAEzSpecSDK/horiba-python-sdk/blob/master/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/HORIBAEzSpecSDK/horiba-python-sdk/releases)
[![License](https://img.shields.io/github/license/HORIBAEzSpecSDK/horiba-python-sdk)](https://github.com/HORIBAEzSpecSDK/horiba-python-sdk/blob/master/LICENSE)
![Coverage Report](assets/images/coverage.svg)
[![Documentation Status](https://readthedocs.org/projects/horiba-python-sdk/badge/?version=latest)](https://horiba-python-sdk.readthedocs.io/en/latest/?badge=latest)


</div>

___

⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️⬇️

> [!WARNING]  
> This SDK is under development and not yet released.

> [!IMPORTANT]  
> For this python code to work, the SDK from Horiba has to be purchased, installed and licensed.
> The code in this repo and the SDK are under development and not yet released for public use!

⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️⬆️

___

# 📦 About this repository
`horiba-sdk` is a package that provides source code for the development of custom applications that include interaction with Horiba devices, namely monochromators and multichannel detectors (e.g. CCD cameras).
Future versions of this package will include access to more devices. The SDK exists for several programming languages:
- Python (this repo)
- [C#](https://github.com/HORIBAEzSpecSDK/dotnet-sdk)
- [C++](https://github.com/HORIBAEzSpecSDK/cpp-sdk)
- [LabVIEW](https://github.com/HORIBAEzSpecSDK/labview-sdk)

# ☑️ Prerequisites

To use this package, the following conditions must be met:
* Python `>=3.9` is installed
* ICL.exe installed as part of the `Horiba SDK`, licensed and activated. The Horiba SDK can be purchased by contacting the [Horiba Support](https://www.horiba.com/int/scientific/contact/) and sending a message to the `Scientific` business segment, specifying `no division` and selecting the `sales` department
*
  <details>
  <summary>To make sure that the USB devices do not get disconnected, uncheck the following boxes in the properties</summary>

  ![generic usb hub properties](docs/source/images/generic_usb_hub_properties.png)

  </details>

# 🛠️ Getting Started

<details>
<summary>Video of the steps below</summary>

![first steps in python](docs/source/images/python_first_steps.gif)

</details>

1. (Optional but recommended) Work in a virtual environment:

   Navigate to the (empty) project folder you want to work and run:

   ```bash
   python -m venv .
   ```

   Activate the virtual environment:

   <details>
   <summary>Windows</summary>

   ```powershell
   .\Scripts\activate
   ```
   </details>

   <details>
   <summary>Unix</summary>

   ```bash
   source ./bin/activate
   ```
   </details>

   *Note: do deactivate it, simply run `deactivate`.*


1. Install the sdk:

   ```bash
   pip install horiba-sdk
   ```

   or install with `Poetry`

   ```bash
   poetry add horiba-sdk
   ```

2. Create a file named `center_scan.py` and copy-paste the content of
   [`examples/asynchronous_examples/center_scan.py`](examples/asynchronous_examples/center_scan.py)

3. Install the required library for plotting the graph in the example:

   ```bash
   pip install matplotlib
   ```

   or install with `Poetry`

   ```bash
   poetry add matplotlib
   ```

4. Run the example with:

   ```bash
   python center_scan.py
   ```
# 🔗 Examples
## Getting Started
The files in the folder [examples/asynchronous_examples/](examples/asynchronous_examples) can be used as a starting point for a custom application.

## Tests
The files in the folder [tests/test_single_devices](tests/test_single_devices) can be used to explore further functionality.

## Asynchronous vs Synchronous Examples
This SDK is based on Websocket communication. The nature of this communication is asynchronous by its design.
The way this SDK uses websockets is to send requests to the underlying `instrument control layer (ICL)` and get a (nearly immediate) reply back.
This is true even for commands that longer to execute, e.g. to move the mono or to acquire data from the CCD. The way this is handled is by sending an acknowledgement back that the command is received and being processed. The user has then to inquire if `mono_isBusy` to see when the hardware is free to receive the next command.
That means that every `async` function can be `awaited` immediately and handled just like any other function.
To learn more about async and await, [check out this introduction](https://www.pythontutorial.net/python-concurrency/python-async-await/) or [take a deeper dive here](https://medium.com/@danielwume/an-in-depth-guide-to-asyncio-and-await-in-python-059c3ecc9d96).



# 🏗️ Architecture
The functionality is distributed over two parts, the `instrument control layer (ICL)` and the `github source code`. This split is shown in the following image:
![SDK Split](docs/SDK_Overview_Dark.png#gh-dark-mode-only "SDK Split")
![SDK Split](docs/SDK_Overview_Dark.png#gh-light-mode-only "SDK Split")

The ICL itself is sold and distributed by Horiba. The source code to communicate with the ICL and drive the instruments is located in this repo for Python, but can be also found for C#, C++ and LabVIEW as described above.
The communication between SDK and ICL is websocket based. I.e. in essence the ICL is steered by a `command and control` pattern where commands and their replies are JSON commands.

# 👩‍💻 First steps as contributor

## Clone and set up the repo

1. Clone the repo:
  
  ```bash
  git clone https://github.com/HORIBAEzSpecSDK/horiba-python-sdk.git
  cd horiba-python-sdk
  ```

2. If you don't have `Poetry` installed run:

```bash
make poetry-download
```

3. Initialize poetry and install `pre-commit` hooks:

```bash
make install
make pre-commit-install
```

4. Run the codestyle:

```bash
make codestyle
```

5. To push local changes to the remote repository, run:

```bash
git add .
git commit -m "feat: add new feature xyz"
git push
```

<!-- ### Set up bots -->

<!-- - Set up [Dependabot](https://docs.github.com/en/github/administering-a-repository/enabling-and-disabling-version-updates#enabling-github-dependabot-version-updates) to ensure you have the latest dependencies. -->
<!-- - Set up [Stale bot](https://github.com/apps/stale) for automatic issue closing. -->

## Poetry

Want to know more about Poetry? Check [its documentation](https://python-poetry.org/docs/).

<details>
<summary>Details about Poetry</summary>
<p>

Poetry's [commands](https://python-poetry.org/docs/cli/#commands) are very intuitive and easy to learn, like:

- `poetry add numpy@latest`
- `poetry run pytest`
- `poetry publish --build`

etc
</p>
</details>

## Building and releasing your package

Building a new version of the application contains steps:

- Bump the version of your package `poetry version <version>`. You can pass the new version explicitly, or a rule such as `major`, `minor`, or `patch`. For more details, refer to the [Semantic Versions](https://semver.org/) standard.
- Update the `CHANGELOG.md` with `git-changelog -B auto -Tio CHANGELOG.md`
- Make a commit to `GitHub`.
- Create a tag and push it. The release is automatically triggered on tag push:

  ```bash
  git tag vX.Y.Z # where the version MUST match the one you indicated before
  git push --tags
  ```

## Makefile usage

[`Makefile`](https://github.com/HORIBAEzSpecSDK/horiba-python-sdk/blob/master/Makefile) contains a lot of functions for faster development.

<details>
<summary>1. Installation of Poetry</summary>
<p>

To download and install Poetry run:

```bash
make poetry-download
```

To uninstall

```bash
make poetry-remove
```

</p>
</details>

<details>
<summary>2. Install all dependencies and pre-commit hooks</summary>
<p>

Install requirements:

```bash
make install
```

Pre-commit hooks could be installed after `git init` via

```bash
make pre-commit-install
```

</p>
</details>

<details>
<summary>3. Codestyle</summary>
<p>

Automatic formatting uses `pyupgrade`, `isort` and `black`.

```bash
make codestyle

# or use synonym
make formatting
```

Codestyle checks only, without rewriting files:

```bash
make check-codestyle
```

> Note: `check-codestyle` uses `isort`, `black` and `darglint` library

Update all dev libraries to the latest version using one comand

```bash
make update-dev-deps
```
</p>
</details>

<details>
<summary>4. Code security</summary>
<p>

```bash
make check-safety
```

This command launches `Poetry` integrity checks as well as identifies security issues with `Safety` and `Bandit`.

```bash
make check-safety
```


</p>
</details>

<details>
<summary>5. Type checks</summary>
<p>

Run `mypy` static type checker

```bash
make mypy
```

</p>
</details>

<details>
<summary>6. Tests with coverage badges</summary>
<p>

Run `pytest`

Unix:

```bash
make test
```

Windows:

```powershell
poetry run pytest -c pyproject.toml --cov-report=html --cov=horiba_sdk tests/
```

For the hardware tests run the following:

Windows:

```powershell
$env:HAS_HARDWARE="true"
# If you want a remote ICL be used for the tests
# $env:TEST_ICL_IP="192.168.21.24"
# $env:TEST_ICL_PORT="1234"
poetry run pytest -c pyproject.toml --cov-report=html --cov=horiba_sdk tests/
```

Unix:

```bash
HAS_HARDWARE="true"
# If you want a remote ICL be used for the tests
# TEST_ICL_IP="192.168.21.24"
# TEST_ICL_PORT="1234"
make test
```

</p>
</details>

<details>
<summary>7. All linters</summary>
<p>

Of course there is a command to ~~rule~~ run all linters in one:

```bash
make lint
```

the same as:

```bash
make test
make check-codestyle
make mypy
make check-safety
```

</p>
</details>

<details>
<summary>8. Docker</summary>
<p>

```bash
make docker-build
```

which is equivalent to:

```bash
make docker-build VERSION=latest
```

Remove docker image with

```bash
make docker-remove
```

More information [about docker](https://github.com/HORIBAEzSpecSDK/horiba-python-sdk/tree/master/docker).

</p>
</details>

<details>
<summary>9. Cleanup</summary>
<p>
Delete pycache files

```bash
make pycache-remove
```

Remove package build

```bash
make build-remove
```

Delete .DS_STORE files

```bash
make dsstore-remove
```

Remove .mypycache

```bash
make mypycache-remove
```

Or to remove all above run:

```bash
make cleanup
```
</p>
</details>

# 📚 Documentation

The latest documentation can be found at
[horiba-python-sdk.readthedocs.io](https://horiba-python-sdk.readthedocs.io/en/latest/).
In order to build it locally, run the following in the `docs/` folder:

```bash
make html
```

The documentation will then be built under `docs/build/html/`.

Documentation is built each time a commit is pushed on `main` or for pull
requests. When release tags are created in the repo, readthedocs will also tag
the documentation accordingly


## 🛡 License

[![License](https://img.shields.io/github/license/HORIBAEzSpecSDK/horiba-python-sdk)](https://github.com/HORIBAEzSpecSDK/horiba-python-sdk/blob/master/LICENSE)

This project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/HORIBAEzSpecSDK/horiba-python-sdk/blob/master/LICENSE) for more details.

## 📃 Citation

```bibtex
@misc{horiba-python-sdk,
  author = {ZühlkeEngineering},
  title = {'horiba-python-sdk' is a package that provides source code for the development with Horiba devices},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/HORIBAEzSpecSDK/horiba-python-sdk}}
}
```


## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)

This project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)
