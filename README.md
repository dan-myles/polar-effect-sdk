# polar-effect

Unofficial [Effect](https://effect.website) SDK for the [Polar](https://polar.sh) API.

- Responses decoded with `Schema`; date-times as `DateTime.Utc`
- Typed, tagged errors: `Effect.catchTag("ResourceNotFound", ...)`
- Pagination as `Stream`
- `Layer`-based config, `Redacted` tokens, pluggable `HttpClient`
- Retries on rate limits (honoring `Retry-After`) and transient failures
- Webhook verification (Standard Webhooks) with typed payloads
- Forward compatible: new enum values, union variants and webhook event types decode instead of failing

```sh
npm install polar-effect effect@4.0.0-rc.117
```

```ts
import { Effect, Stream } from "effect";
import { FetchHttpClient } from "effect/unstable/http";
import { Polar } from "polar-effect";

const program = Effect.gen(function* () {
  const polar = yield* Polar;

  const product = yield* polar.products.get("00000000-0000-0000-0000-000000000000").pipe(
    Effect.catchTag("ResourceNotFound", () => Effect.succeed(null)),
  );

  yield* polar.products.listStream({ is_archived: false }).pipe(
    Stream.runForEach((product) => Effect.log(product.name)),
  );
});

program.pipe(
  Effect.provide(Polar.layerConfig()), // POLAR_ACCESS_TOKEN, POLAR_ENVIRONMENT
  Effect.provide(FetchHttpClient.layer),
  Effect.runPromise,
);
```

See [`sdk/README.md`](sdk/README.md) for the full package docs.

Not affiliated with Polar.

## How it's built

The SDK is generated. Nothing in `sdk/` is edited by hand.

```
upstream/     git submodule: polarsource/polar (sdk/generator + docs/openapi)
generator/    Effect emitter plugged into Polar's SDK generator
  effect/       emitter, type renderer and package templates (incl. the hand-written runtime)
  tests/
  cli.py        builds Polar's IR from the OpenAPI spec and runs the emitter
sdk/          generated `polar-effect` package
```

Polar's generator turns their OpenAPI spec into a language-agnostic IR, which their Python and TypeScript SDKs are rendered from. The emitter in `generator/effect` renders the same IR as Effect code, so this SDK follows the official ones.

## Development

Requires [uv](https://docs.astral.sh/uv/), Node 22+ and pnpm.

```sh
git submodule update --init --depth 1 --filter=blob:none upstream
git -C upstream sparse-checkout set sdk/generator docs/openapi

cd generator
uv sync
uv run pytest                    # emitter tests
uv run ruff check . && uv run ty check .
uv run python cli.py             # regenerate sdk/ and run its format, lint, typecheck, build and tests
```

Runtime changes go in `generator/effect/template/src/`, then regenerate. CI fails if `sdk/` is out of date.

### Syncing with Polar

`.github/workflows/sync-upstream.yml` runs weekly: it bumps `upstream` to Polar's latest `main`, regenerates, and opens a PR if anything changed. To do it by hand:

```sh
git -C upstream fetch --depth 1 origin main && git -C upstream checkout --detach FETCH_HEAD
cd generator && uv run python cli.py
```

### Releasing

```sh
cd generator && uv run python cli.py --version 0.2.0
git commit -am "release: v0.2.0" && git tag v0.2.0 && git push --follow-tags
```

Pushing a `v*` tag runs `.github/workflows/release.yml`, which tests, builds and publishes to npm with provenance via [trusted publishing](https://docs.npmjs.com/trusted-publishers), then creates a GitHub release. Prerelease versions (`0.2.0-beta.1`) are published under the `next` tag.

## License

MIT. The generator builds on [Polar's SDK generator](https://github.com/polarsource/polar/tree/main/sdk/generator) (MIT).
