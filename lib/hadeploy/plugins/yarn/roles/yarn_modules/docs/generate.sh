
ansible-doc -M ../library/ yarn_services 2>/dev/null | sed 's/[(].*yarn_modules[/]library.*[)]//' >yarn_services.txt
