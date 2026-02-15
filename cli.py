#!/usr/bin/env python3
"""DriftCatch CLI entry point."""
import sys

import click

from driftcatch import (
    diff_schemas,
    format_report,
    has_breaking,
    load_snapshot,
    save_snapshot,
    snapshot_csv,
    snapshot_json,
)


@click.group()
@click.version_option("0.1.0", prog_name="driftcatch")
def cli():
    """DriftCatch -- Catch schema drift before it catches you."""


@cli.command()
@click.argument("source")
@click.option("-o", "--output", default=None, help="Output snapshot file path")
@click.option("-f", "--format", "fmt", type=click.Choice(["csv", "json"]), default=None)
def snapshot(source, output, fmt):
    """Take a schema snapshot of a CSV or JSON SOURCE file."""
    if fmt is None:
        fmt = "json" if source.endswith(".json") else "csv"
    snap = snapshot_json(source) if fmt == "json" else snapshot_csv(source)
    out = output or f".driftcatch/{source.replace('/', '_')}.snapshot.json"
    save_snapshot(snap, out)
    col_count = len(snap["columns"])
    click.echo(f"Snapshot saved to {out}  ({col_count} columns)")


@cli.command()
@click.argument("old_snapshot")
@click.argument("new_snapshot")
def diff(old_snapshot, new_snapshot):
    """Compare two snapshots and report all changes."""
    old = load_snapshot(old_snapshot)
    new = load_snapshot(new_snapshot)
    changes = diff_schemas(old, new)
    click.echo(format_report(changes))


@cli.command()
@click.argument("old_snapshot")
@click.argument("new_snapshot")
@click.option("--sarif", "sarif_out", default=None, help="[PRO] Export SARIF report")
def check(old_snapshot, new_snapshot, sarif_out):
    """CI gate: exit 1 on breaking changes, exit 0 if safe."""
    old = load_snapshot(old_snapshot)
    new = load_snapshot(new_snapshot)
    changes = diff_schemas(old, new)
    click.echo(format_report(changes))
    if sarif_out:
        click.echo("\nSARIF export is a DriftCatch Pro feature.")
        click.echo("Upgrade at https://driftcatch.dev/pricing")
    breaking_count = sum(1 for c in changes if c["severity"] == "BREAKING")
    if has_breaking(changes):
        click.echo(f"\n{breaking_count} breaking change(s) detected! Pipeline blocked.")
        sys.exit(1)
    click.echo("\nNo breaking changes. Pipeline is safe.")


if __name__ == "__main__":
    cli()
