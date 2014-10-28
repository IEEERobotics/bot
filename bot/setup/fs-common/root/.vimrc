" vimrc

" === General ===
"
set nocompatible
set showmode
set background=dark
set ffs=        " use fileformat from file (e.g., DOS/Unix)

" filesystem searching
set path+=**    " :find descends subdirs
set wildignore+=**/*.log.*
set wildignore+=**/*.pyc

" put all swap files together in one place, for Dropbox's sake
" (the ^= prepends to the existing value, allowing fallback to defaults)
set directory^=$HOME/.vim/swap//
set hidden   " allow switching away from unsaved buffers

set ttimeoutlen=50  " makes statusbar respond faster when switching modes


" === Tabs and Indents ===
set expandtab
set sts=4
set sw=4
set autoindent

"set number
set showbreak=.
set linebreak   " only wrap at reasonable characters


" === Search ===
set ignorecase
set smartcase
set incsearch
set showmatch
set hlsearch
set gdefault    " global replace by default
" clear search highlight
nnoremap <leader><space> :noh<cr>
" don't move on word-under-cursor search, just search and highlight
nmap <silent>* :let @/ = '\<'.expand('<cword>').'\>'\|set hlsearch<C-M>

" === Navigation ===

" move by visual lines (instead of logical)
nmap j gj
nmap k gk

" move between windows with control
nmap <C-h> <C-w>h
nmap <C-j> <C-w>j
nmap <C-k> <C-w>k
nmap <C-l> <C-w>l


" === Syntax ===

filetype indent plugin on
syntax on
let g:matchparen_insert_timeout = 5


" === Colors ===
set t_Co=256
colorscheme desert

"highlight clear Visual

