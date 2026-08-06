// hedron-extras TerminalView host stub — fail-closed without allowlist
export function mountTerminal(el){if(el.dataset.allowlist!=='1'){el.textContent='Terminal disabled';return;}el.dataset.hedronTerminal='ready';}
