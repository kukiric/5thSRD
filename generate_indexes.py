#!/usr/bin/env python3
import os
import argparse
import markdown
import codecs
import re

spell_list_src = os.path.join(".", "src")
spells_md_src = os.path.join(".", "docs", "spellcasting", "spells")
class_spell_lists_output = os.path.join(".", "docs", "spellcasting", "spell_lists")
spell_indexes_output = os.path.join(".", "docs", "spellcasting", "spell_indexes")
spells_relative_link_prefix = "/spellcasting/spells"

items_md_src = os.path.join(".", "docs", "gamemaster_rules", "magic_items")
item_indexes_output = os.path.join(".", "docs", "gamemaster_rules", "magic_item_indexes")
items_relative_link_prefix = "/gamemaster_rules/magic_items"

monsters_md_src = os.path.join(".", "docs", "gamemaster_rules", "monsters")
monster_indexes_output = os.path.join(".", "docs", "gamemaster_rules", "monster_indexes")
monsters_relative_link_prefix = "/gamemaster_rules/monsters"

metadata_regex = re.compile(r"(.+\n)+\n+")

def create_output_directories():
    directories = [class_spell_lists_output, spell_indexes_output, item_indexes_output, monster_indexes_output]
    for directory in directories:
        if not os.path.exists(directory):
            print("Creating output directory at: %s" % directory)
            os.makedirs(directory)

def write_md_to_file(md, path):
    print("Writing file to: %s\n" % path)
    with open(path, "w") as f:
        for line in md:
            f.write(line + "\n")

def generate_formatted_title(title, spells=True):
    if type(title) == int:
        title = str(title)
    if type(title) == float:
        title = str(title)
    if len(title) == 1 and title.isdigit() and spells:
        if title == "0":
            return "## Cantrips (0-Level)"
        if title == "1":
            return "## 1st Level"
        if title == "2":
            return "## 2nd level"
        if title == "3":
            return "## 3rd level"
        else:
            return "## %sth level" % title
    else:
        return "## %s" % title.capitalize()

# Remove all metadata (eg. title, level, magic school) from the top of a file until the first empty line is found
def trim_metadata(str):
    return metadata_regex.sub("", str, count = 1)

def construct_spell_map():
    output = {}
    spell_files = os.listdir(spells_md_src)
    for filename in spell_files:
        md = markdown.Markdown(extensions=["markdown.extensions.meta"])
        input_file = open(os.path.join(spells_md_src, filename), mode="r", encoding="utf-8")
        raw_data = input_file.read().replace("\r\n", "\n")
        md.convert(raw_data)
        try:
            level = md.Meta["level"][0]
            name = md.Meta["name"][0]
            school = md.Meta["school"][0]
            name_category = md.Meta["name"][0][0].capitalize()
        except KeyError as e:
            print("Error in %s" % filename)
            print("Unable to find meta variable: %s" % e.message)
            exit(1)
        output[name] = {"level": level, "school": school, "name_category": name_category, "text": trim_metadata(raw_data)}
    return output

def construct_item_map():
    output = {}
    item_files = os.listdir(items_md_src)
    for filename in item_files:
        md = markdown.Markdown(extensions=["markdown.extensions.meta"])
        input_file = open(os.path.join(items_md_src, filename), mode="r", encoding="utf-8")
        raw_data = input_file.read().replace("\r\n", "\n")
        md.convert(raw_data)
        try:
            name = md.Meta["name"][0]
            item_type = md.Meta["type"][0]
            name_category = md.Meta["name"][0][0].capitalize()
        except KeyError as e:
            print("Error in %s" % filename)
            print("Unable to find meta variables: %s" % e.message)
            exit(1)
        output[name] = {"type": item_type, "name_category": name_category, "text": trim_metadata(raw_data)}
    return output

