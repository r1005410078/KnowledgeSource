#!/usr/bin/env python3
import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
from pathlib import Path


DAILY_NOTE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
LESSON_RE = re.compile(r"(?:Lesson\s*|L)(\d{1,3})", re.IGNORECASE)


def lesson_tag(lesson_num: int) -> str:
    return f"L{lesson_num:02d}"


def course_paths(course_root: Path, lessons_dir: str):
    lessons_root = course_root / lessons_dir
    return {
        "course_root": course_root,
        "lessons_root": lessons_root,
        "resources_root": course_root / "Resources",
        "vocab": course_root / "生词表.md",
        "errors": course_root / "错题本.md",
        "plan": course_root / "学习计划.md",
    }


def find_daily_notes(course_root: Path, daily_dir: str | None = None):
    target = course_root / daily_dir if daily_dir else course_root
    if not target.exists():
        return []
    return sorted([p for p in target.iterdir() if p.is_file() and DAILY_NOTE_RE.match(p.name)])


def find_highest_lesson_from_text(text: str) -> int | None:
    nums = [int(m.group(1)) for m in LESSON_RE.finditer(text)]
    return max(nums) if nums else None


def detect_progress(course_root: Path, lessons_dir: str, daily_dir: str | None, as_of_date: dt.date | None = None):
    result = {
        "latest_daily": None,
        "daily_lesson": None,
        "lesson_dirs_max": None,
        "detected_current": None,
    }

    dailies = find_daily_notes(course_root, daily_dir)
    if as_of_date:
        filtered = []
        for note in dailies:
            try:
                note_date = dt.date.fromisoformat(note.stem)
            except ValueError:
                continue
            if note_date <= as_of_date:
                filtered.append(note)
        dailies = filtered
    if dailies:
        latest = dailies[-1]
        result["latest_daily"] = latest
        try:
            text = latest.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = latest.read_text(encoding="utf-8", errors="ignore")
        result["daily_lesson"] = find_highest_lesson_from_text(text)

    lessons_root = course_root / lessons_dir
    if lessons_root.exists():
        nums = []
        for child in lessons_root.iterdir():
            if not child.is_dir():
                continue
            m = re.fullmatch(r"L(\d{1,3})", child.name, re.IGNORECASE)
            if m:
                nums.append(int(m.group(1)))
        if nums:
            result["lesson_dirs_max"] = max(nums)

    candidates = [n for n in [result["daily_lesson"], result["lesson_dirs_max"]] if n is not None]
    result["detected_current"] = max(candidates) if candidates else None
    return result


def ensure_parent(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)


def append_or_create_daily_plan(daily_note: Path, plan_md: str):
    if daily_note.exists():
        original = daily_note.read_text(encoding="utf-8", errors="ignore")
        if "## 今日课程计划" in original:
            return False, "Daily note already contains a plan section."
        content = original.rstrip() + "\n\n" + plan_md + "\n"
    else:
        content = f"# 日期：{daily_note.stem}\n\n{plan_md}\n"
    ensure_parent(daily_note)
    daily_note.write_text(content, encoding="utf-8")
    return True, "Wrote daily plan section."


def cmd_plan(args):
    course_root = Path(args.course_root).expanduser().resolve()
    today = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    progress = detect_progress(course_root, args.lessons_dir, args.daily_dir, as_of_date=today)

    current = progress["detected_current"]
    if args.next_lesson is not None:
        target_lesson = args.next_lesson
        reason = "manual override"
    elif current is None:
        target_lesson = 1
        reason = "no prior lesson detected"
    elif args.continue_current:
        target_lesson = current
        reason = "continue current lesson"
    else:
        target_lesson = current + 1
        reason = "next lesson after detected progress"

    plan_md = (
        "## 今日课程计划\n"
        f"- 日期：{today.isoformat()}\n"
        f"- 目标课次：Lesson {target_lesson}\n"
        f"- 学习时长目标：{args.minutes_min}-{args.minutes_max} 分钟\n"
        f"- 每周目标：{args.weekly_target} 课\n"
        "- 流程（课本优先）：听力/课文 -> 课本练习 -> 批改 -> 生词表 -> 错题本 -> 知识点整理\n"
        f"- 进度判定来源：{reason}\n"
        "- 超时规则：超过上限先收尾，记录未完成清单，次日继续\n"
    )

    print(f"course_root: {course_root}")
    print(f"latest_daily: {progress['latest_daily']}")
    print(f"daily_lesson: {progress['daily_lesson']}")
    print(f"lesson_dirs_max: {progress['lesson_dirs_max']}")
    print(f"target_lesson: {target_lesson}")
    print()
    print(plan_md)

    if args.write_daily:
        daily_dir = course_root / args.daily_dir if args.daily_dir else course_root
        daily_note = daily_dir / f"{today.isoformat()}.md"
        changed, message = append_or_create_daily_plan(daily_note, plan_md)
        print(f"[write_daily] {message}")
        if changed:
            print(f"[write_daily] {daily_note}")


