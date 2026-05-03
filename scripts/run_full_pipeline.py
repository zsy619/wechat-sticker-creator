#!/usr/bin/env python3
"""
run_full_pipeline.py - 微信贴图完整工作流串联

一次性执行完整流程：内容聚合 → manifest → prompts → 图片生成 → 打包

Usage:
    python3 scripts/run_full_pipeline.py \
        --input "AI编程助手" \
        --output ~/wechat-stickers/ai-coding-assistant \
        --theme cyberpunk

    python3 scripts/run_full_pipeline.py \
        --input "https://github.com/xxx/ai-tool" \
        --output ~/wechat-stickers/ai-tool \
        --theme neon
"""

import os, sys, argparse, subprocess

# ── 脚本路径 ──────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)


def script_path(name):
    return os.path.join(SCRIPT_DIR, name)


def _session_log_step(project_root, theme, sticker_count, verbose=True):
    """步骤7：生成 session-log.md（输出到项目根目录）"""
    from generate_session_log import generate_session_log

    output = os.path.join(project_root, "session-log.md")
    return generate_session_log(
        project_name=os.path.basename(project_root),
        theme=theme,
        sticker_count=sticker_count,
        output=output,
        verbose=verbose,
    )


def _post_step(project_root, theme, link, verbose=True):
    """步骤8：生成 post.md（微信公众号推广文档，输出到项目根目录）"""
    from generate_post import generate_post

    output = os.path.join(project_root, "post.md")
    return generate_post(
        project_root=project_root,
        theme=theme,
        link=link,
        output=output,
        verbose=verbose,
    )


# ── 步骤执行 ─────────────────────────────────────────────


def run_step(step_name, cmd, cwd=None, timeout=300):
    """执行单个步骤，失败时询问是否继续"""
    print(f"\n{'='*60}")
    print(f"[步骤 {step_name}] {' '.join(cmd)}")
    print("=" * 60)
    effective_cwd = cwd if cwd else os.getcwd()
    try:
        result = subprocess.run(
            cmd, cwd=effective_cwd, timeout=timeout, capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"\n❌ 步骤 {step_name} 失败（退出码 {result.returncode}）")
            if result.stdout:
                print(f"[stdout]\n{result.stdout[:1000]}")
            if result.stderr:
                print(
                    f"[stderr]\n{result.stderr[:1000]}", file=__import__("sys").stderr
                )
            return False
        if result.stdout:
            print(result.stdout[:500])
        print(f"\n✅ 步骤 {step_name} 完成")
        return True
    except subprocess.TimeoutExpired:
        print(f"\n❌ 步骤 {step_name} 超时（>{timeout}s）")
        return False
    except Exception as e:
        print(f"\n❌ 步骤 {step_name} 异常: {e}")
        return False


def ask_continue(step_name):
    """询问是否继续"""
    try:
        response = input(f"\n是否继续？（y/n）: ").strip().lower()
        return response in ("y", "yes", "是", "")
    except EOFError:
        return True


# ── 工作流 ───────────────────────────────────────────────


