import os

from dataclasses import dataclass
from pathlib import Path

import pendulum
import toml


@dataclass
class Account:
    """An item for an [[ACCOUNTS]] collection"""

    address: str
    desc: str


@dataclass
class Principal:
    """An item for a [[PRINICPALS]] collection"""

    name: str
    email: str


class PendulumEncoder(toml.encoder.TomlEncoder):
    def __init__(self, _dict=dict, preserve=False):
        super().__init__(_dict=_dict, preserve=preserve)
        self.dump_funcs[pendulum.DateTime] = lambda v: v.isoformat().replace(
            "+00:00", "Z"
        )
        # self.dump_funcs[Account] = lambda v: v.__dict__


xrp_ledger_toml = Path(".well-known/xrp-ledger.toml")

parsed_toml = toml.load(xrp_ledger_toml)
print(parsed_toml)
current_modified = pendulum.instance(parsed_toml["METADATA"]["modified"])
new_modified = pendulum.now(tz=pendulum.UTC)
new_expiry = new_modified.add(years=2)
modified_delta = pendulum.now() - current_modified
new_expiry_delta = new_expiry - pendulum.now()
print(
    f"Last modified at {current_modified:%Y%m%d %H:%M} or {modified_delta.in_words()} ago."
)
print(
    f"New expiry set for {new_expiry:%Y%m%d %H:%M} or {new_expiry_delta.in_words()} from now."
)


# read in ADDRESS info
xcap = Path("XRPL_CONTRACT_ADDRESS")
our_xca = Account(*xcap.read_text().split(" ", 1))
our_xca.desc = our_xca.desc.strip()

# write our stuff

## METADATA
parsed_toml["ACCOUNTS"] = [our_xca.__dict__]
parsed_toml["METADATA"]["modified"] = new_modified
parsed_toml["METADATA"]["expires"] = new_expiry
me = Principal("Joseph Chiocchi", "admin@egge.gg")
parsed_toml["PRINCIPALS"] = [me.__dict__]


with open(xrp_ledger_toml, "w") as fp:
    toml.dump(parsed_toml, fp, encoder=PendulumEncoder())