def exercise_note_template(lesson_num: int, page_wikilink: str | None, audio_wikilink: str | None):
    lines = [
        f"# Lesson {lesson_num} 练习（填写版）",
        "",
        "目标：按课本流程完成本课学习（课文/听力/课本练习/批改/整理）。",
        "规则：优先按课本原练，不额外加练，除非用户明确要求。",
        "",
        "时间上限：180 分钟（到点就停，剩下的写到“未完成清单”）。",
        "",
        "快速入口：[[生词表]] | [[错题本]]",
        "",
    ]
    if page_wikilink:
        lines += ["## 大图（课本页）", f"![[{page_wikilink}]]", ""]
    if audio_wikilink:
        lines += ["## 听力（本课）", f"- 音频：![[{audio_wikilink}]]", ""]
    lines += [
        "## 课本练习（按课本原题填写）",
        "- 题目类型：",
        "- 我的答案：",
        "",
        "## 批改（待填写）",
        "- 正确点：",
        "- 错误点：",
        "- 纠正后答案：",
        "- 易错原因：",
        "",
        "## 生词与短语（本课）",
        "- ",
        "",
        "## 知识点（本课）",
        "- 句型：",
        "- 语法：",
        "- 场景表达：",
        "",
        "## 自评",
        "- 完成度（1-5）：",
        "- 我想问的问题：",
        "",
        "## 未完成清单",
        "- ",
        "",
    ]
    return "\n".join(lines)


def default_tts_script_path(course_root: Path, lesson_num: int) -> Path:
    return course_root / "Resources" / "Audio" / f"lesson{lesson_num:02d}_listen_practice.txt"


