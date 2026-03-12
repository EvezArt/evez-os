#!/usr/bin/env python3
"""
Tier 2/3: watch loop runner

Runs a probe on an interval and appends to spine.
Designed to be used:
  - interactively (Ctrl-C to stop)
  - from cron/systemd timers
"""
from __future__ import annotations
import time
from typing import Callable, Dict, Any

def watch(run_fn: Callable[[], Dict[str, Any]], interval_s: int = 60, jitter_s: int = 0):
    """Run a probe function on a fixed interval and loop indefinitely.

    Calls ``run_fn`` once per iteration, then sleeps for ``interval_s`` plus
    an optional ``jitter_s`` offset before the next iteration.  The sleep is
    always at least 1 second to prevent tight busy-loops.

    Typical usage::

        from spine.my_module import run as my_probe
        watch(my_probe, interval_s=120, jitter_s=10)

    Designed to be driven interactively (Ctrl-C to stop) or from a cron/
    systemd timer.  The caller is responsible for any spine append logic
    inside ``run_fn``.

    Args:
        run_fn:     Zero-argument callable executed each iteration.  Its return
                    value is ignored by the watch loop.
        interval_s: Base sleep duration in seconds between iterations (default 60).
        jitter_s:   Additional fixed offset added to the sleep (default 0).
                    Pass a randomized value from the caller to spread load.
    """
    n = 0
    while True:
        n += 1
        run_fn()
        sleep = interval_s + (jitter_s if jitter_s else 0)
        time.sleep(max(1, sleep))
