# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

import json
import re
from genlayer import Address, TreeMap, gl, u256

REGISTRY = "https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry"
SUBTAG = re.compile(r"[a-z]{2,8}")


def lookup(source: str, code: str) -> str:
    blocks = source.split("%%")
    header = blocks[0].strip()
    if not re.fullmatch(r"File-Date: [0-9]{4}-[0-9]{2}-[0-9]{2}", header) or len(blocks) < 8000:
        raise gl.vm.UserError("Incomplete IANA registry")
    languages = {}
    for block in blocks[1:]:
        fields = {}
        for line in block.splitlines():
            key, sep, value = line.partition(": ")
            if sep and key in ("Type", "Subtag", "Deprecated", "Preferred-Value"):
                fields[key] = value.strip()
        subtag = fields.get("Subtag", "")
        if fields.get("Type") == "language" and SUBTAG.fullmatch(subtag):
            languages[subtag] = (fields.get("Deprecated"), fields.get("Preferred-Value"))
    if code not in languages:
        return "UNREGISTERED"
    visited = set()
    while code in languages and code not in visited:
        visited.add(code)
        deprecated, preferred = languages[code]
        if not deprecated:
            return code
        if not preferred:
            return "DEPRECATED_WITHOUT_REPLACEMENT"
        code = preferred
    raise gl.vm.UserError("IANA replacement chain is incomplete")


class LocaleRoute(gl.Contract):
    editor: Address
    routes: TreeMap[str, str]

    def __init__(self):
        self.editor = gl.message.sender_address

    @gl.public.write
    def publish(self, code: str, digest: str, expected_revision: u256) -> str:
        if gl.message.sender_address != self.editor:
            raise gl.vm.UserError("Only the route editor may publish")
        if not SUBTAG.fullmatch(code) or not re.fullmatch(r"[a-f0-9]{64}", digest):
            raise gl.vm.UserError("Expected a lowercase primary subtag and SHA-256 hex digest")

        def observe() -> str:
            return lookup(gl.nondet.web.get(REGISTRY).body.decode("utf8"), code)

        canonical = gl.eq_principle.strict_eq(observe)
        if canonical in ("UNREGISTERED", "DEPRECATED_WITHOUT_REPLACEMENT"):
            raise gl.vm.UserError("IANA subtag has no usable canonical route")
        current = json.loads(self.routes.get(canonical, "{}"))
        revision = current.get("revision", 0)
        if expected_revision != revision:
            raise gl.vm.UserError("Canonical route revision conflict")
        if current.get("digest") == digest:
            raise gl.vm.UserError("Content digest already published")
        entry = json.dumps({"canonical": canonical, "submitted": code,
                            "digest": digest, "revision": revision + 1}, separators=(",", ":"))
        self.routes[canonical] = entry
        return entry

    @gl.public.view
    def resolve(self, canonical: str) -> str:
        return self.routes.get(canonical, "")
