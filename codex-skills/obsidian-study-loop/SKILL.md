---
name: obsidian-study-loop
description: "Manage a repeatable course-study workflow inside an Obsidian vault with command-style operations for reading current progress, generating today's study plan, creating lesson exercises, grading homework notes, organizing lesson knowledge points, and running coach dialogue mode. Use when users study textbooks or courses in Obsidian and want a consistent learning loop across planning, practice, grading, coach Q&A, and summary. Trigger this skill when the user asks for 教练模式, coach mode, interactive lesson practice, or study Q&A coaching."
---

# Obsidian Study Loop

Use this skill to standardize an Obsidian-based learning workflow around lesson folders and daily notes.

Prefer the bundled script for scaffolding and file updates, then use Codex for the actual teaching/grading reasoning.

## Quick Start

Run the command helper:

```bash
python3 scripts/study_course.py --help
```

Core subcommands:

- `plan`: Read progress and generate today's course plan
- `exercise`: Create/update a lesson exercise note
- `coach`: Create/update a coach dialogue note and run Q&A-style learning
- `grade`: Append grading template and grading checklist
- `summary`: Create/update lesson knowledge summary note

## Default Workflow

1. Run `plan` to detect recent progress from daily notes and lesson folders.
2. Run `exercise` to create `Lessons/Lxx/01-练习（填写版）.md` with textbook-first sections.
   - If the lesson is image-based and a TTS script exists, `exercise` can auto-generate listening audio into `Lessons/Lxx/assets/`
3. Run `coach` to create `02-教练对话（问答）.md`, load lesson materials, and conduct interactive Q&A teaching in chat.
4. Let the learner fill or refine answers in Obsidian if needed.
5. Run `grade` to append a grading section and checklist, then grade the answers directly in the note.
6. Run `summary` to write `03-知识点整理.md` for the lesson and update long-term notes (`生词表.md` / `错题本.md`) as needed.

## Command Examples

Use the course root (for example: `/Users/rongts/KnowledgeSource/新概念英语一册`).

```bash
python3 scripts/study_course.py plan --course-root "/path/to/course" --write-daily
python3 scripts/study_course.py exercise --course-root "/path/to/course" --lesson 2
python3 scripts/study_course.py coach --course-root "/path/to/course" --lesson 2
python3 scripts/study_course.py grade --course-root "/path/to/course" --lesson 2
python3 scripts/study_course.py summary --course-root "/path/to/course" --lesson 2
```

## Coach Dialogue Mode

Use `coach` when the user wants to learn in a live Q&A conversation instead of finishing the full written exercise first.

When the user says `教练模式`, treat it as a combined action:

1. Prepare lesson documents first (create missing exercise and summary notes)
2. Create or update `Lessons/Lxx/02-教练对话（问答）.md`
3. Start Q&A teaching in chat

Default coach behavior is optimized for responsiveness:

- Do not write to notes on every learner reply
- Keep corrections in chat first (fast feedback)
- Batch-write notes at checkpoints (for example: after 3-5 questions, on user request, or on session end)
- Only re-read files when needed (new lesson, explicit "记录到笔记", or final summary)

The `coach` command now prepares missing lesson documents by default, then prepares `Lessons/Lxx/02-教练对话（问答）.md` and prints the files Codex should read before starting:

- Exercise note (`01-练习（填写版）.md`)
- Knowledge summary note (`03-知识点整理.md`)
- `生词表.md`
- `错题本.md`

Coach shortcut (recommended when user says `教练模式`):

```bash
python3 scripts/study_course.py coach --course-root "/path/to/course" --lesson 2
```

During the session, Codex should:

- Ask short questions in sequence (meaning -> sentence pattern -> textbook items)
- Correct the learner immediately
- Batch record repeated mistakes into `错题本.md` (not every turn)
- Batch record new/weak vocabulary into `生词表.md` (not every turn)
- End with a concise stop/continue plan

## Image Lesson TTS (Exercise Command)

When generating exercises for image-based lessons, prefer adding listening audio automatically:

- Provide `--page-image-wikilink` to indicate this is an image lesson
- `exercise` will try to find `Resources/Audio/lessonXX_listen_practice.txt`
- It will generate `Lessons/Lxx/assets/LessonXX_practice.mp3` and embed it in the exercise note
- Use `edge-tts` only (single output format: MP3)

If no script text exists, `exercise` still creates the note and skips TTS generation.

## Grading Guidance

The `grade` command prepares note structure; Codex should still perform the grading reasoning:

- Read the learner's answers from the exercise note
- Correct errors with concise explanations
- Add standard answers only when helpful
- Update `生词表.md` and `错题本.md` for repeated or important mistakes
- Keep feedback actionable and short

## Expected Vault Layout

Read `references/course-layout.md` when adapting to a different folder structure.

Default assumptions:

- Daily notes: `YYYY-MM-DD.md` in course root
- Lesson folders: `Lessons/Lxx/`
- Exercise note: `Lessons/Lxx/01-练习（填写版）.md`
- Coach dialogue note: `Lessons/Lxx/02-教练对话（问答）.md`
- Knowledge summary note: `Lessons/Lxx/03-知识点整理.md`
- Lesson assets: `Lessons/Lxx/assets/`
- Shared resources: `Resources/`
- Long-term notes: `生词表.md`, `错题本.md`, `学习计划.md`

## Notes

- Keep the workflow textbook-first unless the user explicitly asks for extra practice.
- Respect the user's time limit (commonly 120-180 minutes) and produce a stop/continue plan when time is up.
- Prefer updating existing notes instead of creating duplicates.

## Resources (optional)

This skill uses `scripts/` and `references/`.

### scripts/
- `scripts/study_course.py`: Command helper for `plan`, `exercise`, `coach`, `grade`, `summary`

### references/
- `references/course-layout.md`: Expected note/folder naming and adaptation rules
- `references/commands.md`: Command examples and recommended flags
