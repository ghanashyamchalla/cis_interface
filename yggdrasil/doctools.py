import re
import os
import textwrap


def write_table(lines, fname=None, fname_base=None, fname_dir=None,
                verbose=False, **kwargs):
    r"""Write a table to a file.

    Args:
        fname (str, optional): Name of the file where the table should be written.
            If not provided, one is constructed from fname_base and fname_dir.
        fname_base (str, optional): Base name of the file where the table should
            be written if fname is not provided. If fname is None, fname_base
            must be provided.
        fname_dir (str, optional): Directory where the table should be written
            if fname is not provided. If not provided, this defaults to the
            current working directory.
        verbose (bool, optional): If True, the lines are printed to standard
            out in addition to the file. Defaults to False.
        **kwargs: Additional keyword arguments are ignored.

    Returns:
        str: Name of file created.

    Raises:
        ValueError: If neither fname nor fname_base are provided.

    """
    if fname is None:
        if fname_base is None:
            raise ValueError("If fname is not provided, fname_base must be.")
        if fname_dir is None:
            fname_dir = os.getcwd()
        fname = os.path.join(fname_dir, fname_base)
    else:
        fname_dir, fname_base = os.path.split(fname)
    fname_ref = fname_base.replace('.rst', '_rst')
    # Write
    lines = ['.. _%s:' % fname_ref, ''] + lines
    with open(fname, 'w') as fd:
        fd.write('\n'.join(lines))
    if verbose:
        print('\n'.join(lines))
    return fname


def write_datatype_table(table_type='all', **kwargs):
    r"""Write a table containing entries from the descriptions of datatypes.

    Args:
        table_type (str, optional): Type of table that should be created for the
            class. Defaults to 'all'. Supported values include:

            * 'all': Create each type of table.
            * 'simple': Create a table of standard JSON datatypes.
            * 'container': Create a table of container datatypes.
            * 'yggdrasil': Create a table of yggdrasil specific datatypes.

        **kwargs: Additional keyword arguments are passed to dict2table and
            write_table.

    Returns:
        str, list: Name of file or files created.

    Raises:
        ValueError: If table_type is not one of the supported values.

    """
    from yggdrasil.metaschema.datatypes import _type_registry
    table_type_list = ['simple', 'container', 'yggdrasil']
    if table_type == 'all':
        fname = kwargs.get("fname", None)
        fname_base = kwargs.get("fname_base", None)
        assert((fname is None) and (fname_base is None))
        out = []
        for k in table_type_list:
            out.append(write_datatype_table(table_type=k, **kwargs))
        return out
    elif table_type not in table_type_list:
        raise ValueError("Unsupported table_type: '%s'" % table_type)
    fname_format = 'datatype_table_%s.rst'
    kwargs.setdefault('fname_base', fname_format % (table_type))
    args = {}
    if table_type == 'simple':
        for k, v in _type_registry.items():
            if v._replaces_existing and (not hasattr(v, '_container_type')):
                args[k] = v.description
    elif table_type == 'container':
        for k, v in _type_registry.items():
            if v._replaces_existing and hasattr(v, '_container_type'):
                args[k] = v.description
    elif table_type == 'yggdrasil':
        for k, v in _type_registry.items():
            if not v._replaces_existing:
                args[k] = v.description
    kwargs.setdefault('key_column_name', 'type')
    lines = dict2table(args, **kwargs)
    return write_table(lines, **kwargs)
    

