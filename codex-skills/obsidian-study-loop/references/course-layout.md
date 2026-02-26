# Course Layout Reference

Use this reference when the user's vault does not exactly match the default structure.

## Default Layout

```text
<course-root>/
  YYYY-MM-DD.md
  学习计划.md
  生词表.md
  错题本.md
  Resources/
    PDF/
    Pages/
    Audio/
  Lessons/
    L01/
      01-练习（填写版）.md
      02-教练对话（问答）.md
      03-知识点整理.md
      assets/
```

## Naming Conventions

- Lesson folder: `Lxx` (zero-padded, e.g. `L02`)
- Exercise note: `01-练习（填写版）.md`
- Coach dialogue note: `02-教练对话（问答）.md`
- Knowledge summary note: `03-知识点整理.md`
- Daily note: `YYYY-MM-DD.md`

## Adaptation Rules

- If lesson folders use a different prefix (e.g. `Lesson 02`), pass explicit `--lessons-dir` and `--exercise-name` to the script.
- If the user keeps daily notes in a subfolder, pass `--daily-dir`.
- If the course does not use Chinese filenames, keep the workflow but override file names with command flags.
