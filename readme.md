<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/architect/assets.arc.codes/raw/main/public/architect-logo-light-500b%402x.png">
  <img alt="Architect Logo" src="https://github.com/architect/assets.arc.codes/raw/main/public/architect-logo-500b%402x.png">
</picture>

## [`architect-functions`](https://pypi.org/project/architect-functions/)

> Runtime utility package for [Functional Web Apps (FWAs)](https://fwa.dev/) built with [Architect](https://arc.codes)

[![GitHub CI status](https://github.com/architect/functions-python/actions/workflows/build.yml/badge.svg)](https://github.com/architect/functions-python/actions/workflows/build.yml)

Check out the full docs for [this library](https://arc.codes/docs/en/reference/runtime-helpers/python) and [Architect](https://arc.codes)


## Install

Within your Architect project directory, add `architect-functions` to its root `requirements.txt`:

```bash
pip install architect-functions -r requirements.txt
```

> You may also add `architect-functions` to individual Lambda `requirements.txt` files, but we suggest making use of Architect's automated Lambda treeshaking. See the [Architect dependency management guide](https://staging.arc.codes/docs/en/guides/developer-experience/dependency-management#python) for more details.


## Usage

```py
import arc          # Import all tools, or
import arc.events   # @events pub/sub
import arc.http     # @http tools + sessions
import arc.queues   # @queues pub/sub
import arc.services # Architect resource / service discovery
import arc.tables   # @tables DynamoDB helper methods + API client
import arc.ws       # @ws WebSocket helper + API client
```


## API

[**`@events` methods**](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.events)
- [`arc.events.parse()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.events.parse())
- [`arc.events.publish()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.events.publish())

[**`@http` methods**](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.http)
- [`arc.http.parse_body()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.http.parse_body())
- [`arc.http.res()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.http.res())
- [`arc.http.session_read()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.http.session_read())
- [`arc.http.session_write()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.http.session_write())

[**`@queues` methods**](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.queues)
- [`arc.queues.parse()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.queues.parse())
- [`arc.queues.publish()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.queues.publish())

[**Service discovery**](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.services())
- [`arc.services()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.services())

[**`@tables` methods**](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.tables)
- [`arc.tables.name()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.tables.name())
- [`arc.tables.table()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.tables.table())

[**`@ws` methods**](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.ws)
- [`arc.ws.api()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.ws.api())
- [`arc.ws.close()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.ws.close())
- [`arc.ws.info()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.ws.info())
- [`arc.ws.send()`](https://arc.codes/docs/en/reference/runtime-helpers/python#arc.ws.send())

---

## Development

Install [Pipenv](https://pipenv.pypa.io/en/latest/#install-pipenv-today)

```bash
pipenv install --dev
```

---

## Testing

```bash
pipenv run pytest
```
