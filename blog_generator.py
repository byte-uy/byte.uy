import re
import requests
import os
import json
import shutil
import logging

from datetime import datetime, timezone, timedelta
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
from jinja2 import Environment, FileSystemLoader

CONFIG_PATH = 'config.json'
STATIC_DIRS = ['js', 'img', 'css']
ARTICLES_PER_PAGE = 5

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def setup_environment(template_dir):
    return Environment(loader=FileSystemLoader(template_dir, encoding='utf8'), autoescape=True)

def clear_output_dir(output_dir, img_dir):
    if os.path.exists(output_dir):
        for item in os.listdir(output_dir):
            item_path = os.path.join(output_dir, item)
            if os.path.isdir(item_path) and item != 'img':
                shutil.rmtree(item_path)
            elif os.path.isfile(item_path):
                os.remove(item_path)
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

def copy_static_assets(template_dir, output_dir, static_dirs):
    for static_dir in static_dirs:
        src = os.path.join(template_dir, static_dir)
        dest = os.path.join(output_dir, static_dir)
        if os.path.exists(src):
            shutil.copytree(src, dest, dirs_exist_ok=True)

def get_data_from_endpoint(endpoint_url, auth_token, service):
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = requests.get(f"{endpoint_url}?token={auth_token}&service={service}", headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data: {response.text}")
    return response.json()

def download_image(url, img_dir, filename = None):
    try:
        regex = r'https:\/\/drive\.google\.com\/file\/d\/([a-zA-Z0-9_-]+)\/view\?usp=.*'
        match = re.match(regex, url)

        if match:
            file_id = match.group(1)
            url = f"https://drive.google.com/uc?id={file_id}"

        if not filename:
            filename = f"{url.split('id=')[1]}.jpg"
        image_path = os.path.join(img_dir, filename)
        
        if os.path.exists(image_path):
            logging.debug(f"Image already exists: {filename}")
            return filename
        
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(image_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return filename
        else:
            logging.error(f"Failed to download image: {url}")
            return None
    except Exception as e:
        logging.error(f"Error downloading image {url}: {e}")
        return None
    
def transform_logs(logs, img_dir):
    for index, log in enumerate(logs):
        log['url_slug'] = f"0x{index:x}"
        if not log['image_url']:
            log['type'] = 'note'
        else:
            log['type'] = 'photo'
            log['image_url'] = download_image(log['image_url'], img_dir)
    
    logs.reverse()
    return logs

def blog_to_rss_item(blogs, lang):
    rss_items = []
    for blog in blogs:
        combined_date = f"{blog['date']} {blog['time']}"
        dt = datetime.strptime(combined_date, "%Y-%m-%d %H:%M")
        rss_date = dt.strftime("%a, %d %b %Y %H:%M:%S -0300")

        title = blog['title_en']
        description = blog['brief_en']
        if lang == 'es-UY':
            title = blog['title_es']
            description = blog['brief_es']

        item = {
            'title': title,
            'link': blog['url_slug'],
            'description': description,
            'date': rss_date
        }
        rss_items.append(item)
    return rss_items

def log_to_rss_item(logs, lang):
    rss_items = []
    for log in logs:
        combined_date = f"{log['date']} {log['time']}"
        dt = datetime.strptime(combined_date, "%Y-%m-%d %H:%M")
        rss_date = dt.strftime("%a, %d %b %Y %H:%M:%S -0300")
        
        title = rss_date
        description = log['content_en']
        if lang == 'es-UY':
            description = log['content_es']

        item = {
            'title': title,
            'link': log['url_slug'],
            'description': description,
            'date': rss_date
        }
        rss_items.append(item)
    return rss_items

def paginate_blogs(blogs, blogs_per_page):
    for i in range(0, len(blogs), blogs_per_page):
        yield blogs[i:i + blogs_per_page]

def render_home(env, output_dir, socials, blogs):
    template = env.get_template('index.html')
    total_pages = len(blogs) // ARTICLES_PER_PAGE + 1

    for page_number, page_blogs in enumerate(paginate_blogs(blogs, ARTICLES_PER_PAGE), start=1):
        if page_number == 1:
            content_es = template.render(lang='es-UY', current_page='home', socials=socials, blogs=page_blogs, page_number=page_number, prev_page='#', next_page=f'/page/{page_number + 1}' if page_number < total_pages else '#')
            with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(content_es)
            
            content_en = template.render(lang='en-US', current_page='home', socials=socials, blogs=page_blogs, page_number=page_number, prev_page='#', next_page=f'/en/page/{page_number + 1}' if page_number < total_pages else '#')
            os.makedirs(os.path.join(output_dir, 'en'), exist_ok=True)
            with open(os.path.join(output_dir, 'en', 'index.html'), 'w', encoding='utf-8') as f:
                f.write(content_en)

            os.makedirs(os.path.join(output_dir, 'page'), exist_ok=True)
            with open(os.path.join(output_dir, 'page', 'index.html'), 'w', encoding='utf-8') as f:
                f.write(content_es)
            
            os.makedirs(os.path.join(output_dir, 'en', 'page'), exist_ok=True)
            with open(os.path.join(output_dir, 'en', 'page', 'index.html'), 'w', encoding='utf-8') as f:
                f.write(content_en)

        content_es = template.render(lang='es-UY', current_page='home', socials=socials, blogs=page_blogs, page_number=page_number, prev_page=f'/page/{page_number - 1}' if page_number > 1 else '#', next_page=f'/page/{page_number + 1}' if page_number < total_pages else '#')
        os.makedirs(os.path.join(output_dir, 'page', f'{page_number}'), exist_ok=True)
        with open(os.path.join(output_dir, 'page', f'{page_number}', 'index.html'), 'w', encoding='utf-8') as f:
            f.write(content_es)

        content_en = template.render(lang='en-US', current_page='home', socials=socials, blogs=page_blogs, page_number=page_number, prev_page=f'/en/page/{page_number - 1}' if page_number > 1 else '#', next_page=f'/en/page/{page_number + 1}' if page_number < total_pages else '#')
        os.makedirs(os.path.join(output_dir, 'en', 'page', f'{page_number}'), exist_ok=True)
        with open(os.path.join(output_dir, 'en', 'page', f'{page_number}', 'index.html'), 'w', encoding='utf-8') as f:
            f.write(content_en)

def render_posts(env, output_dir, comments_endpoint, comments, socials, blogs):
    template = env.get_template('post.html')
    for post in blogs:
        comments_es = [comment for comment in comments if comment['path'] == '/' + post['url_slug']]
        comments_es.reverse()
        content_es = template.render(lang='es-UY', path='/', current_page=post['url_slug'], comments_endpoint=comments_endpoint, comments=comments_es, socials=socials, post=post)
        os.makedirs(os.path.join(output_dir, post['url_slug']), exist_ok=True)
        with open(os.path.join(output_dir, post['url_slug'], 'index.html'), 'w', encoding='utf-8') as f:
            f.write(content_es)

        comments_en = [comment for comment in comments if comment['path'] == '/en/' + post['url_slug']]
        comments_en.reverse()
        content_en = template.render(lang='en-US', path='/en/', current_page=post['url_slug'], comments_endpoint=comments_endpoint, comments=comments_en, socials=socials, post=post)
        os.makedirs(os.path.join(output_dir, 'en', post['url_slug']), exist_ok=True)
        with open(os.path.join(output_dir, 'en', post['url_slug'], 'index.html'), 'w', encoding='utf-8') as f:
            f.write(content_en)

def render_about(env, output_dir, socials, about):
    template = env.get_template('about.html')

    content_es = template.render(lang='es-UY', current_page='about', socials=socials, about=about[0])
    os.makedirs(os.path.join(output_dir, 'about'), exist_ok=True)
    with open(os.path.join(output_dir, 'about', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(content_es)

    content_en = template.render(lang='en-US', current_page='about', socials=socials, about=about[0])
    os.makedirs(os.path.join(output_dir, 'en', 'about'), exist_ok=True)
    with open(os.path.join(output_dir, 'en', 'about', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(content_en)

def paginate_logs(logs, logs_per_page):
    for i in range(0, len(logs), logs_per_page):
        yield logs[i:i + logs_per_page]

def render_logs_page(env, output_dir, socials, logs):
    template = env.get_template('logs.html')
    total_pages = len(logs) // ARTICLES_PER_PAGE + 1
    for page_number, page_logs in enumerate(paginate_logs(logs, ARTICLES_PER_PAGE), start=1):
        if page_number == 1:
            content_es = template.render(lang='es-UY', current_page='logs', socials=socials, logs=page_logs, page_number=page_number, prev_page='#', next_page=f'/logs/page/{page_number + 1}' if page_number < total_pages else '#')
            os.makedirs(os.path.join(output_dir, 'logs'), exist_ok=True)
            with open(os.path.join(output_dir, 'logs', 'index.html'), 'w', encoding='utf-8') as f:
                f.write(content_es)

            content_en = template.render(lang='en-US', current_page='logs', socials=socials, logs=page_logs, page_number=page_number, prev_page='#', next_page=f'/en/logs/page/{page_number + 1}' if page_number < total_pages else '#')
            os.makedirs(os.path.join(output_dir, 'en', 'logs'), exist_ok=True)
            with open(os.path.join(output_dir, 'en', 'logs', 'index.html'), 'w', encoding='utf-8') as f:
                f.write(content_en)

            content_es = template.render(lang='es-UY', current_page='logs', socials=socials, logs=page_logs, page_number=page_number, prev_page='#', next_page=f'/logs/page/{page_number + 1}' if page_number < total_pages else '#')
            os.makedirs(os.path.join(output_dir, 'logs', 'page'), exist_ok=True)
            with open(os.path.join(output_dir, 'logs', 'page', 'index.html'), 'w', encoding='utf-8') as f:
                f.write(content_es)

            content_en = template.render(lang='en-US', current_page='logs', socials=socials, logs=page_logs, page_number=page_number, prev_page='#', next_page=f'/en/logs/page/{page_number + 1}' if page_number < total_pages else '#')
            os.makedirs(os.path.join(output_dir, 'en', 'logs', 'page'), exist_ok=True)
            with open(os.path.join(output_dir, 'en', 'logs', 'page', 'index.html'), 'w', encoding='utf-8') as f:
                f.write(content_en)

        content_es = template.render(lang='es-UY', current_page='logs', socials=socials, logs=page_logs, page_number=page_number, prev_page=f'/logs/page/{page_number - 1}' if page_number > 1 else '#', next_page=f'/logs/page/{page_number + 1}' if page_number < total_pages else '#') 
        os.makedirs(os.path.join(output_dir, 'logs', 'page', f'{page_number}'), exist_ok=True)
        with open(os.path.join(output_dir, 'logs', 'page', f'{page_number}', 'index.html'), 'w', encoding='utf-8') as f:
            f.write(content_es)

        content_en = template.render(lang='en-US', current_page='logs', socials=socials, logs=page_logs, page_number=page_number, prev_page=f'/en/logs/page/{page_number - 1}' if page_number > 1 else '#', next_page=f'/en/logs/page/{page_number + 1}' if page_number < total_pages else '#')
        os.makedirs(os.path.join(output_dir, 'en', 'logs', 'page', f'{page_number}'), exist_ok=True)
        with open(os.path.join(output_dir, 'en', 'logs', 'page', f'{page_number}', 'index.html'), 'w', encoding='utf-8') as f:
            f.write(content_en)

def render_logs(env, output_dir, comments_endpoint, comments, socials, logs):
    for log in logs:
        template = env.get_template('log.html')

        comments_es = [comment for comment in comments if comment['path'] == '/logs/' + log['url_slug']]
        comments_es.reverse()
        content_es = template.render(lang='es-UY', path='/logs/', current_page=log['url_slug'], comments_endpoint=comments_endpoint, comments=comments_es, socials=socials, log=log)
        os.makedirs(os.path.join(output_dir, 'logs', log['url_slug']), exist_ok=True)
        with open(os.path.join(output_dir, 'logs', log['url_slug'], 'index.html'), 'w', encoding='utf-8') as f:
            f.write(content_es)

        comments_en = [comment for comment in comments if comment['path'] == '/en/logs/' + log['url_slug']]
        comments_en.reverse()
        content_en = template.render(lang='en-US', path='/en/logs/', current_page=log['url_slug'], comments_endpoint=comments_endpoint, comments=comments_en, socials=socials, log=log)
        os.makedirs(os.path.join(output_dir, 'en', 'logs', log['url_slug']), exist_ok=True)
        with open(os.path.join(output_dir, 'en', 'logs', log['url_slug'], 'index.html'), 'w', encoding='utf-8') as f:
            f.write(content_en)

def render_redirects(env, output_file, redirects):
    template = env.get_template('redirects.nginx')
    content = template.render(redirects=redirects)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

def render_rss_feed(env, output_dir, feed, rss_items):
    template = env.get_template('rss.xml')

    utc_minus_3 = timezone(timedelta(hours=-3))
    date = datetime.now(utc_minus_3).strftime('%a, %d %b %Y %H:%M:%S %z')

    content = template.render(build_date=date, feed=feed, items=rss_items)
    feed_path = output_dir
    if feed['lang'] == 'es-UY':
        feed_path = os.path.join(output_dir, feed['url_slug'])	
    else:  
        feed_path = os.path.join(output_dir, 'en', feed['url_slug'])

    with open(feed_path, 'w', encoding='utf-8') as f:
        f.write(content)

def render_search(env, output_dir, posts, logs, socials, about):
    template = env.get_template('search.html')

    content_es = template.render(lang='es-UY', posts=posts, logs=logs, socials=socials, about=about[0])
    os.makedirs(os.path.join(output_dir, 'search'), exist_ok=True)
    with open(os.path.join(output_dir, 'search', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(content_es)

    content_en = template.render(lang='en-US', posts=posts, logs=logs, socials=socials, about=about[0])
    os.makedirs(os.path.join(output_dir, 'en', 'search'), exist_ok=True)
    with open(os.path.join(output_dir, 'en', 'search', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(content_en)

def generate_blog(config):
    template_dir = config['TEMPLATE_DIR']

    logging.info("Generating static site")
    env = setup_environment(template_dir)

    img_dir = os.path.join(config['OUTPUT_DIR'], 'img')

    logging.debug("Clearing output directory")
    clear_output_dir(config['OUTPUT_DIR'], img_dir)

    logging.debug("Copying static assets")
    copy_static_assets(template_dir, config['OUTPUT_DIR'], STATIC_DIRS)

    logging.debug("Fetching data from endpoint")
    socials = get_data_from_endpoint(config['DATA_ENDPOINT'], config['DATA_AUTH_TOKEN'], "Socials")
    about = get_data_from_endpoint(config['DATA_ENDPOINT'], config['DATA_AUTH_TOKEN'], "About")
    redirects = get_data_from_endpoint(config['DATA_ENDPOINT'], config['DATA_AUTH_TOKEN'], "Redirects")
    feeds = get_data_from_endpoint(config['DATA_ENDPOINT'], config['DATA_AUTH_TOKEN'], "RSS")
    
    comments = get_data_from_endpoint(config['DATA_ENDPOINT'], config['DATA_AUTH_TOKEN'], "Comments")
    comments = [comment for comment in comments if comment['approved']]

    media = get_data_from_endpoint(config['DATA_ENDPOINT'], config['DATA_AUTH_TOKEN'], "Media")
    for item in media:
        download_image(item['media'], img_dir, item['url_slug'])

    logs = get_data_from_endpoint(config['DATA_ENDPOINT'], config['DATA_AUTH_TOKEN'], "Logs")
    logs = transform_logs(logs, img_dir)

    blogs = get_data_from_endpoint(config['DATA_ENDPOINT'], config['DATA_AUTH_TOKEN'], "Blogs")
    blogs = [blog for blog in blogs if blog['published']]

    logging.debug("Rendering templates")
    render_home(env, config['OUTPUT_DIR'], socials, blogs)
    render_posts(env, config['OUTPUT_DIR'], config['COMMENTS_ENDPOINT'], comments, socials, blogs)
    render_about(env, config['OUTPUT_DIR'], socials, about)
    render_logs_page(env, config['OUTPUT_DIR'], socials, logs)
    render_logs(env, config['OUTPUT_DIR'], config['COMMENTS_ENDPOINT'], comments, socials, logs)
    render_redirects(env, config['OUTPUT_REDIRECT_FILE'], redirects)
    render_search(env, config['OUTPUT_DIR'], blogs, logs, socials, about)

    for feed in feeds:
        if feed['type'] == 'blog':
            render_rss_feed(env, config['OUTPUT_DIR'], feed, blog_to_rss_item(blogs, feed['lang']))
        else:
            render_rss_feed(env, config['OUTPUT_DIR'], feed, log_to_rss_item(logs, feed['lang']))

    logging.info(f"Static site generated in {config['OUTPUT_DIR']}/")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    config = load_config(CONFIG_PATH)
    generate_blog(config)
    os.chdir('dist')
    handler = SimpleHTTPRequestHandler
    with TCPServer(("", 8080), handler) as httpd:
        logging.info("Serving at http://localhost:8080/")
        httpd.serve_forever()

