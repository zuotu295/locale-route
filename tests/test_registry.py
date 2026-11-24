"""Unit tests for the parser; no network or chain state is simulated here."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest

sdk = types.ModuleType("genlayer")
sdk.Address, sdk.TreeMap, sdk.u256 = str, dict, int
sdk.gl = types.SimpleNamespace(Contract=object, vm=types.SimpleNamespace(UserError=ValueError),
                               public=types.SimpleNamespace(write=lambda f: f, view=lambda f: f))
sys.modules["genlayer"] = sdk
spec = importlib.util.spec_from_file_location("locale_route", Path(__file__).resolve().parents[1] / "contracts/locale_route.py")
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)


class RegistryTests(unittest.TestCase):
    def registry(self, records):
        return "File-Date: 2026-11-18\n%%\n" + "\n%%\n".join(records) + "\n%%" * 8000

    def test_preferred_value_and_scope(self):
        registry = self.registry(["Type: language\nSubtag: iw\nDeprecated: 1989-01-01\nPreferred-Value: he",
                                  "Type: language\nSubtag: he", "Type: region\nSubtag: br"])
        self.assertEqual(contract.lookup(registry, "iw"), "he")
        self.assertEqual(contract.lookup(registry, "he"), "he")
        self.assertEqual(contract.lookup(registry, "br"), "UNREGISTERED")

    def test_incomplete_registry_fails(self):
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            contract.lookup("File-Date: 2026-11-18", "he")

    def test_replacement_cycle_fails(self):
        registry = self.registry(["Type: language\nSubtag: iw\nDeprecated: 1989-01-01\nPreferred-Value: he",
                                  "Type: language\nSubtag: he\nDeprecated: 1990-01-01\nPreferred-Value: iw"])
        with self.assertRaisesRegex(ValueError, "replacement chain"):
            contract.lookup(registry, "iw")