def run_workflow(args):
    """执行完整工作流"""
    project_root = os.path.abspath(args.output)
    prompts_dir = os.path.join(project_root, "prompts")
    content_analysis = os.path.join(project_root, "content-analysis.md")
    manifest = os.path.join(project_root, "sticker-manifest.md")
    assets_dir = os.path.join(project_root, f"assets-{args.theme}")

    print(
        f"""
╔═══════════════════════════════════════════╗
║   微信贴图完整工作流 (v4.8.5)            ║
╚═══════════════════════════════════════════╝

输入: {args.input[:80]}{'...' if len(args.input) > 80 else ''}
输出: {project_root}
主题: {args.theme}
模式: {args.mode}
标签: {'✓ 包含' if args.with_tags else '✗ 跳过'}
SessionLog: {'✓ 包含' if args.with_session_log else '✗ 跳过'}
Post: {'✓ 包含' if getattr(args, 'with_post', True) else '✗ 跳过'}
"""
    )

    os.makedirs(project_root, exist_ok=True)

    steps = []

    # 步骤1：内容聚合分析（关键步骤，失败立即中止）
    if args.mode in ("auto", "full", "analysis"):
        steps.append(
            {
                "name": "1-内容聚合",
                "critical": True,
                "cmd": [
                    sys.executable,
                    script_path("generate_content_analysis.py"),
                    "--input",
                    args.input,
                    "--output",
                    project_root + "/",
                    "--theme",
                    args.theme,
                ],
            }
        )

    # 步骤2：生成 manifest（关键步骤，失败立即中止）
    if args.mode in ("auto", "full", "manifest"):
        steps.append(
            {
                "name": "2-Manifest",
                "critical": True,
                "cmd": [
                    sys.executable,
                    script_path("generate_manifest.py"),
                    "--input",
                    content_analysis,
                    "--output",
                    manifest,
                    "--project-name",
                    os.path.basename(project_root),
                ],
            }
        )

    # 步骤3：生成 prompts
    if args.mode in ("auto", "full", "prompts"):
        steps.append(
            {
                "name": "3-Prompts",
                "cmd": [
                    sys.executable,
                    script_path("generate_prompts.py"),
                    "--input",
                    manifest,
                    "--output",
                    prompts_dir + "/",
                    "--theme",
                    args.theme,
                ],
            }
        )

    # 步骤4：图片生成
    if args.mode in ("auto", "full", "frames"):
        frame_cmd = [
            sys.executable,
            script_path("generate_frames.py"),
            "--input",
            prompts_dir + "/",
            "--output",
            assets_dir + "/",
            "--theme",
            args.theme,
        ]
        if getattr(args, "continue_on_error", False):
            frame_cmd.append("--continue-on-error")
        if getattr(args, "debug_remotion", False):
            frame_cmd.append("--debug-remotion")
        if getattr(args, "template_dir", None):
            frame_cmd.extend(["--template-dir", args.template_dir])
        if getattr(args, "remotion_version", None):
            frame_cmd.extend(["--remotion-version", args.remotion_version])
        if getattr(args, "parallel", False):
            frame_cmd.append("--parallel")
        if getattr(args, "dry_run", False):
            frame_cmd.append("--dry-run")
        steps.append(
            {
                "name": "4-图片生成",
                "cmd": frame_cmd,
            }
        )

    # 步骤5：QA 检查
    if args.mode in ("auto", "full", "qa") and args.qa:
        steps.append(
            {
                "name": "5-QA检查",
                "cmd": [
                    sys.executable,
                    script_path("qa_check.py"),
                    "--input",
                    assets_dir + "/",
                    "--vocabulary",
                    os.path.join(SKILL_DIR, "docs", "prompts-format.md"),
                    "--prompts",
                    prompts_dir + "/",
                ],
            }
        )

    # 步骤5.5：标签生成（默认开启，输出到项目根目录）
    if args.with_tags:
        tags_output = os.path.join(project_root, "tags.md")
        steps.append(
            {
                "name": "5.5-标签生成",
                "cmd": [
                    sys.executable,
                    script_path("generate_tags.py"),
                    "--input",
                    manifest if os.path.exists(manifest) else prompts_dir + "/",
                    "--output",
                    tags_output,
                    "--theme",
                    args.theme,
                ],
            }
        )

    # 步骤6：打包
    if args.mode in ("auto", "full", "pack") and args.pack:
        zip_path = os.path.join(project_root, f"stickers-{args.theme}.zip")
        steps.append(
            {
                "name": "6-打包",
                "cmd": [
                    sys.executable,
                    script_path("pack_stickers.py"),
                    "--input",
                    assets_dir + "/",
                    "--output",
                    zip_path,
                    "--cover",
                    "900x383",
                    "--thumbnail",
                    "200x267",
                ],
            }
        )

    # 步骤7：session-log（默认开启，在打包之后）
    if args.with_session_log:
        sticker_count = (
            len([f for f in os.listdir(prompts_dir) if f.endswith(".md")])
            if os.path.exists(prompts_dir)
            else 0
        )
        steps.append(
            {
                "name": "7-SessionLog",
                "func": lambda: _session_log_step(
                    project_root, args.theme, sticker_count
                ),
            }
        )

    # 步骤8：post.md（微信公众号推广文档）
    if getattr(args, "with_post", True):
        steps.append(
            {
                "name": "8-Post",
                "func": lambda: _post_step(
                    project_root, args.theme, getattr(args, "link", "")
                ),
            }
        )

    # 执行所有步骤
    if not steps:
        print("[错误] 没有要执行的步骤（请检查 --mode 参数）")
        print(
            "可用模式: auto / full / analysis / manifest / prompts / frames / qa / pack"
        )
        sys.exit(1)

    print(f"[工作流] 共 {len(steps)} 个步骤")
    for i, step in enumerate(steps):
        # 函数类型步骤（步骤0、7）直接调用，不走子进程
        if "func" in step:
            print(f"\n{'='*60}")
            print(f"[步骤 {step['name']}]")
            print("=" * 60)
            try:
                result = step["func"]()
                if result is False:
                    if ask_continue(step["name"]):
                        print(f"\n⚠️  跳过步骤 {step['name']}，继续后续步骤...")
                        continue
                    else:
                        print(f"\n⛔ 工作流在步骤 {step['name']} 中止")
                        sys.exit(1)
                print(f"\n✅ 步骤 {step['name']} 完成")
            except Exception as e:
                print(f"\n❌ 步骤 {step['name']} 异常: {e}")
                if ask_continue(step["name"]):
                    print(f"\n⚠️  跳过步骤 {step['name']}，继续后续步骤...")
                    continue
                else:
                    print(f"\n⛔ 工作流在步骤 {step['name']} 中止")
                    sys.exit(1)
            continue

        ok = run_step(step["name"], step["cmd"])
        if not ok:
            is_critical = step.get("critical", False)
            if is_critical:
                # 关键步骤失败，立即中止，不询问
                print(
                    f"\n⛔ 工作流在关键步骤 {step['name']} 中止（失败则无法继续后续步骤）"
                )
                sys.exit(1)
            if ask_continue(step["name"]):
                print(f"\n⚠️  跳过步骤 {step['name']}，继续后续步骤...")
                continue
            else:
                print(f"\n⛔ 工作流在步骤 {step['name']} 中止")
                sys.exit(1)

    # 最终汇总
    prompts_count = (
        len([f for f in os.listdir(prompts_dir) if f.endswith(".md")])
        if os.path.exists(prompts_dir)
        else "?"
    )
    assets_count = (
        len([f for f in os.listdir(assets_dir) if f.endswith((".png", ".gif"))])
        if os.path.exists(assets_dir)
        else "?"
    )

    print(
        f"""
╔═══════════════════════════════════════════╗
║   工作流完成                             ║
╚═══════════════════════════════════════════╝

📁 项目目录: {project_root}
📋 Manifest: {manifest}
📝 Prompts: {prompts_dir}/ ({prompts_count} 张)
🖼️  贴图: {assets_dir}/ ({assets_count} 张)
"""
    )

    if args.pack and os.path.exists(zip_path):
        print(f"📦 ZIP: {zip_path}")