def construct_monster_map():
    output = {}
    monster_files = os.listdir(monsters_md_src)
    for filename in monster_files:
        md = markdown.Markdown(extensions=["markdown.extensions.meta"])
        input_file = open(os.path.join(monsters_md_src, filename), mode="r", encoding="utf-8")
        raw_data = input_file.read().replace("\r\n", "\n")
        md.convert(raw_data)
        try:
            name = md.Meta["name"][0]
            cr = md.Meta["cr"][0]
            type = md.Meta["type"][0]
            name_category = md.Meta["name"][0][0].capitalize()
        except KeyError as e:
            print("Error in %s" % filename)
            print("Unable to find meta variables: %s" % e.message)
            exit(1)
        output[name] = {"name_category": name_category, "cr": str(cr), "type": type, "text": trim_metadata(raw_data)}
    return output

def convert_to_linkable_name(spell):
    return spell.replace(" ", "_").replace("'", "").replace("/", "").replace(",", "").replace("+", "").replace("-", "_").replace("(", "").replace(")", "").lower()

def convert_map_by_to_markdown(map_by, page_title, link_prefix, spells=True, floats=False):
    output = [page_title]
    if floats:
        sorted_map = sorted(map_by, key=float)
    else:
        sorted_map = sorted(map_by)
    for category in sorted_map:
        output.append(generate_formatted_title(category, spells))
        for item in sorted(map_by[category]):
            item_link_name = convert_to_linkable_name(item)
            output.append("\n##%s" % item)
    return output

def convert_spells_map_to_list(spell_map):
    output = []
    for spell in sorted(spell_map):
        output.append(spell)
    return output

def generate_spells_by_level(spell_map):
    print("Generating spells by level...")
    spells_by_level = {}
    for spell in spell_map:
        spell_level = spell_map[spell]["level"]
        spell_text = spell_map[spell]["text"]
        if spell_level in spells_by_level:
            spells_by_level[spell_level].append(spell_text)
        else:
            spells_by_level[spell_level] = [spell_text]
    md_output = convert_map_by_to_markdown(spells_by_level, "# Spells by Level", spells_relative_link_prefix)
    write_md_to_file(md_output, os.path.join(spell_indexes_output, "spells_by_level.md"))

def generate_spells_by_name(spell_map):
    print("Generating spells by name...")
    spells_by_name = {}
    for spell in spell_map:
        spell_category = spell_map[spell]["name_category"]
        spell_text = spell_map[spell]["text"]
        if spell_category in spells_by_name:
            spells_by_name[spell_category].append(spell_text)
        else:
            spells_by_name[spell_category] = [spell_text]
    md_output = convert_map_by_to_markdown(spells_by_name, "# Spells by Name", spells_relative_link_prefix)
    write_md_to_file(md_output, os.path.join(spell_indexes_output, "spells_by_name.md"))

def generate_spells_by_school(spell_map):
    print("Generating spells by school...")
    spells_by_school = {}
    for spell in spell_map:
        spell_school = spell_map[spell]["school"]
        spell_text = spell_map[spell]["text"]
        if spell_school in spells_by_school:
            spells_by_school[spell_school].append(spell_text)
        else:
            spells_by_school[spell_school] = [spell_text]
    md_output = convert_map_by_to_markdown(spells_by_school, "# Spells by School", spells_relative_link_prefix)
    write_md_to_file(md_output, os.path.join(spell_indexes_output, "spells_by_school.md"))

def generate_items_by_name(item_map):
    print("Generating items by name...")
    items_by_name = {}
    for item in item_map:
        item_category = item_map[item]["name_category"]
        item_text = item_map[item]["text"]
        if item_category in items_by_name:
            items_by_name[item_category].append(item_text)
        else:
            items_by_name[item_category] = [item_text]
    md_output = convert_map_by_to_markdown(items_by_name, "# Items by Name", items_relative_link_prefix)
    write_md_to_file(md_output, os.path.join(item_indexes_output, "items_by_name.md"))

def generate_items_by_type(item_map):
    print("Generating items by type...")
    items_by_type = {}
    for item in item_map:
        item_category = item_map[item]["type"]
        item_text = item_map[item]["text"]
        if item_category in items_by_type:
            items_by_type[item_category].append(item_text)
        else:
            items_by_type[item_category] = [item_text]
    md_output = convert_map_by_to_markdown(items_by_type, "# Items by Type", items_relative_link_prefix)
    write_md_to_file(md_output, os.path.join(item_indexes_output, "items_by_type.md"))