def generate_tts_audio(script_path: Path, out_mp3: Path, engine: str) -> tuple[bool, str]:
    out_mp3.parent.mkdir(parents=True, exist_ok=True)
    edge = shutil.which("edge-tts")
    if not edge:
        return False, "edge-tts not found"
    try:
        subprocess.run(
            [
                edge,
                "-f",
                str(script_path),
                "--voice",
                "en-US-GuyNeural",
                "--rate",
                "+0%",
                "--write-media",
                str(out_mp3),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )
        return True, f"edge-tts -> {out_mp3.name}"
    except subprocess.CalledProcessError as exc:
        return False, f"edge-tts failed: {exc.stderr.strip()[:200]}"


def cmd_exercise(args):
    course_root = Path(args.course_root).expanduser().resolve()
    lesson_dir = course_root / args.lessons_dir / lesson_tag(args.lesson)
    assets_dir = lesson_dir / "assets"
    exercise_path = lesson_dir / args.exercise_name
    lesson_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    if exercise_path.exists() and not args.overwrite:
        print(f"[skip] exists: {exercise_path}")
        return

    audio_wikilink = args.audio_wikilink
    if args.auto_tts_for_image and args.page_image_wikilink:
        script_path = Path(args.tts_script_file).expanduser().resolve() if args.tts_script_file else default_tts_script_path(course_root, args.lesson)
        if script_path.exists():
            out_mp3 = assets_dir / f"Lesson{args.lesson:02d}_practice.mp3"
            ok, msg = generate_tts_audio(script_path, out_mp3, args.tts_engine)
            print(f"[tts] {msg}")
            if ok and not audio_wikilink:
                audio_wikilink = f"assets/{out_mp3.name}"
        else:
            print(f"[tts] skipped: script not found ({script_path})")

    content = exercise_note_template(args.lesson, args.page_image_wikilink, audio_wikilink)
    exercise_path.write_text(content, encoding="utf-8")
    print(f"[ok] created: {exercise_path}")


def append_section_if_missing(path: Path, heading: str, body: str):
    text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    if heading in text:
        return False
    new_text = text.rstrip() + "\n\n" + body.strip() + "\n"
    path.write_text(new_text, encoding="utf-8")
    return True


def cmd_grade(args):
    course_root = Path(args.course_root).expanduser().resolve()
    exercise_path = Path(args.exercise_file).expanduser().resolve() if args.exercise_file else (
        course_root / args.lessons_dir / lesson_tag(args.lesson) / args.exercise_name
    )
    if not exercise_path.exists():
        print(f"[error] exercise file not found: {exercise_path}", file=sys.stderr)
        sys.exit(1)

    today = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    heading = f"## 批改记录（{today.isoformat()}）"
    body = (
        f"{heading}\n"
        "- 批改范围：\n"
        "- 主要问题：\n"
        "- 纠正答案：\n"
        "- 生词表新增：\n"
        "- 错题本新增：\n"
        "- 下次复盘重点：\n"
    )
    changed = append_section_if_missing(exercise_path, heading, body)
    print(f"[ok] exercise: {exercise_path}")
    print("[ok] appended grading section" if changed else "[skip] grading section already exists")
    print("Next: read answers and fill the grading section in the same note.")


def summary_template(lesson_num: int):
    return "\n".join(
        [
            f"# Lesson {lesson_num} 知识点整理",
            "",
            "## 核心句型",
            "- ",
            "",
            "## 重点词汇/短语",
            "- ",
            "",
            "## 语法与表达",
            "- ",
            "",
            "## 易错点",
            "- ",
            "",
            "## 本课最小复习清单（下次先复习）",
            "- ",
            "",
        ]
    )


def coach_template(lesson_num: int, exercise_name: str, summary_name: str):
    lesson_dir_wikilink = f"Lessons/{lesson_tag(lesson_num)}"
    return "\n".join(
        [
            f"# Lesson {lesson_num} 教练对话（问答）",
            "",
            "目标：通过问答对话完成本课学习与练习（解释 -> 提问 -> 回答 -> 纠错 -> 复盘）。",
            "规则：教练主动提问，学习者回答；优先使用课本内容，不额外扩题，除非用户明确要求。",
            "",
            "## 读入资料（教练开局先读）",
            f"- 练习页：![[{exercise_name}]]",
            f"- 知识点整理：![[{summary_name}]]",
            "- 生词表：[[生词表]]",
            "- 错题本：[[错题本]]",
            f"- 本课目录：[[{lesson_dir_wikilink}]]",
            "",
            "## 教练对话流程（执行清单）",
            "- 1) 先问本课大意（中文）",
            "- 2) 再问核心句型（英文/中文都可）",
            "- 3) 做课本原题问答练习（逐题）",
            "- 4) 当场纠错（拼写/语法/表达）",
            "- 5) 收尾：总结错点并写入生词表/错题本",
            "",
            "## 对话记录（本次）",
            "- 教练开场：",
            "- 学习者回答：",
            "- 纠错与讲解：",
            "- 下一问：",
            "",
            "## 本次错点（准备写入错题本）",
            "- ",
            "",
            "## 本次新增生词（准备写入生词表）",
            "- ",
            "",
            "## 收尾计划",
            "- 今天完成到：",
            "- 下次继续点：",
            "- 是否超前：",
            "",
        ]
    )


def cmd_summary(args):
    course_root = Path(args.course_root).expanduser().resolve()
    lesson_dir = course_root / args.lessons_dir / lesson_tag(args.lesson)
    lesson_dir.mkdir(parents=True, exist_ok=True)
    summary_path = lesson_dir / args.summary_name
    if summary_path.exists() and not args.overwrite:
        print(f"[skip] exists: {summary_path}")
        return
    summary_path.write_text(summary_template(args.lesson), encoding="utf-8")
    print(f"[ok] created: {summary_path}")


def cmd_coach(args):
    course_root = Path(args.course_root).expanduser().resolve()
    lesson_dir = course_root / args.lessons_dir / lesson_tag(args.lesson)
    lesson_dir.mkdir(parents=True, exist_ok=True)
    coach_path = lesson_dir / args.coach_name
    exercise_path = lesson_dir / args.exercise_name
    summary_path = lesson_dir / args.summary_name
    assets_dir = lesson_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    prepared = []
    if args.prepare_docs:
        if not exercise_path.exists():
            exercise_path.write_text(
                exercise_note_template(args.lesson, None, None),
                encoding="utf-8",
            )
            prepared.append(f"created exercise note: {exercise_path}")
        if not summary_path.exists():
            summary_path.write_text(summary_template(args.lesson), encoding="utf-8")
            prepared.append(f"created summary note: {summary_path}")

    if coach_path.exists() and not args.overwrite:
        print(f"[skip] exists: {coach_path}")
    else:
        coach_path.write_text(
            coach_template(args.lesson, args.exercise_name, args.summary_name),
            encoding="utf-8",
        )
        print(f"[ok] created: {coach_path}")

    if prepared:
        print("Prepared documents before coach mode:")
        for item in prepared:
            print(f"- {item}")
    elif args.prepare_docs:
        print("Prepared documents before coach mode:")
        print("- no changes (exercise/summary already existed)")

    print("Coach mode context (read before dialogue):")
    print(f"- coach_note: {coach_path}")
    print(f"- exercise_note: {exercise_path} {'[exists]' if exercise_path.exists() else '[missing]'}")
    print(f"- summary_note: {summary_path} {'[exists]' if summary_path.exists() else '[missing]'}")
    print(f"- vocab: {course_root / '生词表.md'}")
    print(f"- errors: {course_root / '错题本.md'}")
    print("Next: conduct Q&A in chat (fast mode) and batch-write corrections at checkpoints or session end.")


def build_parser():
    parser = argparse.ArgumentParser(description="Obsidian course study workflow helper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--course-root", required=True, help="Course folder root in the Obsidian vault")
    common.add_argument("--lessons-dir", default="Lessons", help="Lessons directory relative to course root")
    common.add_argument("--daily-dir", default=None, help="Daily notes directory relative to course root")

    p_plan = sub.add_parser("plan", parents=[common], help="Read progress and generate today's plan")
    p_plan.add_argument("--date", help="YYYY-MM-DD (default: today)")
    p_plan.add_argument("--minutes-min", type=int, default=120)
    p_plan.add_argument("--minutes-max", type=int, default=180)
    p_plan.add_argument("--weekly-target", type=int, default=8)
    p_plan.add_argument("--continue-current", action="store_true", help="Plan current detected lesson instead of next lesson")
    p_plan.add_argument("--next-lesson", type=int, help="Override auto-detected target lesson")
    p_plan.add_argument("--write-daily", action="store_true", help="Append plan to today's daily note")
    p_plan.set_defaults(func=cmd_plan)

    p_ex = sub.add_parser("exercise", parents=[common], help="Create lesson exercise note")
    p_ex.add_argument("--lesson", type=int, required=True)
    p_ex.add_argument("--exercise-name", default="01-练习（填写版）.md")
    p_ex.add_argument("--audio-wikilink", default=None, help="Wikilink path used inside the note, e.g. assets/Lesson02_practice.mp3")
    p_ex.add_argument("--page-image-wikilink", default=None, help="Wikilink path used inside the note, e.g. Resources/Pages/p7-007.png")
    p_ex.add_argument("--auto-tts-for-image", action="store_true", default=True, help="If page image is provided, try to generate lesson listening audio (default: enabled)")
    p_ex.add_argument("--no-auto-tts-for-image", dest="auto_tts_for_image", action="store_false", help="Disable auto TTS generation for image-based lessons")
    p_ex.add_argument("--tts-script-file", default=None, help="Path to TTS script text; default is Resources/Audio/lessonXX_listen_practice.txt")
    p_ex.add_argument("--tts-engine", choices=["edge"], default="edge", help="TTS engine (edge-tts only)")
    p_ex.add_argument("--overwrite", action="store_true")
    p_ex.set_defaults(func=cmd_exercise)

    p_grade = sub.add_parser("grade", parents=[common], help="Append grading template to exercise note")
    p_grade.add_argument("--lesson", type=int, required=True)
    p_grade.add_argument("--exercise-file", help="Absolute/relative exercise note path override")
    p_grade.add_argument("--exercise-name", default="01-练习（填写版）.md")
    p_grade.add_argument("--date", help="YYYY-MM-DD (default: today)")
    p_grade.set_defaults(func=cmd_grade)

    p_sum = sub.add_parser("summary", parents=[common], help="Create/update lesson knowledge summary note")
    p_sum.add_argument("--lesson", type=int, required=True)
    p_sum.add_argument("--summary-name", default="03-知识点整理.md")
    p_sum.add_argument("--overwrite", action="store_true")
    p_sum.set_defaults(func=cmd_summary)

    p_coach = sub.add_parser("coach", parents=[common], help="Create/update coach dialogue note and print context checklist")
    p_coach.add_argument("--lesson", type=int, required=True)
    p_coach.add_argument("--coach-name", default="02-教练对话（问答）.md")
    p_coach.add_argument("--exercise-name", default="01-练习（填写版）.md")
    p_coach.add_argument("--summary-name", default="03-知识点整理.md")
    p_coach.add_argument("--prepare-docs", action="store_true", default=True, help="Create missing exercise/summary notes before coach mode (default: enabled)")
    p_coach.add_argument("--no-prepare-docs", dest="prepare_docs", action="store_false", help="Do not create missing exercise/summary notes before coach mode")
    p_coach.add_argument("--overwrite", action="store_true")
    p_coach.set_defaults(func=cmd_coach)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
