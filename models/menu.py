# coding: utf8
response.menu = [
  (T('Home'), False, URL('default', 'index')),
  (T('Table of Hardware'), False, URL('default', 'router')),
]

if 'auth' in globals() and auth.user:
    response.menu.append((T('Edit'), False, URL('default', 'edit')))
