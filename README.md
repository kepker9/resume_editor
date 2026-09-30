# Resume tailor

A Python 3.10+ CLI that sends your LaTeX resume, optional master profile, and job
description to Claude and saves a tailored LaTeX document. No frontend is required.

## Setup and run

From this directory (macOS/Linux):

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade -r requirements.txt
cp .env.example .env
```

Edit `.env` and add your actual Anthropic key:

```dotenv
ANTHROPIC_API_KEY=your_key_here
```

`your_key_here` is a placeholder, not a usable key. `.env` is ignored by Git.
An existing `ANTHROPIC_API_KEY` shell variable takes precedence over `.env`.

Create your private input files from the public templates (on first setup only):

```sh
cp input/resume.example.tex input/resume.tex
cp input/master_profile.example.txt input/master_profile.txt
cp input/job_description.example.txt input/job_description.txt
```

These commands overwrite existing inputs, so skip them if you already have your
own files. Replace all example text before running the app.

1. Put your complete LaTeX document in `input/resume.tex`.
2. Put additional factual experiences, projects, skills, coursework, and details in
   `input/master_profile.txt`. It may be empty or absent.
3. Put the employer's job description in `input/job_description.txt`.
4. Run `python main.py`.
5. Find the result in `output/tailored_resume.tex`.

Only the three example inputs are committed to Git. Other files and subfolders in
`input/`, including your real resume, master profile, and job description, are
ignored. The example files ensure `input/` exists when someone clones the project.
Never put personal information in the example files.

The entire `output/` folder is ignored. The app automatically creates it and saves
`tailored_resume.tex` after a successful generation, so a new user does not need to
create it manually. Paths are resolved relative to `main.py`, so running from
another directory also works.

## Files and configuration

- `main.py`: loads `.env`, reads inputs, calls Claude, prints usage/cost, saves output.
- `claude_client.py`: API call, error handling, typed LaTeX/usage result.
  Change `MODEL`, `MAX_OUTPUT_TOKENS`, and the two per-million-token price constants
  at the top here. Update prices when changing models; estimates assume standard
  uncached requests and exclude taxes or account-specific discounts.
- `prompts.py`: truthfulness, relevance, formatting, and one-page
  instructions; separates candidate facts from employer requirements with tags.
- `utils.py`: UTF-8 reading, outer-fence cleanup, basic LaTeX validation,
  and atomic writes that preserve previous output on failure.
- `requirements.txt`: only `anthropic` and `python-dotenv`; installation selects the
  current SDK rather than pinning an old release.

The default is `claude-sonnet-5-5` with medium effort. Model, SDK syntax, and standard
pricing ($2 input / $10 output per million tokens) were checked on 2026-09-30:
[models](https://platform.claude.com/docs/en/models/overview),
[Sonnet request example](https://platform.claude.com/docs/en/models/sonnet-5-5/migration-guide),
[Python SDK](https://github.com/anthropics/anthropic-sdk-python),
[pricing](https://platform.claude.com/docs/en/about-claude/pricing).

## Validation and limitations

Empty, prose-like, incomplete, refused, or truncated results are rejected. Only
outer Markdown fences and surrounding whitespace are cleaned. The previous output
is replaced atomically after validation; API/file failures exit with status 1.
The SDK retries transient failures twice, with a 120-second timeout per request.

This first version checks document structure, not LaTeX compilation, factual
accuracy, or rendered page count. The prompt requires exactly one page, but you
must compile in your usual LaTeX editor and check the PDF and claims before use.
It does not automatically compile generated code. The input documents are sent
to Anthropic when run. Git ignore rules keep private inputs out of normal commits;
they do not stop the app from reading them or sending them to Anthropic.
