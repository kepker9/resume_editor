# Resume editor

A Python app that sends your LaTeX resume, optional master profile, and job description to Claude and saves a tailored LaTeX document.

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

1. Put your complete LaTeX document in `input/resume.tex`.
2. Put additional factual experiences, projects, skills, coursework, and details in
   `input/master_profile.txt`. It may be empty or absent.
3. Put the employer's job description in `input/job_description.txt`.
4. Run `python main.py`.
5. Find the result in `output/tailored_resume.tex`.


## Files and configuration

- `main.py`: loads `.env`, reads inputs, calls Claude, prints usage/cost, saves output.
- `claude_client.py`: API call, error handling, typed LaTeX/usage result.
  Change `MODEL`, `MAX_OUTPUT_TOKENS`, and the two per-million-token price constants at the top here. Update prices when changing models; estimates assume standard uncached requests and exclude taxes or account-specific discounts.
- `prompts.py`: truthfulness, relevance, formatting, and one-page
  instructions; separates candidate facts from employer requirements with tags.
- `utils.py`: UTF-8 reading, outer-fence cleanup, basic LaTeX validation,
  and atomic writes that preserve previous output on failure.

The default is `claude-sonnet-5-5` with medium effort. Model, SDK syntax, and standard pricing ($2 input / $10 output per million tokens).