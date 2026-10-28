---
name: rtf-document
description: Writes a complete, valid Rich Text Format (.rtf) document that opens in Microsoft Word and WordPad. Use when someone asks for RTF, an .rtf file, or a formatted document (letter, memo, notice, summary) that must be returned as RTF text rather than Markdown.
license: Proprietary. Internal use at Anglicare SA only.
metadata:
  owner: sherennanayakkara
  version: "1.0"
---

# RTF document

Produce one complete RTF document that Word opens without errors.

## Output

- Return **only** the RTF text: it starts with `{\rtf1` and ends with the matching `}`.
- No Markdown, no code fences, no explanation before or after it. A later step may save
  your reply straight to a `.rtf` file.
- Use only plain ASCII in the file. Write any other character as an escape (see below).

## Skeleton

Start from this and keep the header lines exactly as written:

```
{\rtf1\ansi\ansicpg1252\deff0\uc1
{\fonttbl{\f0\fswiss\fcharset0 Arial;}{\f1\froman\fcharset0 Georgia;}}
{\colortbl;\red0\green0\blue0;\red0\green84\blue166;\red89\green89\blue89;}
\paperw11906\paperh16838\margl1134\margr1134\margt1134\margb1134
\f0\fs22
{\pard\sb0\sa240\b\fs36\cf2 Title\par}
{\pard\sa120 Body paragraph.\par}
}
```

- Page size is A4 with 2 cm margins (1 cm = 567 twips).
- Colour 1 is black, 2 is blue (headings) and 3 is grey (footnotes, captions).
- `\fs` is the font size in half-points, so `\fs22` is 11 pt.

## Building blocks

| Need | RTF |
|---|---|
| Heading 1 | `{\pard\sb240\sa120\keepn\b\fs32\cf2 Text\par}` |
| Heading 2 | `{\pard\sb200\sa80\keepn\b\fs26\cf2 Text\par}` |
| Paragraph | `{\pard\sa120 Text\par}` |
| Bold, italic, underline | `{\b text}`, `{\i text}`, `{\ul text}` |
| Line break in a paragraph | `\line` |
| Bullet item | `{\pard\fi-284\li284\sa60\bullet\tab Item text\par}` |
| Numbered item | `{\pard\fi-284\li284\sa60 1.\tab Item text\par}` |
| Page break | `\page` |
| Grey small note | `{\pard\sa120\fs18\cf3 Note text\par}` |

Wrap every paragraph in its own `{ }` group so formatting can't leak into the next one.

## Tables

Repeat the row definition for every row. `\cellx` is the right edge of each cell in twips
from the left margin, and the full text width on A4 with these margins is 9638.

```
{\trowd\trgaph108\trleft0
\clbrdrt\brdrs\brdrw10\clbrdrl\brdrs\brdrw10\clbrdrb\brdrs\brdrw10\clbrdrr\brdrs\brdrw10\cellx4819
\clbrdrt\brdrs\brdrw10\clbrdrl\brdrs\brdrw10\clbrdrb\brdrs\brdrw10\clbrdrr\brdrs\brdrw10\cellx9638
\pard\intbl{\b Header A}\cell\pard\intbl{\b Header B}\cell\row}
{\trowd\trgaph108\trleft0
\clbrdrt\brdrs\brdrw10\clbrdrl\brdrs\brdrw10\clbrdrb\brdrs\brdrw10\clbrdrr\brdrs\brdrw10\cellx4819
\clbrdrt\brdrs\brdrw10\clbrdrl\brdrs\brdrw10\clbrdrb\brdrs\brdrw10\clbrdrr\brdrs\brdrw10\cellx9638
\pard\intbl Value 1\cell\pard\intbl Value 2\cell\row}
{\pard\sa120\par}
```

Each row needs exactly one `\cell` per `\cellx`, and must end with `\row`. Always put an
ordinary paragraph after the last row.

## Escaping text

| Character | Write |
|---|---|
| `\` | `\\` |
| `{` | `\{` |
| `}` | `\}` |
| en dash, em dash | `\endash `, `\emdash ` |
| curly quotes | `\lquote `, `\rquote `, `\ldblquote `, `\rdblquote ` |
| bullet character in text | `\bullet ` |
| any other non-ASCII character | `\uN?` where N is the decimal code point, for example `\u233?` for é |

A control word ends at the first character that isn't a letter or digit. When the next
character is a letter, put a space after the control word; RTF drops that space.
Code points above 32767 must be written as negative numbers (N minus 65536).

## Before you reply, check

1. The reply starts with `{\rtf1` and ends with `}`.
2. Every `{` has a matching `}`, not counting the escaped `\{` and `\}`.
3. Every paragraph ends with `\par`, and every table row ends with `\row`.
4. No raw non-ASCII characters remain.
5. You have written nothing outside the RTF.
