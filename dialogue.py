import json

EXIT_CONSTS = set(['q', 'quit', 'exit'])
YES_CONSTS = set(['y', 'yes'])
HELP_CONSTS = set(['?', 'help'])

# Json parameters might be subject to change.
TEMPLATE_DATA = 'TemplateData'
RUN_LIST = 'RunList'
RUNLIST_ARGS = 'args'
TAG_ARG = 'Tag'
RUN_TEMPLATE_TYPE = 'template_type'

TEMPLATE_ARGS = 'args'
TEMPLATE_ANNO = 'annotations'
TEMPLATE_TYPES = 'types'
TEMPLATE_TRANS = 'translations'
TEMPLATE_DEFAULT = 'default_props' 

def write_json(filename, python_dict):
    """ 
    Serialize python_dict (dictionary) to filename (text file).
    :param filename: string
    :param python_dict: dict
    """
    with open(filename, 'w') as f:
        json.dump(python_dict, f, indent=4)


def read_json(filename):
    """ 
    Deserializes json formatted string from filename (text file) as a dictionary.
    :param filename: string
    """
    with open(filename) as f:
        return json.load(f)

def print_dict(d):
    for key, value in sorted(d.items(), key=lambda x : x[0]):
        print("{}: {}".format(key, value))

def tag_in_runlist(tag, run_list):
    """
    Returns True if a Run with tag `tag` is in the list.
    """
    return any(map(lambda run : run[RUNLIST_ARGS][TAG_ARG] == tag, run_list))

# Level-one layer of dialogue. All functions take run_dict, template_dict as
# arguments so that they can be called homogeneously from a dictionary in
# `dialogue`. All functions must, in turn, *return* a tuple (run_dict,
# template_dict) as arguments.

def print_all_runs(run_list, template_dict):
    """
    Prints all runs in the RunList. Note that it gets the argument order from
    `template_dict`.
    """
    for run in run_list:
        print('\nTemplate Type: {}'.format(run[RUN_TEMPLATE_TYPE]))
        for arg in template_dict[run[RUN_TEMPLATE_TYPE]][RUNLIST_ARGS]:
            print('{}: {}'.format(arg, run[RUNLIST_ARGS][arg]))
        print()
    return (run_list, template_dict)

def create_run(run_list, template_dict):
    new_run = {}
    # Inputting run type.
    print('Input the run type. Current options: {}'.format(
            ' '.join(sorted(template_dict.keys()))))
    run_type = input('-> ')
    if run_type not in template_dict.keys():
        user_input = input('{} is not currently an option. Add it? ')
        if user_input.lower() in YES_CONSTS:
            pass
        return
    new_run[RUN_TEMPLATE_TYPE] = run_type
    new_run[RUNLIST_ARGS] = {}

    # Input values.
    for arg in template_dict[run_type][RUNLIST_ARGS]:
        while True:
            try:
                user_input = input('{}: '.format(arg))
                if user_input in EXIT_CONSTS:
                    print('Aborting. New run not added.')
                    return (run_list, template_dict)
                elif user_input in HELP_CONSTS:
                    print('Annotation:\n{}\nType:\n{}\n'.format(
                          template_dict[run_type]['annotations'][arg],
                          template_dict[run_type]['types'][arg]))
                else: 
                    new_run[RUNLIST_ARGS][arg] = user_input
                    break
            except:
                print('Invalid input.')
    
    # Validate tag uniqueness.
    while tag_in_runlist(new_run[RUNLIST_ARGS][TAG_ARG], run_list):
        new_run[RUNLIST_ARGS][TAG_ARG] = input('Duplicate tag! Input a new tag. ')
    run_list.append(new_run)
    print('Run {} added to list.'.format(new_run[RUNLIST_ARGS][TAG_ARG]))
    return (run_list, template_dict)