def write_classdocs_table(class_, table_type='all', **kwargs):
    r"""Write a table containing entries from a section in a class's
    documentation.

    Args:
        class_ (type): Class with docstring that should be parsed.
        table_type (str, optional): Type of table that should be created for the
            class. Defaults to 'all'. Supported values include:

            * 'all': Create each type of table for the specified class.
            * 'args': Create a table of the class's argumetns.
            * 'attr': Create a table of the class's attributes.
            * 'classattr': Create a table of the class's class attributes.

        **kwargs: Additional keyword arguments are passed to dict2table and
            write_table.

    Returns:
        str, list: Name of file or files created.

    Raises:
        ValueError: If table_type is not one of the supported values.

    """
    table_type2keys = {'args': ['Args:', 'Arguments:'],
                       'attr': ['Attr:', 'Attributes:'],
                       'classattr': ['Class Attr:', 'Class Attributes']}
    table_type_list = list(table_type2keys.keys())
    if table_type == 'all':
        fname = kwargs.get("fname", None)
        fname_base = kwargs.get("fname_base", None)
        assert((fname is None) and (fname_base is None))
        out = []
        for k in table_type_list:
            out.append(write_classdocs_table(class_, table_type=k, **kwargs))
        return out
    elif table_type not in table_type2keys:
        raise ValueError("Unsupported table_type: '%s'" % table_type)
    fname_format = 'class_table_%s_%s.rst'
    kwargs.setdefault('fname_base', fname_format % (class_.__name__, table_type))
    args = docs2args(class_.__doc__, keys=table_type2keys[table_type])
    if table_type == 'args':
        for k, v in args.items():
            if v.get('type', '').endswith(', optional'):
                v['type'] = v['type'].split(', optional')[0]
                v['required'] = ''
            else:
                v['required'] = 'X'
    else:
        for k, v in args.items():
            if v.get('description', '').endswith(' [REQUIRED]'):
                v['description'] = v['description'].split(' [REQUIRED]')[0]
                v['required'] = 'X'
            else:
                v['required'] = ''
    lines = dict2table(args, **kwargs)
    return write_table(lines, **kwargs)


def write_component_table(comp='all', table_type='all', **kwargs):
    r"""Write a component table to a file.

    Args:
        comp (str): Name of a component type to create a table for. Defaults to
            'all' and tables are created for each of the registered components.
        table_type (str, optional): Type of table that should be created for the
            component. Defaults to 'all'. Supported values include:

            * 'all': Create each type of table for the specified component.
            * 'general': Create a table of properties common to all components
              of the specified type.
            * 'specific': Create a table of properties specific to only some
              components of the specified type.
            * 'subtype': Create a table describing the subtypes available for
              the specified component type.

        **kwargs: Additional keyword arguments are passed to component2table
            and write_table.

    Returns:
        str, list: Name of file or files created.

    """
    from yggdrasil.schema import get_schema
    s = get_schema()
    table_type_list = ['subtype', 'general', 'specific']
    # Loop
    if comp == 'all':
        fname = kwargs.get("fname", None)
        fname_base = kwargs.get("fname_base", None)
        assert((fname is None) and (fname_base is None))
        out = []
        for k in s.keys():
            new_out = write_component_table(comp=k, table_type=table_type, **kwargs)
            if isinstance(new_out, list):
                out += new_out
            else:
                out.append(new_out)
        return out
    if table_type == 'all':
        fname = kwargs.get("fname", None)
        fname_base = kwargs.get("fname_base", None)
        assert((fname is None) and (fname_base is None))
        out = []
        for k in table_type_list:
            out.append(write_component_table(comp=comp, table_type=k, **kwargs))
        return out
    # Construct file name
    fname_format = 'schema_table_%s_%s.rst'
    kwargs.setdefault('subtype_ref',
                      (fname_format % (comp, 'subtype')).replace('.rst', '_rst'))
    kwargs.setdefault('fname_base', fname_format % (comp, table_type))
    lines = component2table(comp, table_type, **kwargs)
    return write_table(lines, **kwargs)


