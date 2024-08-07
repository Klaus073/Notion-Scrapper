from notion_client import Client
import requests
# Replace with your Notion integration token
NOTION_API_TOKEN = 'secret_z8bhSaE7NphBtuQJovH9eB1VTBQ8cZzMKmwbsZGOHQ5'

# Replace with the ID of the specific Notion page you want to retrieve data from
NOTION_PAGE_ID = '04392b7fea314152acd6219e5d2f65b2'

# Initialize the Notion client
notion = Client(auth=NOTION_API_TOKEN)

def retrieve_page_content(page_id):
    children = notion.blocks.children.list(block_id=page_id).get('results', [])
    for block in children:
        print_block_content(block)

def extract_text(block):
    block_type = block['type']
    block_content = block.get(block_type, {})
    rich_text = block_content.get('rich_text', [])
    
    text_parts = []
    for t in rich_text:
        part = t['plain_text']
        if t['annotations']['bold']:
            part = f"**{part}**"
        if t['annotations']['italic']:
            part = f"*{part}*"
        if t['annotations']['code']:
            part = f"`{part}`"
        if t['text']['link']:
            part = f"[{part}]({t['text']['link']['url']})"
        text_parts.append(part)
    
    return ''.join(text_parts)

def get_image_base64(url):
    response = requests.get(url)
    if response.status_code == 200:
        return base64.b64encode(response.content).decode('utf-8')
    else:
        return None

def print_block_content(block, indent=0):
    block_type = block['type']
    text = extract_text(block)
    
    indent_str = ' ' * indent

    if text:
        if block_type == 'paragraph':
            print(f"{indent_str}Paragraph: {text}")
        elif block_type.startswith('heading_'):
            heading_level = block_type.split('_')[1]
            print(f"{indent_str}Heading {heading_level}: {text}")
        elif block_type == 'bulleted_list_item':
            print(f"{indent_str}Bulleted List Item: {text}")
        elif block_type == 'numbered_list_item':
            print(f"{indent_str}Numbered List Item: {text}")
        elif block_type == 'to_do':
            checked = block.get(block_type, {}).get('checked', False)
            print(f"{indent_str}To-Do: {text} - {'Checked' if checked else 'Unchecked'}")
        elif block_type == 'toggle':
            print(f"{indent_str}Toggle: {text}")
        elif block_type == 'callout':
            print(f"{indent_str}Callout: {text}")
        elif block_type == 'quote':
            print(f"{indent_str}Quote: {text}")
        else:
            print(f"{indent_str}Unsupported block type: {block_type}")
    elif block_type == 'child_page':
        title = block[block_type].get('title', 'Untitled')
        print(f"{indent_str}Child Page: {title}")
    elif block_type == 'column_list':
        print(f"{indent_str}Column List Block:")
        column_children = notion.blocks.children.list(block_id=block['id']).get('results', [])
        for column_block in column_children:
            print_block_content(column_block, indent + 2)
    elif block_type == 'column':
        print(f"{indent_str}Column Block:")
        column_children = notion.blocks.children.list(block_id=block['id']).get('results', [])
        for child_block in column_children:
            print_block_content(child_block, indent + 2)
    elif block_type == 'image':
        image_url = block[block_type].get('file', {}).get('url', 'No URL')
        if image_url != 'No URL':
            image_base64 = get_image_base64(image_url)
            if image_base64:
                print(f"{indent_str}Image (Base64): {image_base64}")
            else:
                print(f"{indent_str}Image: {image_url}")
        else:
            print(f"{indent_str}Image: {image_url}")
    else:
        print(f"{indent_str}Unsupported block type: {block_type}")

if __name__ == '__main__':
    print("Page Content:")
    retrieve_page_content(NOTION_PAGE_ID)
