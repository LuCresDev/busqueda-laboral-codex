#!/usr/bin/env python3
"""Check published robots.txt rules for a URL without impersonating another client.

The default evaluates the wildcard group (*), which is a generic policy check,
not proof of permission for a particular Codex browser or search provider. Pass
--agent with the real known product token when appropriate. The robots request
uses an identifiable utility User-Agent; this helper never changes the posting
fetcher's identity or bypasses a login, CAPTCHA, block or rate limit.

Longest matching rule wins; equal specificity is denied conservatively. A 404
means no published robots policy, not authorization to disregard terms. Other
unreadable/error responses leave access unconfirmed. This is a policy signal,
not an API authorization, a guarantee of access or a website terms checker.

Usage: python tools/robots_check.py <url> [--agent <real-product-token>]
Exit 0 = no robots restriction found; 1 = denied or unconfirmed; 2 = CLI misuse.
"""

import argparse
import re, subprocess, sys
from urllib.parse import urlsplit, unquote

REQUEST_AGENT = "ai-job-search-robots-check/2.0"

def _fetch(url, ua):
    """curl, not urllib: some hosts (jobup.ch) hang urllib indefinitely while
    answering curl in under a second, and --max-time is a hard ceiling."""
    # "--" terminates option parsing, so a URL beginning with a dash can never
    # be read by curl as a flag. gate() rebuilds the target as
    # scheme://host/robots.txt before calling here, so this is hardening for
    # direct callers rather than a hole in the gate path itself.
    r = subprocess.run(
        ['curl', '-sS', '-L', '--max-redirs', '5', '--max-time', '12', '-A', ua,
         '-H', 'Accept: text/plain,*/*', '-w', '\n%{http_code}', '--', url],
        # robots.txt is UTF-8 (RFC 9309). Unpinned, Turkish Windows decoded it as
        # cp1254, where bytes like 0x81 are undefined: the pipe reader thread died,
        # stdout came back None, and tr.indeed.com read as UNCONFIRMED.
        capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=20)
    if r.returncode != 0:
        raise RuntimeError('curl exit %d' % r.returncode)
    body, _, code = r.stdout.rpartition('\n')
    return body, int(code or 0)


def is_robots_body(text):
    """Does this actually look like a robots.txt?

    A misconfigured host can answer /robots.txt with 200 and an HTML error page.
    That body parses to zero rules, and zero rules read as "allowed" - so a
    soft-200 granted permission that was never given. An empty or whitespace-only
    body IS a valid allow-all under RFC 9309 and stays allowed; a non-empty body
    with no recognised directive is treated as unreadable.
    """
    text = text.removeprefix('\ufeff')          # byte-order mark, see _groups
    if not text.strip():
        return True
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].strip().lower()
        if ':' in line and line.split(':', 1)[0].strip() in (
            'user-agent', 'allow', 'disallow', 'sitemap', 'crawl-delay', 'host',
        ):
            return True
    return False

def has_undecodable_rule(text):
    """Does a User-agent, Allow or Disallow line hold U+FFFD?

    U+FFFD stands in for a byte that did not decode as UTF-8. A non-conformant
    robots.txt saved in a legacy code page (cp1254, ISO-8859-9) with raw
    non-ASCII bytes in a rule yields a pattern that can never match: the rule
    was silently skipped and the path read as allowed. Such a body is
    unreadable, not permissive. The field is named with U+FFFD removed, so a
    stray byte before "Disallow" cannot hide the line. U+FFFD in a comment or
    in any other field (Sitemap, Crawl-delay, ...) decides nothing and is
    ignored.
    """
    for raw in text.removeprefix('\ufeff').splitlines():
        line = raw.split('#', 1)[0]
        if '\ufffd' in line and ':' in line:
            field = line.split(':', 1)[0].replace('\ufffd', '').strip().lower()
            if field in ('user-agent', 'allow', 'disallow'):
                return True
    return False

