# Architect Functions changelog

---

Also see: [Architect changelog](https://github.com/architect/architect/blob/main/changelog.md)

---

## [1.0.0] 2023-08-11

Hello (again)! This release is a nearly complete rewrite of `architect-functions`, bringing it up to date with all the latest in Architect land, and broadly expanding its functionality. Extensive [docs can be found here](https://arc.codes/docs/en/reference/runtime-helpers/python).

Huge thanks to @lpetre for all his work getting this package in tip-top shape!


### Added

- Added `arc.http.res` method (with built-in session support) and `arc.http.parse_body` helper
- DynamoDB + JWE session support (fully compatible with Node.js's `@architect/functions` sessions)
- Added `arc.events.parse` and `arc.queues.parse` methods
- Added `arc.ws.api`, `arc.ws.info`, and `arc.ws.close` methods


### Changed

- Breaking change: `arc.reflect()` is now `arc.services()`
- Internal change: unit test suite
- Added caching to improve performance of `arc.services()` calls
- Added caching to improve performance of instantiating `arc.tables` clients
- Dev version of this package can now be found at https://test.pypi.org/project/architect-functions/


### Fixed

- `arc.services()` now recursively paginates; thanks @bardbachmann!
- Fixed (or added) proper Sandbox support for everything

---
