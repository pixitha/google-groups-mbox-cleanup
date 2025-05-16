# mbox-cleaner

I was working to recover old news group emails from the `info.gated` group from the mid-90s, the only copy so far that I can find was from [archive.org](https://archive.org/details/usenet-info), however this collection of mbox files appears to have been scraped from Google Groups, which adds a bunch of extra stuff to the headers. The dates were partially broken, but thats probably just due to really old emails.

This script fixes malformed `From_` separator lines, normalizes various date formats in the `Date` headers, and removes unwanted `X-Google-*` metadata headers.

---

## Features

- ✅ Reconstructs proper `From_` separator lines using parsed `From` and `Date` headers.
- ✅ Parses and normalizes multiple date formats into standard RFC 5322-compliant dates.
- ✅ Removes Google-specific metadata headers (`X-Google-Thread`, `X-Google-Attributes`, etc.).
- ✅ Provides informative logs about the number of messages processed and issues corrected.

---

## Usage

```bash
python mbox_cleaner.py input.mbox output.mbox
```

- `input.mbox`: Path to your original, messy mbox file.
- `output.mbox`: Path to save the cleaned and fixed mbox file.

---

## Example

```bash
python mbox_cleaner.py old-archive.mbox cleaned-archive.mbox
```

Output (logs):

```
INFO:__main__:Processed 450 messages, fixed 446 dates
INFO:__main__:Removed 890 X-Google headers
INFO:__main__:Fixed 450 Google From lines
```

---

## Before and After

### Before:
```
From 6027616436443015462
X-Google-Language: ENGLISH,ASCII-7-bit
X-Google-Thread: 106b27,5a841f9366afc02e
X-Google-Attributes: gid106b27,public
From: acee@raleigh.ibm.com (Acee Lindem)
Subject: Re: Selecting routes based on source host names/numbers
Date: 1996/02/29
Message-ID: <9602292009.AA15229@heavens-gated.raleigh.ibm.com>#1/1
X-Deja-AN: 141631199
organization: University of Illinois at Urbana
newsgroups: info.gated
originator: daemon@ux1.cso.uiuc.edu
```

### After:
```
From acee@raleigh.ibm.com Thu Feb 29 00:00:00 1996
From: acee@raleigh.ibm.com (Acee Lindem)
Subject: Re: Selecting routes based on source host names/numbers
Date: Thu, 29 Feb 1996 00:00:00 GMT
Message-ID: <9602292009.AA15229@heavens-gated.raleigh.ibm.com>#1/1
X-Deja-AN: 141631199
organization: University of Illinois at Urbana
newsgroups: info.gated
originator: daemon@ux1.cso.uiuc.edu
```

---

## Requirements

- Python 3.7+
- Standard library only — no external dependencies.

---

## When to Use This

This script is especially useful if:
- You’ve exported a mailing list from **Google Groups** and need to re-import it into a mail client.
- Your mbox file has nonstandard `From ` lines or malformed `Date` headers.
- You want to clean up metadata added by Google or similar archival tools.

---

## TODO

- [ ] Add support for fixing or inferring message threading (e.g. using `In-Reply-To` and `References` headers)

---

## License

This project is licensed under the **Apache License 2.0**.

If you use this tool in your project or archive restoration workflow, attribution by linking to this repo is appreciated.

---

## Author

Created by Kyle Duren — built with the help of LLM tools for email restoration and archiving tasks.
