#!/usr/bin/env python3
"""
[已废弃] generate_cover.py - 旧版封面生成脚本

本脚本已被 scripts/pack_stickers.py 替代。
打包功能（含封面+缩略图）请使用：
  python3 scripts/pack_stickers.py --input assets-{theme}/ --output stickers.zip --cover 900x383

本文件保留仅为兼容性目的，预计在未来版本中移除。
"""

import sys

def main():
    print("[废弃警告] generate_cover.py 已废弃，请使用 pack_stickers.py")
    sys.exit(1)

if __name__ == '__main__':
    main()