# ── 主函数 ───────────────────────────────────────────────


def main():
    ap = argparse.ArgumentParser(
        description="微信贴图完整工作流（文档复制 → 内容聚合 → manifest → prompts → 图片生成）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
模式说明:
  auto     执行全部步骤（默认）
  analysis 仅内容聚合分析
  manifest 仅生成 manifest
  prompts  仅生成 prompts
  frames   仅生成图片
  qa       仅 QA 检查
  pack     仅打包

示例:
  python3 run_full_pipeline.py --input "AI编程助手" --output ~/wechat/ai --theme cyberpunk
  python3 run_full_pipeline.py --input "https://github.com/xxx" --output ~/wechat/xxx --mode prompts
  python3 run_full_pipeline.py --input "AI编程助手" --output ~/wechat/ai --continue-on-error --debug-remotion
  python3 run_full_pipeline.py --input "AI编程助手" --output ~/wechat/ai --parallel --dry-run
  python3 run_full_pipeline.py --input "AI编程助手" --output ~/wechat/ai --no-docs --no-tags
        """,
    )
    ap.add_argument("--input", required=True, help="URL / 主题词 / 内容文本")
    ap.add_argument("--output", required=True, help="项目目录路径")
    ap.add_argument("--theme", default="cyberpunk", help="主题风格（默认 cyberpunk）")
    ap.add_argument(
        "--mode",
        default="auto",
        choices=[
            "auto",
            "full",
            "analysis",
            "manifest",
            "prompts",
            "frames",
            "qa",
            "pack",
        ],
        help="执行模式（默认 auto）",
    )
    ap.add_argument(
        "--qa", action="store_true", default=True, help="生成后自动 QA 检查（默认开启）"
    )
    ap.add_argument("--no-qa", dest="qa", action="store_false", help="跳过 QA 检查")
    ap.add_argument(
        "--pack", action="store_true", default=True, help="生成后自动打包（默认开启）"
    )
    ap.add_argument("--no-pack", dest="pack", action="store_false", help="跳过打包")
    ap.add_argument(
        "--continue-on-error",
        action="store_true",
        help="图片生成失败时跳过继续下一张（透传给 generate_frames.py）",
    )
    ap.add_argument(
        "--debug-remotion",
        action="store_true",
        help="保留 Remotion 调试文件（透传给 generate_frames.py）",
    )
    ap.add_argument(
        "--template-dir", help="自定义 Remotion 模板目录（透传给 generate_frames.py）"
    )
    ap.add_argument(
        "--remotion-version",
        help=f"Remotion 版本（透传给 generate_frames.py，default: 4.0.448）",
    )
    ap.add_argument(
        "--parallel", action="store_true", help="并行生成（透传给 generate_frames.py）"
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="仅打印计划不实际生成（透传给 generate_frames.py）",
    )
    # 标签
    ap.add_argument(
        "--with-tags",
        action="store_true",
        default=True,
        dest="with_tags",
        help="生成标签文档 tags.md（默认开启）",
    )
    ap.add_argument(
        "--no-tags", action="store_false", dest="with_tags", help="跳过标签生成"
    )
    # 新增：session-log
    ap.add_argument(
        "--with-session-log",
        action="store_true",
        default=True,
        dest="with_session_log",
        help="生成 session-log.md（默认开启）",
    )
    ap.add_argument(
        "--no-session-log",
        action="store_false",
        dest="with_session_log",
        help="跳过 session-log 生成",
    )
    # 新增：post.md
    ap.add_argument(
        "--with-post",
        action="store_true",
        default=True,
        dest="with_post",
        help="生成 post.md 微信公众号推广文档（默认开启）",
    )
    ap.add_argument(
        "--no-post", action="store_false", dest="with_post", help="跳过 post.md 生成"
    )
    ap.add_argument("--link", default="", help="项目链接（用于 post.md）")
    args = ap.parse_args()

    run_workflow(args)


if __name__ == "__main__":
    main()
