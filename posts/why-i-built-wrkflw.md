---
title: "Why I built wrkflw"
description: "I got tired of pushing 'fix ci' commits, and somehow that turned into a local GitHub Actions runner."
date: 2026-05-18
author: "bahdotsh"
status: "published"
slug: "why-i-built-wrkflw"
tags: ["projects", "rust", "github-actions", "cicd", "open-source"]
featured: true
---

I didn't wake up one weekend and decide to build a local runner for GitHub Actions. I just got tired of typing `git commit -m "fix ci"`.

If you have spent enough time around CI, you probably know the loop. Change one line in a workflow. Push. Wait for the runner. Watch the job fail for a reason that has nothing to do with the line you changed. Push again. A few rounds later, the real feature is tiny and your git history is mostly you arguing with YAML in public. [wrkflw](https://github.com/bahdotsh/wrkflw) started because I wanted that whole loop to happen on my laptop instead of on GitHub's servers, and preferably without leaving a trail of embarrassing commits behind.

Two years and more edge cases than I expected later, it has turned into a Cargo workspace with sixteen crates. It validates and runs GitHub Actions workflows locally, has a TUI, a proper expression evaluator, four runtime modes, watch mode, secrets, artifacts, cache, reusable workflows, and even a GitLab pipeline parser because apparently I don't know how to leave a side project alone. This post is mostly my attempt to answer the questions people keep asking me: why not just use `act`, why Rust, and what part was actually hard?

## Why not just use act?

This is the first thing everyone asks, which is fair. The honest answer is that [act](https://github.com/nektos/act) is good, and I used it for a while. The thing that pushed me to build my own tool was simpler than some big philosophical disagreement: act depends on Docker, even if all you want to do is validate the YAML.

That validator was the part I cared about most. Most of my "fix ci" commits were not about complex runtime bugs. They were boring mistakes: a typo, a missing key, a wrong input name. If Docker isn't running, or you're on a machine where you can't run Docker at all, act doesn't really help with that use case.

So the main design goal became pretty clear: containers should be optional, not the thing everything else depends on. `wrkflw validate` doesn't even import the runtime crate. It parses the workflow, lints it, cross-checks composite-action inputs against their call sites, and exits with a code that CI can use. `wrkflw run` uses Docker by default if it's available, falls back to Podman if it isn't, and if you have neither, you can still run jobs with `--runtime emulation` or `--runtime secure-emulation`. Same CLI, four runtimes.

The other way it drifted away from act was plain old scope creep. wrkflw now evaluates `${{ ... }}` expressions properly, so `toJSON(needs)` gives you a real nested object instead of a stringified blob, and `matrix.os` resolves against the actual matrix combination instead of the YAML literal. It runs composite actions end to end, supports reusable workflows both local (`./.github/workflows/shared.yml`) and remote (`owner/repo/path@ref`), handles `upload-artifact` / `download-artifact` and the GitHub cache protocol under emulation, and has a `watch` subcommand that reruns only the workflows whose `paths:` filter matches the files you changed.

None of that was part of the original plan. It just kept happening the way side projects usually do. I'd hit some gap between "works on GitHub" and "doesn't work locally," get annoyed by it, and then go build the missing piece.

## Why Rust?

There are two reasons:

The practical one is that I wanted a single static binary. Something you can install with `cargo install wrkflw` or `brew install wrkflw` and just run. No Python environment, no Node setup, no JVM warming up in the background. The CLI starts in milliseconds, which matters when a file watcher is calling it over and over. The TUI is built on [ratatui](https://github.com/ratatui/ratatui), which is genuinely fun to work with once the immediate-mode model clicks.

The more honest reason is that I wanted to learn Rust properly. I [said something similar when I wrote about `zp` a few years ago](/posts/why-i-built-zp.html). That was my first crate, and it was mostly an excuse to stop fighting the borrow checker and actually understand it. wrkflw is what happened when I picked a problem big enough to force me into the parts of Rust you can't fake for long: lifetimes in the expression evaluator, async boundaries between the executor and the runtime, error types that make sense across crate boundaries, and refactors that don't break people who installed the tool last month.

Those aren't things you really learn from a tutorial. You learn them by building something large enough that the design starts to sag a little, and then figuring out how to make it hold together again without throwing the whole thing away.

If you're thinking about a Rust side project, my advice is simple: pick something where the type system earns its keep. CI tooling is great for that. Workflow files can go wrong in a hundred different ways, and the compiler will usually catch a surprising number of them before you even run a test.

## The hardest part: running workflows with no container at all

The piece I'm proudest of, and the one that took the longest to get right, is `--runtime secure-emulation`.

The problem it solves is pretty straightforward. Sometimes you want to run a GitHub Actions workflow locally, but you don't have Docker, and the workflow is from a third-party repo or a PR you haven't reviewed yet. Plain `--runtime emulation` will run every `run:` step directly on your machine with your user's permissions. That's fine for your own code. It's absolutely not fine for code you don't trust.

The careful answer is "just install Docker," but I wanted there to be something in the middle. Not as strong as a real container boundary, but still much better than "hope this shell script behaves itself."

That's what secure emulation tries to be. Every `run:` step still executes on the host, so you don't need a container runtime, but it goes through a sandbox layer first. That layer does a few things:

- It keeps a command whitelist and blocklist. Normal CI commands like `echo`, `git`, `cargo`, `node`, `npm`, `python`, `go`, and `tar` are fine. Obvious foot-guns like `rm`, `dd`, `mkfs`, `mount`, `sudo`, `kill`, `systemctl`, and `reboot` aren't.
- It checks commands for dangerous patterns. Allowing `bash` is one thing; allowing `bash -c "rm -rf /"` is another. So before anything runs, the command is matched against patterns for things like `rm -rf /`, `dd ... of=/dev/...`, `curl | sh`, `wget | sh`, and the classic fork bomb.
- It strips environment variables that can be used to hijack execution, including `LD_PRELOAD`, `LD_LIBRARY_PATH`, `DYLD_INSERT_LIBRARIES`, `DYLD_LIBRARY_PATH`, and even `PATH`, `HOME`, and `SHELL`.
- It puts a ceiling on resource usage: five-minute timeout per step, capped processes, and no network by default.

The most important part, though, is being honest about what it does *not* do. It doesn't give you filesystem isolation. Absolute paths still point at the host filesystem. If you need a real boundary, you should use Docker or Podman.

I went back and forth on whether to ship secure emulation at all, because half-measures in security are how people get burned. What changed my mind was realizing that the real alternative was not "people will just use Docker instead." A lot of the time, the alternative was "people will run it with plain `--runtime emulation` and zero checks because Docker isn't available." In that world, a sandbox that rejects `rm -rf /` and refuses `curl | sh` is a real improvement, as long as the README and the doc comments are very loud about the limits.

Writing it ended up being an exercise in restraint. My first version had path rewriting, a private workspace, and a bunch of clever machinery that mostly just broke the artifact handler. The version that shipped is much more boring: validate the command, strip the environment, set a timeout, run in place. A lot of security work is just slowly deleting your most impressive bad ideas.

