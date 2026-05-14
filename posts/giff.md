---
title: "giff"
description: "git diff terminal visualizer"
date: 2024-08-06
author: "bahdotsh"
status: "published"
slug: "giff"
tags: ["projects", "rust", "cli", "git", "open-source"]
featured: false
---

# giff

[giff](https://github.com/bahdotsh/giff) visualizes the differences between the current `HEAD` and a specified branch in a git repository using a formatted
table output in your terminal. The differences are displayed with color-coded additions and deletions for better readability.

## Features

- **Branch Comparison**: Compare changes between the current HEAD and a specified branch.
- **Color-coded Output**: Additions are displayed in green and deletions in red.
- **Table Formatting**: Uses `comfy_table` to format the output.

## Requirements

- Rust (latest stable version)
- Git
- A terminal supporting ANSI escape codes for color output

## Dependencies

This project uses the following Rust crates:

- `clap`: For command-line argument parsing.
- `comfy_table`: For creating and formatting tables.
- `crossterm`: For terminal manipulation.
- `regex`: For parsing git diff output.

## Installation
```
cargo install giff
```

## From source
```
git clone https://github.com/bahdotsh/giff.git
cd giff
cargo install --path .
```

## Usage
```
giff -b branch //by default, the branch will be main
```