def _groups(text):
    """user-agent -> [(is_allow, pattern)], tolerating blank lines inside a record.

    One leading U+FEFF is skipped, as Google's reference parser does. A file
    saved with a UTF-8 byte-order mark otherwise hid its first field: a leading
    "User-agent: *" went unseen, every rule in its group was dropped for want
    of an agent, and "Disallow: /" read as allow-all.
    """
    out, agents, expect = {}, [], True
    for raw in text.removeprefix('\ufeff').splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line or ':' not in line:
            continue
        field, _, value = line.partition(':')
        field, value = field.strip().lower(), value.strip()
        if field == 'user-agent':
            if not expect:
                agents, expect = [], True
            agents.append(value.lower())
            out.setdefault(value.lower(), [])
        elif field in ('allow', 'disallow') and agents:
            expect = False
            for a in agents:
                out[a].append((field == 'allow', value))
    return out

def _match(pattern, path):
    """RFC 9309 wildcard match; returns match length or -1.

    The pattern is percent-decoded to match the already-decoded path. Without
    this, "Disallow: /foo%20bar" never matched "/foo bar" and the rule was
    silently skipped - a fail-open on any site that encodes its own rules.
    Under RFC 9309 section 2.2.2, '$' anchors the end of the URL only when
    at the end of the pattern; mid-pattern '$' is matched literally.
    """
    if pattern == '':
        return -1
    pattern = unquote(pattern)
    end_anchor = pattern.endswith('$')
    pat = pattern[:-1] if end_anchor else pattern
    rx = '^' + ''.join('.*' if c == '*' else re.escape(c) for c in pat) + ('$' if end_anchor else '')
    return len(pattern) if re.match(rx, path) else -1

def allowed(text, agent, path):
    g = _groups(text)
    rules = g.get(agent.lower()) or g.get('*') or []
    best_len, best_allow = -1, True
    for is_allow, pat in rules:
        n = _match(pat, path)
        if n > best_len or (n == best_len and n >= 0 and not is_allow):
            best_len, best_allow = n, is_allow      # ties -> Disallow wins (cautious)
    return True if best_len < 0 else best_allow

def gate(url, agent='*'):
    parts = urlsplit(url)
    if parts.scheme not in ('http', 'https') or not parts.hostname:
        return 1, 'UNCONFIRMED - expected an absolute HTTP(S) URL'
    if not agent or not re.fullmatch(r'[A-Za-z0-9_.*-]+', agent):
        return 1, 'UNCONFIRMED - --agent must be a real product token or *'
    path = unquote(parts.path) or '/'
    if parts.query:
        path += '?' + unquote(parts.query)
    robots = f'{parts.scheme}://{parts.netloc}/robots.txt'
    body, last = None, 'no attempt'
    for ua in (REQUEST_AGENT,):
        try:
            text, code = _fetch(robots, ua)
        except Exception as e:
            last = type(e).__name__; continue
        if code == 404:
            return 0, 'ALLOWED - no robots.txt published'
        if code == 200:
            if not is_robots_body(text):
                last = 'HTTP 200 but the body is not a robots.txt'
                continue
            if has_undecodable_rule(text):
                last = 'HTTP 200 but a User-agent/Allow/Disallow line is not valid UTF-8'
                continue
            body = text; break
        last = 'HTTP %d' % code
    if body is None:
        return 1, 'UNCONFIRMED (%s) - stop automated access and use a permitted source' % last
    for a in dict.fromkeys((agent, '*')):
        if not allowed(body, a, path):
            return 1, f'DISALLOWED for {a} - stop automated access and use a permitted source'
    return 0, 'ALLOWED - robots.txt permits this path'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    parser.add_argument('--agent', default='*', help='real known robots product token; default: wildcard policy only')
    args = parser.parse_args()
    rc, msg = gate(args.url, args.agent)
    print(msg)
    sys.exit(rc)
