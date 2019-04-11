from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
import markdown
content_dir, template_dir, output_dir = Path('content'), Path('templates'), Path('output')
md = markdown.Markdown(extensions=['meta', 'codehilite', 'fenced_code', 'toc', 'attr_list', 'tables', 'toc'])
env = Environment(loader=FileSystemLoader(['templates', '.']), trim_blocks=True, lstrip_blocks=True)
def jinja_path(*patterns):
    items = []
    for pattern in patterns:
        for path in content_dir.glob(pattern):
            md.convert(path.read_text())
            items.append({**{k:v[0] for k, v in md.Meta.items()}, 'path':path.relative_to(content_dir).with_suffix('.html')})
    return items
for content_file in content_dir.rglob('*'):
    output_file = output_dir.joinpath(content_file.relative_to(content_dir))
    output_file.parent.mkdir(exist_ok=True)
    print(f'parsing {content_file}')
    if content_file.suffix.lower() == '.md':
        html = md.convert(content_file.read_text())
        if 'template' in md.Meta:
            template = env.get_template(template_dir.joinpath(md.Meta['template'][0]).as_posix())
            output_file.with_suffix('.html').write_text(template.render(**{k:v[0] for k, v in md.Meta.items()}, content=html))
    elif content_file.suffix == '.html':
        template = env.get_template(content_file.as_posix())
        output_file.write_text(template.render(path=jinja_path))
    elif content_file.is_file():
        if output_file.is_symlink():
            output_file.unlink()
        output_file.symlink_to(content_file.resolve())