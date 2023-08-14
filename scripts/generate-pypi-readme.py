# PyPI does not support light/dark mode header images yet, per: https://github.com/pypi/warehouse/issues/11251
# So for now, we'll have to do it manually

raw = open("./readme.md", encoding="utf-8")
readme = raw.readlines()

img_tag = '<img alt="Architect Logo" src="https://github.com/architect/assets.arc.codes/raw/main/public/architect-logo-500b%402x.png">\n'
readme.insert(0, img_tag)
del readme[1:5]

new_readme = open("./readme_pypi.md", "w", encoding="utf-8")
new_readme.write("".join(readme))
print("Generated PyPI friendly readme")
