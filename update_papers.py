#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
个人主页论文自动更新脚本
功能：
  1. 从谷歌学术抓取论文列表和引用数
  2. 更新 citations.json
  3. 自动在 index.html 中新增未收录的论文

使用方法：
  pip install scholarly beautifulsoup4
  python update_papers.py

注意：首次使用 scholarly 可能需要验证（输入验证码）
"""

import json
import os
import re
import sys
from datetime import datetime

try:
    from scholarly import scholarly, ProxyGenerator
except ImportError:
    print("请先安装 scholarly: pip install scholarly")
    sys.exit(1)

# ============================================================
# 配置
# ============================================================
SCHOLAR_ID = "Y397uBoAAAAJ"
HTML_FILE = "index.html"
CITATIONS_FILE = "citations.json"
BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def normalize_title(title):
    """标准化论文标题，用于匹配"""
    t = title.lower().strip()
    t = re.sub(r'[^a-z0-9]', '', t)
    return t


def fetch_google_scholar():
    """从谷歌学术获取论文列表"""
    print("正在连接谷歌学术...")

    # 可选：设置代理（如果被墙）
    # pg = ProxyGenerator()
    # pg.FreeProxies()
    # scholarly.use_proxy(pg)

    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=['publications'])

    papers = []
    for pub in author['publications']:
        # 获取详细信息
        try:
            filled = scholarly.fill(pub)
            title = filled.get('bib', {}).get('title', '')
            authors = filled.get('bib', {}).get('author', '')
            venue = filled.get('bib', {}).get('venue', '')
            year = filled.get('bib', {}).get('year', '')
            pub_url = filled.get('pub_url', '')
            citation_url = filled.get('cites_per_year', {})

            # 引用数
            citations = filled.get('citedby', 0)

            papers.append({
                'title': title,
                'authors': authors,
                'venue': venue,
                'year': str(year) if year else '',
                'url': pub_url,
                'citations': citations,
            })
            print(f"  ✓ {title[:60]}... ({citations} 引用)")
        except Exception as e:
            print(f"  ✗ 获取详情失败: {pub.get('bib', {}).get('title', '')[:50]} - {e}")

    return papers


def update_citations_json(papers):
    """更新 citations.json"""
    citations_path = os.path.join(BASE_PATH, CITATIONS_FILE)

    # 读取现有数据
    existing = {}
    if os.path.exists(citations_path):
        with open(citations_path, 'r', encoding='utf-8') as f:
            existing = json.load(f)

    # 更新引用数
    updated = 0
    for p in papers:
        key = normalize_title(p['title'])
        if not key:
            continue
        existing[key] = {
            'count': p['citations'],
            'url': f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={SCHOLAR_ID}&citation_for_view={SCHOLAR_ID}:{key}"
        }
        updated += 1

    # 删除空 key
    existing.pop('', None)

    with open(citations_path, 'w', encoding='utf-8') as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print(f"\n✓ citations.json 已更新：{updated} 条记录")
    return existing


def find_new_papers(papers, html_content):
    """找出 HTML 中未收录的新论文"""
    html_lower = html_content.lower()

    new_papers = []
    for p in papers:
        title = p['title']
        if not title:
            continue
        # 检查标题是否已存在于 HTML 中
        if title.lower()[:30] in html_lower:
            continue
        # 也检查标准化后的标题
        norm = normalize_title(title)
        if norm and norm[:20] in html_lower:
            continue
        new_papers.append(p)

    return new_papers


def generate_paper_html(papers_grouped):
    """生成按年份分组的论文 HTML"""
    html_parts = []

    for year in sorted(papers_grouped.keys(), reverse=True):
        html_parts.append(f'''
                      <h4 style="font-family:Arial; color:#555; border-bottom:1px solid #ddd; padding-bottom:5px;">
                        {year}
                      </h4>
                      <ol>''')

        for p in papers_grouped[year]:
            authors = p.get('authors', '')
            title = p.get('title', '')
            venue = p.get('venue', '')
            citations = p.get('citations', 0)
            key = normalize_title(title)

            cite_badge = f' <span class="cite-badge">[Citations: {citations}]</span>' if citations > 0 else ''

            html_parts.append(f'''
                        <li style="font-family:Arial, Times; color:black;font-size:15px; margin-bottom: 8px;">
                          {authors}
                          <span class="paper-title">{title}</span>.
                          <span class="paper-venue">{venue}</span>. {year}.{cite_badge}
                        </li>''')

        html_parts.append('''
                      </ol>''')

    return '\n'.join(html_parts)


def inject_papers_into_html(html_content, papers):
    """将论文列表注入 HTML 的 publications 部分"""
    # 按年份分组
    papers_grouped = {}
    for p in papers:
        year = p.get('year', 'Unknown')
        if year not in papers_grouped:
            papers_grouped[year] = []
        papers_grouped[year].append(p)

    new_pub_html = generate_paper_html(papers_grouped)

    # 替换 publications 部分
    # 找到 publications section 的起始和结束
    pub_start = html_content.find('<!-- publications 文章发表-->')
    if pub_start == -1:
        pub_start = html_content.find('data-section="publications"')
        if pub_start == -1:
            print("错误：找不到 publications 部分")
            return html_content

    # 找到下一个 section 的起始
    next_section = html_content.find('data-section="patents_books"', pub_start)
    if next_section == -1:
        next_section = html_content.find('<section class="colorlib-about" data-section="patents_books"', pub_start)

    if next_section == -1:
        print("错误：找不到下一个 section")
        return html_content

    # 找到 <section> 的起始
    section_start = html_content.rfind('<section', pub_start - 50, pub_start + 50)
    if section_start == -1:
        # 回退：从 pub_start 开始
        section_start = pub_start

    # 构建新的 publications section
    new_section = f'''        <!-- publications 文章发表-->
        <section class="colorlib-about" data-section="publications">
          <div class="colorlib-narrow-content">
            <div class="row">
              <div class="col-md-12">
                <div class="row row-bottom-padded-sm animate-box" data-animate-effect="fadeInLeft">
                  <div class="col-md-12">
                    <div class="">
                      <hr style="border: 2px solid #000000" />
                      <h2 style="font-family:Arial, Times; color:black;">
                        Publications
                        <a style="font-size:14px;"
                          href="https://scholar.google.com/citations?user={SCHOLAR_ID}&hl=en">[Google Scholar]</a>
                        <span style="font-size:12px; color:gray; font-weight:normal;">(Citations updated
                          automatically via Google Scholar)</span>
                      </h2>

                      <div id="pub-stats" style="margin: 15px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; display: flex; gap: 30px; flex-wrap: wrap;">
                        <div style="text-align:center;"><span style="font-size:24px; font-weight:bold; color:#d9534f;">{sum(len(v) for v in papers_grouped.values())}</span><br><span style="font-size:13px; color:#666;">Total Papers</span></div>
                        <div style="text-align:center;"><span id="total-citations" style="font-size:24px; font-weight:bold; color:#d9534f;">0</span><br><span style="font-size:13px; color:#666;">Total Citations</span></div>
                      </div>
{new_pub_html}
                      </br>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>'''

    # 找到结束标签
    section_end = html_content.find('</section>', next_section - 100)
    if section_end == -1:
        section_end = next_section

    # 替换
    new_html = html_content[:section_start] + new_section + html_content[section_end + 10:]

    return new_html


def main():
    print(f"=== 个人主页论文自动更新工具 ===\n")
    print(f"Google Scholar ID: {SCHOLAR_ID}")
    print(f"工作目录: {BASE_PATH}")
    print()

    # 1. 从谷歌学术抓取
    papers = fetch_google_scholar()
    if not papers:
        print("未获取到论文数据，请检查网络或 Google Scholar ID")
        return

    print(f"\n共获取到 {len(papers)} 篇论文")

    # 2. 更新 citations.json
    update_citations_json(papers)

    # 3. 检查 HTML 中是否有新论文
    html_path = os.path.join(BASE_PATH, HTML_FILE)
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        new_papers = find_new_papers(papers, html_content)
        if new_papers:
            print(f"\n发现 {len(new_papers)} 篇新论文未在 HTML 中收录：")
            for p in new_papers:
                print(f"  - {p['title'][:60]}")
        else:
            print("\n所有论文已在 HTML 中收录")

        # 如果用户想自动更新 HTML
        auto_update = input("\n是否用谷歌学术数据替换 HTML 中的论文列表？(y/n): ")
        if auto_update.lower() == 'y':
            papers_grouped = {}
            for p in papers:
                y = p.get('year', 'Unknown')
                papers_grouped.setdefault(y, []).append(p)

            new_html = inject_papers_into_html(html_content, papers)

            # 同时更新 JavaScript 显示总引用数
            backup = html_path + '.bak'
            with open(backup, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"备份已保存: {backup}")

            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            print(f"✓ {HTML_FILE} 已更新")

    print("\n=== 完成 ===")


if __name__ == '__main__':
    main()