def component2table(comp, table_type, include_required=None,
                    subtype_ref=None, **kwargs):
    r"""Create a table describing a component.

    Args:
        comp (str): Name of a component type to create a table for.
        table_type (str): Type of table that should be created for the component.
            Supported values include:

            * 'general': Create a table of properties common to all components
              of the specified type.
            * 'specific': Create a table of properties specific to only some
              components of the specified type.
            * 'subtype': Create a table describing the subtypes available for
              the specified component type.

        include_required (bool, optional): If True, a required column is
            included. Defaults to True if table_type is 'general' and False
            otherwise.
        subtype_ref (str, optional): Reference for the subtype table for the
            specified component that should be used in the description for the
            subtype property. Defaults to None and is ignored.
        **kwargs: Additional keyword arguments are passed to dict2table.

    Returns:
        list: Lines comprising the table.

    """
    from yggdrasil.schema import get_schema
    if include_required is None:
        if table_type == 'general':
            include_required = True
        else:
            include_required = False
    if table_type in ['subtype', 'specific']:
        kwargs.setdefault('prune_empty_columns', True)
    args = {}
    s = get_schema()
    subtype_key = s[comp].subtype_key
    if table_type in ['general', 'specific']:
        # Set defaults
        kwargs.setdefault('key_column_name', 'option')
        kwargs.setdefault('val_column_name', 'description')
        kwargs.setdefault('column_order', [kwargs['key_column_name'],
                                           'type', 'required',
                                           kwargs['val_column_name']])
        if (not include_required) and ('required' in kwargs['column_order']):
            kwargs['column_order'].remove('required')
        # Get list of component subtypes
        if table_type == 'general':
            s_comp_list = [s[comp].get_subtype_schema('base', unique=True)]
        else:
            s_comp_list = [s[comp].get_subtype_schema(x, unique=True)
                           for x in s[comp].classes]
        # Loop over subtyeps
        out_apply = {}
        for s_comp in s_comp_list:
            for k, v in s_comp['properties'].items():
                if (k == subtype_key) and (table_type == 'specific'):
                    continue
                if k not in args:
                    args[k] = {'type': v.get('type', ''),
                               'description': v.get('description', '')}
                    if include_required:
                        if k in s_comp.get('required', []):
                            args[k]['required'] = ''
                        else:
                            args[k]['required'] = 'X'
                if (table_type == 'specific'):
                    if k not in out_apply:
                        out_apply[k] = []
                    out_apply[k] += s_comp['properties'][subtype_key]['enum']
                elif (subtype_ref is not None) and (k == subtype_key):
                    args[k]['description'] += (
                        ' (Options described :ref:`here <%s>`)' % subtype_ref)
        if table_type == 'specific':
            for k, v in args.items():
                v['Valid for \'%s\' of' % subtype_key] = list(set(out_apply[k]))
    elif table_type == 'subtype':
        kwargs.setdefault('key_column_name', subtype_key)
        for x, subtypes in s[comp].schema_subtypes.items():
            s_comp = s[comp].get_subtype_schema(x, unique=True)
            subt = subtypes[0]
            args[subt] = {
                'description': s_comp['properties'][subtype_key].get(
                    'description', '')}
            if len(subtypes) > 1:
                args[subt]['aliases'] = subtypes[1:]
            if s_comp['properties'][subtype_key].get('default', None) in subtypes:
                args[subt]['description'] = ('[DEFAULT] '
                                             + args[subt]['description'])
    else:
        raise ValueError("Unsupported table_type: '%s'" % table_type)
    return dict2table(args, **kwargs)


