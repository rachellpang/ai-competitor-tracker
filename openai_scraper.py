import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os

class OpenAIScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.base_url = "https://openai.com"
        self.blog_url = "https://openai.com/blog"

    def get_latest_blog_posts(self, limit=10):
        try:
            print(f"Fetching blog posts from {self.blog_url}")
            import time
            time.sleep(2)  # Add delay to be respectful
            response = self.session.get(self.blog_url, timeout=15)
            
            if response.status_code == 403:
                print("Access forbidden. This might be due to bot detection.")
                print("No data will be returned to avoid fake content.")
                return []
            
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            blog_posts = []
            
            # Try multiple selectors to find blog post links
            selectors = [
                'a[href*="/blog/"]',
                '.blog-post a',
                '[data-testid="blog-post"] a',
                'article a',
                '.post-title a'
            ]
            
            found_posts = set()  # Use set to avoid duplicates
            
            for selector in selectors:
                elements = soup.select(selector)
                for element in elements:
                    href = element.get('href', '')
                    if '/blog/' in href and href not in found_posts:
                        title = element.get_text().strip()
                        if title and len(title) > 10:  # Filter out short/empty titles
                            # Make sure URL is absolute
                            if href.startswith('/'):
                                full_url = self.base_url + href
                            else:
                                full_url = href
                            
                            post_data = {
                                'title': title,
                                'url': full_url,
                                'scraped_at': datetime.now().isoformat()
                            }
                            
                            blog_posts.append(post_data)
                            found_posts.add(href)
                            
                            if len(blog_posts) >= limit:
                                break
                
                if len(blog_posts) >= limit:
                    break
            
            # Remove duplicates based on title similarity
            unique_posts = []
            seen_titles = set()
            for post in blog_posts:
                title_lower = post['title'].lower()
                if title_lower not in seen_titles:
                    unique_posts.append(post)
                    seen_titles.add(title_lower)
            
            return unique_posts[:limit]
            
        except Exception as e:
            print(f"Error scraping OpenAI blog: {str(e)}")
            print("No data will be returned to avoid fake content.")
            return []


    def save_posts_to_json(self, posts, filename=None):
        if not filename:
            filename = f"openai_posts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(posts, f, indent=2)
        
        print(f"Saved {len(posts)} posts to {filename}")

    def generate_markdown_report(self, posts):
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_content = f"# OpenAI Blog Posts Report\n\n"
        report_content += f"**Generated:** {report_date}\n\n"
        report_content += f"**Total Posts Found:** {len(posts)}\n\n"
        
        if posts:
            report_content += "## Latest Blog Posts\n\n"
            for i, post in enumerate(posts, 1):
                report_content += f"{i}. **{post['title']}**\n"
                report_content += f"   - URL: {post['url']}\n"
                report_content += f"   - Scraped: {post['scraped_at']}\n\n"
        else:
            report_content += "No blog posts found.\n\n"
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        report_filename = f"reports/openai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        with open(report_filename, 'w') as f:
            f.write(report_content)
        
        print(f"Report saved to {report_filename}")
        return report_filename

    def run(self):
        print("Starting OpenAI blog scraper...")
        posts = self.get_latest_blog_posts()
        
        if posts:
            print(f"\nFound {len(posts)} blog posts:")
            for i, post in enumerate(posts, 1):
                print(f"{i}. {post['title']}")
            
            # Save to JSON
            self.save_posts_to_json(posts)
            
            # Generate markdown report
            self.generate_markdown_report(posts)
        else:
            print("No blog posts found.")

if __name__ == "__main__":
    scraper = OpenAIScraper()
    scraper.run()