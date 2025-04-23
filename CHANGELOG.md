# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [v0.6.0](https://github.com/HORIBAEzSpecSDK/python-sdk/releases/tag/v0.6.0) - 2025-04-23

<small>[Compare with v0.5.4](https://github.com/HORIBAEzSpecSDK/python-sdk/compare/v0.5.4...v0.6.0)</small>

### Added

- added mono code to raman shift example ([d53b7af](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/d53b7afac51d5cb7ea6f1fe73ea534d60e808ad2) by DESKTOP-R7JVAOO\Dell_Z84534).
- added save_spectracq3_data_to_csv function ([ebef175](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/ebef1752be8f31ea07ae44f69d0e1105c394b9ac) by DESKTOP-R7JVAOO\Dell_Z84534).
- added new example for acquisition with spectracq3 ([972f4dd](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/972f4dd086953898bfb3be74515191d15ca10a9d) by DESKTOP-R7JVAOO\Dell_Z84534).
- added skip for test if there is no hardware ([bd15029](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/bd15029657475920139920652be458db2cb44be1) by ads\arbh).
- added unit test for polarity ([b142de9](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/b142de9ae3c6c8505f7b2a7a9d4c2486632fa032) by ads\arbh).
- added TriggerInputPolarity enuma class and added commands for polarity ([ff892ec](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/ff892ecd5b1f1f2303694370b14bd29c39aba5a8) by ads\arbh).
- Add methods to retrieve firmware, FPGA version, and board revision; update acquisition control methods ([0c652c6](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/0c652c65b600c23537f42efeeee2cebbafed3200) by DESKTOP-R7JVAOO\Dell_Z84534).
- Add hardware test for SpectrAcq3 serial number retrieval ([16ad258](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/16ad258ab7eda51ce881a6eb1d603c572a41f7d6) by DESKTOP-R7JVAOO\Dell_Z84534).
- Add SpectrAcq3 device support to DeviceManager and documentation ([e57a59d](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/e57a59dbbafd2c7fbe1b9dbb6d8a9017133c99f3) by DESKTOP-R7JVAOO\Dell_Z84534).

### Fixed

- fix: update marshmallow to version 4.0.0 and add backports-datetime-fromisoformat dependency ([d8e75e2](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/d8e75e2aeff06196444bec4ba7d2e4e29ff93dd4) by DESKTOP-R7JVAOO\Dell_Z84534).
- fix: update Makefile safety checks and bump marshmallow version in poetry.lock ([8e5d73b](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/8e5d73b1bb90f8c98d9f98eabee18f643f42029a) by DESKTOP-R7JVAOO\Dell_Z84534).
- fix: add jinja2 dependency in pyproject.toml ([3e48e3d](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/3e48e3d43c65022994199a7f0452f11e5c5aee73) by DESKTOP-R7JVAOO\Dell_Z84534).
- fix: bump version to 0.6.0 in pyproject.toml ([acb4bd2](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/acb4bd2f0110a3983cacd4bf10203a5eb211d715) by DESKTOP-R7JVAOO\Dell_Z84534).
- fix: update spectrum stitching logic and adjust wavelength handling in range scan ([ea9f5fd](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/ea9f5fd9a71aa7eaa050426f6c85e13bfd146ea5) by DESKTOP-R7JVAOO\Dell_Z84534).
- fix: reduce CCD acquisition count from 200 to 100 ([f7f1acd](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/f7f1acd12c51d65496904cca4eeb0a7999bc5f16) by DESKTOP-R7JVAOO\Dell_Z84534).
- fix: include wavelength in saved spectracq3 data and update CSV saving logic ([1dff282](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/1dff282f978cc0e4fcb941448b0c6d64eb866034) by DESKTOP-R7JVAOO\Dell_Z84534).
- fix: allow user input for excitation and target wavelengths ([f86b6ab](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/f86b6abf0c0d657773b1b036ca55b6dff35e9491) by DESKTOP-R7JVAOO\Dell_Z84534).
- fix: remove unnecessary center wavelength setting before acquisition ([b0323e7](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/b0323e7213330bf7f3b22acbfaa5516502b301c6) by DESKTOP-R7JVAOO\Dell_Z84534).
- fix: enable waiting for saq3 acquisition before data collection ([787fd25](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/787fd25f23694755e011e593ba4e1fa6b1ab4059) by DESKTOP-R7JVAOO\Dell_Z84534).
- fixed errors in example ([f99b3ca](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/f99b3ca2f0a6691d1be97bf88bb39929af9780f9) by DESKTOP-R7JVAOO\Dell_Z84534).
- fixed ccd unit tests wit hw ([debaddc](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/debaddc8c7e4e86b6695424c89f9cb74e128775c) by DESKTOP-R7JVAOO\Dell_Z84534).
- fixed image.py ([ee17841](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/ee17841020986272765adbd0d05b90964d54824c) by DESKTOP-R7JVAOO\Dell_Z84534).
- fixed test_ccd_acquisition_abort test ([77bcb76](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/77bcb76a554583a779c851b1944167e4a85ec19b) by DESKTOP-R7JVAOO\Dell_Z84534).
- fixed test_ccd_range_mode_positions() test ([9df9a04](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/9df9a04965720fa2a40f927850ea3a550d7ba715) by DESKTOP-R7JVAOO\Dell_Z84534).
- fixed some tests ([f9f0498](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/f9f0498076965bb825f8531fc520f5ea94421e5c) by DESKTOP-R7JVAOO\Dell_Z84534).

### Changed

- changed get_error_log return type from str to list[str] ([5572e77](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/5572e771739064e9c1b0565dbdf6433a591489c4) by DESKTOP-R7JVAOO\Dell_Z84534).
- changed saq3_defineAcqSet to saq3_setAcqSet and renamed method ([fc39b9b](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/fc39b9b9812654808bb2b46ac735136b2066845f) by ads\arbh).

### Removed

- removed unneeded variables ([248b456](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/248b456fa5d1c64b0c935fb6d2b5d2b2c3c6e9b0) by DESKTOP-R7JVAOO\Dell_Z84534).
- removed a wait ([80bf1d8](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/80bf1d8e2e97a8b0f7e05b0adb86e1a95f03df90) by DESKTOP-R7JVAOO\Dell_Z84534).
- removed integration time call that wasn't removed before ([7fbaa87](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/7fbaa871262fba7a30c414c0c8a3e5916eb87432) by ads\arbh).
- removed integration time commands and unit test ([f5e99bb](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/f5e99bb8b904772096d061be7b13c7a25cad5ad9) by ads\arbh).

## [v0.5.4](https://github.com/HORIBAEzSpecSDK/python-sdk/releases/tag/v0.5.4) - 2024-12-13

<small>[Compare with v0.5.3](https://github.com/HORIBAEzSpecSDK/python-sdk/compare/v0.5.3...v0.5.4)</small>

## [v0.5.3](https://github.com/HORIBAEzSpecSDK/python-sdk/releases/tag/v0.5.3) - 2024-12-13

<small>[Compare with v0.5.2](https://github.com/HORIBAEzSpecSDK/python-sdk/compare/v0.5.2...v0.5.3)</small>

## [v0.5.2](https://github.com/HORIBAEzSpecSDK/python-sdk/releases/tag/v0.5.2) - 2024-12-13

<small>[Compare with v0.5.1](https://github.com/HORIBAEzSpecSDK/python-sdk/compare/v0.5.1...v0.5.2)</small>

### Fixed

- Fix/bump version (#12) ([4343c7c](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/4343c7c585dc8cc96f209c1d91dc62c678c0b134) by ThatsTheEnd).

## [v0.5.1](https://github.com/HORIBAEzSpecSDK/python-sdk/releases/tag/v0.5.1) - 2024-12-13

<small>[Compare with first commit](https://github.com/HORIBAEzSpecSDK/python-sdk/compare/a2e72bf27ae8064315e37225ce069611c4bf6670...v0.5.1)</small>

### Added

- added image example (#8) ([495ced7](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/495ced7988c416ca3a57abc63af0ca2140b7cdfb) by peter-bartalis). Co-authored-by: Peter Bartalis <PBartalis@horiba.lcl>, Co-authored-by: Samuel Gauthier <samuel.gauthier@zuehlke.com>, Co-authored-by: ThatsTheEnd <66672184+ThatsTheEnd@users.noreply.github.com>
- Addition of missing icl commands (#9) ([74dfe09](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/74dfe09444669bf7d69d60fb4cd251e598f5c360) by bharathZE). Co-authored-by: ThatsTheEnd <66672184+ThatsTheEnd@users.noreply.github.com>
- adds warning also to readthedocs (#53) ([7abb223](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/7abb2239be5e83cfc01542e18c2e810edcb0af9c) by ThatsTheEnd).
- add steps to create virtual env in readme (#49) ([cb51f44](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/cb51f44679a60d0da0caf84191a9324b69bac96a) by Samuel Gauthier).
- add all icl commands ([ee2dab0](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/ee2dab0c24ed765d96af5bfd6b3ddb3890277015) by Samuel Gauthier). Co-authored-by: Nikolaus Naredi-Rainer <nikolaus.naredi-rainer@zuehlke.com>
- add updated ICL API doc ([895fcd2](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/895fcd28bc2a2935020e41ef90b247e5cdfc8366) by isadiq-horiba).

### Fixed

- Fix/stitching (#11) ([d3c9757](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/d3c9757217c150cfa44704deee42ef939c0f25d4) by ThatsTheEnd). Co-authored-by: Peter Bartalis <PBartalis@horiba.lcl>, Co-authored-by: horiba-contributor <peterbartalis@gmail.com>, Co-authored-by: peter-bartalis <peter.bartalis@horiba.com>, Co-authored-by: Samuel Gauthier <46560807+w-samuelgauthier@users.noreply.github.com>, Co-authored-by: Samuel Gauthier <work.samuel.gauthier@gmail.com>, Co-authored-by: ads\arbh <bharath.arun@zuehlke.com>
- fixed range_scan.py (#5) ([0972729](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/0972729d40c9aaef76497e47a3d564ae12650aba) by peter-bartalis). Co-authored-by: Peter Bartalis <PBartalis@horiba.lcl>
- Fix/update readme (#52) ([7d5d5cc](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/7d5d5ccf1d8401b09addca6de227c2d49d04fb12) by ThatsTheEnd).
- fix readme gif (#51) ([5c7c172](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/5c7c172a6f9ad479f48946ab684481f8ca5ad62c) by Samuel Gauthier).
- fix pipeline step for publishing on pypi (#47) ([2fe8c28](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/2fe8c28fc094e9d876e8967c88d110ef991f9bfd) by Samuel Gauthier).
- fix link to classes in docstrings ([adffc64](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/adffc6470989502fdaad663c996943d4444d3013) by Samuel Gauthier).
- fixes: workflow ([16bd35f](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/16bd35f24dc12e60bc055f644e5439011b239334) by Nikolaus Naredi-Rainer).

### Removed

- remove speed and gain enums (#58) ([e055014](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/e0550148cc3a0a1053ade822364e9755f352b5b2) by Samuel Gauthier). Co-authored-by: ThatsTheEnd <66672184+ThatsTheEnd@users.noreply.github.com>
- remove unnecessary command in publish step (#46) ([f9d146a](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/f9d146a21b29f19633cfab833bae8c9d55c97637) by Samuel Gauthier).

## [v0.3.0](https://github.com/HORIBAEzSpecSDK/python-sdk/releases/tag/v0.3.0) - 2024-03-12

<small>[Compare with v0.2.0](https://github.com/HORIBAEzSpecSDK/python-sdk/compare/v0.2.0...v0.3.0)</small>

### Added

- add automatic release to pypi in CI/CD pipeline ([0972376](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/05656454a59d4674291b68cc739f624306c79d97) by Samuel Gauthier).
- add center scan example ([0972376](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/05656454a59d4674291b68cc739f624306c79d97) by Samuel Gauthier).

## [v0.2.0](https://github.com/HORIBAEzSpecSDK/python-sdk/releases/tag/v0.2.0) - 2024-03-07

<small>[Compare with v0.1.0](https://github.com/HORIBAEzSpecSDK/python-sdk/compare/v0.1.0...v0.2.0)</small>

### Added

- add all icl commands ([ee2dab0](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/ee2dab0c24ed765d96af5bfd6b3ddb3890277015) by Samuel Gauthier). Co-authored-by: Nikolaus Naredi-Rainer <nikolaus.naredi-rainer@zuehlke.com>
- add updated ICL API doc ([895fcd2](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/895fcd28bc2a2935020e41ef90b247e5cdfc8366) by isadiq-horiba).

### Fixed

- fix link to classes in docstrings ([adffc64](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/adffc6470989502fdaad663c996943d4444d3013) by Samuel Gauthier).
- fixes: workflow ([16bd35f](https://github.com/HORIBAEzSpecSDK/python-sdk/commit/16bd35f24dc12e60bc055f644e5439011b239334) by Nikolaus Naredi-Rainer).

## [v0.1.0](https://github.com/HORIBAEzSpecSDK/python-sdk/releases/tag/v0.1.0) - 2023-10-31

<small>[Compare with first commit](https://github.com/HORIBAEzSpecSDK/python-sdk/compare/a2e72bf27ae8064315e37225ce069611c4bf6670...v0.1.0)</small>
