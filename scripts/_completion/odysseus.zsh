#compdef honeybadger honeybadger-backup honeybadger-calendar honeybadger-contacts honeybadger-cookbook honeybadger-docs honeybadger-gallery honeybadger-mail honeybadger-mcp honeybadger-memory honeybadger-notes honeybadger-personal honeybadger-preset honeybadger-research honeybadger-sessions honeybadger-signature honeybadger-skills honeybadger-tasks honeybadger-theme honeybadger-webhook
# Zsh tab-completion for the honeybadger umbrella + sub-CLIs.
#
# Drop in any directory on $fpath, e.g.:
#     fpath=(/path/to/honeybadger-ui/scripts/_completion $fpath)
#     autoload -U compinit; compinit
#
# Then `honeybadger <tab>` completes subcommands; `honeybadger mail <tab>`
# completes mail subcommands; `honeybadger-mail <tab>` works the same.

_honeybadger_scripts_dir() {
    local self="${(%):-%x}"
    while [[ -L "$self" ]]; do self="$(readlink "$self")"; done
    cd "${self:h}/.." && pwd
}

typeset -gA _honeybadger_subs

_honeybadger_refresh() {
    _honeybadger_subs=()
    local dir="$(_honeybadger_scripts_dir)"
    local py="$dir/../venv/bin/python"
    [[ -x "$py" ]] || py="$(command -v python3)"
    local f sub help_out commands
    for f in "$dir"/honeybadger-*; do
        [[ -x "$f" ]] || continue
        case "$f" in
            *.bak|*.pyc|*.pre-*) continue ;;
        esac
        sub="${${f:t}#honeybadger-}"
        help_out=$("$py" "$f" --help 2>/dev/null) || continue
        commands=$(echo "$help_out" | grep -oE '\{[a-z0-9_,-]+\}' | head -1 \
            | tr -d '{}' | tr ',' ' ')
        _honeybadger_subs[$sub]="$commands"
    done
}

_honeybadger() {
    [[ ${#_honeybadger_subs} -eq 0 ]] && _honeybadger_refresh

    local cmd="${words[1]}"

    if [[ "$cmd" == "honeybadger" ]]; then
        if (( CURRENT == 2 )); then
            local -a subs=(${(k)_honeybadger_subs} help)
            _describe 'subcommand' subs
            return
        fi
        local sub="${words[2]}"
        if [[ "$sub" == "help" ]] && (( CURRENT == 3 )); then
            local -a subs=(${(k)_honeybadger_subs})
            _describe 'subcommand' subs
            return
        fi
        if (( CURRENT == 3 )); then
            local -a sc=(${(s/ /)_honeybadger_subs[$sub]})
            _describe 'command' sc
            return
        fi
        return
    fi

    # honeybadger-foo <tab>
    local sub="${cmd#honeybadger-}"
    if (( CURRENT == 2 )); then
        local -a sc=(${(s/ /)_honeybadger_subs[$sub]})
        _describe 'command' sc
        return
    fi
}

_honeybadger "$@"
