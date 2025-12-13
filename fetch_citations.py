import json
import re
from scholarly import scholarly

# ========= 请在这里填入你的谷歌学术 ID =========
AUTHOR_ID = 'Y397uBoAAAAJ' 
# =============================================

def normalize_title(title):
    """
    将标题标准化（转小写，去标点），以便进行模糊匹配
    """
    return re.sub(r'[^a-z0-9]', '', title.lower())

def fetch_citation_data():
    print(f"Fetching data for author ID: {AUTHOR_ID}...")
    
    try:
        search_query = scholarly.search_author_id(AUTHOR_ID)
        author = scholarly.fill(search_query, sections=['publications'])
        
        # 生成一个字典: { "标准化的标题": { "citations": 10, "id": "paper_id", "url": "..." } }
        citations_map = {}
        
        for pub in author['publications']:
            title = pub['bib'].get('title', '')
            if not title:
                continue
            
            norm_title = normalize_title(title)
            count = pub.get('num_citations', 0)
            pub_id = pub['author_pub_id']
            # 构建单篇文章的引用详情页链接
            link = f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={AUTHOR_ID}&citation_for_view={pub_id}"
            
            citations_map[norm_title] = {
                "count": count,
                "url": link
            }
            
        return citations_map

    except Exception as e:
        print(f"Error fetching data: {e}")
        return {}

if __name__ == "__main__":
    data = fetch_citation_data()
    
    # 将数据保存为 citations.json
    with open('citations.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Successfully exported {len(data)} papers to citations.json")