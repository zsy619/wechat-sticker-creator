#!/usr/bin/env python3
"""
[已废弃] generate_stickers.py - 旧版贴图生成脚本

本脚本已被以下模块替代：
  - generate_content_analysis.py  （内容分析）
  - generate_manifest.py          （Manifest 生成）
  - generate_prompts.py           （Prompt 生成）
  - generate_frames.py            （帧/图片生成）

请使用 run_full_pipeline.py 执行完整流程。
本文件保留仅为兼容性目的，预计在未来版本中移除。
"""

import sys

def main():
    print("[废弃警告] generate_stickers.py 已废弃，请使用 run_full_pipeline.py")
    sys.exit(1)

if __name__ == '__main__':
    main()
