# GenVM lint and SDK validation

- Source: `contracts/locale_route.py`
- SHA-256: `e8bbaa4f4e67adb73b94318dfb388379665b7916ff223d3843260d8515eec90e`
- Official tool: `genvm-linter==0.11.0`
- Official runner bundle: GenVM `v0.2.16`
- SDK resolved from the declared header: `py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6`
- The runner resolved its standard library from its own manifest. No SDK override was used.

```sh
python -m pip install genvm-linter==0.11.0
env -u GENVMROOT GENVM_VERSION=v0.2.16 genvm-lint check contracts/locale_route.py --json
```

[Raw output](LINT.json) records both AST lint and SDK semantic validation. The read-only chain verifier compares the deployed bytes against this source file.
