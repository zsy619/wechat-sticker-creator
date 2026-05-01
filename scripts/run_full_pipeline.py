#!/usr/bin/env python3
"""
run_full_pipeline.py - 微信贴图完整工作流串联

一次性执行完整流程：
  内容聚合分析 → manifest → prompts → 图片生成

Usage:
    python3 scripts/run_full_pipeline.py \
        --input "AI编程助手" \
        --output wechat-stickers/ai-coding-assistant \
        --theme cyberpunk

    python3 scripts/run_full_pipeline.py \
        --input "https://github.com/xxx/ai-tool" \
        --output wechat-stickers/ai-tool \
        --theme neon
"""

import os, sys, argparse, subprocess

# ── 脚本路径 ──────────────────────────────────────────────

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

def script_path(name):
    return os.path.join(SCRIPT_DIR, name)

# ── 步骤执行 ─────────────────────────────────────────────

def run_step(step_name, cmd, cwd=None, timeout=300):
    """执行单个步骤，失败时询问是否继续"""
    print(f"\n{'='*60}")
    print(f"[步骤 {step_name}] {' '.join(cmd)}")
    print('='*60)
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
                print(f"[stderr]\n{result.stderr[:1000]}", file=__import__('sys').stderr)
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
        return response in ('y', 'yes', '是', '')
    except EOFError:
        return True

# ── 工作流 ───────────────────────────────────────────────

def run_workflow(args):
    """执行完整工作流"""
    project_root = os.path.abspath(args.output)
    prompts_dir = os.path.join(project_root, 'prompts')
    content_analysis = os.path.join(project_root, 'content-analysis.md')
    manifest = os.path.join(project_root, 'sticker-manifest.md')
    assets_dir = os.path.join(project_root, f'assets-{args.theme}')

    print(f"""
╔═══════════════════════════════════════════╗
║   微信贴图完整工作流 (v4.3.1)            ║
╚═══════════════════════════════════════════╝

输入: {args.input[:80]}{'...' if len(args.input) > 80 else ''}
输出: {project_root}
主题: {args.theme}
模式: {args.mode}
""")

    os.makedirs(project_root, exist_ok=True)

    steps = []

    # 步骤1：内容聚合分析
    if args.mode in ('auto', 'full', 'analysis'):
        steps.append({
            'name': '1-内容聚合',
            'cmd': [
                sys.executable, script_path('generate_content_analysis.py'),
                '--input', args.input,
                '--output', project_root + '/',
                '--theme', args.theme,
            ],
        })

    # 步骤2：生成 manifest
    if args.mode in ('auto', 'full', 'manifest'):
        steps.append({
            'name': '2-Manifest',
            'cmd': [
                sys.executable, script_path('generate_manifest.py'),
                '--input', content_analysis,
                '--output', manifest,
                '--project-name', os.path.basename(project_root),
            ],
        })

    # 步骤3：生成 prompts
    if args.mode in ('auto', 'full', 'prompts'):
        steps.append({
            'name': '3-Prompts',
            'cmd': [
                sys.executable, script_path('generate_prompts.py'),
                '--input', manifest,
                '--output', prompts_dir + '/',
                '--theme', args.theme,
            ],
        })

    # 步骤4：图片生成
    if args.mode in ('auto', 'full', 'frames'):
        steps.append({
            'name': '4-图片生成',
            'cmd': [
                sys.executable, script_path('generate_frames.py'),
                '--input', prompts_dir + '/',
                '--output', assets_dir + '/',
                '--theme', args.theme,
            ],
        })

    # 步骤5：QA 检查
    if args.mode in ('auto', 'full', 'qa') and args.qa:
        steps.append({
            'name': '5-QA检查',
            'cmd': [
                sys.executable, script_path('qa_check.py'),
                '--input', assets_dir + '/',
                '--vocabulary', os.path.join(SKILL_DIR, 'docs', 'prompts-format.md'),
                '--prompts', prompts_dir + '/',
            ],
        })

    # 步骤6：打包
    if args.mode in ('auto', 'full', 'pack') and args.pack:
        zip_path = os.path.join(project_root, f'stickers-{args.theme}.zip')
        steps.append({
            'name': '6-打包',
            'cmd': [
                sys.executable, script_path('pack_stickers.py'),
                '--input', assets_dir + '/',
                '--output', zip_path,
                '--cover', '900x383',
                '--thumbnail', '200x267',
            ],
        })

    # 执行所有步骤
    if not steps:
        print("[错误] 没有要执行的步骤（请检查 --mode 参数）")
        print("可用模式: auto / full / analysis / manifest / prompts / frames / qa / pack")
        sys.exit(1)

    print(f"[工作流] 共 {len(steps)} 个步骤")
    for i, step in enumerate(steps):
        ok = run_step(step['name'], step['cmd'])
        if not ok:
            if ask_continue(step['name']):
                print(f"\n⚠️  跳过步骤 {step['name']}，继续后续步骤...")
                continue
            else:
                print(f"\n⛔ 工作流在步骤 {step['name']} 中止")
                sys.exit(1)

    # 最终汇总
    print(f"""
╔═══════════════════════════════════════════╗
║   工作流完成                             ║
╚═══════════════════════════════════════════╝

📁 项目目录: {project_root}
📋 Manifest: {manifest}
📝 Prompts: {prompts_dir}/ ({len([f for f in os.listdir(prompts_dir) if f.endswith('.md')]) if os.path.exists(prompts_dir) else '?'} 张)
🖼️  贴图: {assets_dir}/ ({len([f for f in os.listdir(assets_dir) if f.endswith(('.png','.gif'))]) if os.path.exists(assets_dir) else '?'} 张)
""")

    if args.pack and os.path.exists(zip_path):
        print(f"📦 ZIP: {zip_path}")

# ── 主函数 ───────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description='微信贴图完整工作流（内容聚合 → manifest → prompts → 图片生成）',
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
        """
    )
    ap.add_argument('--input', required=True,
                    help='URL / 主题词 / 内容文本')
    ap.add_argument('--output', required=True,
                    help='项目根目录路径')
    ap.add_argument('--theme', default='cyberpunk',
                    help='主题风格（默认 cyberpunk）')
    ap.add_argument('--mode', default='auto',
                    choices=['auto', 'full', 'analysis', 'manifest', 'prompts', 'frames', 'qa', 'pack'],
                    help='执行模式（默认 auto）')
    ap.add_argument('--qa', action='store_true', default=True,
                    help='生成后自动 QA 检查（默认开启）')
    ap.add_argument('--no-qa', dest='qa', action='store_false',
                    help='跳过 QA 检查')
    ap.add_argument('--pack', action='store_true', default=True,
                    help='生成后自动打包（默认开启）')
    ap.add_argument('--no-pack', dest='pack', action='store_false',
                    help='跳过打包')
    args = ap.parse_args()

    run_workflow(args)

if __name__ == '__main__':
    main()
