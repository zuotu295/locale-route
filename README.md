# LocaleRoute

LocaleRoute gives localization publishers one versioned content pointer for each canonical primary language subtag. A legacy Hebrew publisher using `iw` and a current publisher using `he` must write to the same route. A stale writer cannot overwrite the shared route by submitting its alternate spelling.

## Protocol

The deploying wallet is the route editor. On each `publish(code, digest, expected_revision)`, GenLayer validators independently fetch the [IANA Language Subtag Registry](https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry). They follow the registry's preferred language replacements and agree on the canonical destination, or on the absence of a usable destination. Exact agreement is required on the normalized result, so unrelated registry entries do not cause contention. Missing or incomplete registry data causes the write to abort.

The contract then checks the **canonical** slot's revision and stores the new SHA-256 digest and revision in one write. Revision zero means absent. Successful publications increment the revision exactly once. Replaying the current digest is rejected. `resolve(canonical)` returns the latest route or an empty string. Content clients can use the digest to verify the retrieved bundle. The contract does not host it.

Scope is lowercase, explicit IANA primary language subtags. Compound language tags, range entries, and deprecated subtags without a preferred replacement are outside the supported scope. A client with a legacy code uses the registry's canonical key for read-only resolution. The same editor may intentionally update an existing route by providing its current revision.

## Stable Studionet

Network ID 61999, RPC `https://studio.genlayer.com/api`, Node.js 24, `genlayer-js@2.0.0`.

```sh
npm ci
python -m unittest discover -s tests
STUDIONET_FAUCET=1 npm run deploy
STUDIONET_FAUCET=1 npm run test:studionet
```

Save the JSON object from the smoke test’s `EVIDENCE` output and run `npm run verify -- evidence.json` for read-only verification. The last two commands create new instances with disposable test funds. For a persistent editor identity, supply a funded Studionet key as `STUDIONET_PRIVATE_KEY`. The integration test shows how to submit a digest, handle a revision conflict and read `resolve('he')`.

[Official lint results](LINT.md)
