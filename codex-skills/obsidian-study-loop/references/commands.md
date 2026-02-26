# Command Reference

## 1) Read Progress + Generate Today Plan

```bash
python3 scripts/study_course.py plan --course-root "/path/to/course" --write-daily
```

Optional flags:

- `--date YYYY-MM-DD`
- `--minutes-min 120 --minutes-max 180`
- `--weekly-target 8`
- `--continue-current`
- `--next-lesson N` (override auto-detection)

## 2) Generate Exercises

```bash
python3 scripts/study_course.py exercise --course-root "/path/to/course" --lesson 2
```

Optional flags:

- `--audio-wikilink 'assets/Lesson02_practice.mp3'`
- `--page-image-wikilink 'Resources/Pages/p7-007.png'`
- `--tts-script-file '/path/to/lesson02_listen_practice.txt'`
- `--tts-engine edge`
- `--no-auto-tts-for-image`
- `--overwrite`

Image lesson recommendation (auto-generate listening):

```bash
python3 scripts/study_course.py exercise \
  --course-root "/path/to/course" \
  --lesson 2 \
  --page-image-wikilink "Resources/Pages/p7-007.png"
```

With default settings, this will try to auto-generate `assets/Lesson02_practice.mp3` via `edge-tts` if a matching text script exists at `Resources/Audio/lesson02_listen_practice.txt`.

## 3) Coach Dialogue Mode (Prepare Note + Run Q&A)

```bash
python3 scripts/study_course.py coach --course-root "/path/to/course" --lesson 2
```

Default behavior:

- Automatically create missing `01-练习（填写版）.md` and `03-知识点整理.md`
- Create/update `02-教练对话（问答）.md`
- Print a context checklist for the chat coaching session
- Use fast chat-first coaching after setup (avoid per-turn file writes; batch save at checkpoints)

Optional flags:

- `--coach-name "02-教练对话（问答）.md"`
- `--exercise-name "01-练习（填写版）.md"`
- `--summary-name "03-知识点整理.md"`
- `--no-prepare-docs` (skip auto document preparation)
- `--overwrite`

After running this command, read the printed context files and start Q&A teaching in chat.

## 4) Grade Homework (Prepare Note)

```bash
python3 scripts/study_course.py grade --course-root "/path/to/course" --lesson 2
```

The script appends a grading section template. Codex then reads the learner's answers and fills it.

## 5) Course Knowledge Summary

```bash
python3 scripts/study_course.py summary --course-root "/path/to/course" --lesson 2
```

The script creates or updates the lesson summary note with a stable structure.
