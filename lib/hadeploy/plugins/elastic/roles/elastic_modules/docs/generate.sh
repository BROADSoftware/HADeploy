
ansible-doc -M ../library/ elasticsearch_index 2>/dev/null | sed 's/[(].*elastic_modules[/]library.*[)]//' >elasticsearch_index.txt
ansible-doc -M ../library/ elasticsearch_template 2>/dev/null | sed 's/[(].*elastic_modules[/]library.*[)]//' >elasticsearch_template.txt
