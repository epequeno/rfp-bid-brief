"""Command-line surface for the span index.

    uv run rfpbrief build  fixtures/<fixture>.pdf          # write results/spans/<fixture>.json
    uv run rfpbrief find   fixtures/<fixture>.pdf "quote"  # which span, or nothing
    uv run rfpbrief verify results/spans/<fixture>.json    # is the index still reproducible?
    uv run rfpbrief stats  fixtures/<fixture>.pdf

`build` refuses a fixture that is not in the provenance manifest, and `verify` fails if the fixture,
the engine version or the page text has moved. Both refusals are the point: an index that silently
stops describing its document turns every citation against it into a confident guess.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from . import spans

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "fixtures"
DEFAULT_OUT = REPO / "results" / "spans"
MANIFEST = FIXTURES / "PROVENANCE.md"

_MANIFEST_LINE = re.compile(r"^(?P<sha>[0-9a-f]{64})\s+(?P<name>\S+\.pdf)$")


def manifest_hashes() -> dict[str, str]:
    """The committed sha256 for each fixture, read from the manifest block in PROVENANCE.md."""
    if not MANIFEST.exists():
        return {}
    insec = fence = False
    out: dict[str, str] = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.startswith("## Integrity manifest"):
            insec = True
            continue
        if insec and line.startswith("```"):
            fence = not fence
            continue
        if insec and fence:
            m = _MANIFEST_LINE.match(line.strip())
            if m:
                out[m.group("name")] = m.group("sha")
    return out


def cmd_build(args: argparse.Namespace) -> int:
    path = Path(args.fixture)
    doc = spans.build(path, fixture_name=path.name)
    known = manifest_hashes()
    if known and path.name not in known:
        print(f"refusing: {path.name} has no provenance row in fixtures/PROVENANCE.md", file=sys.stderr)
        return 2
    if known and known[path.name] != doc.fixture_sha256:
        print(
            f"refusing: {path.name} does not match its published hash\n"
            f"  manifest {known[path.name]}\n  fixture  {doc.fixture_sha256}",
            file=sys.stderr,
        )
        return 2
    out = Path(args.out) if args.out else DEFAULT_OUT / f"{path.stem}.json"
    spans.write_index(doc, out)
    print(
        f"{doc.fixture}: {len(doc.pages)} pages, {len(doc.spans)} spans, "
        f"{sum(len(p.text) for p in doc.pages)} chars, {doc.hyphen_breaks} hyphenated line breaks\n"
        f"  engine    {doc.engine_version}\n"
        f"  fixture   {doc.fixture_sha256[:16]}…\n"
        f"  index     {out.relative_to(REPO) if str(out).startswith(str(REPO)) else out}"
    )
    return 0


def cmd_find(args: argparse.Namespace) -> int:
    """Locate a quote. Exit 0 only when the answer is exactly one span.

    Ambiguity exits non-zero on purpose: a quote that appears on three pages is not a citation yet,
    and silently taking the first hit is how a brief ends up quoting the wrong section.
    """
    doc = spans.build(Path(args.fixture), fixture_name=Path(args.fixture).name)
    if args.exact:
        hits = doc.find(args.quote)
        if not hits:
            print("no span equals that quote exactly (try without --exact)", file=sys.stderr)
            return 1
        for s in hits:
            print(f"{s.id}\tpage {s.page}\t{s.quote}")
        return 0 if len(hits) == 1 else 1

    cites = doc.locate(args.quote, page=args.page)
    if not cites:
        print("not found: no span contains that quote under the verbatim rule "
              "(whitespace-only differences tolerated)", file=sys.stderr)
        return 1
    for c in cites:
        print(f"{c.id}\tpage {c.page}\t{c.quote}")
    if len(cites) > 1:
        pages = sorted({c.page for c in cites})
        print(f"ambiguous: {len(cites)} spans on page(s) {pages} contain that quote. "
              f"Re-run with --page to say which one you meant.", file=sys.stderr)
        return 1
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    index = spans.read_index(Path(args.index))
    fixture = FIXTURES / index["fixture"]
    if not fixture.exists():
        print(f"refusing: {fixture.name} is not in fixtures/", file=sys.stderr)
        return 2
    doc = spans.build(fixture, fixture_name=fixture.name)
    problems = spans.reproducibility_report(doc, index)
    if problems:
        print(f"{index['fixture']}: index is NOT reproducible", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"{index['fixture']}: reproducible ({len(doc.spans)} spans, {len(doc.pages)} pages)")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    doc = spans.build(Path(args.fixture), fixture_name=Path(args.fixture).name)
    lengths = sorted(len(s.text) for s in doc.spans)
    n = len(lengths)
    if not n:
        print("no spans extracted")
        return 1
    print(f"{doc.fixture}")
    print(f"  pages                 {len(doc.pages)}")
    print(f"  spans                 {n}")
    print(f"  span chars            min {lengths[0]}  median {lengths[n // 2]}  p90 {lengths[int(n * .9)]}  max {lengths[-1]}")
    print(f"  hyphenated breaks     {doc.hyphen_breaks}")
    print(f"  engine                {doc.engine_version}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="rfpbrief", description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build a span index and write it to results/spans/")
    b.add_argument("fixture")
    b.add_argument("--out", help="output path (default results/spans/<fixture>.json)")
    b.set_defaults(func=cmd_build)

    f = sub.add_parser("find", help="locate a quote inside a span (exactly one, or it fails)")
    f.add_argument("fixture")
    f.add_argument("quote")
    f.add_argument("--page", type=int, help="disambiguate a quote that appears on several pages")
    f.add_argument("--exact", action="store_true",
                   help="require a whole-span match instead of containment")
    f.set_defaults(func=cmd_find)

    v = sub.add_parser("verify", help="check a committed index is still reproducible")
    v.add_argument("index")
    v.set_defaults(func=cmd_verify)

    s = sub.add_parser("stats", help="span size distribution for one fixture")
    s.add_argument("fixture")
    s.set_defaults(func=cmd_stats)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
