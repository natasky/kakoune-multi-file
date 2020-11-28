# kak-multi-file

Kakoune plugin to make changes across multiple files in one buffer.

TODO: demo clip

## Workflow

### Collect lines to change

Tip: ...use kakoune-find to make quick changes...
Tip: ...remove uninteresting lines, add more lines with `!grep`...
Tip: ...use compiler/linter output...

### Make changes in a single buffer

### Optional: review changes

### Apply changes

## Caveats

... this works directly on disk, no support for modifying open buffers
... changing files while multi-file buffer exists will prevent it from applying

## Setup

Requirements:

- Python 3.6 or newer.

Use `plug.kak` to install:

```
plug "natasky/kak-multi-file"
```

## Comparison with kakoune-find

## Contibuting

Bug reports, ideas for features and PRs are welcome!
