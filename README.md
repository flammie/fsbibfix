# F’sbibfix

Flammie’s bib fixer is a tool to sort and unify bib files in my style. It
doesn't implement a generic bib parser or anything, just reads line-by-line and
expects somewhat sane bib file formatting, then sorts lowercased id's and keys
and prints a new file.

## Usage

```shell
fsbibfix.py -i INPUT -o OUTPUT
```

