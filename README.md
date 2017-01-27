# blog
Lev's Hacking Notes Blog

[![CI](https://circleci.com/gh/levlaz/blog.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/levlaz/blog)

## Installation

## Development

### Generating Documentation

From the project root run `pydoc -w ./` to generate documentation for all python files. Then you can remove all of the tests and should move all of the newly generated html files to the docs/ folder.

```
pydoc -w ./
rm test*.html
mv *.html docs/
```
