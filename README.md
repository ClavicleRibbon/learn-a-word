# Learn a Word

Learn one English word in every language Wiktionary has a translation for, using spaced repetition.
Works offline after the first load. No account, no tracking. Installing the app picks your word;
reinstalling gives you a new one.

## Use it
Open the site in Chrome (Android) or Safari (iOS) and choose "Install app" / "Add to Home Screen".

## Build the word database
1. Download the English-language dictionary file from https://kaikki.org/dictionary/English/ (link at the bottom of the page). Don't commit it.
2. `python build_data.py kaikki.org-dictionary-English.jsonl --min-langs 10`
3. Commit the generated `data/` folder. Use `--max-words 20000` if the repo gets too large.

## Deploy
Repo settings, Pages, deploy from the `main` branch, root folder.
The service worker loads fresh files whenever online and uses its cache offline, so updates arrive on the next open.
To test locally, run `python -m http.server` in this folder and open http://localhost:8000 (opening index.html directly does not work).

## Credits and licenses
- Code: MIT, see `LICENSE`.
- Word data (`data/`): from [Wiktionary](https://en.wiktionary.org/) contributors, extracted by Wiktextract and distributed by [Kaikki.org](https://kaikki.org/). Licensed [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), see `data/LICENSE.md`.
