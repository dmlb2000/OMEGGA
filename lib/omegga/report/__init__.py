#!/usr/bin/python
from os import makedirs, getcwd
from os.path import join
from uuid import uuid4
from jinja2 import Environment, FileSystemLoader
from installed_clients.DataFileUtilClient import DataFileUtil

def generate_report(dfu: DataFileUtil, scratchdir: str, renderargs: dict, template_name: str = 'report.html'):
    """
    Generate HTML report from output of the code.

    Args:
        dfu (DataFileUtil): DataFileUtil for uploading HTML bundles.
        scratchdir (str): Scratch directory for loading the HTML files.
    """
    output_directory = join(scratchdir, str(uuid4()))
    makedirs(output_directory, exist_ok=True)
    env = Environment(
        loader=FileSystemLoader(['/kb/module/templates', '/kb/module/lib/templates'])
    )
    template = env.get_template(f"{template_name}.j2")
    result_file_path = join(output_directory, template_name)
    with open(result_file_path, 'w') as result_file:
        result_file.write(template.render(**renderargs))
    report_shock_id = dfu.file_to_shock({
        'file_path': output_directory,
        'pack': 'zip'
    })['shock_id']
    return [{
        'shock_id': report_shock_id,
        'name': template_name,
        'label': template_name,
        'description': 'HTML summary report for OMEGGA App'
    }]
