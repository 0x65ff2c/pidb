import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pidb.settings')
import django
django.setup()
from tabby.models import *

def main():
    with open('tags') as f:
        str = f.read()
        list = str.split('\n')
    tag_list = []
    for tem in list:
        if len(tem) > 2:
            tag = {}
            tem_list = tem.split('$')
            print(tem_list)
            tag['tag_name'] = tem_list[0]
            tag['base_tag'] = tem_list[1]
            tag['description'] = tem_list[2]
            tag_list.append(tag)
    '''
    for tag in Category.objects.all():
        tag.delete()
    '''
    for tag in tag_list:
        if tag['tag_name'] == tag['base_tag']:
            tem_tag = Category(name=tag['tag_name'], description=tag['description'])
        else:
            tem_tag = Category(name=tag['tag_name'], description=tag['description'], base=Category.objects.get(name=tag['base_tag']))
        tem_tag.save()

if __name__ == '__main__':
    main()

