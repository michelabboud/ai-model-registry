# Reserved media directory

`media/` is reserved for Genie's future media data. R1 defines no media schema or
validation contract. `scripts/validate.py` intentionally ignores this directory.

Harness icons are separate: a harness `icon` is an identifier that the consuming
app maps to an embedded asset. The registry does not ship harness icon files.
