# horiba-python-sdk

<div align="center">

[![build](https://github.com/ThatsTheEnd/horiba-python-sdk/actions/workflows/build.yml/badge.svg)](https://github.com/ThatsTheEnd/horiba-python-sdk/actions/workflows/build.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/horiba-sdk)](https://pypi.org/project/horiba-sdk/)
[![Python Version](https://img.shields.io/pypi/pyversions/horiba-sdk.svg)](https://pypi.org/project/horiba-sdk/)
[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/ThatsTheEnd/horiba-python-sdk/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/ThatsTheEnd/horiba-python-sdk/releases)
[![License](https://img.shields.io/github/license/ThatsTheEnd/horiba-python-sdk)](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/LICENSE)
![Coverage Report](assets/images/coverage.svg)
[![Documentation Status](https://readthedocs.org/projects/horiba-python-sdk/badge/?version=latest)](https://horiba-python-sdk.readthedocs.io/en/latest/?badge=latest)

'horiba-sdk' is a package that provides source code for the development with Horiba devices

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

**📦 Prerequisites**

* Python `>=3.9`
* ICL.exe installed as part of the Horiba SDK, licensed and activated

  <details>
  <summary>To make sure that the USB devices do not get disconnected, uncheck the following boxes in the properties</summary>

  ![generic usb hub properties](docs/source/images/generic_usb_hub_properties.png)

  </details>

## 🛠️ Usage

<details>
<summary>Video of the steps below</summary>

![first steps in python](docs/source/images/python_first_steps.gif)

</details>

0. (Optional but recommended) Work in a virtual environment:

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

## 👩‍💻 First steps as contributor

### Clone and setup the repo

1. Clone the repo:

```bash
git clone https://github.com/ThatsTheEnd/horiba-python-sdk.git
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

### Poetry

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

### Building and releasing your package

Building a new version of the application contains steps:

- Bump the version of your package `poetry version <version>`. You can pass the new version explicitly, or a rule such as `major`, `minor`, or `patch`. For more details, refer to the [Semantic Versions](https://semver.org/) standard.
- Update the `CHANGELOG.md` with `git-changelog -B auto -Tio CHANGELOG.md`
- Make a commit to `GitHub`.
- Create a tag and push it. The release is automatically triggered on tag push:

  ```bash
  git tag vX.Y.Z # where the version MUST match the one you indicated before
  git push --tags
  ```

### Makefile usage

[`Makefile`](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/Makefile) contains a lot of functions for faster development.

<details>
<summary>1. Download and remove Poetry</summary>
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

Pre-commit hooks coulb be installed after `git init` via

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

More information [about docker](https://github.com/ThatsTheEnd/horiba-python-sdk/tree/master/docker).

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

## 📚 Documentation

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

## 🚀 Features

### Development features

- Supports for `Python 3.9` and higher.
- [`Poetry`](https://python-poetry.org/) as the dependencies manager. See configuration in [`pyproject.toml`](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/pyproject.toml).
- Automatic codestyle with [`ruff`](https://github.com/astral-sh/ruff)
- Ready-to-use [`pre-commit`](https://pre-commit.com/) hooks with code-formatting.
- Type checks with [`mypy`](https://mypy.readthedocs.io); security checks with [`safety`](https://github.com/pyupio/safety) and [`bandit`](https://github.com/PyCQA/bandit)
- Testing with [`pytest`](https://docs.pytest.org/en/latest/).
- Ready-to-use [`.editorconfig`](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/.editorconfig), [`.dockerignore`](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/.dockerignore), and [`.gitignore`](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/.gitignore). You don't have to worry about those things.

### Deployment features

- `GitHub` integration: issue and pr templates.
- `Github Actions` with predefined [build workflow](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/.github/workflows/build.yml) as the default CI/CD.
- Everything is already set up for security checks, codestyle checks, code formatting, testing, linting, docker builds, etc with [`Makefile`](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/Makefile#L89). More details in [makefile-usage](#makefile-usage).
- [Dockerfile](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/docker/Dockerfile) for your package.
- Always up-to-date dependencies with [`@dependabot`](https://dependabot.com/). You will only [enable it](https://docs.github.com/en/github/administering-a-repository/enabling-and-disabling-version-updates#enabling-github-dependabot-version-updates).
- Automatic drafts of new releases with [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). You may see the list of labels in [`release-drafter.yml`](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/.github/release-drafter.yml). Works perfectly with [Semantic Versions](https://semver.org/) specification.

### Open source community features

- Ready-to-use [Pull Requests templates](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/.github/PULL_REQUEST_TEMPLATE.md) and several [Issue templates](https://github.com/ThatsTheEnd/horiba-python-sdk/tree/master/.github/ISSUE_TEMPLATE).
- Files such as: `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, and `SECURITY.md` are generated automatically.
- [Semantic Versions](https://semver.org/) specification with [`Release Drafter`](https://github.com/marketplace/actions/release-drafter).
<!-- - [`Stale bot`](https://github.com/apps/stale) that closes abandoned issues after a period of inactivity. (You will only [need to setup free plan](https://github.com/marketplace/stale)). Configuration is [here](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/.github/.stale.yml). -->


## 📈 Releases

You can see the list of available releases on the [GitHub Releases](https://github.com/ThatsTheEnd/horiba-python-sdk/releases) page.

We follow [Semantic Versions](https://semver.org/) specification.

<!-- We use [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). As pull requests are merged, a draft release is kept up-to-date listing the changes, ready to publish when you’re ready. With the categories option, you can categorize pull requests in release notes using labels. -->

### List of labels and corresponding titles

|               **Label**               |  **Title in Releases**  |
| :-----------------------------------: | :---------------------: |
|       `enhancement`, `feature`        |       🚀 Features       |
| `bug`, `refactoring`, `bugfix`, `fix` | 🔧 Fixes & Refactoring  |
|       `build`, `ci`, `testing`        | 📦 Build System & CI/CD |
|              `breaking`               |   💥 Breaking Changes   |
|            `documentation`            |    📝 Documentation     |
|            `dependencies`             | ⬆️ Dependencies updates |

<!-- You can update it in [`release-drafter.yml`](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/.github/release-drafter.yml). -->

<!-- GitHub creates the `bug`, `enhancement`, and `documentation` labels for you. Dependabot creates the `dependencies` label. Create the remaining labels on the Issues tab of your GitHub repository, when you need them. -->

## 🛡 License

[![License](https://img.shields.io/github/license/ThatsTheEnd/horiba-python-sdk)](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/LICENSE)

This project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/ThatsTheEnd/horiba-python-sdk/blob/master/LICENSE) for more details.

## 📃 Citation

```bibtex
@misc{horiba-python-sdk,
  author = {ZühlkeEngineering},
  title = {'horiba-python-sdk' is a package that provides source code for the development with Horiba devices},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/ThatsTheEnd/horiba-python-sdk}}
}
```

## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)

This project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)