def dict2table(args, key_column_name='option', val_column_name='description',
               column_order=None, wrapped_columns=None,
               sort_on_key=True, prune_empty_columns=False, **kwargs):
    r"""Convert a dictionary to a table.

    Args:
        args (dict): Dictionary of entries for the table. The keys will go in
            the first column (the key column) as named by key_column_name.
            If the values are dictionaries, the elements in each dictionary
            will be put in different columns. If the values are strings, they
            will be put in the column identified by val_column_name.
        key_column_name (str, optional): Label that the key column should have.
            Defaults to 'option'.
        val_column_name (str, optional): Lable that the value column should have.
            Defaults to 'description'.
        column_order (list, optional): List specifying the roder that fields
            should be added to the table as columns. Defaults to None and is set
            to [key_column_name, val_column_name]. If a column is missing from
            an entry in args, an empty value will be added to the table in its
            place. Columns in args entries that are not in column_order are
            appended to column_order in sorted order.
        wrapped_columns (dict, optional): Dictionary specifying fields that
            should be wrapped as columns and the widths that the corresponding
            column should be wrapped to. Defaults to {'Description': 80}.
        sort_on_key (bool, optional): If True, the entries in args are added
            as rows in the order determined by sorting on the keys. If False,
            the order will be determine by prop (which is not deterministic
            if a Python 2 dictionary). Defaults to True.
        prune_empty_columns (bool, optional): If True, empty columns will be
            removed. If False, they will be included. Defaults to False.
        **kwargs: Additional keyword arguments are ignored.
            
    Returns:
        list: Lines comprising the table.

    """
    if wrapped_columns is None:
        wrapped_columns = {'description': 80}
    # Determine column order
    if column_order is None:
        column_order = [key_column_name, val_column_name]
    # Create dictionary of columns
    columns = {k: [] for k in column_order}
    pos = 0
    prop_order = list(args.keys())
    if sort_on_key:
        prop_order = sorted(prop_order)
    for k in prop_order:
        v = args[k]
        if not isinstance(v, dict):
            v = {val_column_name: v}
        for pk in v.keys():
            if pk not in columns:
                columns[pk] = pos * ['']
        for pk in columns.keys():
            if pk == key_column_name:
                columns[key_column_name].append(k)
            else:
                columns[pk].append(str(v.get(pk, '')))
        pos += 1
    # Add non-standard fields
    for k in sorted(columns.keys()):
        if k not in column_order:
            column_order.append(k)
    # Prune empty columns
    column_widths = {}
    for k in list(columns.keys()):
        if len(columns[k]) == 0:
            column_widths[k] = 0
        else:
            column_widths[k] = len(max(columns[k], key=len))
        if prune_empty_columns and (column_widths[k] == 0):
            del column_widths[k]
            del columns[k]
            column_order.remove(k)
    # Get sizes that include headers and wrapping
    for k in columns.keys():
        if k in wrapped_columns:
            w = wrapped_columns[k]
        else:
            w = column_widths[k]
        column_widths[k] = max(w, len(k))
    # Create format string
    column_sep = '   '
    column_format = column_sep.join(['%-' + str(column_widths[k]) + 's'
                                     for k in column_order])
    divider = column_sep.join(['=' * column_widths[k]
                               for k in column_order])
    header = column_format % tuple([k.title() for k in column_order])
    # Table
    if len(columns) == 0:
        pos = 0
    else:
        pos = len(columns[list(columns.keys())[0]])
    lines = [divider, header, divider]
    for i in range(pos):
        row = []
        max_row_len = 1
        for k in column_order:
            if k in wrapped_columns:
                row.append(textwrap.wrap(columns[k][i], wrapped_columns[k]))
            else:
                row.append([columns[k][i]])
            max_row_len = max(max_row_len, len(row[-1]))
        for j in range(len(row)):
            row[j] += (max_row_len - len(row[j])) * ['']
        for k in range(max_row_len):
            lines.append(column_format % tuple([row[j][k] for j in range(len(row))]))
    lines.append(divider)
    return lines


def docs2args(docs, keys=['Args:', 'Arguments:']):
    r"""Get a dictionary of arguments and argument descriptions from a docstring.

    Args:
        docs (str): Docstring that should be parsed.
        keys (list): Strings that should be used to identify the target section
            in the docstring. Defaults to ['Args:', 'Arguments:'].

    Returns:
        dict: Dictionary of arguments/description pairs.

    """
    if docs is None:
        return {}
    docs_lines = docs.splitlines()
    # Isolate arguments section based on heading
    in_args = False
    args_lines = []
    for x in docs_lines:
        if in_args:
            if (len(x.strip()) == 0) or (not x.startswith(8 * ' ')):
                # Blank line or no indent indicates new section
                in_args = False
                break
            else:
                args_lines.append(x)
        elif any([x.startswith('    %s' % k) for k in keys]):
            in_args = True
    # Parse argument lines
    out = {}
    curr_arg = None
    for x in args_lines:
        if x.startswith(12 * ' '):
            out[curr_arg]['description'] += ' ' + x.strip()
        else:
            re_arg = r'        ([\S]+)[\s]+\(([^\)]+)\):[\s]+([\S\s]+)'
            x_match = re.match(re_arg, x)
            if x_match is None:
                break
            curr_arg = x_match.group(1)
            out[curr_arg] = {'type': x_match.group(2),
                             'description': x_match.group(3)}
    return out
