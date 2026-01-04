# CHANGELOG


## v1.1.1 (2026-01-04)

### Removed

- Uv dependency (we will revert it back when uv is more mature)
  ([`e81dc57`](https://github.com/URV-teacher/bmde/commit/e81dc57227fb84e10de3558e72f607c2d84c7858))


## v1.1.0 (2026-01-04)

### Added

- Chmod of fat image to be mounted into desmume
  ([`15faf8c`](https://github.com/URV-teacher/bmde/commit/15faf8c4bb5cea73c4752543c544e65cd2a4448a))

- Desmume cli as entrypoint in test
  ([`cd94e6d`](https://github.com/URV-teacher/bmde/commit/cd94e6ddf351b23bcfdf29d3a233f2c4b12e11bf))

- Docs with mkdocs, refined commis message target for semantic release
  ([`e199f26`](https://github.com/URV-teacher/bmde/commit/e199f262910db01ce9d8f0cc2fe25451496190df))

- Dummy variables for runtime dir
  ([`cb104e9`](https://github.com/URV-teacher/bmde/commit/cb104e9f8ad011d17ec8b5f974dd2ee6d81d6966))

- Dynamic versioning
  ([`908bf26`](https://github.com/URV-teacher/bmde/commit/908bf264a91087d7f1f978f2cc39e6d0f8d53504))

- Exec as trace
  ([`b7cf2e2`](https://github.com/URV-teacher/bmde/commit/b7cf2e2cd80055a9aa16757743cd92a32c9edaa5))

- Fmt
  ([`4527615`](https://github.com/URV-teacher/bmde/commit/4527615009e2512d36a480466240d5012118321e))

- Github workflow variables
  ([`47f03f3`](https://github.com/URV-teacher/bmde/commit/47f03f3c4b5ff13a8e7b5ab5eb9b45389d369d61))

- Hide sensibles implemented in logger and also available in logging config
  ([`647730f`](https://github.com/URV-teacher/bmde/commit/647730f9e38cc31a99b2b2ec2662f6c0e0f152fc))

- Interactive false into patch of test and also interactive into patch
  ([`2f2d486`](https://github.com/URV-teacher/bmde/commit/2f2d486aa06dc6dc0e9851791a81c7cf9f550f23))

- Interactive mode for seelecting it to false on tests, put docker as the default option when
  backend is none
  ([`5a82d8d`](https://github.com/URV-teacher/bmde/commit/5a82d8d4f0722a13626c4a1115d80997b6d84bb5))

- None to docker output option
  ([`47427af`](https://github.com/URV-teacher/bmde/commit/47427af15749ec3497285c4613344df083b093a7))

- Patch command directory option, removed dev reuirements and moved into pyproject section,
  refactored makefile
  ([`049c125`](https://github.com/URV-teacher/bmde/commit/049c12532703f532a51dddabb77499d0b1670ec2))

- Release workflow
  ([`d15cb79`](https://github.com/URV-teacher/bmde/commit/d15cb79e8d929047ffd0f2080a1a3dbe064fbd31))

- Release workflow
  ([`78b501d`](https://github.com/URV-teacher/bmde/commit/78b501dd243f03d1a7f659a9d613d4bda7fae734))

- Trace debugging in tests
  ([`af8a11d`](https://github.com/URV-teacher/bmde/commit/af8a11d12c860853981ca5113882a1e24bdf81ac))

- Unbufferring to python
  ([`2e6cf7b`](https://github.com/URV-teacher/bmde/commit/2e6cf7b42c76ba3345854f06af6e465f98d4f3e2))

### Fixed

- Missing connection of intercative arg with internal opt
  ([`ac6c24f`](https://github.com/URV-teacher/bmde/commit/ac6c24fd0d3034704d4d67fee1bb60138a187721))

### Removed

- Interactive behaviour in run command of test
  ([`110eb7d`](https://github.com/URV-teacher/bmde/commit/110eb7db3c2ab5efe62d8b1f317779bbff2f8795))

### Updated

- Desmume container to not use autodiscovery or ROM var by default
  ([`2932b2b`](https://github.com/URV-teacher/bmde/commit/2932b2bbbe113cd493f4d614248b9b72550a581a))

- Logging in all commands at api level (needs more working) added argument for the rom
  ([`285d0ff`](https://github.com/URV-teacher/bmde/commit/285d0ff56b9cc01f8b2d4043db6088a9fb1b11f5))

- Makefile to not rebuild env on dev targets
  ([`d728ac0`](https://github.com/URV-teacher/bmde/commit/d728ac02d8784e7719b8fb93364842ac8908f594))

- Removed duplicated options
  ([`4a7569b`](https://github.com/URV-teacher/bmde/commit/4a7569bd5af7654d8be91868327e8672b6256f87))

- Restored original entrypoint in run command of test
  ([`3c3ed13`](https://github.com/URV-teacher/bmde/commit/3c3ed13406ffb78f2a96c27360d4b6dbfa107d4a))

- Restored original entrypoint in run command of test
  ([`5d88c00`](https://github.com/URV-teacher/bmde/commit/5d88c004b5d40182a1c0cfd16e8db1b4c7fcdb50))


## v1.0.0 (2026-01-02)

### Added

- Agentic development and support for gemini
  ([`15093bf`](https://github.com/URV-teacher/bmde/commit/15093bf17cff254b6f37b491c6559751208b642f))

- Badges to readme and restored images
  ([`af824e0`](https://github.com/URV-teacher/bmde/commit/af824e0671a8005a10ea020b696e0e3987913c29))

- Debug command, but debugger backend is not working as expected
  ([`a6f8ae7`](https://github.com/URV-teacher/bmde/commit/a6f8ae728f5a575dc67ceb9231b2d29a80b3ecd9))

- Debug implementation
  ([`ed6179c`](https://github.com/URV-teacher/bmde/commit/ed6179c9da3cf0de9e2c940f6cf213b135e31a86))

- Dev environment that is used in workflows
  ([`58382b4`](https://github.com/URV-teacher/bmde/commit/58382b46f24699f8a5ccdf21d1d8e4938d55c235))

- Implemented best readme template
  ([`21137ef`](https://github.com/URV-teacher/bmde/commit/21137efb18063c63193de85dab89a57dc094047e))

- Initial commit for BMDE, split from tot tool
  ([`c347a2e`](https://github.com/URV-teacher/bmde/commit/c347a2eb7930d3645c5aff960a7fd575287ade62))

- Insight debugger component, initial repo
  ([`deae4c5`](https://github.com/URV-teacher/bmde/commit/deae4c5f10d259c9d4a79b12a90f2046c059dc49))

- Insight docker, desmume run perisistence in control configs
  ([`ff2ba3a`](https://github.com/URV-teacher/bmde/commit/ff2ba3a26c4f3280cfb5fdbeacb32a567ce59e89))

- Integration testing
  ([`896c8f0`](https://github.com/URV-teacher/bmde/commit/896c8f06f845ce1edba926b2327117f65ca95f3e))

- Logs folder
  ([`2c12f65`](https://github.com/URV-teacher/bmde/commit/2c12f659b6b3253f1b308aeba22a001d60f3d286))

- Mypy to dev dependencies
  ([`cfefba5`](https://github.com/URV-teacher/bmde/commit/cfefba57df976ccfaec19ab4e6625c66d2c97ea3))

- New defaults with full config options and CLI commands to invoke the view of current config and
  default config
  ([`4d599aa`](https://github.com/URV-teacher/bmde/commit/4d599aa668899a40410360e3d820a42d40cfad2e))

- Notes on apparently unused lines so they are not deleted by ruff fix and also FIXED logging
  ([`20ab694`](https://github.com/URV-teacher/bmde/commit/20ab6947f5179cfff046ed1438bf70ca762e03dc))

- Obfuscated text containing credentials for security
  ([`7dcd9f5`](https://github.com/URV-teacher/bmde/commit/7dcd9f5f93d77e24cf3ba96988c9b673bc0a0228))

- Permissions in the workflows
  ([`55f2e7d`](https://github.com/URV-teacher/bmde/commit/55f2e7dcbace2071487f42188177b97bea5ec988))

- Shields in README for testing
  ([`647b1e9`](https://github.com/URV-teacher/bmde/commit/647b1e97278b64bddabb31ca157699eceaa46c29))

- Submodules
  ([`1539c25`](https://github.com/URV-teacher/bmde/commit/1539c250673c2451b56bca9dbf7568a34737641f))

- Test structure with 2 smoke tests
  ([`d3da93b`](https://github.com/URV-teacher/bmde/commit/d3da93b79c4fca7d4a2f72864aa5157ba47a868a))

- Tests and workflows for testing and style
  ([`573120b`](https://github.com/URV-teacher/bmde/commit/573120b21e78f60a01eb40eca7c70b36d9ae707f))

- Workflow of autopublish in PyPI
  ([`6e03d2b`](https://github.com/URV-teacher/bmde/commit/6e03d2b228014b84dac5a739ceee5e5f96b91342))

### Fixed

- Dependency in make
  ([`e4927e7`](https://github.com/URV-teacher/bmde/commit/e4927e71a9bea731cba3f86737aa5c9303a8874f))

- Lint types for logger
  ([`dd3fd90`](https://github.com/URV-teacher/bmde/commit/dd3fd90386877f63b67863fd5d10be7be9b76c87))

- Security issue
  ([`47945bf`](https://github.com/URV-teacher/bmde/commit/47945bf11a87e52cd3b88b5a030bd598835f248d))

### Removed

- Data from components, which were erroneusly uploaded without being a module
  ([`ccc5b33`](https://github.com/URV-teacher/bmde/commit/ccc5b33f995e9c52fda1ce8fecaa8abed7d461fa))

- Unused import
  ([`711e107`](https://github.com/URV-teacher/bmde/commit/711e10729f5240646de5a580b26de551b137f092))

### Updated

- Auto-format
  ([`6c6e438`](https://github.com/URV-teacher/bmde/commit/6c6e43818fb2c09f789166d28ee0f67852db64f6))

- Backend base class
  ([`de9038c`](https://github.com/URV-teacher/bmde/commit/de9038c91bb92233cbb3e6049d6608b34bf46c05))

- Binary from makefile to generic python
  ([`69d29ad`](https://github.com/URV-teacher/bmde/commit/69d29ad0417d1da809279745f233d9bae2e27cd1))

- Changed url of readme with placeholders
  ([`a49d27b`](https://github.com/URV-teacher/bmde/commit/a49d27bdafeaa51670e33f1ead46e1a8106e752e))

- Cli options and api of git command
  ([`d61d84f`](https://github.com/URV-teacher/bmde/commit/d61d84f42e567ab81093e3fdefe1040574106716))

- Debug and patch command for new structure
  ([`76ea8ab`](https://github.com/URV-teacher/bmde/commit/76ea8ab4807cd8a4196325b23a680bb72d4fe86e))

- Devkitarm docker with icon
  ([`fd45cd7`](https://github.com/URV-teacher/bmde/commit/fd45cd7d0bc4234b01e63b0cbb03919cfcbc9fd2))

- Logging levels
  ([`877bc74`](https://github.com/URV-teacher/bmde/commit/877bc7466a138df828be4d163360fc67ca831bf6))

- Many changes related to typing and general refactoing using ruff and mypy
  ([`ac4c850`](https://github.com/URV-teacher/bmde/commit/ac4c850b525078e258f2a3cbedef8404e979a05e))

- More changes in debug and run spec, unified backend types
  ([`6f221c6`](https://github.com/URV-teacher/bmde/commit/6f221c60e0c07b3542b2900806c8497a210b7967))

- More changes into the spec, CLI and API of build
  ([`4d61531`](https://github.com/URV-teacher/bmde/commit/4d61531652e244e0f87c3ea3c26f64abd531ab44))

- More changes to make the command debug work
  ([`18bf6fc`](https://github.com/URV-teacher/bmde/commit/18bf6fc9211b845ac7b806d51d611e7e08d17ff0))

- Readme
  ([`c19a0d9`](https://github.com/URV-teacher/bmde/commit/c19a0d97270dc99f6e3eb2b179ba5598e1431004))

- Refactored build docker, added docker function for detecting availability, refactored logging
  ([`06ac646`](https://github.com/URV-teacher/bmde/commit/06ac64655403f7ac6f1b475a715a80519859f688))

- Refactored docker functions
  ([`d28896d`](https://github.com/URV-teacher/bmde/commit/d28896d31c132ffe328126cedeb5a7b051222319))

- Reordered roadmap in readme, added check command
  ([`ae715cd`](https://github.com/URV-teacher/bmde/commit/ae715cd35de6b7214c2254a81d243d2ec6f52a97))

- Roadmap and deleted deprecated config from the schema
  ([`1ecc4c4`](https://github.com/URV-teacher/bmde/commit/1ecc4c46398c83dd6b262d3c18b44be9ddd7758f))

- Run spec and command for unified API access and more CLI options
  ([`2da62df`](https://github.com/URV-teacher/bmde/commit/2da62df87cc5d4f76136c2cfecd8a9792485a500))

- Services refactored into a common class Service and inheritance with typing, deleted code related
  with deliveries, converted cli hard coded types to annotated arguments in shared options, general
  style refactor
  ([`77fd098`](https://github.com/URV-teacher/bmde/commit/77fd09828f2043e57eb9d644face9aedd15940eb))

- Workflow files
  ([`68f7816`](https://github.com/URV-teacher/bmde/commit/68f78167230fced932e8a0a44ed3531606665849))
