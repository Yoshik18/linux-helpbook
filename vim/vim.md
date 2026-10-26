# Vim: edit a file without getting lost

Vim is a terminal text editor. It has modes: the same key can insert text in
Insert mode or run an editing command in Normal mode. Press `Esc` to return to
Normal mode if you are unsure where you are.

Source the fixture from the repository root in the same terminal first:

```bash
source fundamentals/labs/setup.sh
printf '%s\n' "$LINUX_LAB"
```

This creates a private temporary notes directory and exports `LINUX_LAB` for this
shell. Now open a disposable file, not a system configuration file:

```bash
vim "$LINUX_LAB/notes/vim-practice.txt"
```

## Make and save a small edit

1. Vim starts in Normal mode. Press `i` to enter Insert mode.
2. Type `first line` and press `Enter`, then type `second line`.
3. Press `Esc`. You are back in Normal mode.
4. Type `:wq` and press `Enter` to write the file and quit.
5. Check the result from the shell:

```bash
cat "$LINUX_LAB/notes/vim-practice.txt"
```

`cat` prints the saved two lines. Vim commands in this guide assume you have
pressed `Esc` first unless they explicitly say Insert mode. `:` opens Vim's
command line, where you type an Ex command and press `Enter`.

## Move around and find text

| In Normal mode | Action | Detail |
|---|---|---|
| `h`, `j`, `k`, `l` | Left, down, up, right | Arrow keys often work too; these keys work without leaving the home row. |
| `w`, `b` | Next word, previous word | Word boundaries depend on punctuation and Vim's `iskeyword` setting. |
| `0`, `^`, `$` | Line start, first nonblank, line end | `^` differs from `0` on an indented line. |
| `gg`, `G` | First line, last line | `:25` then Enter jumps to line 25. |
| `/pattern` | Search forward | Press Enter, then `n` for next and `N` for previous match. |
| `?pattern` | Search backward | Press Enter to search; `n` repeats in the same search direction. |
| `*`, `#` | Search word under cursor | Forward and backward respectively. |

Use `/timeout` then Enter to find a word. Press `Esc` to stop highlighting or
continue editing. Vim regular expressions are not identical to shell globs.

## Change text

These are Normal-mode commands. Start on the disposable practice file:

| Command | Effect | How to read it |
|---|---|---|
| `i` | Insert before cursor | Press `Esc` when done typing. |
| `a` | Insert after cursor | Useful when the cursor is on the last character. |
| `o` | Open a line below and insert | `O` opens one above. |
| `x` | Delete character under cursor | Changes the buffer immediately; `u` undoes. |
| `dd` | Delete current line | `p` puts the deleted text after the cursor. |
| `yy` | Copy (yank) current line | `p` puts the copied line below. |
| `u` / `Ctrl+r` | Undo / redo | Undo applies to the current buffer's change history. |
| `dw` | Delete from cursor to next word boundary | Vim combines an operator (`d`) with a motion (`w`). |
| `ciw` | Change the word under cursor | Deletes that word and enters Insert mode. |
| `dd` then `p` | Move a line down | Delete and put are operations, not shell commands. |

For example, `d$` means delete from the cursor (`d`) to the end of the line (`$`).
This operator-plus-motion pattern is reusable: `y$` copies to line end, while
`c$` changes text to line end and enters Insert mode. If you make a mistake,
press `Esc` and `u` before saving.

## Replace carefully

From Normal mode, `:%s/old/new/gc` searches the whole file (`%`), substitutes
`new` for `old` (`s`), applies to every match on each line (`g`) and asks before
each change (`c`). Review prompts before accepting. Without `c`, the edit happens
without confirmation; inspect with `u` to undo before writing.

- `:s/old/new/` changes the first match on the current line.
- `:s/old/new/g` changes every match on the current line.
- `:%s/old/new/g` changes matches throughout the buffer.
- `:%s/old/new/gc` asks before each replacement throughout the buffer.

The slash separates pattern and replacement. Escape a literal slash or choose a
different delimiter, for example `:%s#old/path#new/path#g`.

## Save, quit and recover

| Command | Result |
|---|---|
| `:w` | Write changes to the current file. |
| `:q` | Quit if there are no unsaved changes. |
| `:wq` | Write, then quit. |
| `:q!` | Discard unsaved buffer changes and quit. Use only when you mean to lose them. |
| `:x` | Write and quit if changed; otherwise just quit. |

If `:q` says there are unsaved changes, do not jump straight to `:q!`. Use `:w`
to save, or inspect/undo the changes first. For a new buffer, `:w filename` sets
its path and writes it. Vim's swap/recovery behavior can depend on configuration;
follow its message before removing any recovery file.

## Windows and settings

Vim can show multiple buffers in windows. `:split filename` opens a horizontal
split, `:vsplit filename` a vertical split. Press `Ctrl+w` then `h`, `j`, `k` or
`l` to move between windows; `:close` closes the current window, not necessarily
the whole Vim process.

Useful temporary display settings:

```vim
:set number
:set nonumber
:set wrap
:set nowrap
```

These affect the current session; whether settings persist depends on your Vim
configuration. `:help motion`, `:help :s` and `:help write` open Vim's built-in
help. Press `q` from a help window to close it.

## Keep this short list handy

- `Esc`: return to Normal mode.
- `i`: insert before cursor.
- `/word`: search forward.
- `u`: undo.
- `:w`: save.
- `:q`: quit when clean.
- `:q!`: quit and discard unsaved edits.

Vim and Neovim share many basic commands, but plugins, defaults and configuration
can differ. Learn a few motions and save/quit safely before exploring macros,
registers or complex text objects.

[Back to the Linux Helpbook](../README.md)