def create_runtype(run_list, template_dict):
    new_template = {}
    new_template[TEMPLATE_ARGS] = []
    new_template[TEMPLATE_ANNO] = {}
    new_template[TEMPLATE_TYPES] = {}
    new_template[TEMPLATE_TRANS] = {}
    new_template[TEMPLATE_DEFAULT] = {}

    # Template name must be unique.
    while True:
        new_template_name = input('Input the name of the new Template. ')
        if new_template_name not in template_dict.keys():
            break
        if input('Template name already exists! Do you want to delete it? ')\
           in YES_CONSTS:
            break

    # Args.
    while True:
        new_arg = input('Input an arg. ')
        if not new_arg:
            continue
        if new_arg in EXIT_CONSTS:
            break
        if new_arg in new_template[TEMPLATE_ARGS]:
            if input('Argument already exists! Overwrite? ') not in YES_CONSTS:
                continue
        new_arg_type = input('Input a type for the arg. Default is string. ')
        if new_arg_type in EXIT_CONSTS:
            break
        # TODO: Needs validation!!
        new_arg_annotation = input('Input an annotation for the arg. ')
        if new_arg_annotation in EXIT_CONSTS:
            break
        new_arg_trans = input('Input the property that will be modified. '\
                              'Blank input skips this step. ')
        if new_arg_trans in EXIT_CONSTS:
            break
        
        print('Current argument:\n',
              'Arg: {}\n'.format(new_arg),
              'Type: {}\n'.format(new_arg_type),
              'Annotation: {}\n'.format(new_arg_annotation),
              'Translation: {}'.format(new_arg_trans))
        if input('Add to the argument? ') in YES_CONSTS:
            if new_arg not in new_template[TEMPLATE_ARGS]:
                new_template[TEMPLATE_ARGS].append(new_arg)
            new_template[TEMPLATE_ANNO][new_arg] = new_arg_annotation
            new_template[TEMPLATE_TYPES][new_arg] = new_arg_type
            if new_arg_trans:
                new_template[TEMPLATE_TRANS][new_arg] = new_arg_trans
    
    # Default props.
    while True:
        default_property = input('Input a default property. Blank or \'exit\' '\
                                 'exits. ')
        if not default_property or default_property in EXIT_CONSTS:
            break
        if default_property in new_template[TEMPLATE_DEFAULT].keys():
            if input('Property is already in template! Overwrite? ')\
                in YES_CONSTS:
                continue
        value = input('Input a value for the property. ')
        new_template[TEMPLATE_DEFAULT][default_property] = value

    if input('Add template to the TateConfig? ') in YES_CONSTS:
        template_dict[new_template_name] = new_template
        print('Template {} added.'.format(new_template_name))
    else:
        if input('Are you sure? ') not in YES_CONSTS:
            template_dict[new_template_name] = new_template
            print('Template {} added.'.format(new_template_name))

    return run_list, template_dict

def delete_run(run_list, template_dict):
    print('Input the tag of the Run that you want to delete. Available tags')
    print('are {}'.format(
                   ' '.join(run[RUNLIST_ARGS]['Tag'] for run in run_list)))
    delete_tag = input('-> ')

    new_run_list = [run for run in run_list 
                    if run[RUNLIST_ARGS]['Tag'] != delete_tag]
    if len(run_list) == len(new_run_list):
        print('Tag {} does not exist.'.format(delete_tag))
    else:
        if input('Found tag {}. Do you want to delete? '.format(delete_tag)) \
           in YES_CONSTS:
            print('Tag {} deleted.'.format(delete_tag))
            run_list = new_run_list
        else:
            print('Deletion of tag {} cancelled.'.format(delete_tag))
    return run_list, template_dict


def error(run_dict, template_dict):
    print('Invalid input.')
    return run_dict, template_dict


def dialogue():
    """
    A dialogue function for creating, editing, and saving TateConfig objects
    as JSON objects.
    """

    default_json = 'example_config2.json'

    json_filename = input('Input TateConfig filename. Default = {} '\
                          .format(default_json))
    if not json_filename:
        json_filename = default_json

    function_dict = {
        'print all' : print_all_runs,
        'create run' : create_run,
        'create runtype' : create_runtype,
        'delete run' : delete_run,
    }

    option_description_dict = {
        'print all' : 'Print all runs',
        'create run' : 'Create a run',
        'create runtype' : 'Create a runtype',
        'delete run' : 'Delete a run',
    }

    try:
        tate_config = read_json(json_filename)
        run_list = tate_config[RUN_LIST]
        template_dict = tate_config[TEMPLATE_DATA]
    except:
        user_input = input("Unable to open file. Open a blank file? ")
        if user_input not in YES_CONSTS:
            return
        run_list = []
        template_dict = {}
    if run_list and template_dict:
        print('TateConfig successfully loaded.')
    else:
        print('Blank TateConfig created.')

    user_input = ""

    while user_input.lower() not in EXIT_CONSTS:
        print("\nWhat would you like to do?\n")
        print_dict(option_description_dict)
        user_input = input("-> ")
        if user_input.lower() in HELP_CONSTS:
            continue
        elif user_input.lower() not in EXIT_CONSTS:
            run_list, template_dict = function_dict.get(user_input, error)(run_list, template_dict)
    print('Exiting.')


