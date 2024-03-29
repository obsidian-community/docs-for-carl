#!/usr/bin/python3
import os
import json
import urllib.parse
import sys
import requests
import re


if os.path.isfile("paste_ids.py"):
    print("paste_ids.py is already present")
else:
    with open("paste_ids.py", "w", encoding="utf-8") as p:
        p.write("to_delete = []")

from paste_ids import to_delete

api_dev_key : str = ""
api_user_key : str = ""

try:
    if sys.argv[1]:
        api_dev_key = sys.argv[1]
    if sys.argv[2]:
        api_user_key = sys.argv[2]
except:
    raise Exception("You didn't provide the api_dev_key or api_user_key or both.")

#print(api_dev_key)
#print(api_user_key)

# deletion of old pastes

if os.path.isfile("paste_ids.py"):
    if len(to_delete) > 0:
        for el in to_delete:
            data_to_delete : dict = {'api_dev_key':api_dev_key, 'api_user_key':api_user_key, 'api_option':'delete', 'api_paste_key':el}
            removed_paste = requests.post(url="https://pastebin.com/api/api_post.php", data=data_to_delete)
            removed_paste = removed_paste.text
            print(removed_paste)
        with open("paste_ids.py", "w", encoding="utf-8") as p:
            p.write("to_delete = []")



color : int = 3092790
tagscript_file : str = """
{=(b-obsidian):Obsidian/Obsidian}
{c:cembed https://pastebin.com/{{block}}}\n\n
"""
tagscript_file_list : list = []


included_files : list = ["Android app.md", "iOS app.md", "Mobile app beta.md", "Obsidian.md", "Obsidian Mobile.md", "How Obsidian stores data.md", "Third-party plugins.md", "Insider builds.md", "YAML front matter.md", "Catalyst license.md", "Commercial license.md", "Obsidian Publish.md", "Obsidian Sync.md", "Obsidian Unlimited.md", "Refund policy.md", "Add aliases to note.md", "Folding.md", "Format your notes.md", "Link to blocks.md", "Templates.md"] 


all_urls : dict = {}

paste_ids : list = []


def get_url(normalised_path : str) -> str:
    url : str = "https://help.obsidian.md/"
    split_path : list = normalised_path.split("/")[2:]
    unencoded_url_part : str = "/".join(split_path)
    url += urllib.parse.quote(unencoded_url_part)
    url = url.replace("%20", "+")
    if url == "https://help.obsidian.md/Obsidian/Index.md":
        url = url.replace("Obsidian/", "")
    url = url[:-3]
    return url

def replace_links(content_str : str) -> str:
    content_str = content_str
    link_result = re.compile(r"\[\[(.*?)(?=(?:\]\]|#|\|))(?:.+?)?\]\]", re.MULTILINE)
    for match in link_result.finditer(content_str):
        link_url : str = all_urls[match.group(1)]
        content_str = content_str.replace(match.group(0), f"[{match.group(1)}]({link_url})")
    return content_str

for dirpath, dirnames, files in os.walk("./obsidian-docs/en/"):
    for file_name in files:
        if file_name.endswith(".md"):
            normalised_path = os.path.normpath(dirpath + "/" + file_name)
            # URL
            url = get_url(normalised_path)
            all_urls[file_name[:-3]] = url



#print(all_urls)
#counter : int = 0

for dirpath, dirnames, files in os.walk("./obsidian-docs/en/"):
    for file_name in files:
        if file_name.endswith(".md"):
            normalised_path = os.path.normpath(dirpath + "/" + file_name)
            if file_name in included_files:# and counter < 3:
                #counter += 1

                file_dict : dict = {}
                title : str = ""
                description : str = ""

                # title
                title = file_name[:-3]
                file_dict["title"] = title

                # URL
                url = all_urls[title]
                file_dict["url"] = url
            
                # color
                file_dict["color"] = color
                # description
                with open(normalised_path, "r", encoding="utf-8") as f:
                    content = f.readlines()
                    content_str = "".join(content)
                    result = re.findall(r"^(#{1,4})\s(.+)", content_str, re.MULTILINE)
                    # if there are no headings, use the raw text
                    if len(result) == 0:
                        content_str = replace_links(content_str)
                        # convert highlights to bold
                        content_str = re.sub(r"==(.+?)==", r"**\1**", content_str)
                        # limit result to 10 lines
                        result = "\n".join(content_str.split("\n")[:10])
                    # if there are headings, replace them all with links to the headings
                    # on the Obsidian Publish help site
                    else:
                        result_headings : list = []
                        for el in result:
                            heading : str = f"[{el[1]}]" + f"({url}/"
                            heading += "#" + urllib.parse.quote(el[1]).replace("%20", "+") + ")"
                            if len(el[0]) == 1:
                                heading = "__**" + heading + "**__"
                            elif len(el[0]) == 2:
                                heading = "**" + heading + "**"
                            elif len(el[0]) == 3:
                                heading = "- " + heading
                            else:
                                heading = "  - " + heading
                            result_headings.append(heading)
                        result = "\n".join(result_headings)

                    #print(file_name)
                    #print(normalised_path)
                    #print(result)
                    file_dict["description"] = result

                # convert dict to json
                json_string = json.dumps(file_dict, indent=4)
                #print(json_string)


                # upload files to pastebin
                data_to_post : dict = {'api_dev_key':api_dev_key, 'api_user_key':api_user_key, 'api_option':'paste', 'api_paste_code':json_string, 'api_paste_name':title, 'api_paste_format':'json', 'api_paste_private':1, 'api_paste_expire_date':'N'}

                pastebin_id = requests.post(url="https://pastebin.com/api/api_post.php", data=data_to_post)
                pastebin_id = pastebin_id.text
                pastebin_id = str(pastebin_id.split("/")[-1])
                print(pastebin_id)

                paste_ids.append(pastebin_id)

                # append files for tagscript file
                tagscript_title : str = title.replace(" ", "-").lower()
                tagscript_file_list.append("{=(" + tagscript_title + "):" + pastebin_id + "}")
            

tagscript_file += "\n".join(tagscript_file_list)

# write tagscript
with open("tagscript", "w", encoding="utf-8") as t:
    t.write(tagscript_file)

# write list for next deletion
with open("paste_ids.py", "w", encoding="utf-8") as p:
    p.write("to_delete = " + str(paste_ids))
