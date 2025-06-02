import ast
import logging
import os.path
import sys

import coverage

# 3.5->3.6: Added `Constant` (unified literal representation)
# 3.7->3.8: Removed `Num`/`Str`/`Bytes`/`NameConstant`/`Ellipsis`, unified as `Constant`
if sys.version_info < (3, 8):
    PLACEHOLDER = ast.Ellipsis()
    
    def is_string_comment(node):
        return isinstance(node, ast.Expr) and isinstance(node.value, ast.Str)
else:
    PLACEHOLDER = ast.Constant(value=Ellipsis)
    
    def is_string_comment(node):
        return isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)

if sys.version_info < (3, 9):
    from astor import to_source as unparse
else:
    from ast import unparse


def remove_string_comments_and_consecutive_placeholders(body):
    result = []
    prev_was_target = False

    for x in body:
        if is_string_comment(x):
            continue
        elif x == PLACEHOLDER:
            if not prev_was_target:
                result.append(x)
                prev_was_target = True
        else:
            result.append(x)
            prev_was_target = False

    return result


class CoverageSketch(ast.NodeTransformer):
    def __init__(self, covered_lines):
        self.covered_lines = set(covered_lines)

    def generic_visit(self, node):
        # Skip nodes with line numbers not in coverage
        if hasattr(node, 'lineno'):
            start = node.lineno
            end = getattr(node, 'end_lineno', start)
            if not any(line in self.covered_lines for line in range(start, end + 1)):
                if isinstance(node, (ast.expr, ast.stmt)):
                    return PLACEHOLDER
                else:
                    return node

        # Apply normal traversal
        node = super().generic_visit(node)

        # Clean up bodies to avoid multiple pass
        for field, value in ast.iter_fields(node):
            if isinstance(value, list):
                new_body = remove_string_comments_and_consecutive_placeholders(value)
                setattr(node, field, new_body)
        
        return node


def extract_sketch(filename, covered_lines):
    with open(filename, 'r') as f:
        source = f.read()

    tree = ast.parse(source, filename=filename)
    filtered_tree = CoverageSketch(covered_lines).visit(tree)
    ast.fix_missing_locations(filtered_tree)

    return unparse(filtered_tree)


def extract_sketches(coverage_file_path):
    # Initialize coverage object
    cov = coverage.Coverage(data_file=coverage_file_path)

    # Load .coverage file
    cov.load()

    # Get coverage data
    data = cov.get_data()

    measured_files = data.measured_files()
    
    sketches = {}
    
    for measured_file in measured_files:
        if not os.path.isfile(measured_file):
            logging.error("Cannot find script file: %s", measured_file)
            continue
        
        sketch = extract_sketch(measured_file, data.lines(measured_file))
        
        sketches[measured_file] = sketch
    
    return sketches


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--coverage-file', type=str, required=True)
    args = parser.parse_args()

    measured_files_to_sketches = extract_sketches(args.coverage_file)

    for measured_file, sketch in measured_files_to_sketches.items():
        print('`%s`:' % measured_file)
        print()
        print('```python')
        print(sketch)
        print('```')
        print()
