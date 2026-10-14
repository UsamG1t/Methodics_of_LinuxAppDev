#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from urllib.parse import unquote
from unicodedata import lookup

def normalize_anchor(anchor):
    """
    Преобразует якорь в формат GitHub Pages
    """
    anchor = unquote(anchor)
    
    anchor = re.sub(r'\s+', '-', anchor)
    anchor = re.sub(r'[`:]', '', anchor)
    
    anchor = re.sub(r'-+', '-', anchor)
    anchor = anchor.strip('-').lower()
    
    return anchor

def replace_link_with_anchor(match):
    path_part = match.group(1)
    anchor_part = match.group(2)
    
    normalized_anchor = normalize_anchor(anchor_part)
    new_path = path_part.replace('.md', '.html')

    return f"]({new_path}#{normalized_anchor})"


def convert_links_in_file(filepath):
    """
    1. .md#anchor -> .html#normalized-anchor
    2. .md) -> .html)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original_content = content

    pattern_with_anchor = r'\]\(([^\)]+\.md)#([^\)]*)\)'
    content = re.sub(pattern_with_anchor, replace_link_with_anchor, content)
    content = re.sub(r'\.md\)', '.html)', content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Updated: {filepath}")
        return True
    else:
        print(f"  No changes: {filepath}")
        return False

def convert_emojies_in_file(filepath):

    emojies_dict = {
        r":warning:": lookup("WARNING SIGN"),
        r':round_pushpin:': lookup("ROUND PUSHPIN"),
        r':information_source:': lookup("INFORMATION SOURCE"),
        r':large_blue_diamond:': lookup("LARGE BLUE DIAMOND")
    }

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original_content = content

    for ptn in emojies_dict.keys():
        content = re.sub(ptn, emojies_dict[ptn], content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Update emojies: {filepath}")
        return True
    else:
        print(f"  No changes with emojies: {filepath}")
        return False

def convert_refs_in_file(filename):
    """
    Добавляет поддержку собственных генерируемых ссылок формата [SOURCE:User:page_path]
    """
    refs_dict = {
        "GT": "https://github.com/",
        "default_name": "UsamG1t/",
    }

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original_content = content

    ptn = r"\[([A-Z]+):([\w]*):([\w-]+)\]"
    while res := re.search(ptn, content):
        site, user, link = res.group(1, 2, 3)
        res_link = refs_dict[site] + (user if user else refs_dict["default_name"]) + link
        content = content.replace(res.group(), f'[{res_link}]({res_link})')

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Update refs: {filepath}")
        return True
    else:
        print(f"  No changes with refs: {filepath}")
        return False

def generate_contents(filename):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    original_content = content

    header_pattern = r'^(#{1,6})\s+(.+)$'
    headers = []

    for line in content.split('\n'):
        match = re.match(header_pattern, line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            headers.append((level, title))

    if not headers:
        print(f"  No changes with contents: {filepath}")
        return False

    toc_lines = [
        ''
        '# Быстрый поиск',
        ''
    ]

    seen_titles = {}

    for level, title in headers:
        anchor = unquote(title)

        anchor = re.sub(r'\s+', '-', anchor)
        anchor = re.sub(r'[`:]', '', anchor)

        anchor = re.sub(r'-+', '-', anchor)
        anchor = anchor.strip('-').lower()

        if anchor in seen_titles:
            seen_titles[anchor] += 1
            anchor = f"{anchor}-{seen_titles[anchor]}"
        else:
            seen_titles[anchor] = 1

        indent = ' ' * (2 * (level - 1))
        toc_lines.append(f'{indent} + [{title}](#{anchor})')

    toc_lines.append('')
    toc_lines.append('---')

    content = re.sub(r'\[:contents:\]', '\n'.join(toc_lines), content, flags=re.MULTILINE)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Generate contents: {filepath}")
        return True
    else:
        print(f"  No changes with contents: {filepath}")
        return False

md_files = [f for f in Path('.').rglob('*.md') if '.git' not in str(f)]
    
if not md_files:
    print("No .md files found")
    exit(0)

changed = 0
for filepath in sorted(md_files):
    if any([
        generate_contents(filepath),
        convert_links_in_file(filepath),
        convert_emojies_in_file(filepath),
        convert_refs_in_file(filepath)
    ]):
        changed += 1


print(f"\nTotal: {len(md_files)} files processed, {changed} files changed")

