#!/usr/bin/env python3
"""
getdesign-cli
基于 Kimi Claw / Playwright 的网站设计系统抓取工具
用途: 输入任意品牌 URL，自动生成 DESIGN.md 供 Coding Agent 复刻 UI
版本: 0.1.0
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

# 颜色处理
def rgb_to_hex(s: str) -> str:
    s = s.strip().lower()
    if s.startswith("#") and len(s) in (4, 7, 9):
        return s
    m = re.search(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', s)
    if m:
        return '#{:02x}{:02x}{:02x}'.format(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return s

def hex_to_rgb_tuple(hex_color: str):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join([c*2 for c in hex_color])
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def luminance(rgb):
    r, g, b = [x/255.0 for x in rgb]
    def _c(c):
        return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*_c(r) + 0.7152*_c(g) + 0.0722*_c(b)

def classify_color(hex_color: str) -> str:
    try:
        rgb = hex_to_rgb_tuple(hex_color)
        r, g, b = rgb
        lum = luminance(rgb)
        maxc, minc = max(rgb), min(rgb)
        sat = 0 if maxc == 0 else (maxc - minc) / maxc
        
        if sat < 0.08:
            if lum > 0.9: return "background"
            if lum < 0.15: return "text"
            return "neutral"
        if lum > 0.75: return "background"
        if r > 150 and g < 100 and b < 100: return "semantic-error"
        if r > 150 and g > 120 and b < 80: return "semantic-warning"
        if g > 140 and r < 100 and b < 100: return "semantic-success"
        if b > 150 and r < 120 and g < 120: return "semantic-info"
        return "primary"
    except Exception:
        return "unknown"

class DesignCrawler:
    def __init__(self, headless: bool = True, viewport: dict = None):
        self.headless = headless
        self.viewport = viewport or {"width": 1440, "height": 900}
        self.raw_data: Dict = {
            "url": "",
            "brand_name": "",
            "pages": [],
            "styles": {},
            "screenshots": [],
        }

    def crawl(self, url: str, pages: Optional[List[str]] = None, out_dir: Path = Path("output")) -> Dict:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("❌ 请先安装 Playwright: pip install playwright \u0026\u0026 playwright install chromium")
            sys.exit(1)

        out_dir.mkdir(parents=True, exist_ok=True)
        self.raw_data["url"] = url
        if pages is None:
            pages = ["/"]

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(viewport=self.viewport)
            page = context.new_page()

            for path in pages:
                full_url = f"{url.rstrip('/')}{path}"
                try:
                    page.goto(full_url, wait_until="networkidle", timeout=30000)
                except Exception as e:
                    print(f"⚠️  页面加载超时或失败: {full_url} ({e})")
                    continue
                
                shot_name = f"screenshot_{path.replace('/', '_') or 'home'}.png"
                shot_path = out_dir / shot_name
                page.screenshot(path=str(shot_path), full_page=True)
                self.raw_data["screenshots"].append(str(shot_path))

                selectors = [
                    "body", "h1", "h2", "h3", "button", "a", "input",
                    "nav", "header", "footer", "[class*='card']", "[class*='container']"
                ]
                for selector in selectors:
                    styles = page.evaluate("""
                        (selector) => {
                            const els = document.querySelectorAll(selector);
                            const out = [];
                            for (let i = 0; i < Math.min(els.length, 20); i++) {
                                const s = window.getComputedStyle(els[i]);
                                out.push({
                                    color: s.color,
                                    backgroundColor: s.backgroundColor,
                                    fontFamily: s.fontFamily,
                                    fontSize: s.fontSize,
                                    fontWeight: s.fontWeight,
                                    lineHeight: s.lineHeight,
                                    letterSpacing: s.letterSpacing,
                                    padding: s.padding,
                                    margin: s.margin,
                                    borderRadius: s.borderRadius,
                                    boxShadow: s.boxShadow,
                                    borderColor: s.borderColor
                                });
                            }
                            return out;
                        }
                    """, selector)
                    key = f"{selector}_{path}"
                    self.raw_data["styles"][key] = styles
            
            browser.close()
        return self.raw_data

class DesignAnalyzer:
    def __init__(self, raw_data: Dict):
        self.raw_data = raw_data
        self.tokens = {
            "colors": {},
            "typography": {},
            "spacing": {},
            "radii": {},
            "shadows": {},
        }

    def analyze(self) -> Dict:
        all_colors = []
        all_styles = []
        for key, styles in self.raw_data["styles"].items():
            for s in styles:
                if s.get("color"): all_colors.append(s["color"])
                if s.get("backgroundColor") and s["backgroundColor"] != "rgba(0, 0, 0, 0)":
                    all_colors.append(s["backgroundColor"])
                if s.get("borderColor") and s["borderColor"] != "rgba(0, 0, 0, 0)":
                    all_colors.append(s["borderColor"])
                all_styles.append(s)

        # Color tokens
        color_counts = Counter([rgb_to_hex(c) for c in all_colors if c and "rgba(0,0,0,0)" not in c.replace(" ", "")])
        categorized = defaultdict(list)
        for hex_color, count in color_counts.most_common(30):
            role = classify_color(hex_color)
            categorized[role].append({"hex": hex_color, "count": count})
        self.tokens["colors"] = dict(categorized)

        # Typography
        font_counts = Counter()
        size_counts = Counter()
        weight_counts = Counter()
        for s in all_styles:
            ff = s.get("fontFamily", "").split(",")[0].strip('"\'').strip()
            if ff:
                font_counts[ff] += 1
            if s.get("fontSize"):
                size_counts[s["fontSize"]] += 1
            if s.get("fontWeight"):
                weight_counts[s["fontWeight"]] += 1
        
        heading_font = font_counts.most_common(1)[0][0] if font_counts else "Inter"
        self.tokens["typography"] = {
            "heading": heading_font,
            "body": heading_font,
            "mono": "JetBrains Mono",
            "sizes": [s for s, _ in size_counts.most_common(8)],
            "weights": [w for w, _ in weight_counts.most_common(4)],
        }

        # Spacing / Radii / Shadows (sample from data + defaults)
        radii_found = Counter()
        shadows_found = Counter()
        for s in all_styles:
            if s.get("borderRadius") and s["borderRadius"] != "0px":
                radii_found[s["borderRadius"]] += 1
            if s.get("boxShadow") and s["boxShadow"] != "none":
                shadows_found[s["boxShadow"]] += 1
        
        self.tokens["radii"] = {
            "sm": "0.25rem",
            "md": ".5rem" if not radii_found else radii_found.most_common(1)[0][0],
            "lg": "1rem",
            "full": "9999px",
        }
        self.tokens["shadows"] = {
            "sm": "0 1px 2px 0 rgb(0 0 0 / 0.05)",
            "md": list(shadows_found.keys())[0] if shadows_found else "0 4px 6px -1px rgb(0 0 0 / 0.1)",
            "lg": "0 10px 15px -3px rgb(0 0 0 / 0.1)",
        }
        self.tokens["spacing"] = {
            "unit": "4px",
            "scale": {"0": "0", "1": "0.25rem", "2": "0.5rem", "4": "1rem", "8": "2rem", "16": "4rem"}
        }

        return self.tokens

class DesignMdGenerator:
    def __init__(self, tokens: Dict, brand_name: str, url: str):
        self.tokens = tokens
        self.brand_name = brand_name
        self.url = url

    def generate(self) -> str:
        lines = [
            f"# {self.brand_name} Design System",
            "",
            f"> Auto-generated by getdesign-cli on {datetime.now().strftime('%Y-%m-%d')}",
            f"> Source: {self.url}",
            "",
            "## Color Palette",
            "",
        ]
        for role, colors in self.tokens["colors"].items():
            lines.append(f"### {role}")
            for c in colors[:8]:
                lines.append(f"- `{c['hex']}` (used {c['count']} times)")
            lines.append("")
        
        lines.extend([
            "## Typography",
            "",
            f"- **Heading**: {self.tokens['typography']['heading']}",
            f"- **Body**: {self.tokens['typography']['body']}",
            f"- **Mono**: {self.tokens['typography']['mono']}",
            "",
            "### Common Sizes",
        ])
        for s in self.tokens["typography"]["sizes"]:
            lines.append(f"- {s}")
        lines.append("")
        
        lines.extend([
            "## Spacing",
            "",
            f"Base Unit: {self.tokens['spacing']['unit']}",
            "",
            "| Token | Value |",
            "|-------|-------|",
        ])
        for k, v in self.tokens["spacing"]["scale"].items():
            lines.append(f"| {k} | {v} |")
        lines.append("")
        
        lines.extend([
            "## Border Radius",
            "",
            "| Token | Value |",
            "|-------|-------|",
        ])
        for k, v in self.tokens["radii"].items():
            lines.append(f"| {k} | {v} |")
        lines.append("")
        
        lines.extend([
            "## Shadows",
            "",
            "| Token | Value |",
            "|-------|-------|",
        ])
        for k, v in self.tokens["shadows"].items():
            lines.append(f"| {k} | `{v}` |")
        lines.append("")
        
        # Simple component CSS snippet
        primary = self.tokens["colors"].get("primary", [{}])[0].get("hex", "#000")
        bg = self.tokens["colors"].get("background", [{}])[0].get("hex", "#fff")
        text = self.tokens["colors"].get("text", [{}])[0].get("hex", "#000")
        
        lines.extend([
            "## Component Patterns",
            "",
            "### Button (Primary)",
            "```css",
            ".btn-primary {",
            f"  background: {primary};",
            f"  color: {bg if primary != bg else text};",
            f"  padding: {self.tokens['spacing']['scale']['2']} {self.tokens['spacing']['scale']['4']};",
            f"  border-radius: {self.tokens['radii']['md']};",
            "  font-weight: 500;",
            "}",
            "```",
            "",
            "### Card",
            "```css",
            ".card {",
            f"  background: {bg};",
            f"  border-radius: {self.tokens['radii']['lg']};",
            f"  padding: {self.tokens['spacing']['scale']['4']};",
            "}",
            "```",
            "",
            "## Usage for Coding Agent",
            "",
            f'"Create a React landing page matching the {self.brand_name} design system. Use primary color `{primary}` and the spacing scale above."',
            "",
        ])
        return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="生成任意网站的 DESIGN.md")
    parser.add_argument("url", help="目标网站 URL，例如 https://linear.app")
    parser.add_argument("--name", "-n", help="品牌名（默认从 URL 解析）")
    parser.add_argument("--pages", "-p", help="额外页面路径，逗号分隔，例如 /about,/pricing")
    parser.add_argument("--out", "-o", default="output", help="输出目录")
    parser.add_argument("--headless", action="store_true", default=True, help="无头模式")
    args = parser.parse_args()

    brand = args.name or args.url.replace("https://", "").replace("www.", "").split(".")[0].capitalize()
    pages = ["/"]
    if args.pages:
        pages += [p if p.startswith("/") else f"/{p}" for p in args.pages.split(",")]
    pages = list(dict.fromkeys(pages))  # 去重保序
    out_dir = Path(args.out)

    print(f"🚀 开始抓取 {brand} ({args.url})")
    print(f"📄 页面列表: {pages}")

    crawler = DesignCrawler(headless=args.headless)
    raw = crawler.crawl(args.url, pages=pages, out_dir=out_dir)

    print("🔬 分析设计 Tokens...")
    analyzer = DesignAnalyzer(raw)
    tokens = analyzer.analyze()

    print("📝 生成 DESIGN.md...")
    generator = DesignMdGenerator(tokens, brand, args.url)
    md = generator.generate()

    md_path = out_dir / f"{brand}.design.md"
    md_path.write_text(md, encoding="utf-8")
    print(f"✅ 已保存: {md_path}")

    # 打印 Kimi prompt
    print("\n💡 快速使用方式:")
    print(f"在 Kimi 中引用 `{md_path}`，然后说:")
    print(f'  "请基于 {brand} 的设计系统，生成一个官网首页的 React 组件。"')

if __name__ == "__main__":
    main()
