# Vim Cheatsheet

## Modes
- **Normal Mode**: Default mode for navigation and commands
- **Insert Mode**: For typing text (press `i` to enter)
- **Visual Mode**: For selecting text (press `v` to enter)
- **Command Mode**: For executing commands (press `:` to enter)

## Navigation (Normal Mode)

### Basic Movement
- `h` - Move left
- `j` - Move down
- `k` - Move up
- `l` - Move right
- `w` - Move to next word
- `b` - Move to previous word
- `e` - Move to end of word
- `0` - Move to beginning of line
- `$` - Move to end of line
- `^` - Move to first non-blank character
- `gg` - Move to beginning of file
- `G` - Move to end of file
- `:n` - Jump to line n

### Advanced Movement
- `Ctrl+f` - Page down
- `Ctrl+b` - Page up
- `Ctrl+d` - Half page down
- `Ctrl+u` - Half page up
- `%` - Jump to matching bracket
- `{` - Jump to previous empty line
- `}` - Jump to next empty line
- `*` - Jump to next occurrence of word under cursor
- `#` - Jump to previous occurrence of word under cursor

## Entering Insert Mode
- `i` - Insert before cursor
- `a` - Insert after cursor
- `I` - Insert at beginning of line
- `A` - Insert at end of line
- `o` - Insert new line below
- `O` - Insert new line above
- `s` - Delete character and insert
- `S` - Delete line and insert

## Exiting Insert Mode
- `Esc` - Return to normal mode
- `Ctrl+c` - Return to normal mode

## Visual Mode
- `v` - Start visual mode
- `V` - Start visual line mode
- `Ctrl+v` - Start visual block mode
- `Esc` - Exit visual mode

## Editing Commands

### Delete
- `x` - Delete character under cursor
- `X` - Delete character before cursor
- `dd` - Delete entire line
- `dw` - Delete word
- `d$` - Delete to end of line
- `d0` - Delete to beginning of line
- `dgg` - Delete to beginning of file
- `dG` - Delete to end of file

### Copy (Yank)
- `yy` - Copy entire line
- `yw` - Copy word
- `y$` - Copy to end of line
- `y0` - Copy to beginning of line

### Paste
- `p` - Paste after cursor
- `P` - Paste before cursor

### Change
- `cw` - Change word
- `cc` - Change entire line
- `c$` - Change to end of line
- `c0` - Change to beginning of line

### Undo/Redo
- `u` - Undo
- `Ctrl+r` - Redo

## Search and Replace

### Search
- `/pattern` - Search forward for pattern
- `?pattern` - Search backward for pattern
- `n` - Next search result
- `N` - Previous search result
- `*` - Search for word under cursor
- `#` - Search backward for word under cursor

### Replace
- `:s/old/new` - Replace first occurrence on current line
- `:s/old/new/g` - Replace all occurrences on current line
- `:%s/old/new/g` - Replace all occurrences in file
- `:%s/old/new/gc` - Replace all with confirmation

## File Operations

### Save and Quit
- `:w` - Save file
- `:q` - Quit (if no changes)
- `:wq` - Save and quit
- `:x` - Save and quit
- `ZZ` - Save and quit
- `:q!` - Quit without saving
- `ZQ` - Quit without saving

### File Navigation
- `:e filename` - Edit file
- `:sp filename` - Split window and edit file
- `:vsp filename` - Vertical split and edit file
- `:bn` - Next buffer
- `:bp` - Previous buffer
- `:bd` - Delete buffer

## Window Management
- `Ctrl+w h` - Move to left window
- `Ctrl+w j` - Move to window below
- `Ctrl+w k` - Move to window above
- `Ctrl+w l` - Move to right window
- `Ctrl+w s` - Split window horizontally
- `Ctrl+w v` - Split window vertically
- `Ctrl+w c` - Close window
- `Ctrl+w o` - Close other windows

## Marks and Registers
- `ma` - Set mark 'a'
- `'a` - Jump to mark 'a'
- `"ayy` - Copy line to register 'a'
- `"ap` - Paste from register 'a'
- `:reg` - Show registers

## Macros
- `qa` - Start recording macro 'a'
- `q` - Stop recording
- `@a` - Execute macro 'a'
- `@@` - Execute last macro

## Folding
- `zf` - Create fold
- `zo` - Open fold
- `zc` - Close fold
- `za` - Toggle fold
- `zR` - Open all folds
- `zM` - Close all folds

## Indentation
- `>>` - Indent line
- `<<` - Unindent line
- `>G` - Indent to end of file
- `>gg` - Indent to beginning of file
- `=G` - Auto-indent to end of file

## Text Objects
- `diw` - Delete inner word
- `daw` - Delete a word (including space)
- `di"` - Delete inside quotes
- `da"` - Delete around quotes
- `dip` - Delete inside paragraph
- `dap` - Delete around paragraph

## Command Line
- `:help` - Open help
- `:set number` - Show line numbers
- `:set nonumber` - Hide line numbers
- `:set wrap` - Enable line wrapping
- `:set nowrap` - Disable line wrapping
- `:set ignorecase` - Ignore case in search
- `:set smartcase` - Smart case matching
- `:syntax on` - Enable syntax highlighting
- `:syntax off` - Disable syntax highlighting

## Advanced Commands
- `gq` - Format text
- `gw` - Format text and return to original position
- `J` - Join lines
- `gJ` - Join lines without spaces
- `Ctrl+a` - Increment number
- `Ctrl+x` - Decrement number
- `~` - Toggle case
- `guu` - Convert line to lowercase
- `gUU` - Convert line to uppercase
- `g~~` - Toggle case of line

## Tips
- Use `:help` to get help on any command
- Press `Esc` to return to normal mode
- Use `Ctrl+g` to show file information
- Use `Ctrl+l` to redraw screen
- Use `:set paste` before pasting to preserve formatting
- Use `:set nopaste` after pasting
