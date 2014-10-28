# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

# If not running interactively, don't do anything
[ -z "$PS1" ] && return

# don't put duplicate lines in the history. See bash(1) for more options
# ... or force ignoredups and ignorespace
HISTCONTROL=ignoredups:ignorespace

# append to the history file, don't overwrite it
shopt -s histappend

# attempt to save each line of a multi-line command in the same
# history entry, adding  semicolons  where necessary
shopt -s cmdhist

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)
HISTSIZE=5000
HISTFILESIZE=10000
HISTTIMEFORMAT='%Y-%m-%d %H:%M:%S  '

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
        # We have color support; assume it's compliant with Ecma-48
        # (ISO/IEC-6429). (Lack of such support is extremely rare, and such
        # a case would tend to support setf rather than setaf.)
        color_prompt=yes
    else
        color_prompt=
    fi
fi

RESET='\[\033[0m\]'
RED='\[\033[00;31m\]'
GREEN='\[\033[00;32m\]'
YELLOW='\[\033[00;33m\]'
BLUE='\[\033[00;34m\]'
PURPLE='\[\033[00;35m\]'
CYAN='\[\033[00;36m\]'
LIGHTGRAY='\[\033[00;37m\]'
LRED='\[\033[01;31m\]'
LGREEN='\[\033[01;32m\]'
LYELLOW='\[\033[01;33m\]'
LBLUE='\[\033[01;34m\]'
LPURPLE='\[\033[01;35m\]'
LCYAN='\[\033[01;36m\]'
WHITE='\[\033[01;37m\]'

if [ "$color_prompt" = yes ]; then
    if [ $(hostname) = bot ]; then
        PS1="${WHITE}\u@${LRED}\h${RESET}:${LBLUE}\w${RESET}\\$ "
    else
        PS1="${WHITE}\u@\h${RESET}:${LBLUE}\w${RESET}\\$ "
    fi
else
    PS1='\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;\u@\h: \w\a\]$PS1"
    ;;
*)
    ;;
esac

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    #alias dir='dir --color=auto'
    #alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# some more ls aliases
alias bc='bc -l'
alias pylab='ipython --pylab'

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if [ -f /etc/bash_completion ] && ! shopt -oq posix; then
    . /etc/bash_completion
fi

set -o vi

export EDITOR=vim
export PAGER="less -R"

# Automatically enter virtualenv if .venv is present
cd ()
{
    builtin cd "$@"
    RETVAL=$?
    # Test for successful real cd:
    if [ 0 -ne $RETVAL ]; then
        return $RETVAL
    fi
    # Deactivate once I move outside the virtualenv directory or 
    # do nothing when I'm still in this same virtualenv directory
    # (Assuming no one nests virtualenvs....)
    if [ ! -z "$VIRTUAL_ENV" ]; then
        if [ "$PWD" = "${PWD#$VIRTUAL_ENV}" ]; then
            deactivate
        else
            return 0
        fi
    fi
    # Determine if we've designated a venv
    if [ -r ".venv" ]; then
        VENV_DIR=$(cat .venv)
        source "${VENV_DIR}/bin/activate"
    fi
    return 0
}

# Convenient bone-specific variables
export SLOTS=/sys/devices/bone_capemgr.*/slots
export PINS=/sys/kernel/debug/pinctrl/44e10800.pinmux/pins
export PINMUX=/sys/kernel/debug/pinctrl/44e10800.pinmux/pinmux-pins
export PINGROUPS=/sys/kernel/debug/pinctrl/44e10800.pinmux/pingroups

# Additional C libraries (prussdrv, etc)
export LD_LIBRARY_PATH=/usr/local/lib