def generate_monsters_by_name(monster_map):
    print("Generating monsters by name...")
    monsters_by_name = {}
    for monster in monster_map:
        monster_category = monster_map[monster]["name_category"]
        monster_text = monster_map[monster]["text"]
        if monster_category in monsters_by_name:
            monsters_by_name[monster_category].append(monster_text)
        else:
            monsters_by_name[monster_category] = [monster_text]
    md_output = convert_map_by_to_markdown(monsters_by_name, "# Monsters by Name", monsters_relative_link_prefix)
    write_md_to_file(md_output, os.path.join(monster_indexes_output, "monsters_by_name.md"))

def generate_monsters_by_type(monster_map):
    print("Generating monsters by type...")
    monsters_by_type = {}
    for monster in monster_map:
        monster_category = monster_map[monster]["type"]
        monster_text = monster_map[monster]["text"]
        if monster_category in monsters_by_type:
            monsters_by_type[monster_category].append(monster_text)
        else:
            monsters_by_type[monster_category] = [monster_text]
    md_output = convert_map_by_to_markdown(monsters_by_type, "# Monsters by type", monsters_relative_link_prefix)
    write_md_to_file(md_output, os.path.join(monster_indexes_output, "monsters_by_type.md"))

def generate_monsters_by_cr(monster_map):
    print("Generating monsters by cr...")
    monsters_by_cr = {}
    for monster in monster_map:
        monster_category = monster_map[monster]["cr"]
        monster_text = monster_map[monster]["text"]
        if monster_category in monsters_by_cr:
            monsters_by_cr[monster_category].append(monster_text)
        else:
            monsters_by_cr[monster_category] = [monster_text]
    md_output = convert_map_by_to_markdown(monsters_by_cr, "# Monsters by CR", monsters_relative_link_prefix, spells=False, floats=True)
    write_md_to_file(md_output, os.path.join(monster_indexes_output, "monsters_by_cr.md"))

def generate_md_spell_list(class_name, class_files_path):
    md = []
    md.append("# %s Spells" % class_name.capitalize())
    files = sorted(os.listdir(class_files_path))
    for file in files:
        # Insert the section header
        md.append(generate_formatted_title(file.split(".")[0]))
        with open("%s/%s" % (class_files_path, file)) as f:
            # Loop over each line, should be one spell name per line
            for line in f.readlines():
                spell_name = line.strip()
                spell_name_link = "%s.md" % convert_to_linkable_name(spell_name)
                # Get the spell text from the file
                with open(os.path.join(spells_md_src, spell_name_link), mode="r", encoding="utf-8") as f:
                    raw_data = f.read().replace("\r\n", "\n")
                    md.append("\n##%s" % trim_metadata(raw_data))
    return md

def generate_linked_spell_lists(spell_map):
    spell_list = convert_spells_map_to_list(spell_map)
    for root, directories, files in os.walk(spell_list_src):
        if not directories:
            class_name = os.path.split(root)[1]
            class_files_path = root
            print("Generating spell list for class: %s" % class_name)
            class_md = generate_md_spell_list(class_name, class_files_path)
            write_md_to_file(class_md, os.path.join(class_spell_lists_output, "%s_spells.md" % class_name))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", default=False)
    args = parser.parse_args()
    if args.offline:
        print("Generating in offline mode")
    create_output_directories()
    spell_map = construct_spell_map()
    item_map = construct_item_map()
    monster_map = construct_monster_map()

    generate_spells_by_level(spell_map)
    generate_spells_by_name(spell_map)
    generate_spells_by_school(spell_map)
    generate_linked_spell_lists(spell_map)

    generate_items_by_name(item_map)
    generate_items_by_type(item_map)

    generate_monsters_by_name(monster_map)
    generate_monsters_by_type(monster_map)
    generate_monsters_by_cr(monster_map)
