import os
from dotenv import load_dotenv, find_dotenv
from atlassian import Confluence

_ = load_dotenv(find_dotenv())

ATLASSIAN_USER = os.getenv("ATLASSIAN_USER")
ATLASSIAN_TOKEN = os.getenv("ATLASSIAN_TOKEN")

confluence = Confluence(
    url='https://amadeus.atlassian.net',
    username=ATLASSIAN_USER,
    password=ATLASSIAN_TOKEN,
    cloud=True,
    api_version='cloud')

def get_page_id_by_title(space, title):
    if confluence.page_exists(space, title):
        return confluence.get_page_id(space, title)
    
    return None

def get_body(space, title):
    page_id = get_page_id_by_title(space, title)
    if page_id is not None:
        page_content = confluence.get_page_by_id(page_id, expand="body.view", status=None, version=None)
        return page_content["body"]["view"]["value"]
    return None

def delete_page(space, title):
    page_id = get_page_id_by_title(space, title)
    if page_id is not None:
        confluence.remove_page(page_id)

def get_parent_id(page_id):
    ancestors = confluence.get_page_ancestors(page_id)
    if ancestors is not None:
        return ancestors[-1]["id"]
    return None

def reupload_page(space, title, body):
    page_id = get_page_id_by_title(space, title)
    if page_id is not None:
        parent_id = get_parent_id(space, title)
        confluence.remove_page(page_id)
        confluence.create_page(space, title, body, parent_id=parent_id)

# confluence.update_page(2315732224, title="Update Page API Test", body="<i><b>page successfully updated!</b></i>")

def publish_content(space, title, body):
    page_id = get_page_id_by_title(space, title)
    if page_id:
        # Update existing page
        confluence.update_page(page_id, title=title, body=body)
        print(f"Page '{title}' updated successfully.")
    else:
        # Create new page
        confluence.create_page(space, title, body)
        print(f"Page '{title}' created successfully.")

# Example usage
if __name__ == "__main__":
    space = "CATS"
    title = "Test_nikhil"
    body = "<h1>Updated</h1>"

    print(get_page_id_by_title("CATS", "Test_nikhil"))
    print(get_body("CATS", "Test_nikhil"))
    # publish_content(space, title, body)
    